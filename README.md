# Final-Project


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

### Application Operations

**Run the Python service:**
```bash
cd service
python app.py
```