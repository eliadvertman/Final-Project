-- Migration: Create evaluation table and update jobs table job_type constraint
-- Created: 2025-12-13
-- Description:
--   - Create evaluation table for storing model evaluation records
--   - Update jobs.job_type constraint to include 'EVALUATION'

-- ==== FORWARD MIGRATION ====

-- Update jobs table job_type constraint to include EVALUATION
DO $$
BEGIN
    -- Drop existing constraint
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'jobs'
        AND constraint_name = 'jobs_job_type_check'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE jobs DROP CONSTRAINT jobs_job_type_check;
        RAISE NOTICE 'Dropped existing job_type constraint from jobs table';
    END IF;

    -- Add new constraint with EVALUATION
    ALTER TABLE jobs ADD CONSTRAINT jobs_job_type_check
        CHECK (job_type IN ('INFERENCE', 'TRAINING', 'EVALUATION'));
    RAISE NOTICE 'Added new job_type constraint with EVALUATION to jobs table';
END $$;

-- Create evaluation table
CREATE TABLE IF NOT EXISTS evaluation (
    id VARCHAR(36) PRIMARY KEY,
    model_id VARCHAR(36) NOT NULL REFERENCES model(id),
    job_id VARCHAR(36) NOT NULL REFERENCES jobs(id),
    evaluation_path VARCHAR(500) NOT NULL,
    configurations JSONB NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'EVALUATING', 'COMPLETED', 'FAILED')),
    results JSONB,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_evaluation_model_id ON evaluation(model_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_job_id ON evaluation(job_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_status ON evaluation(status);
CREATE INDEX IF NOT EXISTS idx_evaluation_created_at ON evaluation(created_at DESC);

RAISE NOTICE 'Created evaluation table with indexes';

-- ==== ROLLBACK MIGRATION ====

-- To rollback this migration, run the following commands:
--
-- DROP TABLE IF EXISTS evaluation;
-- ALTER TABLE jobs DROP CONSTRAINT jobs_job_type_check;
-- ALTER TABLE jobs ADD CONSTRAINT jobs_job_type_check
--     CHECK (job_type IN ('INFERENCE', 'TRAINING'));

-- ==== VERIFICATION ====

-- Verify the migration was successful
DO $$
BEGIN
    -- Check that evaluation table exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'evaluation'
        AND table_schema = 'public'
    ) THEN
        RAISE EXCEPTION 'Migration failed: evaluation table does not exist';
    END IF;

    -- Check that job_type constraint includes EVALUATION
    -- We verify by checking the constraint definition
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints
        WHERE constraint_name = 'jobs_job_type_check'
        AND check_clause LIKE '%EVALUATION%'
    ) THEN
        RAISE EXCEPTION 'Migration failed: jobs job_type constraint does not include EVALUATION';
    END IF;

    RAISE NOTICE 'Migration completed successfully';
END $$;

