# Stroke Segmentation

A machine learning service for stroke image segmentation with PostgreSQL database persistence and automated testing infrastructure.

## Project Structure

```
├── service/                    # Python ML service
│   ├── main/                  # Main application package
│   │   ├── controller/        # API specification
│   │   └── dao/              # Data access layer (Peewee ORM)
│   ├── test/                 # Test suite with testcontainers
│   └── requirements.txt      # Python dependencies
├── db/                       # Database configuration
│   ├── docker-compose.yml    # Docker setup
│   ├── postgres.def          # Singularity definition
│   └── init/                 # Database initialization scripts
└── stroke_seg/               # Virtual environment
```

## Quick Start

**Setup and test:**
```bash
# Activate virtual environment
source stroke_seg/bin/activate

# Install dependencies
pip install -r service/requirements.txt

# Run tests (automatic container management)
pytest service/test/ -v
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
pytest service/test/ -v

# Run specific test
pytest service/test/test_integration.py::TestDatabaseIntegration::test_model_dao_crud_integration -v
```

**Manual testing with existing database:**
```bash
# Start database first
docker-compose -f db/docker-compose.yml up -d database

# Run tests against existing database
pytest service/test/ -v
```