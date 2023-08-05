import sys
import os, os.path as osp
import shutil

import hglib

from logilab.common.decorators import classproperty
from logilab.common.shellutils import unzip

from cubicweb.devtools.testlib import CubicWebTC

from cubes.vcsfile import bridge

DATA = osp.abspath(osp.join(osp.dirname(__file__), 'data'))

def setup_repos(*reponames):
    for repo in reponames:
        if isinstance(repo, unicode):
            repo = repo.encode('utf-8')
        if osp.exists(repo):
            shutil.rmtree(repo)
        if osp.exists('%s.zip' % repo):
            unzip('%s.zip' % repo, osp.dirname(repo))
        else: # no zip file, let's init a new repo
            hglib.init(repo)

def init_vcsrepo(repo, commitevery=1):
    with repo.internal_cnx() as cnx:
        bridge.import_content(cnx, commitevery=commitevery,
                              raise_on_error=True)

class VCSRepositoryTC(CubicWebTC):
    """base class for test which should import a repository during setup"""
    _repo_path = None
    repo_type = u'mercurial'
    repo_encoding = u'utf-8'
    repo_import_revision_content = True
    repo_title = None

    commitevery = 3

    @classproperty
    def test_db_id(cls):
        if cls._repo_path is None:
            return None
        ids = [cls._repo_path]
        if not cls.repo_import_revision_content:
            ids.append('nocontent')
        return '-'.join(ids)

    @classproperty
    def repo_path(cls):
        assert cls._repo_path, 'you must set repository through _repo_path first'
        return osp.join(cls.datadir, cls._repo_path)

    @classmethod
    def _create_repo(cls, cnx):
        return cnx.create_entity(
            'Repository', type=cls.repo_type, source_url='file://'+cls.repo_path,
            encoding=cls.repo_encoding,
            title=cls.repo_title,
            import_revision_content=cls.repo_import_revision_content)

    @classmethod
    def grant_write_perm(cls, session, group, vcsrepoeid=None):
        if vcsrepoeid is None:
            vcsrepoeid = cls.vcsrepoeid
        cls.grant_permission(session, vcsrepoeid, 'managers', 'write',
                             u'repo x write perm')

    @classmethod
    def pre_setup_database(cls, cnx, config):
        setup_repos(cls.repo_path)
        # don't use cls.vcsrepo in regular test, only in pre_setup_database
        cls.vcsrepoeid = cls._create_repo(cnx).eid
        cnx.commit()

    def setUp(self):
        setup_repos(self.repo_path)
        super(VCSRepositoryTC, self).setUp()
        self.refresh()
        with self.admin_access.repo_cnx() as cnx:
            vcsrepo = cnx.find('Repository').one()
            self.vcsrepoeid = vcsrepo.eid
            self.vcsrepopath = vcsrepo.localcachepath

    def tearDown(self):
        super(VCSRepositoryTC, self).tearDown()
        shutil.rmtree(self.vcsrepopath, ignore_errors=True)

    def refresh(self):
        with self.repo.internal_cnx() as cnx:
            bridge.import_content(cnx, commitevery=1, raise_on_error=True)
        with hglib.open(self.repo_path) as repo:
            return dict((int(rev.rev), rev.node[:12].decode('ascii'))
                        for rev in repo.log(hidden=True))


class HGRCMixin(object):
    _old_files = ()
    hgconfig = {'ui': {'username': 'babar',},
                'extensions': {'rebase': '',
                               'evolve': '',},
                'phases': {'publish': 'False',},
                }
    def setUp(self):
        hgrcpath = osp.join(self.datadir, 'obsolete.hgrc')
        self._oldhgrc = os.environ.get('HGRCPATH')
        extpath = osp.join(self.datadir, 'obs.py')
        with open(extpath, 'wb') as obs:
            print >> obs, 'from mercurial import obsolete'
            print >> obs, 'obsolete._enabled = True'
        hgconfig = self.hgconfig.copy()
        hgconfig['extensions']['obs'] = extpath

        with open(hgrcpath, 'wb') as hgrc:
            for section, values in hgconfig.items():
                print >> hgrc, '[%s]'%section.strip()
                for attr, value in values.items():
                    print >> hgrc, '%s=%s'%(attr, value)
        os.environ['HGRCPATH'] = hgrcpath
        self._old_files = [extpath, hgrcpath]
        super(HGRCMixin, self).setUp()

    def tearDown(self):
        super(HGRCMixin, self).tearDown()
        if self._oldhgrc is None:
            os.environ.pop('HGRCPATH')
        else:
            os.environ['HGRCPATH'] = self._oldhgrc
        for path in self._old_files:
            os.unlink(path)

class VCSFileTC(HGRCMixin, VCSRepositoryTC):
    _repo_path = u'testrepo'
