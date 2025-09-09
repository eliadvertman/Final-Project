# PIC - Prediction and Model Management Service

A scalable machine learning prediction service with PostgreSQL database persistence, connection pooling, and comprehensive API endpoints for model training and inference.

## Project Structure

```
├── serving/                   # Python ML service
│   ├── stroke_seg/            # Main application package
│   │   ├── app.py             # Flask application with health checks
│   │   ├── controller/        # REST API controllers
│   │   ├── bl/                # Business logic layer
│   │   ├── dao/               # Data access layer (Peewee ORM + connection pooling)
│   │   ├── error_handler.py   # Centralized error handling
│   │   ├── exceptions.py      # Custom exception hierarchy
│   │   ├── logging_config.py  # Centralized logging configuration
│   │   └── test/              # Comprehensive test suite with testcontainers
│   └── requirements.txt       # Python dependencies
├── db/                        # Database configuration
│   ├── docker-compose.yml     # Docker setup
│   ├── postgres-fixed.def     # Singularity definition
│   └── DATABASE_SETUP.md      # Database setup instructions
└── stroke_seg/                # Virtual environment (excluded from git)
```

## Features

✅ **Complete REST API** - Full CRUD operations for models and predictions  
✅ **Connection Pooling** - High-performance database connections (~50x faster)  
✅ **UUID Primary Keys** - Scalable distributed system architecture  
✅ **Smart Error Handling** - Centralized, consistent error responses  
✅ **Health Monitoring** - Database pool status endpoint  
✅ **Automated Testing** - Comprehensive test suite with testcontainers  
✅ **Multi-Environment** - Docker (dev) + Singularity (HPC) support  

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

**API Endpoints:**
```bash
# Health check
curl http://localhost:8080/health/db

# Model management
curl -X POST http://localhost:8080/api/v1/model/train
curl http://localhost:8080/api/v1/model/list

# Predictions  
curl -X POST http://localhost:8080/api/v1/predict/predict
curl http://localhost:8080/api/v1/predict/list
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