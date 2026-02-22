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
INSERT INTO students (first_name, last_name, date_of_birth, email, phone, organization_id, class_id, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
RETURNING *
"""

UPDATE_STUDENT_QUERY = """
UPDATE students
SET first_name = $1, last_name = $2, date_of_birth = $3, email = $4, phone = $5, organization_id = $6, class_id = $7, updated_at = NOW()
WHERE id = $8
RETURNING *
"""

DELETE_STUDENT_QUERY = """
DELETE FROM students WHERE id = $1
"""

