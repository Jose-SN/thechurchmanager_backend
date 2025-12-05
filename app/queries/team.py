GET_TEAMS_QUERY = """
SELECT * FROM teams
"""

GET_TEAM_BY_ID_QUERY = """
SELECT * FROM teams WHERE id = $1
"""

GET_TEAMS_BY_ORGANIZATION_QUERY = """
SELECT * FROM teams WHERE organization_id = $1
"""

INSERT_TEAM_QUERY = """
INSERT INTO teams (name, organization_id, created_at, updated_at)
VALUES ($1, $2, NOW(), NOW())
RETURNING *
"""

INSERT_BULK_TEAMS_QUERY = """
INSERT INTO teams (name, organization_id, created_at, updated_at)
VALUES ($1, $2, NOW(), NOW())
RETURNING *
"""

UPDATE_TEAM_QUERY = """
UPDATE teams
SET name = $1, organization_id = $2, updated_at = NOW()
WHERE id = $3
RETURNING *
"""

DELETE_TEAM_QUERY = """
DELETE FROM teams WHERE id = $1
"""

