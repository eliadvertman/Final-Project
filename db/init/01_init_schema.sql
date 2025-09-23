-- Create Training table
CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(36) PRIMARY KEY,
    sbatch_id VARCHAR(255) NOT NULL,
    fold_index NUMERIC(4) NOT NULL,
    job_type VARCHAR(20) NOT NULL CHECK (job_type IN ('INFERENCE', 'TRAINING')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    sbatch_content TEXT
);

-- Create Training table
CREATE TABLE IF NOT EXISTS training (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    images_path VARCHAR(500) NOT NULL,
    labels_path VARCHAR(500) NOT NULL,
    model_path VARCHAR(500) NOT NULL,
    job_id VARCHAR(36) NOT NULL REFERENCES jobs(id),
    status VARCHAR(20) NOT NULL CHECK (status IN ('TRAINING', 'TRAINED', 'FAILED')),
    progress REAL DEFAULT 0.0,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE
);


-- Create Inference table
CREATE TABLE IF NOT EXISTS model (
    id VARCHAR(36) PRIMARY KEY,
    training_id VARCHAR(36) NOT NULL REFERENCES training(id),
    model_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE
);


-- Create Inference table
CREATE TABLE IF NOT EXISTS inference (
    predict_id VARCHAR(36) PRIMARY KEY,
    model_id VARCHAR(36) NOT NULL REFERENCES model(id),
    job_id VARCHAR(36) REFERENCES jobs(id),
    input_data JSONB NOT NULL,
    output_dir VARCHAR(500),
    prediction JSONB,
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);