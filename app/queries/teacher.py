GET_TEACHERS_QUERY = """
SELECT * FROM teachers
"""

GET_TEACHER_BY_ID_QUERY = """
SELECT * FROM teachers WHERE id = $1
"""

INSERT_TEACHER_QUERY = """
INSERT INTO teachers (name, email, phone, ...)  -- add all required columns
VALUES ($1, $2, $3, ...)                       -- match the number of columns
RETURNING *
"""

UPDATE_TEACHER_QUERY = """
UPDATE teachers
SET name = $1, email = $2, phone = $3, ...     -- add all updatable columns
WHERE id = $N                                  -- $N is the last parameter (teacher_id)
RETURNING *
"""

DELETE_TEACHER_QUERY = """
DELETE FROM teachers WHERE id = $1
"""
