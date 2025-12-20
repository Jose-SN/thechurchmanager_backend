GET_PERMISSIONS_QUERY = """
SELECT * FROM permissions
"""

GET_PERMISSION_BY_ID_QUERY = """
SELECT * FROM permissions WHERE id = $1
"""

GET_PERMISSIONS_BY_ORGANIZATION_QUERY = """
SELECT * FROM permissions WHERE organization_id = $1
"""

GET_PERMISSIONS_BY_ROLE_QUERY = """
SELECT * FROM permissions WHERE role_id = $1
"""

GET_PERMISSIONS_BY_MODULE_QUERY = """
SELECT * FROM permissions WHERE module_id = $1
"""

GET_PERMISSIONS_BY_TEAM_QUERY = """
SELECT * FROM permissions WHERE team_id = $1
"""

INSERT_PERMISSION_QUERY = """
INSERT INTO permissions (organization_id, role_id, module_id, team_id, view, edit, "create", "delete", created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
RETURNING *
"""

INSERT_BULK_PERMISSIONS_QUERY = """
INSERT INTO permissions (organization_id, role_id, module_id, team_id, view, edit, "create", "delete", created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
RETURNING *
"""

UPDATE_PERMISSION_QUERY = """
UPDATE permissions
SET organization_id = $1, role_id = $2, module_id = $3, team_id = $4, view = $5, edit = $6, "create" = $7, "delete" = $8, updated_at = NOW()
WHERE id = $9
RETURNING *
"""

DELETE_PERMISSION_QUERY = """
DELETE FROM permissions WHERE id = $1
"""

