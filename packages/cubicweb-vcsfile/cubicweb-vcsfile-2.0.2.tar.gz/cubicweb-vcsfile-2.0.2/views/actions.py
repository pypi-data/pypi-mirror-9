"""actions for entity types defined by the vcsfile package

:organization: Logilab
:copyright: 2007-2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.predicates import (one_line_rset, is_instance, rql_condition,
                                 score_entity, match_user_groups, anonymous_user)
from cubicweb.web.action import Action
from cubicweb.web.views.actions import CopyAction

class RepositoryRefreshAction(Action):
    __regid__ = 'refresh'
    __select__ = is_instance('Repository') & match_user_groups('managers')

    title = _('refresh repository')
    order = 130
    #category = 'moreactions'

    def url(self):
        entity = self.cw_rset.get_entity(0, 0)
        repoeid = entity.eid
        return self._cw.build_url('refresh_repository', eid=repoeid)


# deactivate copy action for entities coming from the svn source
CopyAction.__select__ = CopyAction.__select__ & ~is_instance('Revision')
