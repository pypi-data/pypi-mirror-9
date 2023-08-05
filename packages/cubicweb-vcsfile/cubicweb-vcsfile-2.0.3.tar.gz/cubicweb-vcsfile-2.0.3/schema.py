"""entity types used to represent a version control system (vcs) content

:organization: Logilab
:copyright: 2007-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from yams.buildobjs import (DEFAULT_ATTRPERMS,
                            EntityType, RelationDefinition,
                            String, Boolean)
from cubicweb.schema import RRQLExpression

PRIVATE_ATTRPERMS = DEFAULT_ATTRPERMS.copy()
PRIVATE_ATTRPERMS['read'] = ('managers',)
PRIVATE_ATTRPERMS['update'] = ('managers',)

RO_ATTRPERMS = DEFAULT_ATTRPERMS.copy()
RO_ATTRPERMS['update'] = ()
RO_RELPERMS = DEFAULT_ATTRPERMS.copy()
RO_RELPERMS['add'] = (RRQLExpression('X from_repository R, U in_group G, '
                                     'R require_permission P, P require_group G'))


class Repository(EntityType):
    """a local VCS repository which will be used as versionned content
    entity source
    """
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers',),
        'update': ('managers',),
        'delete': ('managers',),
        }

    title = String(description=_('optional title. If the repository has a public url, '
                                 'it may be a good idea to put it as title.'),
                   maxsize=256)
    type = String(required=True, vocabulary=('mercurial',),
                  description=_('repository\'s type'))
    source_url = String(description=_('source url (must be of the form protocol://path/to/stuff)'),
                        unique=True)
    local_cache = String(unique=True,
                         description=_('relative path to the local cache of the repository'),
                         __permissions__=PRIVATE_ATTRPERMS)
    encoding = String(default='utf-8', maxsize=20, required=True,
                      description=_('encoding used for the repository (e.g.'
                                    ' for file path and check-in comments)'))
    import_revision_content = Boolean(default=True,
                                      description=_('import contents of files touched by a revision. '
                                                    'It may cause performance issue when scaling.'))
    has_anonymous_access = Boolean(default=True,
                                   description=_('Tell if user needs an account to checkout the repository.'))


class Revision(EntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (),
        'update': (),
        'delete': (),
        }
    __unique_together__ = [('from_repository', 'changeset')]
    # NOTE: creation_date will be set at revision date

    description = String(description=_('comment for this revision.'))

    author = String(indexed=True, maxsize=200,
                    description=_("author of this revision."))

    changeset = String(indexed=True, maxsize=100,
                       description=_('change set identifier, when used by the '
                                     'underlying version control system.'),
                       fulltextindexed=True,
                       __permissions__=RO_ATTRPERMS)

    branch = String(indexed=True, maxsize=255,
                    description=_("branch of this revision."),
                   __permissions__=RO_ATTRPERMS)

    phase = String(description=_('phase of the changeset'), indexed=True,
                   default='draft', vocabulary=[_('secret'), _('draft'), _('public')])

    vcstags = String(indexed=True, maxsize=255,
                     description=_('Tags on this revision (comma separated values)'),
                     __permissions__=RO_ATTRPERMS)

    hidden = Boolean(required=True, indexed=True)


class from_repository(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (),
        'delete': (),
        }
    inlined = True
    subject = 'Revision'
    object = 'Repository'
    cardinality = '1*'
    composite = 'object'


class parent_revision(RelationDefinition): # XXX ordered
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (),
        'delete': (),
        }
    subject = 'Revision'
    object = 'Revision'

class obsoletes(RelationDefinition):
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': (),
                       'delete': ()}
    subject = 'Revision'
    object = 'Revision'

class granted_permission(RelationDefinition):
    subject = 'Repository'
    object = 'CWPermission'

class require_permission(RelationDefinition):
    subject = 'Repository'
    object = 'CWPermission'
