GET_USER_ROLES_QUERY = """
SELECT * FROM user_roles
"""

GET_USER_ROLE_BY_ID_QUERY = """
SELECT * FROM user_roles WHERE id = $1
"""

GET_USER_ROLES_BY_ORGANIZATION_QUERY = """
SELECT * FROM user_roles WHERE organization_id = $1
"""

GET_USER_ROLES_BY_USER_QUERY = """
SELECT * FROM user_roles WHERE user_id = $1
"""

GET_USER_ROLES_BY_ROLE_QUERY = """
SELECT * FROM user_roles WHERE role_id = $1
"""

GET_USER_ROLES_BY_TEAM_QUERY = """
SELECT * FROM user_roles WHERE team_id = $1
"""

GET_USER_ROLES_BY_USER_AND_ORGANIZATION_QUERY = """
SELECT * FROM user_roles WHERE user_id = $1 AND organization_id = $2
"""

INSERT_USER_ROLE_QUERY = """
INSERT INTO user_roles (organization_id, user_id, role_id, team_id, created_at, updated_at)
VALUES ($1, $2, $3, $4, NOW(), NOW())
RETURNING *
"""

INSERT_BULK_USER_ROLES_QUERY = """
INSERT INTO user_roles (organization_id, user_id, role_id, team_id, created_at, updated_at)
VALUES ($1, $2, $3, $4, NOW(), NOW())
RETURNING *
"""

UPDATE_USER_ROLE_QUERY = """
UPDATE user_roles
SET organization_id = $1, user_id = $2, role_id = $3, team_id = $4, updated_at = NOW()
WHERE id = $5
RETURNING *
"""

DELETE_USER_ROLE_QUERY = """
DELETE FROM user_roles WHERE id = $1
"""

DELETE_USER_ROLE_BY_USER_AND_ROLE_QUERY = """
DELETE FROM user_roles WHERE user_id = $1 AND role_id = $2
"""

