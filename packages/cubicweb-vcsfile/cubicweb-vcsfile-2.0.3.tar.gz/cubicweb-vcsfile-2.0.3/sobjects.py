
from hglib.error import CommandError
from cubicweb.server import Service

class RevisionExportService(Service):
    """return the patch version of a revision
    """

    __regid__ = 'vcs.export-rev'

    def call(self, repo, nodeid):
        repo_ent = self._cw.entity_from_eid(repo)
        if repo_ent.type != 'mercurial':
            # no svn support yet (use a selector when we have multiple versions)
            return None
        hdrepo = repo_ent.cw_adapt_to('VCSRepo')
        try:
            with hdrepo.hgrepo() as hgrepo:
                if nodeid in hgrepo:
                    return hgrepo.export(revs=nodeid, git=True)
        except CommandError as e:
            return None

