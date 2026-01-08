GET_ACCOUNTS_QUERY = """
SELECT * FROM accounts
"""

GET_ACCOUNT_BY_ID_QUERY = """
SELECT * FROM accounts WHERE id = $1
"""

GET_ACCOUNTS_BY_ORGANIZATION_QUERY = """
SELECT * FROM accounts WHERE organization_id = $1
"""

INSERT_ACCOUNT_QUERY = """
INSERT INTO accounts (date, type, payment_type, description, paid_out, paid_in, organization_id, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
RETURNING *
"""

UPDATE_ACCOUNT_QUERY = """
UPDATE accounts
SET date = $1, type = $2, payment_type = $3, description = $4, paid_out = $5, paid_in = $6, organization_id = $7, updated_at = NOW()
WHERE id = $8
RETURNING *
"""

DELETE_ACCOUNT_QUERY = """
DELETE FROM accounts WHERE id = $1
"""

