-- Create inventories table
CREATE TABLE IF NOT EXISTS inventories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2),
    stock_left INTEGER NOT NULL DEFAULT 0,
    purchase_date DATE,
    patch_test_date DATE,
    warranty_date DATE,
    organization_id UUID NOT NULL,
    team_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
);

-- Create composite index on (organization_id, team_id) for query optimization
CREATE INDEX IF NOT EXISTS idx_inventories_org_team ON inventories(organization_id, team_id);

-- Create index on organization_id for faster queries
CREATE INDEX IF NOT EXISTS idx_inventories_organization_id ON inventories(organization_id);

-- Create index on team_id for faster queries
CREATE INDEX IF NOT EXISTS idx_inventories_team_id ON inventories(team_id);

-- Create index on item_name for faster searches
CREATE INDEX IF NOT EXISTS idx_inventories_item_name ON inventories(item_name);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_inventories_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_inventories_updated_at
    BEFORE UPDATE ON inventories
    FOR EACH ROW
    EXECUTE FUNCTION update_inventories_updated_at();

