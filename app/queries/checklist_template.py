GET_CHECKLIST_TEMPLATES_QUERY = """
SELECT * FROM checklist_templates ORDER BY created_at DESC
"""

GET_CHECKLIST_TEMPLATE_BY_ID_QUERY = """
SELECT * FROM checklist_templates WHERE id = $1
"""

GET_CHECKLIST_TEMPLATES_BY_TEAM_QUERY = """
SELECT * FROM checklist_templates WHERE team_id = $1 ORDER BY created_at DESC
"""

INSERT_CHECKLIST_TEMPLATE_QUERY = """
INSERT INTO checklist_templates (team_id, name, description, is_active, created_by, created_at)
VALUES ($1, $2, $3, $4, $5, NOW())
RETURNING *
"""

UPDATE_CHECKLIST_TEMPLATE_QUERY = """
UPDATE checklist_templates
SET name = $1, description = $2, is_active = $3, created_by = $4
WHERE id = $5
RETURNING *
"""

DELETE_CHECKLIST_TEMPLATE_QUERY = """
DELETE FROM checklist_templates WHERE id = $1
"""
