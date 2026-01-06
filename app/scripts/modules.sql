-- Modules table reflecting IModuleSchema (merged from both definitions)
CREATE TABLE IF NOT EXISTS modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    key TEXT NOT NULL,
    description TEXT,
    organization_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index on organization_id for faster queries
CREATE INDEX IF NOT EXISTS idx_modules_organization_id ON modules(organization_id);

-- Create index on name for faster searches
CREATE INDEX IF NOT EXISTS idx_modules_name ON modules(name);

-- Create index on key for faster lookups
CREATE INDEX IF NOT EXISTS idx_modules_key ON modules(key);

-- Keep updated_at in sync for modules
CREATE OR REPLACE FUNCTION set_modules_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_modules_updated_at ON modules;
CREATE TRIGGER trg_modules_updated_at
BEFORE UPDATE ON modules
FOR EACH ROW
EXECUTE FUNCTION set_modules_updated_at();

