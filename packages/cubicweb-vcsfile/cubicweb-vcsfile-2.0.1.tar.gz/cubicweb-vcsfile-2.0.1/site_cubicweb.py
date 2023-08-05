# repository specific stuff ####################################################

try:
    from cubicweb import server
except ImportError: # no server installation
    pass
else:
    options = (
        ('repository-import',
         {'type' : 'yn',
          'default': True,
          'help': 'Is the instance responsible to automatically import new '
                   'revisions from repositories? '
                   'You should say yes unless you don\'t want this behaviour '
                   'or if you use a multiple repositories setup, in which '
                   'case you should say yes on one repository, no on others.',
          'level': 2,
          'group': 'vcsfile',
          }),
        ('check-revision-interval',
         {'type' : 'int',
          'default': 5*60,
          'help': 'interval between checking of new revisions in repositories \
(default to 5 minutes).',
          'level': 2,
          'group': 'vcsfile',
          }),
        ('check-revision-commit-every',
         {'type' : 'int',
          'default': 1000,
          'help': 'after how much new imported revisions the transaction \
should be commited (default to 1000).',
          'level': 2,
          'group': 'vcsfile',
          }),
        ('import-revision-content',
         {'type' : 'yn',
          'default': True,
          'help': 'This option is now deprecated in favor of the import_revision_content attribute per Repository.',
          'level': 2,
          'group': 'vcsfile',
          }),
        ('local-repo-cache-root',
         {'type':'string',
          'default': 'repo_cache', # XXX /var/lib/cubicweb/<instance>
          'help':'Local repository cache location (if not absolute, will be '
          'relative to instance data home directory).',
          'level': 2,
          'group': 'vcsfile'
          }
         ),
        ('cache-external-repositories',
         {'type':'yn',
          'default': False,
          'help':'Should repositories from external source have a local cache?'
          'This is usually not necessary, beside cases where for instance a '
          'narval bot on the same host as the instance could benefit from them '
          'to run apycot tests.',
          'level': 2,
          'group': 'vcsfile'
          }
         ),
        ('hgrc-path',
         {'type': 'string',
          'default': None,
          'help': 'a list of files or directories to search for mercurial configuration',
          'level': 2,
          'group': 'vcsfile',
          }
         ),
        )

from docutils import nodes, statemachine
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.misc import Include

from cubes.vcsfile.entities import Repository
from cubes.vcsfile.docparser import Diff2HTMLTransform
from cubicweb.mttransforms import ENGINE

COMPONENT_CONTEXT = 'navcontentbottom'

if Diff2HTMLTransform.name not in ENGINE.transforms:
    ENGINE.add_transform(Diff2HTMLTransform())


class VCSInclude(Include):
    option_spec = Include.option_spec.copy()
    option_spec['revision'] = str
    option_spec['repository'] = int

    def run(self):
        # This is a partial copy of Include.run method, but
        # docutils...
        entity = self.state.document.settings.context
        repoeid = self.options.get('repository')
        if repoeid is None:
            try:
                repo = entity.vcsrepository
            except AttributeError:
                raise self.severe("vcsinclude directive requires the 'repository' option"
                                  "when used in the context of a %s" %
                                  entity.__class__.__name__)
            repo = entity.repository
        else:
            repo = entity._cw.entity_from_eid(repoeid)
        if not isinstance(repo, Repository):
            raise self.severe('\'repository\' option value is not the eid of a '
                              'Repository but a %s.' % repo.__class__.__name__)

        path = self.arguments[0]

        rev = self.options.get('revision')
        vcsrepo = repo.cw_adapt_to('VCSRepo')
        try:
            content = vcsrepo.cat(rev, path)
        except Exception:
            entity.warning('Could not get included file at revision "%s", '
                           'using latest revision instead' % rev)
            content = vcsrepo.cat('tip', path)

        if content is None:
            return []

        source = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1)
        encoding = self.options.get('encoding', 'utf-8')
        tab_width = self.options.get(
            'tab-width', self.state.document.settings.tab_width)
        startline = self.options.get('start-line', None)
        endline = self.options.get('end-line', None)

        rawtext = content.decode(encoding)

        if startline or (endline is not None):
            lines = rawtext.splitlines(True)
            rawtext = ''.join(lines[startline:endline])

        # start-after/end-before: no restrictions on newlines in match-text,
        # and no restrictions on matching inside lines vs. line boundaries
        after_text = self.options.get('start-after', None)
        if after_text:
            # skip content in rawtext before *and incl.* a matching text
            after_index = rawtext.find(after_text)
            if after_index < 0:
                raise self.severe('Problem with "start-after" option of "%s" '
                                  'directive:\nText not found.' % self.name)
            rawtext = rawtext[after_index + len(after_text):]
        before_text = self.options.get('end-before', None)
        if before_text:
            # skip content in rawtext after *and incl.* a matching text
            before_index = rawtext.find(before_text)
            if before_index < 0:
                raise self.severe('Problem with "end-before" option of "%s" '
                                  'directive:\nText not found.' % self.name)
            rawtext = rawtext[:before_index]
        if 'literal' in self.options:
            # Convert tabs to spaces, if `tab_width` is positive.
            if tab_width >= 0:
                text = rawtext.expandtabs(tab_width)
            else:
                text = rawtext
            literal_block = nodes.literal_block(rawtext, text, source=path)
            literal_block.line = 1
            return [literal_block]
        else:
            include_lines = statemachine.string2lines(
                rawtext, tab_width, convert_whitespace=1)
            self.state_machine.insert_input(include_lines, path)
            return []


directives.register_directive('vcsinclude', VCSInclude)
