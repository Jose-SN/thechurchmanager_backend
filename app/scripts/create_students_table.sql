-- Create students table
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    organization_id UUID NOT NULL,
    class_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_students_class FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL
);

-- Create index on organization_id for faster queries
CREATE INDEX IF NOT EXISTS idx_students_organization_id ON students(organization_id);

-- Create index on class_id for faster queries
CREATE INDEX IF NOT EXISTS idx_students_class_id ON students(class_id);

-- Create index on email for faster searches
CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_students_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_students_updated_at
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_students_updated_at();

