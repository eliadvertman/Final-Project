-- Migration script to handle existing completed training jobs
-- This script migrates training records and creates model records for jobs that completed before the new workflow was implemented

-- Begin transaction to ensure atomicity
BEGIN;

-- Step 1: Update training records to 'TRAINED' status for completed training jobs
UPDATE training
SET
    status = 'TRAINED',
    end_time = COALESCE(end_time, (
        SELECT j.end_time
        FROM jobs j
        WHERE j.id = training.job_id
        AND j.job_type = 'TRAINING'
        AND j.status = 'COMPLETED'
    ), CURRENT_TIMESTAMP)
WHERE job_id IN (
    SELECT id
    FROM jobs
    WHERE job_type = 'TRAINING'
    AND status = 'COMPLETED'
)
AND status != 'TRAINED';  -- Only update if not already trained

-- Step 2: Create model records for completed training jobs that don't have models yet
INSERT INTO model (id, training_id, model_name, created_at)
SELECT
    gen_random_uuid()::text AS id,
    t.id AS training_id,
    t.name || '_model' AS model_name,
    COALESCE(t.end_time, j.end_time, CURRENT_TIMESTAMP) AS created_at
FROM training t
JOIN jobs j ON t.job_id = j.id
WHERE j.job_type = 'TRAINING'
  AND j.status = 'COMPLETED'
  AND t.status = 'TRAINED'  -- Only create models for trained records
  AND NOT EXISTS (
      SELECT 1
      FROM model m
      WHERE m.training_id = t.id
  );  -- Only if model doesn't already exist

-- Log the migration results
DO $$
DECLARE
    updated_trainings INTEGER;
    created_models INTEGER;
BEGIN
    -- Count updated training records
    SELECT COUNT(*) INTO updated_trainings
    FROM training t
    JOIN jobs j ON t.job_id = j.id
    WHERE j.job_type = 'TRAINING'
      AND j.status = 'COMPLETED'
      AND t.status = 'TRAINED';

    -- Count created model records
    SELECT COUNT(*) INTO created_models
    FROM model m
    JOIN training t ON m.training_id = t.id
    JOIN jobs j ON t.job_id = j.id
    WHERE j.job_type = 'TRAINING'
      AND j.status = 'COMPLETED';

    -- Log results (these will appear in database logs)
    RAISE NOTICE 'Migration completed: % training records updated to TRAINED status', updated_trainings;
    RAISE NOTICE 'Migration completed: % model records created', created_models;
END $$;

-- Commit the transaction
COMMIT;

-- Verification queries (commented out - uncomment to run verification after migration)
/*
-- Verify completed training jobs have corresponding trained training records
SELECT
    j.id as job_id,
    j.sbatch_id,
    j.status as job_status,
    t.id as training_id,
    t.name as training_name,
    t.status as training_status,
    CASE WHEN m.id IS NOT NULL THEN 'YES' ELSE 'NO' END as has_model
FROM jobs j
LEFT JOIN training t ON j.id = t.job_id
LEFT JOIN model m ON t.id = m.training_id
WHERE j.job_type = 'TRAINING'
  AND j.status = 'COMPLETED'
ORDER BY j.id;

-- Count summary
SELECT
    'Completed Training Jobs' as category,
    COUNT(*) as count
FROM jobs
WHERE job_type = 'TRAINING' AND status = 'COMPLETED'
UNION ALL
SELECT
    'Trained Training Records' as category,
    COUNT(*) as count
FROM training t
JOIN jobs j ON t.job_id = j.id
WHERE j.job_type = 'TRAINING' AND j.status = 'COMPLETED' AND t.status = 'TRAINED'
UNION ALL
SELECT
    'Model Records for Completed Training' as category,
    COUNT(*) as count
FROM model m
JOIN training t ON m.training_id = t.id
JOIN jobs j ON t.job_id = j.id
WHERE j.job_type = 'TRAINING' AND j.status = 'COMPLETED';
*/