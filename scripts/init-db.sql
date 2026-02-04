-- MediNote-AI Database Initialization Script
-- This script runs when PostgreSQL container is first created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database if not exists (handled by POSTGRES_DB env var)
-- Additional setup can be added here

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE medinote TO medinote;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'MediNote-AI database initialized successfully';
END $$;
