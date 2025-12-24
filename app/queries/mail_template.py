GET_MAIL_TEMPLATES_QUERY = """
SELECT * FROM mail_templates
"""

GET_MAIL_TEMPLATE_BY_ID_QUERY = """
SELECT * FROM mail_templates WHERE id = $1
"""

GET_MAIL_TEMPLATE_BY_KEY_QUERY = """
SELECT * FROM mail_templates WHERE key = $1
"""

GET_MAIL_TEMPLATES_BY_ORGANIZATION_QUERY = """
SELECT * FROM mail_templates WHERE organization_id = $1
"""

INSERT_MAIL_TEMPLATE_QUERY = """
INSERT INTO mail_templates (key, subject, body, organization_id, created_at, updated_at)
VALUES ($1, $2, $3, $4, NOW(), NOW())
RETURNING *
"""

UPDATE_MAIL_TEMPLATE_QUERY = """
UPDATE mail_templates
SET key = $1, subject = $2, body = $3, organization_id = $4, updated_at = NOW()
WHERE id = $5
RETURNING *
"""

DELETE_MAIL_TEMPLATE_QUERY = """
DELETE FROM mail_templates WHERE id = $1
"""

