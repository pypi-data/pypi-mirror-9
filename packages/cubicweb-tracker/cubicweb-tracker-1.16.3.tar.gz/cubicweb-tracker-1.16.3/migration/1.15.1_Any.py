# try to repair the damage done by 1.15.0

add_relation_definition('Version', 'assigned_to', 'CWUser')
if 'todo_by' in fsschema:
    add_relation_type('todo_by')
if 'todo_by' in schema and ('Version', 'CWUser') in schema['todo_by'].rdefs:
    rql('SET V assigned_to U WHERE V todo_by U, NOT V assigned_to U')
drop_relation_definition('Version', 'todo_by', 'CWUser')

# constraint was modified
sync_schema_props_perms('assigned_to', syncperms=False)
