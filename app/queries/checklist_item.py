GET_CHECKLIST_ITEMS_QUERY = """
SELECT * FROM checklist_items ORDER BY "order", created_at
"""

GET_CHECKLIST_ITEM_BY_ID_QUERY = """
SELECT * FROM checklist_items WHERE id = $1
"""

GET_CHECKLIST_ITEMS_BY_TEMPLATE_QUERY = """
SELECT * FROM checklist_items WHERE template_id = $1 ORDER BY "order", created_at
"""

INSERT_CHECKLIST_ITEM_QUERY = """
INSERT INTO checklist_items (template_id, title, description, "order", is_required, created_at)
VALUES ($1, $2, $3, $4, $5, NOW())
RETURNING *
"""

UPDATE_CHECKLIST_ITEM_QUERY = """
UPDATE checklist_items
SET title = $1, description = $2, "order" = $3, is_required = $4
WHERE id = $5
RETURNING *
"""

DELETE_CHECKLIST_ITEM_QUERY = """
DELETE FROM checklist_items WHERE id = $1
"""
