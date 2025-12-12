GET_ROLES_QUERY = """
SELECT * FROM roles
"""

GET_ROLE_BY_ID_QUERY = """
SELECT * FROM roles WHERE id = $1
"""

GET_ROLES_BY_ORGANIZATION_QUERY = """
SELECT * FROM roles WHERE organization_id = $1
"""

GET_ROLES_BY_TEAM_QUERY = """
SELECT * FROM roles WHERE team_id = $1
"""

INSERT_ROLE_QUERY = """
INSERT INTO roles (name, description, team_id, organization_id, type, permissions, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
RETURNING *
"""

INSERT_BULK_ROLES_QUERY = """
INSERT INTO roles (name, description, team_id, organization_id, type, permissions, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
RETURNING *
"""

UPDATE_ROLE_QUERY = """
UPDATE roles
SET name = $1, description = $2, team_id = $3, organization_id = $4, type = $5, permissions = $6, updated_at = NOW()
WHERE id = $7
RETURNING *
"""

DELETE_ROLE_QUERY = """
DELETE FROM roles WHERE id = $1
"""

