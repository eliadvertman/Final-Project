# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a machine learning prediction service project (PIC - Prediction and Model Management) that consists of:
- A Python web service for model training and prediction
- A PostgreSQL database for data persistence
- Docker and Singularity deployment configurations

## Architecture

### Service Layer (`service/`)
- **`main/`**: Main application package containing core functionality
  - **`controller/swagger.yaml`**: OpenAPI specification defining the ML prediction API
  - **`dao/`**: Data access object layer with complete CRUD operations
    - **`database.py`**: Database connection and configuration
    - **`models.py`**: Peewee ORM model definitions (ModelRecord, InferenceRecord)
    - **`model_dao.py`**: Model data access operations
    - **`inference_dao.py`**: Inference data access operations
- **`test/`**: Comprehensive test suite with automated container management
  - **`conftest.py`**: Test configuration with testcontainers support
  - **`test_integration.py`**: Integration tests for database operations
- **`requirements.txt`**: Python dependencies including testcontainers

### Database Layer (`db/`)
- **PostgreSQL database**: Configured for both Docker (development) and Singularity (HPC production) environments
- **`docker-compose.yml`**: Docker Compose configuration for PostgreSQL
- **`postgres.def`**: Singularity definition file for HPC deployment
- **`DATABASE_SETUP.md`**: Comprehensive setup instructions for both environments



Database connection uses environment variables for configuration with Peewee ORM for data persistence.

## Database Configuration

**Default credentials:**
- Database: `pic_db`
- User: `pic_user`
- Password: `pic_password`
- Port: `5432`

**Environment variables for application:**
- `DB_NAME`: Database name (default: pic_db)
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_USER`: Database user (default: pic_user)
- `DB_PASSWORD`: Database password (default: pic_password)

**Docker environment variables:**
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_PORT`: Host port to bind
- `DB_VOLUME_PATH`: Host path for data persistence
- `DB_INIT_PATH`: Path to initialization scripts

## API Specification

The service is designed to provide these endpoints (defined in `swagger.yaml`):

**Model Management:**
- `POST /api/v1/model/train` - Initiate model training
- `GET /api/v1/model/{modelId}/status` - Get model training status
- `GET /api/v1/model/list` - List all available models

**Prediction:**
- `POST /api/v1/predict/predict` - Make predictions
- `GET /api/v1/predict/{predictId}/status` - Get prediction status
- `GET /api/v1/predict/list` - List all predictions

## Implementation Status

**Implemented:**
- Complete database layer with Peewee ORM
- Data access objects for models and inference
- Database schema with models and inference tables
- Comprehensive test suite with testcontainers
- Automated database container management for tests
- Database connection management and configuration
- API specification is defined
- Both Docker and Singularity deployment configurations are ready

**Missing Implementation:**
- Business logic layer
- API endpoint implementations (web server/controllers)
- Model training and prediction logic
- Web service integration with database layer

## Development Notes

- Database layer is fully implemented with complete CRUD operations
- Test infrastructure supports both isolated testcontainers and manual database setup
- Database setup is well-documented and production-ready for HPC environments using Singularity
- Tests automatically manage PostgreSQL containers with proper cleanup
- Container reuse is enabled for improved test performance


# Workflow

1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the [todo.md](http://todo.md/) file with a summary of the changes you made and any other relevant information.


## Python
- `source stroke_seg/bin/activate` : Activate virtual environment
- `pip install -r service/requirements.txt` : Install requirements (includes testcontainers)
- `pytest service/test/` : Run integration tests with automatic container management
- `pytest service/test/ -v` : Run tests with verbose output 

## Docker Commands

**PostgreSQL Database:**
- `docker-compose up -d database` : Start the postgres container
- `docker-compose down` : Stop and remove containers
- `docker-compose ps` : Check container status
- `docker logs db-database-1` : View container logs
- `docker exec db-database-1 psql -U pic_user -d pic_db -c "\dt"` : List database tables
- `docker exec db-database-1 psql -U pic_user -d pic_db -c "\d [table_name]"` : Describe table structure
- `DB_VOLUME_PATH=/tmp/postgres_data docker-compose up -d database` : Start with custom volume path (useful for permission issues)

**Database Verification:**
- Tables created: `models` and `inference`
- Initialization script: `init/01_init_schema.sql` runs automatically on first startup
- Database ready when logs show: "database system is ready to accept connections"

## Code Best Practices

- Always use descriptive variable names