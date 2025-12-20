-- Create the IAM database (run separately if it already exists)
CREATE DATABASE thechurchmanager;

-- Connect to the IAM database
\c thechurchmanager;

-- Enable UUID generation helper
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

