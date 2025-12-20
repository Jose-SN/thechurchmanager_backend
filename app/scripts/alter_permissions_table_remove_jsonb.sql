-- Migration script to remove permissions JSONB column and add separate boolean columns
-- Run this if the permissions table already exists with the old structure

-- Add new boolean columns if they don't exist
ALTER TABLE permissions ADD COLUMN IF NOT EXISTS view BOOLEAN DEFAULT FALSE;
ALTER TABLE permissions ADD COLUMN IF NOT EXISTS edit BOOLEAN DEFAULT FALSE;
ALTER TABLE permissions ADD COLUMN IF NOT EXISTS "create" BOOLEAN DEFAULT FALSE;
ALTER TABLE permissions ADD COLUMN IF NOT EXISTS "delete" BOOLEAN DEFAULT FALSE;

-- Migrate data from JSONB permissions column to boolean columns (if permissions column exists)
-- This will extract View, Edit, Create, Delete from the JSONB permissions column
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'permissions' AND column_name = 'permissions'
    ) THEN
        -- Update view column
        UPDATE permissions 
        SET view = COALESCE((permissions->>'View')::boolean, (permissions->>'view')::boolean, FALSE)
        WHERE permissions IS NOT NULL;
        
        -- Update edit column
        UPDATE permissions 
        SET edit = COALESCE((permissions->>'Edit')::boolean, (permissions->>'edit')::boolean, FALSE)
        WHERE permissions IS NOT NULL;
        
        -- Update create column
        UPDATE permissions 
        SET "create" = COALESCE((permissions->>'Create')::boolean, (permissions->>'create')::boolean, FALSE)
        WHERE permissions IS NOT NULL;
        
        -- Update delete column
        UPDATE permissions 
        SET "delete" = COALESCE((permissions->>'Delete')::boolean, (permissions->>'delete')::boolean, FALSE)
        WHERE permissions IS NOT NULL;
        
        -- Drop the old permissions JSONB column
        ALTER TABLE permissions DROP COLUMN IF EXISTS permissions;
    END IF;
END $$;

