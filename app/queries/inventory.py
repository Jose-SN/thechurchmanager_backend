GET_INVENTORIES_QUERY = """
SELECT * FROM inventories
"""

GET_INVENTORY_BY_ID_QUERY = """
SELECT * FROM inventories WHERE id = $1
"""

INSERT_INVENTORY_QUERY = """
INSERT INTO inventories (name, description, quantity, created_at, updated_at)
VALUES ($1, $2, $3, NOW(), NOW())
RETURNING *
"""

INSERT_BULK_INVENTORIES_QUERY = """
INSERT INTO inventories (name, description, quantity, created_at, updated_at)
VALUES ($1, $2, $3, NOW(), NOW())
RETURNING *
"""

UPDATE_INVENTORY_QUERY = """
UPDATE inventories
SET name = $1, description = $2, quantity = $3, updated_at = NOW()
WHERE id = $4
RETURNING *
"""

DELETE_INVENTORY_QUERY = """
DELETE FROM inventories WHERE id = $1
"""

