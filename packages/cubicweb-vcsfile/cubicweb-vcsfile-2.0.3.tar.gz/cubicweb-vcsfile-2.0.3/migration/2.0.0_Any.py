def drop_entity_types_fast(*etypes, **kwargs):
    """drop entity types bypassing all hooks"""

    for etype in etypes:
        if etype not in schema:
            print '%s does not exist' % etype
            continue
        etype = schema[etype]

        # ignore attributes and inlined rels since they'll be dropped anyway
        srels = [x for x in etype.subject_relations() if x.eid and not (x.final or x.inlined)]

        orels = [x for x in etype.object_relations() if x.eid and not x.inlined]
        inlined_rels = [x for x in etype.object_relations() if x.eid and x.inlined]

        # eids to be deleted could be listed in some other entity tables through inlined relations
        for rtype in inlined_rels:
            for subjtype in rtype.subjects(etype):
                if subjtype in etypes:
                    continue
                print 'updating', subjtype.type
                sql('UPDATE cw_%(stype)s SET cw_%(rtype)s = NULL '
                    'WHERE cw_%(rtype)s IN (SELECT eid FROM entities WHERE type = %%s)' %
                    {'stype': subjtype.type, 'rtype': rtype.type},
                    (etype.type,))

        for rel in srels:
            print 'deleting from', rel.type
            if all(subj in etypes for subj in rel.subjects()) or all(obj in etypes for obj in rel.objects()):
                sql('DELETE FROM %s_relation' % rel.type)
            else:
                sql('DELETE FROM %s_relation WHERE eid_from IN (SELECT eid FROM entities WHERE type = %%s)' % rel.type, (etype.type,))
        for rel in orels:
            print 'deleting from', rel.type
            if all(subj in etypes for subj in rel.subjects()) or all(obj in etypes for obj in rel.objects()):
                sql('DELETE FROM %s_relation' % rel.type)
            else:
                sql('DELETE FROM %s_relation WHERE eid_to IN (SELECT eid FROM entities WHERE type = %%s)' % rel, (etype.type,))

        sql('DELETE FROM appears WHERE uid IN (SELECT eid FROM entities WHERE type = %s)', (etype.type,))
        sql('DELETE FROM cw_%s' % etype.type)
        sql('DELETE FROM entities WHERE type = %s', (etype.type,))

    for etype in etypes:
        drop_entity_type(etype, **kwargs)


if session.find('Repository', type=u'subversion'):
    print "subversion repositories are no longer supported, aborting"
    raise SystemExit(1)

# changed constraint
# must be done here (before the add/drop attributes)  otherwise
# the migration crashes for some reason I prefer not to know
sync_schema_props_perms('Revision')

drop_attribute('Revision', 'revision')

if 'path' in schema['Repository'].subject_relations():
    for vcsrepo in session.find('Repository').entities():
        if vcsrepo.source_url is not None:
            continue
        if vcsrepo.local_cache is not None:
            continue
        if vcsrepo.path is None:
            continue
        vcsrepo.cw_set(source_url=u'file://' + vcsrepo.path)

drop_attribute('Repository', 'path')
drop_attribute('Repository', 'subpath')
add_attribute('Revision', 'vcstags')

# changed description
sync_schema_props_perms('Repository')

# changed vocabulary
sync_schema_props_perms('type')

drop_entity_types_fast('DeletedVersionContent', 'VersionContent', 'VersionedFile')
drop_relation_type('content_for')
drop_relation_type('from_revision')
drop_relation_type('at_revision')
drop_relation_type('vc_copy')
drop_relation_type('vc_rename')
