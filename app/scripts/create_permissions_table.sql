-- Create permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    role_id UUID,
    module_id UUID,
    team_id UUID,
    view BOOLEAN DEFAULT FALSE,
    edit BOOLEAN DEFAULT FALSE,
    "create" BOOLEAN DEFAULT FALSE,
    "delete" BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_permissions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_permissions_updated_at
    BEFORE UPDATE ON permissions
    FOR EACH ROW
    EXECUTE FUNCTION update_permissions_updated_at();

