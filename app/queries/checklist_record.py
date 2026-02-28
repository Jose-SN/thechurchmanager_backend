GET_CHECKLIST_RECORDS_QUERY = """
SELECT * FROM checklist_records ORDER BY date DESC, created_at DESC
"""

GET_CHECKLIST_RECORD_BY_ID_QUERY = """
SELECT * FROM checklist_records WHERE id = $1
"""

GET_CHECKLIST_RECORDS_BY_TEMPLATE_QUERY = """
SELECT * FROM checklist_records WHERE template_id = $1 ORDER BY date DESC
"""

GET_CHECKLIST_RECORDS_BY_TEAM_QUERY = """
SELECT * FROM checklist_records WHERE team_id = $1 ORDER BY date DESC
"""

GET_CHECKLIST_RECORD_BY_TEMPLATE_TEAM_DATE_QUERY = """
SELECT * FROM checklist_records WHERE template_id = $1 AND team_id = $2 AND date = $3
"""

INSERT_CHECKLIST_RECORD_QUERY = """
INSERT INTO checklist_records (template_id, team_id, date, completed_by, notes, created_at)
VALUES ($1, $2, $3, $4, $5, NOW())
RETURNING *
"""

UPDATE_CHECKLIST_RECORD_QUERY = """
UPDATE checklist_records
SET completed_by = $1, notes = $2
WHERE id = $3
RETURNING *
"""

DELETE_CHECKLIST_RECORD_QUERY = """
DELETE FROM checklist_records WHERE id = $1
"""
