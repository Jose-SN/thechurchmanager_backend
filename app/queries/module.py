GET_MODULES_QUERY = """
SELECT * FROM modules
"""

GET_MODULE_BY_ID_QUERY = """
SELECT * FROM modules WHERE id = $1
"""

GET_MODULES_BY_ORGANIZATION_QUERY = """
SELECT * FROM modules WHERE organization_id = $1
"""

INSERT_MODULE_QUERY = """
INSERT INTO modules (name, description, organization_id, created_at, updated_at)
VALUES ($1, $2, $3, NOW(), NOW())
RETURNING *
"""

INSERT_BULK_MODULES_QUERY = """
INSERT INTO modules (name, description, organization_id, created_at, updated_at)
VALUES ($1, $2, $3, NOW(), NOW())
RETURNING *
"""

UPDATE_MODULE_QUERY = """
UPDATE modules
SET name = $1, description = $2, organization_id = $3, updated_at = NOW()
WHERE id = $4
RETURNING *
"""

DELETE_MODULE_QUERY = """
DELETE FROM modules WHERE id = $1
"""

