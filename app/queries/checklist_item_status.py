GET_CHECKLIST_ITEM_STATUSES_QUERY = """
SELECT * FROM checklist_item_statuses
"""

GET_CHECKLIST_ITEM_STATUS_BY_ID_QUERY = """
SELECT * FROM checklist_item_statuses WHERE id = $1
"""

GET_CHECKLIST_ITEM_STATUSES_BY_RECORD_QUERY = """
SELECT * FROM checklist_item_statuses WHERE checklist_record_id = $1
"""

GET_CHECKLIST_ITEM_STATUS_BY_RECORD_AND_ITEM_QUERY = """
SELECT * FROM checklist_item_statuses 
WHERE checklist_record_id = $1 AND checklist_item_id = $2
"""

INSERT_CHECKLIST_ITEM_STATUS_QUERY = """
INSERT INTO checklist_item_statuses (checklist_record_id, checklist_item_id, is_checked, issue_reported)
VALUES ($1, $2, $3, $4)
ON CONFLICT (checklist_record_id, checklist_item_id) 
DO UPDATE SET is_checked = EXCLUDED.is_checked, issue_reported = EXCLUDED.issue_reported
RETURNING *
"""

UPDATE_CHECKLIST_ITEM_STATUS_QUERY = """
UPDATE checklist_item_statuses
SET is_checked = $1, issue_reported = $2
WHERE id = $3
RETURNING *
"""

DELETE_CHECKLIST_ITEM_STATUS_QUERY = """
DELETE FROM checklist_item_statuses WHERE id = $1
"""
