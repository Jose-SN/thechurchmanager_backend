-- Create classes table
CREATE TABLE IF NOT EXISTS classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    organization_id UUID NOT NULL,
    teacher_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_classes_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
);

-- Create index on organization_id for faster queries
CREATE INDEX IF NOT EXISTS idx_classes_organization_id ON classes(organization_id);

-- Create index on teacher_id for faster queries
CREATE INDEX IF NOT EXISTS idx_classes_teacher_id ON classes(teacher_id);

-- Create index on name for faster searches
CREATE INDEX IF NOT EXISTS idx_classes_name ON classes(name);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_classes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_classes_updated_at
    BEFORE UPDATE ON classes
    FOR EACH ROW
    EXECUTE FUNCTION update_classes_updated_at();

