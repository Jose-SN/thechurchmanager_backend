-- =====================================================
-- ROTAS TABLE - PostgreSQL Schema
-- =====================================================
-- This table stores service schedules/rotas with date, team, and organization
-- =====================================================

CREATE TABLE IF NOT EXISTS rotas (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    team_id UUID NOT NULL,
    service_type VARCHAR(100),
    notes TEXT,
    organization_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    
    CONSTRAINT fk_rotas_team 
        FOREIGN KEY (team_id) 
        REFERENCES teams(id) 
        ON DELETE CASCADE,
    
    -- Ensure date is not null
    CONSTRAINT chk_rotas_date_not_null 
        CHECK (date IS NOT NULL),
    
    -- Ensure team_id is not null
    CONSTRAINT chk_rotas_team_id_not_null 
        CHECK (team_id IS NOT NULL)
);

-- Indexes for rotas table
CREATE INDEX IF NOT EXISTS idx_rotas_organization_id ON rotas(organization_id);
CREATE INDEX IF NOT EXISTS idx_rotas_team_id ON rotas(team_id);
CREATE INDEX IF NOT EXISTS idx_rotas_date ON rotas(date);
CREATE INDEX IF NOT EXISTS idx_rotas_created_at ON rotas(created_at);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_rotas_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_rotas_updated_at
    BEFORE UPDATE ON rotas
    FOR EACH ROW
    EXECUTE FUNCTION update_rotas_updated_at();
