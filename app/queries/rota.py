GET_ROTAS_QUERY = """
SELECT * FROM rotas
ORDER BY date DESC, created_at DESC
"""

GET_ROTA_BY_ID_QUERY = """
SELECT * FROM rotas WHERE id = $1
"""

GET_ROTAS_BY_ORGANIZATION_QUERY = """
SELECT * FROM rotas 
WHERE organization_id = $1
ORDER BY date DESC, created_at DESC
"""

GET_ROTAS_BY_TEAM_QUERY = """
SELECT * FROM rotas 
WHERE team_id = $1
ORDER BY date DESC, created_at DESC
"""

SEARCH_ROTAS_QUERY = """
SELECT * FROM rotas
WHERE organization_id = $1
    AND ($2::TIMESTAMP IS NULL OR date::date = $2::date)
    AND ($3::INTEGER IS NULL OR team_id = $3)
    AND ($4::VARCHAR IS NULL OR LOWER(service_type) LIKE LOWER('%' || $4 || '%'))
ORDER BY date DESC, created_at DESC
"""

INSERT_ROTA_QUERY = """
INSERT INTO rotas (
    date,
    team_id,
    service_type,
    notes,
    organization_id,
    created_at,
    updated_at
) VALUES (
    $1, $2, $3, $4, $5, NOW(), NOW()
)
RETURNING *
"""

UPDATE_ROTA_QUERY = """
UPDATE rotas
SET 
    date = $1,
    team_id = $2,
    service_type = $3,
    notes = $4,
    updated_at = NOW()
WHERE id = $5 AND organization_id = $6
RETURNING *
"""

DELETE_ROTA_QUERY = """
DELETE FROM rotas 
WHERE id = $1 AND organization_id = $2
"""
