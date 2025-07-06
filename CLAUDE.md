# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a machine learning prediction service project (PIC - Prediction and Model Management) that consists of:
- A Python web service for model training and prediction
- A PostgreSQL database for data persistence
- Docker and Singularity deployment configurations

## Architecture

### Service Layer (`service/`)
- **`app.py`**: Main application entry point - currently a basic HTTP server on port 8080
- **`controller/swagger.yaml`**: OpenAPI specification defining the ML prediction API with endpoints for model training, prediction, and status management
- **`bl/`**: Business logic layer (currently empty - needs implementation)
- **`dao/`**: Data access object layer (currently empty - needs implementation)

### Database Layer (`db/`)
- **PostgreSQL database**: Configured for both Docker (development) and Singularity (HPC production) environments
- **`docker-compose.yml`**: Docker Compose configuration for PostgreSQL
- **`postgres.def`**: Singularity definition file for HPC deployment
- **`DATABASE_SETUP.md`**: Comprehensive setup instructions for both environments



The service will start on port 8080 and serve a basic HTTP response.

## Database Configuration

**Default credentials:**
- Database: `pic_db`
- User: `pic_user`
- Password: `pic_password`
- Port: `5432`

**Environment variables for customization:**
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

**Current State:**
- Basic HTTP server is implemented
- Database infrastructure is configured
- API specification is defined
- Both Docker and Singularity deployment configurations are ready

**Missing Implementation:**
- Business logic layer (`bl/` directory is empty)
- Data access layer (`dao/` directory is empty)
- API endpoint implementations
- Database schema and migrations
- Model training and prediction logic
- Connection between service and database

## Development Notes

- The project appears to be in early development stage with infrastructure set up but core functionality not yet implemented
- The current `app.py` serves as a placeholder - the actual ML service needs to be built according to the OpenAPI specification
- Database setup is well-documented and production-ready for HPC environments using Singularity
- No testing framework, linting, or build tools are currently configured




## Standard Workflow
1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the [todo.md](http://todo.md/) file with a summary of the changes you made and any other relevant information.



