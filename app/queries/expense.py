GET_EXPENSES_QUERY = """
SELECT * FROM expenses
ORDER BY expense_date DESC, created_at DESC
"""

GET_EXPENSE_BY_ID_QUERY = """
SELECT * FROM expenses WHERE id = $1
"""

GET_EXPENSES_BY_ORGANIZATION_QUERY = """
SELECT * FROM expenses 
WHERE organization_id = $1
ORDER BY expense_date DESC, created_at DESC
"""

GET_EXPENSES_BY_TEAM_QUERY = """
SELECT * FROM expenses 
WHERE team_id = $1
ORDER BY expense_date DESC, created_at DESC
"""

SEARCH_EXPENSES_QUERY = """
SELECT * FROM expenses
WHERE organization_id = $1
    AND ($2::DATE IS NULL OR expense_date = $2::DATE)
    AND ($3::UUID IS NULL OR team_id = $3)
    AND ($4::VARCHAR IS NULL OR LOWER(category) LIKE LOWER('%' || $4 || '%'))
    AND ($5::VARCHAR IS NULL OR LOWER(title) LIKE LOWER('%' || $5 || '%'))
ORDER BY expense_date DESC, created_at DESC
"""

INSERT_EXPENSE_QUERY = """
INSERT INTO expenses (
    title,
    amount,
    category,
    expense_date,
    description,
    organization_id,
    team_id,
    created_at,
    updated_at
) VALUES (
    $1, $2, $3, $4, $5, $6, $7, NOW(), NOW()
)
RETURNING *
"""

UPDATE_EXPENSE_QUERY = """
UPDATE expenses
SET 
    title = $1,
    amount = $2,
    category = $3,
    expense_date = $4,
    description = $5,
    team_id = $6,
    updated_at = NOW()
WHERE id = $7 AND organization_id = $8
RETURNING *
"""

DELETE_EXPENSE_QUERY = """
DELETE FROM expenses 
WHERE id = $1 AND organization_id = $2
"""
