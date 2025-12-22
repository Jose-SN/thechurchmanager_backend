-- Create user_roles table
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role_id UUID NOT NULL,
    team_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_user_roles_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_roles_team FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL
);

-- Create index on organization_id for faster queries
CREATE INDEX IF NOT EXISTS idx_user_roles_organization_id ON user_roles(organization_id);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);

-- Create index on role_id for faster queries
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id);

-- Create index on team_id for faster queries
CREATE INDEX IF NOT EXISTS idx_user_roles_team_id ON user_roles(team_id);

-- Create composite index for common queries (user + role)
CREATE INDEX IF NOT EXISTS idx_user_roles_user_role ON user_roles(user_id, role_id);

-- Create unique constraint to prevent duplicate user-role assignments within same organization
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_roles_unique_user_role_org ON user_roles(user_id, role_id, organization_id);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_user_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_roles_updated_at
    BEFORE UPDATE ON user_roles
    FOR EACH ROW
    EXECUTE FUNCTION update_user_roles_updated_at();

