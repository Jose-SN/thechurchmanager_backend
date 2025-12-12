CREATE DATABASE thechurchmanager

-- Create teams table
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    organization_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on organization_id for faster queries
CREATE INDEX IF NOT EXISTS idx_teams_organization_id ON teams(organization_id);

-- Create index on name for faster searches
CREATE INDEX IF NOT EXISTS idx_teams_name ON teams(name);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_teams_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_teams_updated_at
    BEFORE UPDATE ON teams
    FOR EACH ROW
    EXECUTE FUNCTION update_teams_updated_at();

-- Alternative version using SERIAL instead of UUID (if you prefer integer IDs)
/*
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    organization_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_teams_organization FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);
*/
-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    team_id UUID,
    organization_id UUID NOT NULL,
    type VARCHAR(50),
    permissions JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on organization_id for faster queries
CREATE INDEX IF NOT EXISTS idx_roles_organization_id ON roles(organization_id);

-- Create index on team_id for faster queries
CREATE INDEX IF NOT EXISTS idx_roles_team_id ON roles(team_id);

-- Create index on name for faster searches
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);

-- Create index on type for faster filtering
CREATE INDEX IF NOT EXISTS idx_roles_type ON roles(type);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE FUNCTION update_roles_updated_at();

-- Create modules table
CREATE TABLE IF NOT EXISTS modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    key VARCHAR(255) NOT NULL,
    description TEXT,
    organization_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on organization_id for faster queries
CREATE INDEX IF NOT EXISTS idx_modules_organization_id ON modules(organization_id);

-- Create index on name for faster searches
CREATE INDEX IF NOT EXISTS idx_modules_name ON modules(name);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_modules_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_modules_updated_at
    BEFORE UPDATE ON modules
    FOR EACH ROW
    EXECUTE FUNCTION update_modules_updated_at();



-- Create permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    role_id UUID,
    module_id UUID,
    team_id UUID,
    permissions JSONB DEFAULT '{}'::jsonb,
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

