-- Organizations table for church/organization profiles and auth metadata
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    contact JSONB DEFAULT '{}'::jsonb,
    leadership JSONB DEFAULT '[]'::jsonb,
    social JSONB DEFAULT '{}'::jsonb,
    volunteers JSONB DEFAULT '[]'::jsonb,
    additional_information JSONB DEFAULT '{}'::jsonb,
    profile_image TEXT,
    about TEXT,
    members JSONB DEFAULT '[]'::jsonb,
    password TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_organizations_contact_email
    ON organizations ((contact->>'email'));

CREATE INDEX IF NOT EXISTS idx_organizations_supabase_user_id
    ON organizations ((additional_information->>'supabase_user_id'));

CREATE OR REPLACE FUNCTION update_organizations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_organizations_updated_at ON organizations;

CREATE TRIGGER trigger_update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_organizations_updated_at();
