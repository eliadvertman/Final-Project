-- Database initialization script for PIC (Prediction and Model Management) service
-- This script creates the core tables for model management and inference tracking

-- Create Models table
CREATE TABLE IF NOT EXISTS models (
    model_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    images_path VARCHAR(500),
    labels_path VARCHAR(500),
    dataset_path VARCHAR(500),
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'TRAINING', 'TRAINED', 'FAILED', 'DEPLOYED')),
    progress REAL DEFAULT 0.0,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Inference table
CREATE TABLE IF NOT EXISTS inference (
    predict_id VARCHAR(36) PRIMARY KEY,
    model_id VARCHAR(36) NOT NULL REFERENCES models(model_id),
    input_data JSONB NOT NULL,
    prediction JSONB,
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);