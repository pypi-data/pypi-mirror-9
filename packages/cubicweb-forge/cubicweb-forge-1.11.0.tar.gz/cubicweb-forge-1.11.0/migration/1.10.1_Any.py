drop_relation_definition('ExtProject', 'require_permission', 'CWPermission')

# some old instances may not have it
if not rql('CWConstraintType C WHERE C name "IntervalBoundConstraint"'):
    create_entity('CWConstraintType', name=u'IntervalBoundConstraint')

sync_schema_props_perms('load')
sync_schema_props_perms('load_left')
