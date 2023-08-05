"""entity classes for vcsfile content types

:organization: Logilab
:copyright: 2007-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
import os, os.path as osp
from contextlib import contextmanager
import tempfile
import shutil
import errno
from itertools import izip_longest

import hglib
from hglib import context
from hglib.error import CommandError

from yams import ValidationError
from cubicweb import QueryError
from cubicweb.predicates import is_instance, score_entity
from cubicweb.view import EntityAdapter

from cubes.vcsfile import bridge
from cubes.vcsfile.hooks import repo_cache_dir


class HGRepo(EntityAdapter):
    __regid__ = 'VCSRepo'
    __select__ = (is_instance('Repository') &
                  score_entity(lambda repo: repo.type == u'mercurial'))
    configs = None
    path = None

    def full_path(self, path):
        return osp.join(self.path, path)

    def __contains__(self, path):
        with self.hgrepo() as hgclient:
            return path in hgclient.manifest(all=True)

    def _create_repo(self):
        if osp.exists(self.path):
            return
        hglib.init(self.path)

    def __init__(self, *args, **kwargs):
        super(HGRepo, self).__init__(*args, **kwargs)
        cnx = self._cw
        try:
            security_enabled = cnx.security_enabled
        except AttributeError:
            # XXX Request objects don't have that method in cw 3.19
            security_enabled = cnx.cnx.security_enabled

        cacheroot = repo_cache_dir(self.entity._cw.vreg.config)
	# deactivate read security first, needed to get access to local_cache
        with security_enabled(read=False):
            if cacheroot is not None and self.entity.local_cache is not None:
                self.path = osp.join(cacheroot, self.entity.local_cache)

        if not self.path:
            raise ValidationError(self.entity.eid,
                    {'source_url': cnx._('no local access to repository')})

        if not osp.exists(self.path):
            self._create_repo() # ensure local cache exists

    @contextmanager
    def hgrepo(self):
        client = hglib.client.hgclient(self.path, encoding=self.entity.encoding,
                                       configs=self.configs, connect=False)
        client.hidden = True
        with client:
            yield client

    def manifest(self, rev):
        with self.hgrepo() as hgclient:
            return list(hgclient.manifest(rev=rev))

    def file_deleted(self, path):
        with self.hgrepo() as repo:
            log = repo.log(files=[self.full_path(path)], removed=True, limit=1)
            if not log:
                raise Exception('this file does not even exist')
            head = log[0][1][:12]
            for file in repo.manifest(rev=head):
                if file[4] == path:
                    return False
            return True

    def next_versions(self, rev, path):
        with self.hgrepo() as repo:
            return repo.log(files=[self.full_path(path)], revrange='%s::' % rev.changeset)

    def previous_versions(self, rev, path):
        with self.hgrepo() as repo:
            return repo.log(files=[self.full_path(path)], revrange='::%s' % rev.changeset)

    def root(self):
        with self.hgrepo() as repo:
            return repo.root()

    def head(self, path):
        with self.hgrepo() as repo:
            return repo.log(files=[self.full_path(path)], limit=1, removed=True)[0]

    def log(self, path=None, **args):
        args.setdefault('removed', True)
        with self.hgrepo() as repo:
            if path is not None:
                args['files'] = [self.full_path(path)]
            return repo.log(**args)

    def log_rset(self, path=None, **args):
        """Returns a ResultSet of the Revisions
        """
        args.setdefault('removed', True)
        log = self.log(path, **args)
        # XXX what a funny joke
        # we need to split the big IN into several queries to
        # prevent a "Too many SQL variables" error
        rsets = []
        # itertools grouper pattern
        args = [iter(log)] * 50
        for partiallog in izip_longest(fillvalue=None, *args):
            rql =  ('Revision R ORDERBY R DESC WHERE '
                    'R from_repository REPO, REPO eid %%(x)s, R changeset IN (%s)'
                    % ','.join('"%s"' % rev.node[:12].decode('ascii')
                               for rev in partiallog if rev is not None))
            rsets.append(self._cw.execute(rql,
                                          {'x': self.entity.eid}))
        if rsets:
            return reduce(lambda x, y: x+y, rsets)
        return self._cw.empty_rset()

    def status(self, cset):
        import hglib.context
        with self.hgrepo() as repo:
            return hglib.context.changectx(repo, cset).files()

    def cat(self, rev, path):
        with self.hgrepo() as repo:
            return repo.cat([self.full_path(path)], rev=rev)

    def add_revision(self, description, author, branch, parent, added, deleted):
        tmpdir = tempfile.mkdtemp()
        hglib.clone(self.full_path(''), tmpdir, rev=parent, updaterev=parent)
        try:
            with hglib.open(tmpdir) as client:
                if branch is not None:
                    client.branch(branch, force=True)
                for (file, content) in added:
                    path = osp.realpath(osp.join(tmpdir, file))
                    assert path.startswith(osp.realpath(tmpdir))
                    try:
                        os.makedirs(osp.dirname(path))
                    except OSError as exc:
                        if exc.errno != errno.EEXIST:
                            raise
                    with open(path, 'wb') as f:
                        while True:
                            buf = content.read(4096)
                            if not buf:
                                break
                            f.write(buf)
                for file in deleted:
                    path = osp.realpath(osp.join(tmpdir, file))
                    assert path.startswith(osp.realpath(tmpdir))
                    try:
                        os.unlink(path)
                    except OSError as exc:
                        if exc.errno == errno.ENOENT:
                            raise QueryError('%s is already deleted from the vcs' % file)
                        raise
                rev, cset = client.commit(message=description, addremove=True, user=author)
                client.push(rev=cset, force=True)
                return cset[:12]
        finally:
            shutil.rmtree(tmpdir)

    def pull(self):
        self._create_repo()
        if self.entity.source_url:
            with self.hgrepo() as hgrepo:
                try:
                    hgrepo.pull(source=self.entity.source_url)
                except CommandError as exc:
                    raise EnvironmentError('pull or clone from %s failed %s' %
                                           (self.entity.source_url, exc))

    def import_content(self, commitevery):
        cnx = self._cw
        try:
            self.pull()
        except EnvironmentError as exc:
            # repo at source_url may not be available, notify it but
            # go on since there might have new commits in local cache
            self.warning(exc.message)
        with self.hgrepo() as hgrepo:
            knownheads = [r.changeset for r in self.entity.heads_rset().entities()]
            # detect stripped branches
            needsstrip = False
            for cset in knownheads:
                try:
                    hgrepo.log(cset)
                except CommandError:
                    needsstrip = True
                    self.warning('%s: strip detected. %s is unknown in local cache',
                                 self.path, cset)

            if needsstrip:
                self.warning('%s: strip from %s.',
                             self.entity.dc_title(), self.path)
                revs = cnx.execute('Any R WHERE R is Revision, R from_repository REPO, '
                                   'REPO eid %(reid)s', {'reid': self.entity.eid})
                for reventity in revs.entities():
                    try:
                        hgrepo.log(reventity.changeset)
                    except CommandError:
                        reventity.cw_delete()

                cnx.commit()

            # update phases and visibility of already known revisions
            self.update_phases(cnx, hgrepo)
            self.update_hidden(cnx, hgrepo)
            # XXX we need to update obsolescence markers without new revision
            #     involved.
            knownheads_cs = [str(r.changeset) for r in self.entity.heads_rset().entities()
                             if str(r.changeset) in hgrepo]
            revrange = ' and '.join(('not(::%s)' % i) for i in knownheads_cs) if knownheads_cs else None
            missing = [int(rev[0]) for rev in hgrepo.log(revrange=revrange)]
            missing.sort()
            while missing:
                for rev in missing[:commitevery]:
                    try:
                        self.import_revision(hgrepo, rev)
                    except Exception:
                        self.critical('error while importing revision %s of %s',
                                      rev, self.path, exc_info=True)
                        raise
                cnx.commit()
                del missing[:commitevery] # pop iterated value
            cnx.commit()

    def update_phases(self, cnx, hgrepo):
        """ update all phases (this potentially affects all revs since
        phase changes are not transactional) """
        repoeid = self.entity.eid
        for phase in (u'public', u'draft', u'secret'):
            revs = set(ctx.node[:12] for ctx in hgrepo.log(revrange='%s()' % phase))
            if revs:
                cnx.execute('SET R phase %%(phase)s WHERE R changeset IN (%s),'
                            'NOT R phase %%(phase)s, R from_repository REPO,'
                            'REPO eid %%(repo)s' %
                            ','.join(repr(rev) for rev in revs),
                            {'repo': repoeid, 'phase': phase})

    def update_hidden(self, cnx, hgrepo):
        """ maintain hidden status for all revs """
        repoeid = self.entity.eid
        oldhidden = set(num for num, in cnx.execute('Any CS WHERE R hidden True, '
                                                    'R from_repository H, '
                                                    'R changeset CS, H eid %(hg)s',
                                                    {'hg': repoeid}).rows)
        newhidden = set(rev.node[:12] for rev in hgrepo.log(revrange='hidden()'))
        hide = newhidden - oldhidden
        show = oldhidden - newhidden
        for revs, setto in ((hide, 'True'), (show, 'False')):
            if revs:
                cnx.execute('SET R hidden %s WHERE R from_repository H,'
                            'H eid %%(hg)s, R changeset IN (%s)' %
                            (setto, ','.join('"%s"' % cs for cs in revs)),
                            {'hg': self.entity.eid})

        # very partial handling of obsolescence relation added after a revision
        # issue #2731056
        # this tries to find explanation for changeset that becomes hidden
        # - does not work for changesets already hidden
        # - does not work for public changesets
        for new_hide in hide:
            ctx = context.changectx(hgrepo, changeid=new_hide)
            RQL = '''SET S obsoletes P
                     WHERE R eid %(r)s,
                     P from_repository R,
                     P changeset %(p)s,
                     S from_repository R,
                     S changeset %(s)s,
                     NOT S obsoletes P
            '''
            # unknown successors will create the relation at insertion time
            data = {'r': self.entity.eid,
                    'p': str(ctx)}
            successors_changesets = [cs.node[:12] for cs in hgrepo.log(revrange='successors(%s)' % ctx.node())]
            for succ in successors_changesets:
                data['s'] = str(succ)
                cnx.execute(RQL, data)

    def import_revision(self, hgrepo, i):
        self.info('importing revision %s from %s', i, self.entity.dc_title())
        cnx = self._cw
        execute = cnx.execute
        ctx = context.changectx(hgrepo, changeid=i)
        ctx_hex = ctx.node()[:12]
        if execute('Any X WHERE X from_repository R, R eid %(repo)s, X changeset %(cs)s',
                   {'repo': self.entity.eid, 'cs': ctx_hex}):
            self.warning('skip revision %s, seems already imported',
                         ctx_hex)
            return
        revdata = {'date': ctx.date(),
                   'author': unicode(ctx.author(), self.entity.encoding),
                   'description': unicode(ctx.description(), self.entity.encoding),
                   'changeset': unicode(ctx_hex, self.entity.encoding),
                   'phase': unicode(ctx.phase()),
                   'branch': unicode(ctx.branch()),
                   'hidden': ctx.hidden(),
                   'vcstags': unicode(ctx.tags),
                   }
        #XXX workaround, parents may return None
        parent_changesets = hgrepo.parents(ctx_hex)
        parent_changesets = [n.node[:12] for n in parent_changesets] if parent_changesets else []
        precursors_changesets = [cs.node[:12] for cs in hgrepo.log(revrange='allprecursors(%s)' % i)]
        if not precursors_changesets:
            precursors = []
        else:
            precursors = execute(
                    'Any X WHERE X changeset XC, '
                    'X changeset IN (%s), X from_repository R, R eid %%(r)s'
                    % ','.join("'%s'" % cs for cs in precursors_changesets),
                    {'r': self.entity.eid})
        revdata['precursors'] = [p[0] for p in precursors]
        if not parent_changesets:
            parents = []
        else:
            parents = execute(
                    'Any X,XC WHERE X changeset XC, '
                    'X changeset IN (%s), X from_repository R, R eid %%(r)s'
                    % ','.join("'%s'"%cs for cs in parent_changesets),
                    {'r': self.entity.eid})
        revdata['parents'] = [r[0] for r in parents]
        reveid = bridge.import_revision(cnx, self.entity.eid, **revdata)
