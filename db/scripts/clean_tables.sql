-- Script to clean all database tables
-- This script truncates all tables using CASCADE to handle foreign key constraints
-- 
-- Usage:
--   psql -U pic_user -d pic_db -f scripts/clean_tables.sql
--   Or from docker:
--   docker-compose -f db/docker-compose.yml exec database psql -U pic_user -d pic_db -f /path/to/scripts/clean_tables.sql

-- Truncate all tables in dependency order
-- Using CASCADE to automatically handle foreign key relationships
TRUNCATE TABLE evaluation CASCADE;
TRUNCATE TABLE inference CASCADE;
TRUNCATE TABLE model CASCADE;
TRUNCATE TABLE training CASCADE;
TRUNCATE TABLE jobs CASCADE;

-- Note: The order doesn't strictly matter with CASCADE, but it's listed for clarity
-- CASCADE will automatically truncate dependent tables regardless of order
