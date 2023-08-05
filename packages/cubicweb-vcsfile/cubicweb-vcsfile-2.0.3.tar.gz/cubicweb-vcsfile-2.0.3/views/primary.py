"""primary views for entity types defined by the vcsfile package

:organization: Logilab
:copyright: 2007-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import TransformError, xml_escape

from cubicweb import Unauthorized, tags
from cubicweb.mttransforms import ENGINE
from cubicweb.predicates import is_instance, score_entity
from cubicweb.view import EntityView
from cubicweb.web.views import (ibreadcrumbs, idownloadable, tableview,
                                baseviews, primary, tabs, navigation, uicfg)

# primary view tweaks
_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl
_abaa = uicfg.actionbox_appearsin_addmenu

# internal purpose relation
_pvs.tag_attribute(('Repository', 'local_cache'), 'hidden')
_pvs.tag_attribute(('Repository', 'source_url'), 'hidden') # custom view
_pvs.tag_object_of(('*', 'from_repository', 'Repository'), 'hidden')

_pvs.tag_subject_of(('Revision', 'parent_revision', 'Revision'), 'attributes')
_pvs.tag_object_of(('Revision', 'parent_revision', 'Revision'), 'attributes')
_pvs.tag_subject_of(('Revision', 'from_repository', '*'), 'hidden') # in breadcrumb

_pvdc.tag_subject_of(('*', 'from_repository', '*'), {'vid': 'incontext'})

_pvdc.tag_attribute(('Repository', 'source_url'), {'vid': 'urlattr'})

# we don't want automatic addrelated action for the following relations...
for rtype in ('from_repository', 'parent_revision'):
    _abaa.tag_object_of(('*', rtype, '*'), False)


def render_entity_summary(self, entity):
    if not entity.is_head(entity.rev.branch):
        msg = self._cw._('this file has newer revisions')
        self.w(tags.div(msg, klass='warning'))
    if entity.description:
        self.field(self._cw._('commit message:'), xml_escape(entity.description),
                   tr=False, table=False)


class RepositoryPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('Repository')

    tabs = [_('repositoryinfo_tab'), _('repositoryhistory_tab')]
    default_tab = 'repositoryinfo_tab'


class RepositoryInfoTab(tabs.PrimaryTab):
    __regid__ = 'repositoryinfo_tab'
    __select__ = is_instance('Repository')

    def render_entity_attributes(self, entity):
        super(RepositoryInfoTab, self).render_entity_attributes(entity)
        if entity.source_url:
            entity.view('vcsfile.repository.checkout', w=self.w)
        rset = self._cw.execute('Any REV, REVB ORDERBY REV DESC '
                                'WHERE REV branch REVB, REV from_repository R, '
                                'R eid %(r)s, NOT X parent_revision REV, REV hidden FALSE',
                                {'r': entity.eid})
        if rset:
            self.w('<h3>%s</h3>' % self._cw._('heads'))
            self.wview('table', rset)


class RepositoryHistoryTab(EntityView):
    __regid__ = 'repositoryhistory_tab'
    __select__ = is_instance('Repository')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute(
            'Any R,RB,RA,RD,RCD, RCS ORDERBY R DESC WHERE '
            'R branch RB, R author RA, R description RD, R creation_date RCD,'
            'R changeset RCS, R from_repository X, X eid %(x)s',
            {'x': entity.eid})
        self.wview('vcsfile.table.revisions', rset, 'noresult')

class RevisionsTable(tableview.RsetTableView):
    __regid__ = 'vcsfile.table.revisions'
    __select__ = is_instance('Revision')
    displaycols = range(5)
    layout_args = {'display_filter': 'top'}


class RepositoryCheckOutInstructionsView(EntityView):
    __regid__ = 'vcsfile.repository.checkout'
    __select__ = is_instance('Repository') & score_entity(lambda x: x.source_url)

    def entity_call(self, entity):
        w = self.w
        _ = self._cw._
        url_scheme = entity.source_url.split(':')[0]
        if url_scheme.startswith('http'):
            w(u'<h3>%s</h3>' % _('Browse source'))
            w(u'<p>%s</p>' % _('You can browse the source code by following <a href="%s">this link</a>.')
              % xml_escape(entity.source_url))
        w(u'<h3>%s</h3>' % _('Command-Line Access'))
        if entity.has_anonymous_access:
            msg = _('Non-members may check out a read-only working copy anonymously over %s.') % xml_escape(url_scheme.upper())
        else:
            msg = _('Members only may check out working copy over %s.') % xml_escape(url_scheme.upper())
        w(u'<p>%s</p>' % msg)
        w(u'<p>%s</p>' % _('Use this command to check out the latest project source code:'))
        w(u'<pre>')
        if entity.type == 'mercurial':
            w(u'hg clone %s' % xml_escape(entity.source_url))
        w(u'</pre>')


class RevisionShortView(EntityView):
    __regid__ = 'shorttext'
    __select__ = is_instance('Revision')
    content_type = 'text/plain'

    def cell_call(self, row, col):
        rev = self.cw_rset.get_entity(row, col)
        self.w(u'#%s' % rev.changeset)


class RevisionPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Revision')

    def render_entity_relations(self, rev):
        repo = rev.repository.cw_adapt_to('VCSRepo')
        versioned = repo.status(rev.changeset)
        if versioned:
            self.w(u'<table class="listing">')
            self.w(u'<tr><th>%s</th></tr>' %
                   self._cw._('files modified by this revision'))
            for obj in versioned:
                self.w(u'<tr><td>%s</td></tr>' % (
                    xml_escape(obj)))
            self.w(u'</table>')
        else:
            self.w(u'<p>%s</p>' % self._cw._('this revision hasn\'t modified any files'))
        patch = rev.export()
        if patch is not None:
            self.w(u'<h3>Changes</h3>')
            self.w(u'<div class="content">')
            transformer = rev._cw_mtc_transform
            html = transformer(patch, 'text/x-diff', 'text/annotated-html', 'utf8')
            self.w(html)
            self.w(u'</div>')




# navigation: breadcrumbs / prevnext adapters ##################################

class RepoContentIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('Revision')

    def parent_entity(self):
        try:
            return self.entity.repository
        except Unauthorized:
            return None

class RevisionIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance('Revision')

    def previous_entity(self):
        # may have multiple parents, give priority to the one in the same
        # branch.
        parent = None
        for parent in self.entity.parent_revision:
            if parent.branch == self.entity.branch:
                return parent
        return parent

    def next_entity(self):
        # may have multiple children, give priority to the one in the same
        # branch.
        child = None
        for child in self.entity.reverse_parent_revision:
            if child.branch == self.entity.branch:
                return child
        return child
