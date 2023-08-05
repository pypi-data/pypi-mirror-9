# -*- coding: utf-8 -*-
"""makes the bridge between repository handlers and related cubicweb entities

:organization: Logilab
:copyright: 2007-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement

__docformat__ = "restructuredtext en"

from yams import ValidationError

from cubes.vcsfile import queries


class VCSException(Exception):
    def __init__(self, repoeid, attr, msgid, msgargs=()):
        self.repoeid = repoeid
        self.attr = attr
        self.msgid = msgid
        self.msgargs = msgargs

    def __str__(self):
        return '%s.%s: %s' % (self.repoeid, self.attr,
                              self.msgid % self.msgargs)

    def to_validation_error(self, translate):
        msg = translate(self.msgid)
        if self.msgargs:
            msg %= self.msgargs
        return ValidationError(self.repoeid, {self.attr: msg})


def import_content(cnx, commitevery=1000, raise_on_error=False):
    """synchronize content of known vcs repositories
    """
    for vcsrepo in cnx.execute(
        'Any X,T,U,L,E WHERE X is Repository, '
        'X type T, X source_url U, X local_cache L, '
        'X encoding E').entities():
        try:
            repohdlr = vcsrepo.cw_adapt_to('VCSRepo')
        except VCSException, ex:
            if raise_on_error:
                raise
            cnx.error(str(ex))
            continue
        import_vcsrepo_content(cnx, repohdlr,
                               commitevery=commitevery,
                               raise_on_error=raise_on_error)


def import_vcsrepo_content(cnx, repohdlr, commitevery=10,
                           raise_on_error=False):
    """synchronize content of given vcs repository"""
    vcsrepo = repohdlr.entity
    try:
        repohdlr.import_content(commitevery)
        # give other threads a chance to run: commit will release the cnxset, get
        # it back afterwards
        cnx.commit()
    except Exception:
        if raise_on_error:
            raise
        try:
            title = vcsrepo.dc_title()
        except Exception:
            title = str(vcsrepo)
        repohdlr.exception(
            'error while importing content for vcs repo %s', title)
        cnx.rollback()


def import_revision(cnx, repoeid, date, **kwargs):
    """import a new revision from a repository"""
    args = {'date': date}
    args['repoeid'] = repoeid
    for attr in ('author', 'description', 'changeset', 'branch', 'phase', 'hidden', 'vcstags'):
        args[attr] = kwargs.get(attr)
    prevs = kwargs['parents']
    if prevs:
        args['parent'] = prevs[0]
    precs = kwargs['precursors']
    if precs:
        args['precursor'] = precs[0]
    reveid = cnx.execute(queries.new_revision_rql(prevs, precs, True), args)[0][0]
    # complete other parents & precursors relations
    if len(prevs) > 1:
        for preveid in prevs[1:]:
            cnx.execute('SET R parent_revision PR WHERE R eid %(r)s, PR eid %(pr)s',
                        {'r': reveid, 'pr': preveid})
    if len(precs) > 1:
        for preceid in precs[1:]:
            cnx.execute('SET R obsoletes PREC WHERE R eid %(r)s, PREC eid %(pr)s',
                        {'r': reveid, 'pr': preceid})
    return reveid
