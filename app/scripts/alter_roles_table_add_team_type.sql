-- Migration script to add team_id and type columns to existing roles table
-- Run this if the roles table already exists

-- Add team_id column (nullable, can be added to existing roles later)
ALTER TABLE roles ADD COLUMN IF NOT EXISTS team_id UUID;

-- Add type column (nullable)
ALTER TABLE roles ADD COLUMN IF NOT EXISTS type VARCHAR(50);

-- Create index on team_id for faster queries
CREATE INDEX IF NOT EXISTS idx_roles_team_id ON roles(team_id);

-- Create index on type for faster filtering
CREATE INDEX IF NOT EXISTS idx_roles_type ON roles(type);

