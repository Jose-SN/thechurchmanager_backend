GET_TEACHERS_QUERY = """
SELECT * FROM teachers
"""

GET_TEACHER_BY_ID_QUERY = """
SELECT * FROM teachers WHERE id = $1
"""

GET_TEACHERS_BY_ORGANIZATION_QUERY = """
SELECT * FROM teachers WHERE organization_id = $1
"""

INSERT_TEACHER_QUERY = """
INSERT INTO teachers (name, email, phone, organization_id, created_at, updated_at)
VALUES ($1, $2, $3, $4, NOW(), NOW())
RETURNING *
"""

UPDATE_TEACHER_QUERY = """
UPDATE teachers
SET name = $1, email = $2, phone = $3, organization_id = $4, updated_at = NOW()
WHERE id = $5
RETURNING *
"""

DELETE_TEACHER_QUERY = """
DELETE FROM teachers WHERE id = $1
"""
