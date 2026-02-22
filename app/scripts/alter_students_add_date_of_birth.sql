-- Add date_of_birth column to students table
ALTER TABLE students
ADD COLUMN IF NOT EXISTS date_of_birth DATE;

-- Add index on date_of_birth for faster queries (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_students_date_of_birth ON students(date_of_birth);

-- Add comment to document the column
COMMENT ON COLUMN students.date_of_birth IS 'Student date of birth';
