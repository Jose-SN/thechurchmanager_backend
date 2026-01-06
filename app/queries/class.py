GET_CLASSES_QUERY = """
SELECT * FROM classes
"""

GET_CLASS_BY_ID_QUERY = """
SELECT * FROM classes WHERE id = $1
"""

GET_CLASSES_BY_ORGANIZATION_QUERY = """
SELECT * FROM classes WHERE organization_id = $1
"""

GET_CLASSES_BY_TEACHER_QUERY = """
SELECT * FROM classes WHERE teacher_id = $1
"""

INSERT_CLASS_QUERY = """
INSERT INTO classes (name, description, organization_id, teacher_id, created_at, updated_at)
VALUES ($1, $2, $3, $4, NOW(), NOW())
RETURNING *
"""

UPDATE_CLASS_QUERY = """
UPDATE classes
SET name = $1, description = $2, organization_id = $3, teacher_id = $4, updated_at = NOW()
WHERE id = $5
RETURNING *
"""

DELETE_CLASS_QUERY = """
DELETE FROM classes WHERE id = $1
"""

