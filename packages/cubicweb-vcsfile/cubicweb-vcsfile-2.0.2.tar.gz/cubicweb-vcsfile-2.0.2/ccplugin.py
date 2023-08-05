"""cubicweb-ctl plugin providing the vcscheck command

:organization: Logilab
:copyright: 2013-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.cwctl import CWCTL
from cubicweb.toolsutils import Command

class VCSRefreshCommand(Command):
    """ Refresh repository

    <instance id>
      identifier of the instance
    """
    name = 'vcsrefresh'
    min_args = max_args = 1
    arguments = '<instance id>'

    def run(self, args):
        """run the command with its specific arguments"""
        from cubicweb.server.serverconfig import ServerConfiguration
        from cubicweb.server.serverctl import repo_cnx
        appid = args.pop(0)
        config = ServerConfiguration.config_for(appid)
        config.__class__.cube_appobject_path = set(('hooks', 'entities'))
        config.__class__.cubicweb_appobject_path = set(('hooks', 'entities'))
        repo, cnx = repo_cnx(config)

        with cnx:
            rset = cnx.execute('Any X,S where X is Repository, X source_url S')
            for hgrepo, source_url in rset:
                print 'refreshing', source_url
                cnx.call_service('refresh_repository', eids=hgrepo)

CWCTL.register(VCSRefreshCommand)
