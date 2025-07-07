import pytest
import os
import sys
from pathlib import Path
from testcontainers.postgres import PostgresContainer

# Add service directory to Python path
service_dir = Path(__file__).parent.parent
sys.path.insert(0, str(service_dir))

from main.dao.database import database, connect_db, close_db
from main.dao.models import ModelRecord, InferenceRecord

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Setup test database configuration with testcontainers."""
    import docker
    from testcontainers.postgres import PostgresContainer
    
    try:
        if 'TESTCONTAINERS_REUSE_ENABLE' not in os.environ:
            os.environ['TESTCONTAINERS_REUSE_ENABLE'] = 'true'
        
        # Start PostgreSQL container
        postgres = PostgresContainer("postgres:15-alpine")
        postgres.with_env("POSTGRES_DB", "pic_db")
        postgres.with_env("POSTGRES_USER", "pic_user") 
        postgres.with_env("POSTGRES_PASSWORD", "pic_password")
        
        # Mount init script to automatically create tables
        init_script_path = str(service_dir.parent / "db" / "init" / "01_init_schema.sql")
        postgres.with_volume_mapping(init_script_path, "/docker-entrypoint-initdb.d/01_init_schema.sql")
        
        postgres.start()
        
        # Configure database connection for testing
        os.environ['DB_NAME'] = postgres.dbname
        os.environ['DB_HOST'] = postgres.get_container_host_ip()
        os.environ['DB_PORT'] = str(postgres.get_exposed_port(5432))
        os.environ['DB_USER'] = postgres.username
        os.environ['DB_PASSWORD'] = postgres.password
        
        connect_db()
        yield
        close_db()
        postgres.stop()
        
    except Exception as e:
        # Fallback to existing container if testcontainers fails
        print(f"Testcontainers failed ({e}), using existing container")
        os.environ['DB_NAME'] = 'pic_db'
        os.environ['DB_HOST'] = 'localhost'
        os.environ['DB_PORT'] = '5432'
        os.environ['DB_USER'] = 'pic_user'
        os.environ['DB_PASSWORD'] = 'pic_password'
        
        connect_db()
        yield
        close_db()

@pytest.fixture
def clean_db():
    """Clean database before each test."""
    # Delete all records to ensure test isolation
    InferenceRecord.delete().execute()
    ModelRecord.delete().execute()
    yield
    # Clean up after test
    InferenceRecord.delete().execute()
    ModelRecord.delete().execute()