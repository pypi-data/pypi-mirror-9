"""custom forms to submit new revision to the svn repository or to edit
some information about existing revisions.

:organization: Logilab
:copyright: 2007-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.web import formwidgets as fw
from cubicweb.web.views import uicfg

_afs = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs
_rctl = uicfg.reledit_ctrl
_pvdc = uicfg.primaryview_display_ctrl

for attr in ('path', 'type', 'source_url', 'encoding'):
    _pvdc.tag_attribute(('Repository', attr), {'vid': 'attribute'})
_rctl.tag_attribute(('Repository', 'title'), {'reload': True})
_affk.tag_attribute(('Repository', 'source_url'), {'widget': fw.TextInput})
_affk.tag_attribute(('Repository', 'path'), {'widget': fw.TextInput})
_afs.tag_attribute(('Repository', 'local_cache'), 'main', 'hidden')

