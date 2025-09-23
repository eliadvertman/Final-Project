-- Migration: Remove task_number from jobs table, add output_dir to inference table, and add sbatch_content to jobs table
-- Created: 2025-09-23
-- Description:
--   - Remove task_number column from jobs table (no longer needed as it's a constant)
--   - Add output_dir column to inference table (for dynamic output directory tracking)
--   - Add sbatch_content column to jobs table (for storing interpolated SLURM template content)

-- ==== FORWARD MIGRATION ====

-- Remove task_number column from jobs table
-- Note: This column is not currently in the schema but may exist in some databases
-- The IF EXISTS clause prevents errors if the column doesn't exist
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'jobs'
        AND column_name = 'task_number'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE jobs DROP COLUMN task_number;
        RAISE NOTICE 'Dropped task_number column from jobs table';
    ELSE
        RAISE NOTICE 'task_number column does not exist in jobs table, skipping';
    END IF;
END $$;

-- Add output_dir column to inference table if it doesn't exist
-- Note: This column may already exist based on current schema
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'inference'
        AND column_name = 'output_dir'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE inference ADD COLUMN output_dir VARCHAR(500);
        RAISE NOTICE 'Added output_dir column to inference table';
    ELSE
        RAISE NOTICE 'output_dir column already exists in inference table, skipping';
    END IF;
END $$;

-- Add sbatch_content column to jobs table if it doesn't exist
-- This column stores the interpolated SLURM template content for audit trail
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'jobs'
        AND column_name = 'sbatch_content'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE jobs ADD COLUMN sbatch_content TEXT;
        RAISE NOTICE 'Added sbatch_content column to jobs table';
    ELSE
        RAISE NOTICE 'sbatch_content column already exists in jobs table, skipping';
    END IF;
END $$;

-- ==== ROLLBACK MIGRATION ====

-- To rollback this migration, run the following commands:
--
-- -- Re-add task_number column to jobs table
-- ALTER TABLE jobs ADD COLUMN task_number DECIMAL(4,0) NOT NULL DEFAULT 130;
--
-- -- Remove output_dir column from inference table
-- ALTER TABLE inference DROP COLUMN output_dir;
--
-- -- Remove sbatch_content column from jobs table
-- ALTER TABLE jobs DROP COLUMN sbatch_content;

-- ==== VERIFICATION ====

-- Verify the migration was successful
DO $$
BEGIN
    -- Check that task_number is removed from jobs
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'jobs'
        AND column_name = 'task_number'
        AND table_schema = 'public'
    ) THEN
        RAISE EXCEPTION 'Migration failed: task_number column still exists in jobs table';
    END IF;

    -- Check that output_dir exists in inference
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'inference'
        AND column_name = 'output_dir'
        AND table_schema = 'public'
    ) THEN
        RAISE EXCEPTION 'Migration failed: output_dir column missing from inference table';
    END IF;

    -- Check that sbatch_content exists in jobs
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'jobs'
        AND column_name = 'sbatch_content'
        AND table_schema = 'public'
    ) THEN
        RAISE EXCEPTION 'Migration failed: sbatch_content column missing from jobs table';
    END IF;

    RAISE NOTICE 'Migration completed successfully';
END $$;