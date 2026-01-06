GET_INVENTORIES_QUERY = """
SELECT * FROM inventories
"""

GET_INVENTORY_BY_ID_QUERY = """
SELECT * FROM inventories WHERE id = $1
"""

GET_INVENTORIES_BY_ORGANIZATION_QUERY = """
SELECT * FROM inventories WHERE organization_id = $1
"""

GET_INVENTORIES_BY_ORGANIZATION_AND_TEAM_QUERY = """
SELECT * FROM inventories WHERE organization_id = $1 AND team_id = $2
"""

INSERT_INVENTORY_QUERY = """
INSERT INTO inventories (item_name, price, stock_left, purchase_date, patch_test_date, warranty_date, organization_id, team_id, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
RETURNING *
"""

UPDATE_INVENTORY_QUERY = """
UPDATE inventories
SET item_name = $1, price = $2, stock_left = $3, purchase_date = $4, patch_test_date = $5, warranty_date = $6, organization_id = $7, team_id = $8, updated_at = NOW()
WHERE id = $9
RETURNING *
"""

DELETE_INVENTORY_QUERY = """
DELETE FROM inventories WHERE id = $1
"""
