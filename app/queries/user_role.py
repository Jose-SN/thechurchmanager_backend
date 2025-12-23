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

# Overview queries with role details joined
GET_USER_ROLES_OVERVIEW_QUERY = """
SELECT 
    ur.id,
    ur.organization_id,
    ur.user_id,
    ur.role_id,
    ur.team_id,
    ur.created_at,
    ur.updated_at,
    r.name as role_name,
    r.description as role_description,
    r.type as role_type,
    r.permissions as role_permissions,
    r.team_id as role_team_id,
    r.organization_id as role_organization_id,
    r.created_at as role_created_at,
    r.updated_at as role_updated_at
FROM user_roles ur
LEFT JOIN roles r ON ur.role_id = r.id
"""

GET_USER_ROLE_OVERVIEW_BY_ID_QUERY = """
SELECT 
    ur.id,
    ur.organization_id,
    ur.user_id,
    ur.role_id,
    ur.team_id,
    ur.created_at,
    ur.updated_at,
    r.name as role_name,
    r.description as role_description,
    r.type as role_type,
    r.permissions as role_permissions,
    r.team_id as role_team_id,
    r.organization_id as role_organization_id,
    r.created_at as role_created_at,
    r.updated_at as role_updated_at
FROM user_roles ur
LEFT JOIN roles r ON ur.role_id = r.id
WHERE ur.id = $1
"""

GET_USER_ROLES_OVERVIEW_BY_ORGANIZATION_QUERY = """
SELECT 
    ur.id,
    ur.organization_id,
    ur.user_id,
    ur.role_id,
    ur.team_id,
    ur.created_at,
    ur.updated_at,
    r.name as role_name,
    r.description as role_description,
    r.type as role_type,
    r.permissions as role_permissions,
    r.team_id as role_team_id,
    r.organization_id as role_organization_id,
    r.created_at as role_created_at,
    r.updated_at as role_updated_at
FROM user_roles ur
LEFT JOIN roles r ON ur.role_id = r.id
WHERE ur.organization_id = $1
"""

GET_USER_ROLES_OVERVIEW_BY_USER_QUERY = """
SELECT 
    ur.id,
    ur.organization_id,
    ur.user_id,
    ur.role_id,
    ur.team_id,
    ur.created_at,
    ur.updated_at,
    r.name as role_name,
    r.description as role_description,
    r.type as role_type,
    r.permissions as role_permissions,
    r.team_id as role_team_id,
    r.organization_id as role_organization_id,
    r.created_at as role_created_at,
    r.updated_at as role_updated_at
FROM user_roles ur
LEFT JOIN roles r ON ur.role_id = r.id
WHERE ur.user_id = $1
"""

GET_USER_ROLES_OVERVIEW_BY_USER_AND_ORGANIZATION_QUERY = """
SELECT 
    ur.id,
    ur.organization_id,
    ur.user_id,
    ur.role_id,
    ur.team_id,
    ur.created_at,
    ur.updated_at,
    r.name as role_name,
    r.description as role_description,
    r.type as role_type,
    r.permissions as role_permissions,
    r.team_id as role_team_id,
    r.organization_id as role_organization_id,
    r.created_at as role_created_at,
    r.updated_at as role_updated_at
FROM user_roles ur
LEFT JOIN roles r ON ur.role_id = r.id
WHERE ur.user_id = $1 AND ur.organization_id = $2
"""

GET_USER_ROLES_OVERVIEW_BY_ROLE_QUERY = """
SELECT 
    ur.id,
    ur.organization_id,
    ur.user_id,
    ur.role_id,
    ur.team_id,
    ur.created_at,
    ur.updated_at,
    r.name as role_name,
    r.description as role_description,
    r.type as role_type,
    r.permissions as role_permissions,
    r.team_id as role_team_id,
    r.organization_id as role_organization_id,
    r.created_at as role_created_at,
    r.updated_at as role_updated_at
FROM user_roles ur
LEFT JOIN roles r ON ur.role_id = r.id
WHERE ur.role_id = $1
"""

GET_USER_ROLES_OVERVIEW_BY_TEAM_QUERY = """
SELECT 
    ur.id,
    ur.organization_id,
    ur.user_id,
    ur.role_id,
    ur.team_id,
    ur.created_at,
    ur.updated_at,
    r.name as role_name,
    r.description as role_description,
    r.type as role_type,
    r.permissions as role_permissions,
    r.team_id as role_team_id,
    r.organization_id as role_organization_id,
    r.created_at as role_created_at,
    r.updated_at as role_updated_at
FROM user_roles ur
LEFT JOIN roles r ON ur.role_id = r.id
WHERE ur.team_id = $1
"""

