-- Roles table reflecting IRoleSchema (merged from both definitions)
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    team_id UUID,
    organization_id UUID NOT NULL,
    type TEXT,
    permissions JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index on organization_id for faster queries
CREATE INDEX IF NOT EXISTS idx_roles_organization_id ON roles(organization_id);

-- Create index on team_id for faster queries
CREATE INDEX IF NOT EXISTS idx_roles_team_id ON roles(team_id);

-- Create index on name for faster searches
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);

-- Create index on type for faster filtering
CREATE INDEX IF NOT EXISTS idx_roles_type ON roles(type);

-- Keep updated_at in sync for roles
CREATE OR REPLACE FUNCTION set_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_roles_updated_at ON roles;
CREATE TRIGGER trg_roles_updated_at
BEFORE UPDATE ON roles
FOR EACH ROW
EXECUTE FUNCTION set_roles_updated_at();

