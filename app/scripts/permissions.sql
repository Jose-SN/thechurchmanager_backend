-- Permissions table reflecting IPermissionSchema (merged from both definitions)
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    role_id UUID,
    module_id UUID,
    team_id UUID,
    permissions JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(organization_id, role_id, module_id, team_id)
);

-- Create index on organization_id for faster queries
CREATE INDEX IF NOT EXISTS idx_permissions_organization_id ON permissions(organization_id);

-- Create index on role_id for faster queries
CREATE INDEX IF NOT EXISTS idx_permissions_role_id ON permissions(role_id);

-- Create index on module_id for faster queries
CREATE INDEX IF NOT EXISTS idx_permissions_module_id ON permissions(module_id);

-- Create index on team_id for faster queries
CREATE INDEX IF NOT EXISTS idx_permissions_team_id ON permissions(team_id);

-- Create composite index for common queries
CREATE INDEX IF NOT EXISTS idx_permissions_role_module ON permissions(role_id, module_id);

-- Keep updated_at in sync for permissions
CREATE OR REPLACE FUNCTION set_permissions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_permissions_updated_at ON permissions;
CREATE TRIGGER trg_permissions_updated_at
BEFORE UPDATE ON permissions
FOR EACH ROW
EXECUTE FUNCTION set_permissions_updated_at();

