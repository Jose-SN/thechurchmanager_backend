GET_PLANS_QUERY = """
SELECT * FROM plans
"""

GET_PLAN_BY_ID_QUERY = """
SELECT * FROM plans WHERE id = $1
"""

INSERT_PLAN_QUERY = """
INSERT INTO plans (name, description, created_at, updated_at)
VALUES ($1, $2, NOW(), NOW())
RETURNING *
"""

INSERT_BULK_PLANS_QUERY = """
INSERT INTO plans (name, description, created_at, updated_at)
VALUES ($1, $2, NOW(), NOW())
RETURNING *
"""

UPDATE_PLAN_QUERY = """
UPDATE plans
SET name = $1, description = $2, updated_at = NOW()
WHERE id = $3
RETURNING *
"""

DELETE_PLAN_QUERY = """
DELETE FROM plans WHERE id = $1
"""

