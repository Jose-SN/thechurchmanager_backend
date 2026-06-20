GET_ORGANIZATIONS_QUERY = """
SELECT * FROM organizations
"""

GET_ORGANIZATION_BY_ID_QUERY = """
SELECT * FROM organizations WHERE id = $1
"""

GET_ORGANIZATION_BY_EMAIL_QUERY = """
SELECT * FROM organizations WHERE contact->>'email' = $1
"""

GET_ORGANIZATION_BY_SUPABASE_USER_ID_QUERY = """
SELECT * FROM organizations WHERE additional_information->>'supabase_user_id' = $1
"""

INSERT_ORGANIZATION_QUERY = """
INSERT INTO organizations (
    name, title, contact, leadership, social, volunteers,
    additional_information, profile_image, about, members, password,
    created_at, updated_at
)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW(), NOW())
RETURNING *
"""

UPDATE_ORGANIZATION_QUERY = """
UPDATE organizations
SET
    name = $1,
    title = $2,
    contact = $3,
    leadership = $4,
    social = $5,
    volunteers = $6,
    additional_information = $7,
    profile_image = $8,
    about = $9,
    members = $10,
    password = $11,
    updated_at = NOW()
WHERE id = $12
RETURNING *
"""

DELETE_ORGANIZATION_QUERY = """
DELETE FROM organizations WHERE id = $1
"""
