-- Run when organizations table exists but is missing JSON/auth columns
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS title VARCHAR(255);
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS contact JSONB DEFAULT '{}'::jsonb;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS leadership JSONB DEFAULT '[]'::jsonb;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS social JSONB DEFAULT '{}'::jsonb;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS volunteers JSONB DEFAULT '[]'::jsonb;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS additional_information JSONB DEFAULT '{}'::jsonb;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS profile_image TEXT;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS about TEXT;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS members JSONB DEFAULT '[]'::jsonb;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS password TEXT;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx_organizations_contact_email
    ON organizations ((contact->>'email'));

CREATE INDEX IF NOT EXISTS idx_organizations_supabase_user_id
    ON organizations ((additional_information->>'supabase_user_id'));
