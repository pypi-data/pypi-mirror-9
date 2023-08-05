# -*- coding: utf-8 -*-
"""hooks for vcsfile content types

:organization: Logilab
:copyright: 2007-2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement

__docformat__ = "restructuredtext en"

import os
import os.path as osp
import errno
import shutil

from logilab.common.textutils import unormalize
from cubicweb import QueryError, ValidationError
from cubicweb.server import hook, session, Service
from cubicweb.predicates import is_instance, score_entity, match_user_groups

from cubes.vcsfile import bridge

def repo_cache_dir(config):
    """Return the directory to use for repo cache

    This function create directory if necessary."""
    directory = config['local-repo-cache-root']
    if not osp.isabs(directory):
        directory = osp.join(config.appdatahome, directory)
    config.local_repo_cache_root = directory
    if not osp.exists(directory):
        try:
            os.makedirs(directory)
        except Exception:
            config.critical('could not find local repo cache directory; check '
                            'local-repo-cache-root option whose present value '
                            'is %r)', config['local-repo-cache-root'])
            raise
    return directory

def url_to_relative_path(url):
    scheme, url = url.split('://', 1)
    if scheme == 'file':
        return url.rstrip('/').rsplit('/', 1)[-1]
    else:
        try:
            return url.rstrip('/').rsplit('/', 1)[1]
        except IndexError:
            return '/'

def set_local_cache(vcsrepo):
    if 'local_cache' in vcsrepo.cw_edited:
        return
    cachedir = osp.join(repo_cache_dir(vcsrepo._cw.vreg.config),
                        unicode(vcsrepo.eid))
    if not osp.exists(cachedir):
        try:
            os.makedirs(cachedir)
        except OSError:
            vcsrepo.exception('cant create repo cache directory %s', cachedir)
            return
    if vcsrepo.source_url:
        reponame = vcsrepo.source_url.rstrip('/').rsplit('/', 1)[-1]
    elif vcsrepo.title:
        reponame = unormalize(vcsrepo.title).replace(' ', '_')
    else:
        reponame = 'repository'
    vcsrepo.cw_edited['local_cache'] = osp.join(unicode(vcsrepo.eid), reponame)

def clone_to_local_cache(vcsrepo):
    handler = vcsrepo.cw_adapt_to('VCSRepo')
    url = vcsrepo.source_url
    try:
        handler.pull()
    except Exception:
        handler.exception('while trying to clone repo %s', url)
        msg = vcsrepo._cw._('can not clone the repo from %s, '
                            'please check the source url')
        raise ValidationError(vcsrepo.eid, {'source_url': msg % url})


def missing_relation_error(entity, rtype):
    # use __ since msgid recorded in cw, we don't want to translate it in
    # this cube
    __ = entity._cw._
    msg = __('at least one relation %(rtype)s is required on %(etype)s (%(eid)s)')
    errors = {'from_repository': msg % {'rtype': __(rtype),
                                        'etype': __(entity.__regid__),
                                        'eid': entity.eid}}
    return ValidationError(entity.eid, errors)

def missing_attribute_error(entity, attrs):
    msg = _('at least one attribute of %s must be set on a Repository')
    errors = {}
    for attr in attrs:
        errors[attr] = msg % ', '.join(attrs)
    return ValidationError(entity.eid, errors)


# initialization hooks #########################################################


class VCSFileInitHook(hook.Hook):
    """install attribute map on the system source sql generator and init
    configuration
    """
    __regid__ = 'vcsfile.hook.init'
    events = ('server_startup', 'server_maintenance')

    def __call__(self):
        cacheroot = repo_cache_dir(self.repo.config)
        if not os.access(cacheroot, os.W_OK):
            raise ValueError('directory %r is not writable (check "local-repo-'
                             'cache-root" option)' % cacheroot)
        hgrcpath = self.repo.config['hgrc-path']
        if hgrcpath is not None:
            os.environ['HGRCPATH'] = hgrcpath



class VCSFileStartHook(hook.Hook):
    """register task to regularly pull/import vcs repositories content"""
    __regid__ = 'vcsfile.hook.start'
    events = ('server_startup',)

    def __call__(self):
        # closure to avoid error on code reloading
        interval = self.repo.config.get('check-revision-interval')
        if interval < 0:
            return
        repo = self.repo
        def refresh_vcsrepos():
            from cubes.vcsfile.hooks import _refresh_repos as refresh
            return refresh(repo)
        self.repo.looping_task(interval, refresh_vcsrepos)

# internals to be able to create new vcs repo revision using rql queries #######

### Other hooks
###############################################################################

class SetRepoCacheBeforeAddHook(hook.Hook):
    """clone just after repo creation

    mostly helps the tests
    """
    __regid__ = 'clone_repo_after_add'
    __select__ = (hook.Hook.__select__ & is_instance('Repository'))
    events = ('before_add_entity',)
    category = 'vcsfile.cache'
    order = 2

    def __call__(self):
        repo = self.entity
        if repo.type == 'mercurial':
            set_local_cache(repo)


class UpdateRepositoryHook(hook.Hook):
    """add repository eid to vcs bridge cache

    - Check that the type attribute is immutable
    - refresh the cache on url changes

    XXX stuff claiming to be cache but actually necessary are EVIL"""
    __regid__ = 'vcsfile.update_repository_hook'
    __select__ = hook.Hook.__select__ & is_instance('Repository')
    events = ('before_update_entity', )
    # XXX no category, contains integrity, mandatory and vcsfile.cache behaviour

    def __call__(self):
        vcsrepo = self.entity
        if 'type' in vcsrepo.cw_edited:
            msg = self._cw._('updating type attribute of a repository isn\'t '
                             'supported. Delete it and add a new one.')
            raise ValidationError(vcsrepo.eid, {'type': msg})
        if vcsrepo.type == 'mercurial' and not vcsrepo.local_cache:
            # XXX rmdir on rollback
            set_local_cache(vcsrepo)
            if (vcsrepo.import_revision_content
                or self._cw.vreg.config['repository-import']):
                clone_to_local_cache(vcsrepo)


class DeleteDirsOp(hook.DataOperationMixIn, hook.Operation):

    def postcommit_event(self):
        for cachedir in self.get_data():
            try:
                try:
                    shutil.rmtree(cachedir)
                    self.info('deleted repository cache at %s', cachedir)
                except OSError, exc:
                    if (exc.errno != errno.ENOENT
                        or getattr(exc, 'filename', None) != cachedir):
                        raise
            except Exception:
                self.exception('cannot delete repository cache at %s', cachedir)

class DeleteRepositoryHook(hook.Hook):
    __regid__ = 'vcsfile.add_update_repository_hook'
    __select__ = (hook.Hook.__select__ &
                  is_instance('Repository') &
                  score_entity(lambda x: x.local_cache))
    events = ('before_delete_entity',)
    # XXX mandatory hook?

    def __call__(self):
        if self.entity.local_cache:
            cachedir = osp.dirname(osp.join(
                self._cw.vreg.config.local_repo_cache_root,
                self.entity.local_cache)).encode('ascii')
            DeleteDirsOp.get_instance(self._cw).add_data(cachedir)


# safety belts #################################################################

def _check_in_transaction(vf_or_rev):
    """check that a newly added versioned file or revision entity is done in
    a vcs repository transaction.
    """
    try:
        vcsrepo = vf_or_rev.from_repository[0]
    except IndexError:
        raise missing_relation_error(vf_or_rev, 'from_repository')
    try:
        transactions = vcsrepo._cw.transaction_data['vctransactions']
        transaction = transactions[vcsrepo.eid]
    except KeyError:
        raise QueryError('no transaction in progress for repository %s'
                         % vcsrepo.eid)
    return transaction


class AddUpdateRepositoryHook(hook.Hook):
    __regid__ = 'vcsfile.add_update_repository_hook'
    __select__ = hook.Hook.__select__ & is_instance('Repository')
    events = ('after_add_entity', 'after_update_entity')
    category = 'integrity'
    required_attrs = ('source_url',)
    order = 1

    def __call__(self):
        entity = self.entity
        if entity.source_url:
            try:
                url_to_relative_path(entity.source_url)
            except Exception:
                msg = self._cw._('url must be of the form protocol://path/to/stuff')
                raise ValidationError(entity.eid, {'source_url': msg})
        # ensure local cache exists
        entity.cw_adapt_to('VCSRepo')

def _refresh_repos(repo, eids=None, bridge=bridge):
    '''
    Refresh vcs repos designated by the `eids` parameter, if refreshable:

      * None for all vcs repos
      * a list of integers for specific vcs repos
    '''
    with repo.internal_cnx() as cnx:
        config = cnx.vreg.config
        rql = ('Any R, RT, RE, RLC, RSU, RIRC WHERE R is Repository, '
               'NOT (R local_cache NULL),'
               'R type RT, R encoding RE, R local_cache RLC, R source_url RSU, '
               'R import_revision_content RIRC')
        if not config['cache-external-repositories']:
            rql += ', R cw_source S, S name "system"'
        kwargs = None
        if eids is not None:
            if isinstance(eids, int):
                rql += ', R eid %(x)s'
                kwargs = {'x': eids}
            else:
                rql += ', R eid IN (%s)' % ','.join(str(eid) for eid in eids)
        reposrset = cnx.execute(rql, kwargs)
        for vcsrepo in reposrset.entities():
            # watch for repository being shut-down, our thread may:
            # * not receive the KeyboardInterrupt or shutdown signal
            # * loop a while without accessing the session (actually
            #   until some repository is actually not up-to-date, while
            #   this access to the session would abort the task)
            try:
                repohdlr = vcsrepo.cw_adapt_to('VCSRepo')
            except bridge.VCSException, ex:
                cnx.error(str(ex))
                continue
            except Exception:
                cnx.exception('error while retrieving handler for %s',
                                  vcsrepo.eid)
                continue
            if (config['repository-import'] or vcsrepo.import_revision_content) \
                   and vcsrepo.local_cache is not None:
                try:
                    repohdlr.pull()
                except bridge.VCSException, ex:
                    repohdlr.error(str(ex))
                except Exception:
                    repohdlr.exception(
                        'error while updating local cache of repository %s',
                        vcsrepo.eid)
            if (config['repository-import']
                and vcsrepo.cw_metainformation()['source']['uri'] == 'system'):
                bridge.import_vcsrepo_content(cnx, repohdlr,
                    commitevery=config.get('check-revision-commit-every', 1))


class RefreshRepoService(Service):
    __regid__ = 'refresh_repository'
    __select__ = Service.__select__ & match_user_groups('managers')

    def call(self, eids=None):
        _refresh_repos(self._cw.repo, eids)


class VCSRepoNotifHook(hook.Hook):
    events = ('server_startup',)
    __regid__ = 'vcsfile_repo_notif_startup'
    order = 10 # make sure it is loaded "late" (in fact, it must be
               # loaded after ZMQStartHook but we lack a dependency
               # system here, see http://www.cubicweb.org/ticket/2900987)
    def __call__(self):
        def callback(msg):
            self.debug('received notification: %s', ' '.join(msg))
            msg = msg[-1]
            with self.repo.internal_cnx() as cnx:
                for suffix in ('', '/'):
                    rset = cnx.execute('Any R WHERE R source_url U, '
                                            'R source_url LIKE %(u)s',
                                            {'u': '%/'+msg+suffix})
                    if rset:
                        break
                if rset:
                    assert len(rset) == 1, 'found multiple repos for "%s"'%msg
                    eid = rset[0][0]
                    self.debug('Calling refresh service for repo %s', eid)
                    cnx.call_service('refresh_repository', eids=[eid])
                else:
                    self.debug('No repo for %s', msg)

        self.repo.app_instances_bus.add_subscription('vcsfile-repo-notif', callback)
