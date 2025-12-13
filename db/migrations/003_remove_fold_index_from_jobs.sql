-- Migration: Remove fold_index from jobs table and add configuration to training table
-- Created: 2025-12-13
-- Description:
--   - Remove fold_index column from jobs table (no longer needed)
--   - Add configuration column to training table (nnUNet configuration: 2d, 3d_fullres, 3d_lowres, 3d_cascade_lowres)

-- ==== FORWARD MIGRATION ====

-- Remove fold_index column from jobs table
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'jobs'
        AND column_name = 'fold_index'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE jobs DROP COLUMN fold_index;
        RAISE NOTICE 'Dropped fold_index column from jobs table';
    ELSE
        RAISE NOTICE 'fold_index column does not exist in jobs table, skipping';
    END IF;
END $$;

-- Add configuration column to training table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'training'
        AND column_name = 'configuration'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE training ADD COLUMN configuration VARCHAR(20) NOT NULL DEFAULT '3d_fullres'
            CHECK (configuration IN ('2d', '3d_fullres', '3d_lowres', '3d_cascade_lowres'));
        RAISE NOTICE 'Added configuration column to training table';
    ELSE
        RAISE NOTICE 'configuration column already exists in training table, skipping';
    END IF;
END $$;

-- ==== ROLLBACK MIGRATION ====

-- To rollback this migration, run the following commands:
--
-- ALTER TABLE jobs ADD COLUMN fold_index DECIMAL(4,0) NOT NULL DEFAULT 0;
-- ALTER TABLE training DROP COLUMN configuration;

-- ==== VERIFICATION ====

-- Verify the migration was successful
DO $$
BEGIN
    -- Check that fold_index is removed from jobs
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'jobs'
        AND column_name = 'fold_index'
        AND table_schema = 'public'
    ) THEN
        RAISE EXCEPTION 'Migration failed: fold_index column still exists in jobs table';
    END IF;

    -- Check that configuration exists in training
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'training'
        AND column_name = 'configuration'
        AND table_schema = 'public'
    ) THEN
        RAISE EXCEPTION 'Migration failed: configuration column missing from training table';
    END IF;

    RAISE NOTICE 'Migration completed successfully';
END $$;

