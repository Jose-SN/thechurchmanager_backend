GET_STUDENTS_QUERY = """
SELECT * FROM students
"""

GET_STUDENT_BY_ID_QUERY = """
SELECT * FROM students WHERE id = $1
"""

GET_STUDENTS_BY_ORGANIZATION_QUERY = """
SELECT * FROM students WHERE organization_id = $1
"""

GET_STUDENTS_BY_CLASS_QUERY = """
SELECT * FROM students WHERE class_id = $1
"""

INSERT_STUDENT_QUERY = """
INSERT INTO students (name, email, phone, organization_id, class_id, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
RETURNING *
"""

UPDATE_STUDENT_QUERY = """
UPDATE students
SET name = $1, email = $2, phone = $3, organization_id = $4, class_id = $5, updated_at = NOW()
WHERE id = $6
RETURNING *
"""

DELETE_STUDENT_QUERY = """
DELETE FROM students WHERE id = $1
"""

