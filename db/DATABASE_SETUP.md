# PostgreSQL Database Setup

This document describes how to run PostgreSQL database for the PIC project in both Docker (development) and Singularity (SLURM production) environments, including the complete database schema for the ML orchestration platform.

## Database Schema Overview

The database supports a complete ML workflow with job tracking, training management, model lifecycle, and prediction handling:

### **Core Tables**
- **`jobs`** - SLURM job tracking with sbatch integration
- **`training`** - Training record management linked to jobs
- **`model`** - Model lifecycle management linked to training
- **`inference`** - Prediction/inference tracking with job integration

### **Key Features**
- **UUID primary keys** for distributed system scalability
- **Foreign key relationships** maintaining data integrity
- **JSON fields** for flexible input/output data storage
- **Timestamp tracking** for complete audit trails
- **Status management** with proper state transitions

## Complete Database Schema

### **Jobs Table (`jobs`)**
Tracks SLURM job submissions and status for both training and inference.

```sql
CREATE TABLE jobs (
    id VARCHAR(36) PRIMARY KEY,           -- UUID primary key
    sbatch_id VARCHAR(255) NOT NULL,     -- SLURM job ID from sbatch
    fold_index DECIMAL(4,0) NOT NULL,    -- Cross-validation fold
    job_type VARCHAR(20) NOT NULL        -- 'TRAINING' or 'INFERENCE'
        CHECK (job_type IN ('INFERENCE', 'TRAINING')),
    status VARCHAR(20) NOT NULL          -- Job status
        CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')),
    start_time TIMESTAMP NULL,           -- Job start time from SLURM
    end_time TIMESTAMP NULL,             -- Job completion time
    error_message TEXT NULL,             -- Error details for failed jobs
    sbatch_content TEXT NULL             -- Interpolated SLURM template content
);
```

### **Training Table (`training`)**
Manages model training records with progress tracking.

```sql
CREATE TABLE training (
    id VARCHAR(36) PRIMARY KEY,          -- UUID primary key
    name VARCHAR(255) NOT NULL,          -- Training name/identifier
    images_path VARCHAR(500) NULL,       -- Path to training images
    labels_path VARCHAR(500) NULL,       -- Path to training labels
    model_path VARCHAR(500) NULL,        -- Output model path
    job_id VARCHAR(36) NOT NULL          -- Foreign key to jobs table
        REFERENCES jobs(id),
    status VARCHAR(20) NOT NULL          -- Training status
        CHECK (status IN ('TRAINING', 'TRAINED', 'FAILED')),
    progress FLOAT DEFAULT 0.0,          -- Training progress (0.0-100.0)
    start_time TIMESTAMP NULL,           -- Training start time
    end_time TIMESTAMP NULL              -- Training completion time
);
```

### **Model Table (`model`)**
Tracks trained models and their metadata.

```sql
CREATE TABLE model (
    id VARCHAR(36) PRIMARY KEY,          -- UUID primary key
    training_id VARCHAR(36) NOT NULL     -- Foreign key to training table
        REFERENCES training(id),
    model_name VARCHAR(255) NOT NULL,    -- Model identifier
    created_at TIMESTAMP NULL            -- Model creation timestamp
);
```

### **Inference Table (`inference`)**
Manages prediction requests and results.

```sql
CREATE TABLE inference (
    predict_id VARCHAR(36) PRIMARY KEY,  -- UUID primary key
    model_id VARCHAR(36) NOT NULL        -- Foreign key to model table
        REFERENCES model(id),
    job_id VARCHAR(36) NULL              -- Foreign key to jobs table
        REFERENCES jobs(id),
    input_data JSONB NOT NULL,           -- Input data for prediction
    output_dir VARCHAR(500) NULL,        -- Dynamic output directory path
    prediction JSONB NULL,               -- Prediction results
    status VARCHAR(20) NOT NULL          -- Inference status
        CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    start_time TIMESTAMP NULL,           -- Inference start time
    end_time TIMESTAMP NULL,             -- Inference completion time
    error_message TEXT NULL,             -- Error details
    created_at TIMESTAMP DEFAULT NOW(),  -- Record creation time
    updated_at TIMESTAMP DEFAULT NOW()   -- Last update time
);
```

### **Relationship Diagram**
```
jobs (1) ←→ (1) training (1) ←→ (*) model (1) ←→ (*) inference
  ↑                                                     ↓
  └─────────────────────────────────────────────────────┘
  (jobs can also link directly to inference for prediction jobs)
```

### **Connection Pooling Configuration**
The application uses Peewee ORM with connection pooling for high performance:

- **Pool size**: Configurable via `DB_MAX_CONNECTIONS` (default: 5)
- **Stale timeout**: Idle connection timeout via `DB_STALE_TIMEOUT` (default: 300s)
- **Connection timeout**: New connection timeout via `DB_CONNECTION_TIMEOUT` (default: 30s)
- **Performance**: ~50x improvement over per-request connections

## Docker Setup (Development)

### Prerequisites
- Docker and Docker Compose installed

### Configuration
The Docker setup uses environment variables with default values:
- `POSTGRES_DB`: Database name (default: `pic_db`)
- `POSTGRES_USER`: Database user (default: `pic_user`)
- `POSTGRES_PASSWORD`: Database password (default: `pic_password`)
- `POSTGRES_PORT`: Host port to bind (default: `5432`)
- `DB_VOLUME_PATH`: Host path for data persistence (default: `./postgres_data`)
- `DB_INIT_PATH`: Path to initialization scripts (default: `./db/init`)

### Running with Docker Compose

#### Basic usage (with defaults):
```bash
docker-compose up -d database
```

#### With custom volume path:
```bash
DB_VOLUME_PATH=/path/to/your/data docker-compose up -d database
```

#### With custom configuration:
```bash
export DB_VOLUME_PATH=/custom/data/path
export POSTGRES_PASSWORD=your_secure_password
export POSTGRES_PORT=5433
docker-compose up -d database
```

#### Using .env file:
Create a `.env` file in the project root:
```
DB_VOLUME_PATH=/home/user/pic_data
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=my_pic_db
POSTGRES_USER=my_user
POSTGRES_PORT=5433
```

Then run:
```bash
docker-compose up -d database
```

### Managing the Database
```bash
# Start the database
docker-compose up -d database

# Stop the database
docker-compose down

# View logs
docker-compose logs database

# Connect to database
docker-compose exec database psql -U pic_user -d pic_db

# Check database status
docker-compose ps database
```

## Singularity Setup (Slurm Production)

### Prerequisites
- Singularity installed on Slurm cluster
- Access to build Singularity images

### Building the Singularity Image

#### On a machine with build privileges:
```bash
sudo singularity build postgres.sif postgres.def
```

#### Using remote builder (if available):
```bash
singularity build --remote postgres.sif postgres.def
```

### Running with Singularity

#### Basic usage:
```bash
# Create data directory
mkdir -p /path/to/postgres/data

# Run PostgreSQL
singularity run --bind /path/to/postgres/data:/var/lib/postgresql/data postgres.sif
```

#### With custom configuration:
```bash
# Set environment variables
export POSTGRES_DB=my_pic_db
export POSTGRES_USER=my_user
export POSTGRES_PASSWORD=secure_password
export PGDATA=/var/lib/postgresql/data

# Create data directory
mkdir -p /custom/data/path

# Run with custom data path
singularity run \
    --env POSTGRES_DB=$POSTGRES_DB \
    --env POSTGRES_USER=$POSTGRES_USER \
    --env POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
    --env PGDATA=$PGDATA \
    --bind /custom/data/path:/var/lib/postgresql/data \
    postgres.sif
```

#### Running as a background service:
```bash
# Create data directory
mkdir -p /path/to/postgres/data

# Run in background
nohup singularity run --bind /path/to/postgres/data:/var/lib/postgresql/data postgres.sif > postgres.log 2>&1 &

# Check if running
ps aux | grep postgres
```

### Slurm Job Example

Create a Slurm job script (`postgres_job.sh`):
```bash
#!/bin/bash
#SBATCH --job-name=postgres-db
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --output=postgres_%j.out
#SBATCH --error=postgres_%j.err

# Set up environment
export POSTGRES_DB=pic_db
export POSTGRES_USER=pic_user
export POSTGRES_PASSWORD=secure_password

# Create data directory
DATA_DIR="/scratch/$USER/postgres_data"
mkdir -p $DATA_DIR

# Run PostgreSQL
singularity run \
    --env POSTGRES_DB=$POSTGRES_DB \
    --env POSTGRES_USER=$POSTGRES_USER \
    --env POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
    --bind $DATA_DIR:/var/lib/postgresql/data \
    postgres.sif
```

Submit the job:
```bash
sbatch postgres_job.sh
```

## Connection Details

### From Python Service
The Python service can connect using these connection strings:

#### Development (Docker):
```python
# Default configuration
DATABASE_URL = "postgresql://pic_user:pic_password@localhost:5432/pic_db"

# Custom configuration
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER', 'pic_user')}:{os.getenv('POSTGRES_PASSWORD', 'pic_password')}@localhost:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'pic_db')}"
```

#### Production (Singularity on Slurm):
```python
# You'll need to determine the container's IP or use host networking
# This depends on your Slurm/Singularity networking configuration
DATABASE_URL = "postgresql://pic_user:pic_password@<container_ip>:5432/pic_db"
```

## Troubleshooting

### Docker Issues
```bash
# Check if container is running
docker-compose ps

# View logs
docker-compose logs database

# Restart database
docker-compose restart database

# Remove data and restart fresh
docker-compose down -v
docker-compose up -d database
```

### Singularity Issues
```bash
# Check if process is running
ps aux | grep postgres

# View logs (if running in background)
tail -f postgres.log

# Test connection
singularity exec postgres.sif psql -U pic_user -d pic_db -c "SELECT version();"
```

## Database Schema Verification

### **Table Structure Validation**
```bash
# Verify all tables exist
docker-compose -f db/docker-compose.yml exec database psql -U pic_user -d pic_db -c "\dt"

# Expected output should show:
#           List of relations
#  Schema |   Name    | Type  |  Owner
# --------+-----------+-------+---------
#  public | inference | table | pic_user
#  public | jobs      | table | pic_user
#  public | model     | table | pic_user
#  public | training  | table | pic_user

# Check jobs table structure
docker-compose -f db/docker-compose.yml exec database psql -U pic_user -d pic_db -c "\d jobs"

# Check foreign key relationships
docker-compose -f db/docker-compose.yml exec database psql -U pic_user -d pic_db -c "\d+ training"
```

### **Data Consistency Checks**
```bash
# Verify foreign key constraints
docker-compose -f db/docker-compose.yml exec database psql -U pic_user -d pic_db -c "
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM
    information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY';
"

# Check table constraints
docker-compose -f db/docker-compose.yml exec database psql -U pic_user -d pic_db -c "
SELECT table_name, constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_schema = 'public'
ORDER BY table_name, constraint_type;
"
```

### **Performance Verification**
```bash
# Check connection pooling is working (requires app running)
curl http://localhost:8080/health/db

# Expected response:
# {
#   "status": "healthy",
#   "database": {
#     "connected": true,
#     "pool_size": 5,
#     "active_connections": 1,
#     "available_connections": 4
#   }
# }
```

## Application Integration

### **Environment Variables for Application**
```bash
# Development environment
export DB_NAME=pic_db
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=pic_user
export DB_PASSWORD=pic_password

# Connection pooling
export DB_MAX_CONNECTIONS=5
export DB_STALE_TIMEOUT=300
export DB_CONNECTION_TIMEOUT=30

# Logging
export LOG_LEVEL=INFO
export LOG_FORMAT=standard
```

### **Production Environment (HPC)**
```bash
# SLURM environment variables
export DB_NAME=pic_db
export DB_HOST=<singularity_container_ip>
export DB_PORT=5432
export DB_USER=pic_user
export DB_PASSWORD=secure_production_password

# SLURM job configuration
export SLURM_POLL_INTERVAL=30
export TRAINING_TEMPLATE_PATH=/work/templates/sbatch_train_template
export INFERENCE_TEMPLATE_PATH=/work/templates/sbatch_inference_template
export MODELS_BASE_PATH=/work/models
```

## Migration and Backup

### **Database Backup**
```bash
# Create backup
docker-compose -f db/docker-compose.yml exec database pg_dump -U pic_user pic_db > backup.sql

# Restore from backup
docker-compose -f db/docker-compose.yml exec -T database psql -U pic_user -d pic_db < backup.sql
```

### **Schema Migration**
The application uses Peewee ORM which handles schema changes programmatically. For manual migration:

```bash
# Connect to database
docker-compose -f db/docker-compose.yml exec database psql -U pic_user -d pic_db

# Example: Add new column to jobs table
ALTER TABLE jobs ADD COLUMN priority INTEGER DEFAULT 0;

# Example: Create index for performance
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_training_status ON training(status);
CREATE INDEX idx_inference_status ON inference(status);
```