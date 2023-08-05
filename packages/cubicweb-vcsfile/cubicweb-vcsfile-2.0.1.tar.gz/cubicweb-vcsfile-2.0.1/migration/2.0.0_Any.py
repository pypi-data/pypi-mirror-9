if session.find('Repository', type=u'subversion'):
    print "subversion repositories are no longer supported, aborting"
    raise SystemExit(1)

# changed constraint
# must be done here (before the add/drop attributes)  otherwise
# the migration crashes for some reason I prefer not to know
sync_schema_props_perms('Revision')

drop_attribute('Revision', 'revision')

if 'path' in schema['Repository'].subject_relations():
    for vcsrepo in session.find('Repository'):
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

drop_entity_type('DeletedVersionContent')
drop_entity_type('VersionContent')
drop_entity_type('VersionedFile')
drop_relation_type('content_for')
drop_relation_type('from_revision')
drop_relation_type('at_revision')
drop_relation_type('vc_copy')
drop_relation_type('vc_rename')
