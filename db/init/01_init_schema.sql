-- Database initialization script for PIC (Prediction and Model Management) service
-- This script creates the core tables for model management and inference tracking

-- Create Models table
CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    batch_id VARCHAR(255),
    input_path VARCHAR(500),
    output_path VARCHAR(500),
    status VARCHAR(20) NOT NULL CHECK (status IN ('TRAINING', 'SERVING', 'DELETED', 'INVALID')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Inference table
CREATE TABLE IF NOT EXISTS inference (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(id),
    batch_id VARCHAR(255),
    input_path VARCHAR(500),
    output_path VARCHAR(500),
    status VARCHAR(20) NOT NULL CHECK (status IN ('COMPLETED', 'RUNNING', 'FAILED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);