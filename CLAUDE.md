# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive machine learning prediction service project (Prediction and Model Management) that consists of:
- A **production-ready Python web service** for model training and prediction with SLURM HPC integration
- A **PostgreSQL database** with connection pooling and comprehensive schema
- **Advanced job monitoring system** with real-time SLURM job tracking
- **Docker and Singularity deployment configurations** for development and HPC environments
- **Complete REST API** with structured logging, error handling, and health monitoring

This project demonstrates enterprise-grade ML orchestration patterns and is designed as a university capstone project.

## Architecture

### Service Layer (`serving/stroke_seg/`)
- **Main application package containing core functionality:**
  - **`app.py`**: Flask application with CORS, health checks, route registration, and job poller integration
  - **`logging_config.py`**: Centralized logging configuration with structured logging and correlation IDs
  - **`error_handler.py`**: Centralized error handling with smart decorators and auto JSON validation
  - **`exceptions.py`**: Custom exception hierarchy for proper error responses
  - **`config.py`**: Application configuration and template path management
- **`controller/`**: REST API controllers with comprehensive endpoints
  - **`model_controller.py`**: Model management endpoints with status and listing
  - **`prediction_controller.py`**: Prediction/inference endpoints with job tracking
  - **`training_controller.py`**: Training management endpoints with SLURM integration
  - **`models.py`**: Pydantic models for request/response validation
- **`bl/`**: Business logic layer with complete ML workflow orchestration
  - **`model_bl.py`**: Model business logic and lifecycle management
  - **`inference_bl.py`**: Prediction business logic with job submission
  - **`training_bl.py`**: Training business logic with SLURM job orchestration
  - **`jobs.py`**: Job type enumeration for training and inference
  - **`client/`**: External system integrations
    - **`slurm/`**: SLURM client and job state management
    - **`fs/`**: File system utilities for temporary file management
  - **`poller/`**: Advanced job monitoring system (SOLID architecture)
    - **`base_job_monitor.py`**: Abstract base class for job monitoring
    - **`training_job_monitor.py`**: Training-specific job monitoring
    - **`prediction_job_monitor.py`**: Prediction-specific job monitoring
    - **`job_monitor_manager.py`**: Orchestrator for all job monitors
    - **`poller_facade.py`**: Async polling service with thread management
  - **`template/`**: Template system for job generation
    - **`template_variables.py`**: Variable definitions for SLURM job templates
  - **`training/`**: Training-specific business logic
    - **`training_facade.py`**: Training job submission and management
  - **`prediction/`**: Prediction-specific business logic
    - **`prediction_facade.py`**: Prediction job submission and management
- **`dao/`**: Data access object layer with complete CRUD operations and connection pooling
  - **`database.py`**: Database connection pooling and configuration management
  - **`models.py`**: Peewee ORM model definitions (JobRecord, TrainingRecord, ModelRecord, InferenceRecord with output_dir)
  - **`model_dao.py`**: Model data access operations with UUID support
  - **`inference_dao.py`**: Inference data access operations with job linking
  - **`training_dao.py`**: Training data access operations with job relationships
  - **`job_dao.py`**: Job data access operations for SLURM job tracking
- **`test/`**: Comprehensive test suite with automated container management
  - **`conftest.py`**: Test configuration with testcontainers support
  - **`test_dao.py`**: Integration tests for database operations
- **`requirements.txt`**: Python dependencies including testcontainers, peewee, and SLURM integrations

### Frontend Layer (`fe/`)
- **React/TypeScript SPA**: Modern web interface built with React 19.1.1 and TypeScript 5.8.3
- **Component Architecture**: Modular components with Layout, Navigation, and specialized page views
- **State Management**: React Query for server state + local component state for optimal data flow
- **API Integration**: Type-safe Axios client with automatic error handling and request/response logging
- **Development Tools**: Vite build system, ESLint for code quality, and hot module replacement
- **Real-time Updates**: Automatic polling for job status updates and live dashboard metrics
- **Responsive Design**: Mobile-friendly interface with modern UI patterns

### Database Layer (`db/`)
- **PostgreSQL database**: Configured for both Docker (development) and Singularity (HPC production) environments
- **`docker-compose.yml`**: Docker Compose configuration for PostgreSQL
- **`postgres-fixed.def`**: Singularity definition file for HPC deployment
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

**Logging Configuration:**
- `LOG_LEVEL`: Logging level (default: INFO) - DEBUG, INFO, WARNING, ERROR
- `LOG_FORMAT`: Log format (default: standard) - standard or json
- `LOG_FILE`: Optional log file path for file output with rotation

**Connection Pool Configuration:**
- `DB_MAX_CONNECTIONS`: Maximum connections in pool (default: 5)
- `DB_STALE_TIMEOUT`: Close idle connections after X seconds (default: 300)
- `DB_CONNECTION_TIMEOUT`: Connection timeout in seconds (default: 30)

**Docker environment variables:**
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_PORT`: Host port to bind
- `DB_VOLUME_PATH`: Host path for data persistence
- `DB_INIT_PATH`: Path to initialization scripts

**SLURM Job Configuration:**
- `SLURM_POLL_INTERVAL`: Job polling interval in seconds (default: 30)
- `TRAINING_TEMPLATE_PATH`: Path to SLURM training job template
- `INFERENCE_TEMPLATE_PATH`: Path to SLURM inference job template
- `MODELS_BASE_PATH`: Base directory for model storage

**Job Template Variables:**
- Templates support variable substitution for dynamic job generation
- Training templates: model_name, model_path, fold_index, task_number
- Inference templates: model_name, model_path, output_path (dynamically generated output directories)

## API Specification

The service provides a comprehensive REST API with full CRUD operations and real-time job tracking:

**Training Management:**
- `POST /api/v1/training/train` - Initiate model training with SLURM job submission
- `GET /api/v1/training/{trainingId}/status` - Get training status with progress and timing
- `GET /api/v1/training/list` - List all trainings with pagination support

**Model Management:**
- `GET /api/v1/model/list` - List all available models with pagination
- `GET /api/v1/model/{modelId}/status` - Get model status and metadata

**Prediction/Inference:**
- `POST /api/v1/inference/predict` - Make predictions using specified model with job tracking
- `GET /api/v1/inference/{predictId}/status` - Get prediction status with timing and results
- `GET /api/v1/inference/list` - List all predictions with pagination support

**Health & Monitoring:**
- `GET /health` - Overall application health status
- `GET /health/db` - Database connection pool health and metrics
- `GET /health/poller` - Job poller health and monitoring status

**All endpoints support:**
- JSON request/response with Pydantic validation
- Structured error responses with correlation IDs
- Request timing and performance monitoring
- Comprehensive logging with debugging support

## Implementation Status

**✅ Fully Implemented - Production Ready:**
- **Complete three-tier architecture**: Controllers → Business Logic → Data Access Objects
- **Full REST API**: All training, model, and prediction endpoints with pagination
- **Advanced database layer**: Peewee ORM with connection pooling (~50x performance improvement)
- **Comprehensive job system**: SLURM integration with real-time job monitoring
- **SOLID job monitoring**: Separate monitors for training and prediction jobs following SOLID principles
- **Database schema**: Complete with jobs, training, model, and inference tables (UUID primary keys)
- **Health monitoring**: Database pool status and job poller health endpoints
- **Centralized error handling**: Smart decorators with auto JSON validation and correlation IDs
- **Structured logging**: Request correlation IDs, performance monitoring, JSON/standard formats
- **Testing infrastructure**: Comprehensive test suite with automated testcontainers
- **Multi-environment deployment**: Docker (development) and Singularity (HPC production)
- **Template system**: Configurable SLURM job templates for training and inference
- **Async job polling**: Background thread with graceful shutdown and error recovery
- **Connection pooling**: High-performance database connections with configurable limits

**🔄 Partially Implemented:**
- **Job execution logic**: SLURM job submission works, but ML algorithm implementation is placeholder
- **Template validation**: Basic template path validation, could be enhanced

**❌ Missing Implementation:**
- **Actual ML algorithms**: No scikit-learn, TensorFlow, PyTorch integration within job containers
- **Model serialization**: No model file handling and storage implementation
- **Result processing**: No prediction result parsing from job outputs

## Development Notes

### **System Architecture**
- **Enterprise-grade ML orchestration platform** with complete job lifecycle management
- **SOLID principles implementation** with separate job monitors for training and prediction
- **Production-ready patterns**: Connection pooling, structured logging, health monitoring
- **Scalable design**: UUID primary keys, async job processing, HPC integration

### **Performance & Reliability**
- **Connection pooling**: ~50x performance improvement (5ms → 0.1ms connection overhead)
- **Async job monitoring**: Real-time SLURM job status updates with error recovery
- **Database resilience**: Automatic reconnection and transaction management
- **Graceful shutdown**: Proper cleanup of async tasks and database connections

### **Development Experience**
- **Comprehensive testing**: Automated testcontainers with clean isolation
- **Smart error handling**: Auto-detected JSON endpoints with correlation IDs
- **Structured logging**: Request tracing, performance metrics, configurable formats
- **Multi-environment**: Seamless Docker (dev) to Singularity (HPC) deployment

### **Job Processing System**
- **Template-based job generation**: Configurable SLURM job templates
- **State machine validation**: Proper job state transitions with logging
- **Real-time monitoring**: Automatic status updates from SLURM to database
- **Fault tolerance**: Job poller survives database disconnections and SLURM issues

### **API Design**
- **RESTful with pagination**: All list endpoints support limit/offset
- **Validation**: Pydantic models for request/response consistency
- **Health endpoints**: Comprehensive monitoring for database and job systems
- **Error consistency**: Standardized error responses with debug information

## Recent Major Changes

### **Dynamic Output Directory System (Latest)**
- **Dynamic output path generation**: Inference jobs now use dynamically generated output directories with pattern `{model_path}/inference/{inference_id}-{timestamp}`
- **Enhanced database schema**: Added `output_dir` column to inference table for tracking job output locations
- **Improved job isolation**: Each prediction job gets a unique output directory preventing conflicts
- **Backward compatibility**: Existing inference records remain unaffected with nullable output_dir column

### **SLURM Job Monitoring System**
- **Complete job orchestration**: End-to-end training and prediction job management
- **SOLID refactoring**: Broke monolithic JobsMonitor into separate TrainingJobMonitor and PredictionJobMonitor
- **Real-time polling**: Async job status updates with SLURM state machine validation
- **Job lifecycle management**: Automatic model creation on training completion, inference result tracking
- **Fault-tolerant monitoring**: Database reconnection, graceful error handling, proper shutdown

### **Advanced Job Processing Architecture**
- **Template system**: Configurable SLURM job submission with variable substitution
- **Job state machine**: Proper state transitions (PENDING → RUNNING → COMPLETED/FAILED)
- **Atomic transactions**: Database consistency during job state changes and model creation
- **Background polling**: Separate thread with event loop for continuous monitoring

### **Connection Pooling Implementation**
- Replaced per-request database connections with connection pooling
- Performance improvement: ~5ms → 0.1ms connection overhead (~50x faster)
- Configurable pool size and timeout settings via environment variables
- Automatic connection lifecycle management with health monitoring

### **ID Field Modernization**
- Migrated from AutoField integer IDs to UUID primary keys
- Updated all DAO methods to handle UUID parameters
- Enhanced database schema for better distributed system scalability
- Maintained backward compatibility in API responses

### **Error Handling Consolidation**
- Eliminated duplicate error handlers between app.py and controllers
- Created smart `@handle_errors` decorator with auto JSON validation
- Reduced ~150+ lines of repetitive error handling code
- Centralized error response format and logging with correlation IDs

### **Comprehensive Logging Infrastructure**
- **Centralized logging configuration** with structured logging across all layers
- **Request correlation IDs** for tracing requests through the entire system
- **Performance monitoring** with request timing and database operation metrics
- **Environment-based configuration** supporting both development and production
- **JSON and standard formatting** options for different deployment environments
- **Zero print statements** - all replaced with appropriate logging levels
- **File and console handlers** with rotation and proper log levels


# Workflow

1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. As this is a university project, when planning, consider the functional requirements. non-functional requirements like testing is not important.  
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Make sure to not create large Python files. Follow SOLID principles to break big components to smaller ones.
8. Finally, add a review section to the [todo.md](http://todo.md/) file with a summary of the changes you made and any other relevant information.


## Python Backend
- `source stroke_seg/bin/activate` : Activate virtual environment
- `pip install -r serving/requirements.txt` : Install requirements (includes testcontainers)
- `python serving/stroke_seg/app.py` : Start the Flask application
- `pytest serving/stroke_seg/test/` : Run integration tests with automatic container management
- `pytest serving/stroke_seg/test/ -v` : Run tests with verbose output

## Frontend Development
- `cd fe` : Navigate to frontend directory
- `npm install` : Install Node.js dependencies
- `npm run dev` : Start Vite development server with HMR
- `npm run build` : Build production bundle with TypeScript compilation
- `npm run lint` : Run ESLint for code quality checks
- `npm run preview` : Preview production build locally 

## Docker Commands

**PostgreSQL Database:**
- `docker-compose -f db/docker-compose.yml up -d database` : Start the postgres container
- `docker-compose -f db/docker-compose.yml down` : Stop and remove containers
- `docker-compose -f db/docker-compose.yml ps` : Check container status
- `docker-compose -f db/docker-compose.yml logs database` : View container logs
- `docker-compose -f db/docker-compose.yml exec database psql -U pic_user -d pic_db -c "\dt"` : List database tables
- `docker-compose -f db/docker-compose.yml exec database psql -U pic_user -d pic_db -c "\d [table_name]"` : Describe table structure
- `DB_VOLUME_PATH=/tmp/postgres_data docker-compose -f db/docker-compose.yml up -d database` : Start with custom volume path (useful for permission issues)

**Database Verification:**
- Tables created: `models` and `inference`
- Initialization script: `init/01_init_schema.sql` runs automatically on first startup
- Database ready when logs show: "database system is ready to accept connections"

## Code Best Practices

- Always use descriptive variable names