# PIC - Prediction and Model Management Service

**Enterprise-grade ML orchestration platform** with SLURM HPC integration, real-time job monitoring, and production-ready architecture for scalable machine learning workflows.

## Project Structure

```
├── serving/                   # Python ML orchestration service
│   ├── stroke_seg/            # Main application package
│   │   ├── app.py             # Flask app with CORS, health checks, job poller integration
│   │   ├── controller/        # REST API controllers with comprehensive endpoints
│   │   ├── bl/                # Business logic layer with SLURM integration
│   │   │   ├── client/        # External system integrations (SLURM, filesystem)
│   │   │   ├── poller/        # SOLID job monitoring architecture
│   │   │   ├── template/      # Job template system with variable substitution
│   │   │   ├── training/      # Training-specific business logic
│   │   │   └── prediction/    # Prediction-specific business logic
│   │   ├── dao/               # Data access layer with connection pooling & UUID support
│   │   ├── config.py          # Application configuration management
│   │   ├── error_handler.py   # Smart error handling with auto JSON validation
│   │   ├── exceptions.py      # Custom exception hierarchy
│   │   ├── logging_config.py  # Structured logging with correlation IDs
│   │   └── test/              # Comprehensive test suite with automated testcontainers
│   └── requirements.txt       # Python dependencies (peewee, testcontainers, etc.)
├── db/                        # Database configuration & deployment
│   ├── docker-compose.yml     # Docker development setup
│   ├── postgres-fixed.def     # Singularity HPC production setup
│   ├── init/                  # Database initialization scripts
│   └── DATABASE_SETUP.md      # Comprehensive setup instructions
├── fe/                        # Frontend React application (optional)
└── docs/                      # Additional documentation
```

## Key Features

✅ **SLURM HPC Integration** - Native integration with high-performance computing clusters
✅ **Real-time Job Monitoring** - Async polling with automatic status updates and fault tolerance
✅ **SOLID Architecture** - Separate monitors for training and prediction jobs following best practices
✅ **Complete REST API** - Full CRUD operations with pagination and health monitoring
✅ **Connection Pooling** - High-performance database connections (~50x faster)
✅ **Template System** - Configurable SLURM job templates with variable substitution
✅ **Structured Logging** - Request correlation IDs, performance metrics, configurable formats
✅ **Smart Error Handling** - Centralized error responses with auto JSON validation
✅ **Health Monitoring** - Database pool status and job poller health endpoints
✅ **Automated Testing** - Comprehensive test suite with automated testcontainers
✅ **Multi-Environment** - Docker (development) + Singularity (HPC production)
✅ **UUID Architecture** - Scalable distributed system with proper data relationships

## System Capabilities

This platform provides **enterprise-grade ML orchestration** with the following capabilities:

### **🚀 Job Orchestration**
- **End-to-end ML workflows**: From training request to model deployment
- **SLURM integration**: Native HPC cluster job submission and monitoring
- **Real-time tracking**: Automatic job status updates with state machine validation
- **Template system**: Configurable job generation with variable substitution
- **Dynamic output directories**: Unique output paths for each inference job preventing conflicts
- **Fault tolerance**: Graceful handling of job failures and system errors

### **🏗️ Production Architecture**
- **Three-tier design**: Controllers → Business Logic → Data Access Objects
- **SOLID principles**: Separate monitors for training and prediction jobs
- **Connection pooling**: ~50x performance improvement with configurable limits
- **Async processing**: Background job monitoring with proper lifecycle management
- **Health monitoring**: Comprehensive status endpoints for system observability

### **📊 Data Management**
- **UUID-based architecture**: Scalable distributed system design
- **Atomic transactions**: Database consistency during complex operations
- **Relationship mapping**: Complete foreign key relationships between entities
- **JSON flexibility**: Structured input/output data with schema validation
- **Output directory tracking**: Dynamic path generation for inference job outputs
- **Migration support**: Schema evolution with backward compatibility

### **🔍 Observability & Monitoring**
- **Structured logging**: Request correlation IDs and performance metrics
- **Health endpoints**: Database pool status and job poller monitoring
- **Error tracking**: Centralized error handling with smart validation
- **Request tracing**: Complete request lifecycle monitoring
- **Configurable formats**: JSON and standard logging for different environments

### **🐳 Deployment Flexibility**
- **Docker development**: Easy local setup with docker-compose
- **Singularity production**: HPC deployment with container isolation
- **Environment configuration**: Flexible configuration for different deployments
- **Template management**: Configurable job templates for different environments

## Quick Start

**Setup and test:**
```bash
# Activate virtual environment
source stroke_seg/bin/activate

# Install dependencies
pip install -r serving/requirements.txt

# Run tests (automatic container management)
pytest serving/stroke_seg/test/ -v

# Start the Flask application
python serving/stroke_seg/app.py
```

## Complete API Documentation

### **Health & Monitoring Endpoints**
```bash
# Overall application health
curl http://localhost:8080/health

# Database connection pool health and metrics
curl http://localhost:8080/health/db

# Job poller health and monitoring status
curl http://localhost:8080/health/poller
```

### **Training Management (SLURM Job Integration)**
```bash
# Initiate model training with SLURM job submission
curl -X POST http://localhost:8080/api/v1/training/train \
  -H "Content-Type: application/json" \
  -d '{
    "modelName": "CustomerChurnPredictor",
    "imagesPath": "/work/images",
    "labelsPath": "/work/labels",
    "foldIndex": 0,
    "taskNumber": 1
  }'

# Get training status with progress and timing
curl http://localhost:8080/api/v1/training/d290f1ee-6c54-4b01-90e6-d701748f0851/status

# List all trainings with pagination
curl "http://localhost:8080/api/v1/training/list?limit=10&offset=0"
```

### **Model Management**
```bash
# List all available models with pagination
curl "http://localhost:8080/api/v1/model/list?limit=10&offset=0"

# Get model status and metadata
curl http://localhost:8080/api/v1/model/d290f1ee-6c54-4b01-90e6-d701748f0851/status
```

### **Prediction/Inference (SLURM Job Integration)**
```bash
# Make predictions using specified model with job tracking
# Note: outputDir is automatically generated for each prediction job
curl -X POST http://localhost:8080/api/v1/inference/predict \
  -H "Content-Type: application/json" \
  -d '{
    "modelId": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "inputPath": "/work/input/patient_scan.nii"
  }'

# Get prediction status with timing and results
curl http://localhost:8080/api/v1/inference/e678f2ee-1a2b-3c4d-5e6f-7a8b9c0d1e2f/status

# List all predictions with pagination
curl "http://localhost:8080/api/v1/inference/list?limit=10&offset=0"
```

### **Response Examples**

**Training Status Response:**
```json
{
  "trainingId": "d290f1ee-6c54-4b01-90e6-d701748f0851",
  "status": "TRAINING",
  "progress": 45.2,
  "startTime": "2024-01-15T10:30:00Z",
  "batchJobId": "12345"
}
```

**Health Check Response:**
```json
{
  "status": "healthy",
  "database": {
    "connected": true,
    "pool_size": 5,
    "active_connections": 2
  },
  "job_poller": {
    "running": true,
    "monitors": {
      "training": "running",
      "prediction": "running"
    }
  }
}
```

## Development Commands

### Database Operations

**Docker Environment (Development):**
```bash
# Start database (default volume path)
docker-compose -f db/docker-compose.yml up -d database

# Start database with custom volume path
DB_VOLUME_PATH=/custom/data/path docker-compose -f db/docker-compose.yml up -d database

# Stop database
docker-compose -f db/docker-compose.yml down

# Connect to database
docker-compose -f db/docker-compose.yml exec database psql -U pic_user -d pic_db

# View logs
docker-compose -f db/docker-compose.yml logs database
```

**Singularity Environment (HPC Production):**
```bash
# Build Singularity image
sudo singularity build postgres.sif db/postgres.def

# Run database (default data directory)
singularity run --bind /path/to/postgres/data:/var/lib/postgresql/data postgres.sif

# Run database with custom volume path
singularity run --bind /custom/data/path:/var/lib/postgresql/data postgres.sif
```

### Testing

**Automated testing (recommended):**
```bash
# Tests automatically start/stop PostgreSQL containers
pytest serving/stroke_seg/test/ -v

# Run specific test
pytest serving/stroke_seg/test/test_dao.py::TestModelDAO::test_create_model -v
```

**Manual testing with existing database:**
```bash
# Start database first
docker-compose -f db/docker-compose.yml up -d database

# Run tests against existing database
pytest serving/stroke_seg/test/ -v
```



# Setup 

## local

### DB
run docker-compose 
```bash
docker-compose -f db/docker-compose.yml up -d database
```

### Webserver
run app.py
```bash
python -m stroke_seg.app
```

### Frontend
```bash
npm run dev
```
*make sure that the ports routing are correct 

## runlogin

### DB
run this on runlogin:
1. build singularity container out of postgres-lean.def 
```bash
singularity build --notest postgres-lean.sif postgres-lean.def
```
2. run singularity container 
```bash
 singularity run --writable-tmpfs --bind /home/veeliad/work/BrainSegmentation/services/postgres_data/:/var/lib/postgresql/data postgres-lean.sif
```
3. create db and tables (this needs to run only on the 1st time)
```bash
python db_setup.py
```

### webserver 
run app.py on runlogin
```bash
python -m stroke_seg.app
```

### Frontend
run this on local machine 
```bash
npm run dev
```
*make sure that the ports routing are correct and there's port forwarding to runlogin 
