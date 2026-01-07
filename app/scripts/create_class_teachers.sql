CREATE TABLE class_teachers (
    class_id UUID NOT NULL,
    user_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (class_id, user_id),

    CONSTRAINT fk_class_teachers_class FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);

-- Create index on class_id for faster queries
CREATE INDEX IF NOT EXISTS idx_class_teachers_class_id ON class_teachers(class_id);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_class_teachers_user_id ON class_teachers(user_id);

-- Create composite index for common queries
CREATE INDEX IF NOT EXISTS idx_class_teachers_class_user ON class_teachers(class_id, user_id);
