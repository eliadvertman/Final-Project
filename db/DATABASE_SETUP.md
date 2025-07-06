# PostgreSQL Database Setup

This document describes how to run PostgreSQL database for the PIC project in both Docker (development) and Singularity (Slurm production) environments.

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