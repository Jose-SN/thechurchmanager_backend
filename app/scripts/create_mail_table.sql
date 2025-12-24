-- Create mail_templates table
CREATE TABLE IF NOT EXISTS mail_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255) NOT NULL UNIQUE,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on key for faster lookups
CREATE INDEX IF NOT EXISTS idx_mail_templates_key ON mail_templates(key);


-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_mail_templates_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_mail_templates_updated_at
    BEFORE UPDATE ON mail_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_mail_templates_updated_at();

