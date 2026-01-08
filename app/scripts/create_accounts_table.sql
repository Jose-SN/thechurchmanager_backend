-- Create accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
    payment_type VARCHAR(10) CHECK (payment_type IN ('VIS', 'CR', 'TFR', 'BP')),
    description VARCHAR(500) NOT NULL,
    paid_out DECIMAL(10, 2) DEFAULT 0 CHECK (paid_out >= 0),
    paid_in DECIMAL(10, 2) DEFAULT 0 CHECK (paid_in >= 0),
    organization_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on organization_id for faster queries
CREATE INDEX IF NOT EXISTS idx_accounts_organization_id ON accounts(organization_id);

-- Create index on date for faster date-based queries
CREATE INDEX IF NOT EXISTS idx_accounts_date ON accounts(date);

-- Create index on type for faster filtering
CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(type);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_accounts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_accounts_updated_at
    BEFORE UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_accounts_updated_at();

