import pytest
import os
import sys
from pathlib import Path
from testcontainers.postgres import PostgresContainer

# Add service directory to Python path
service_dir = Path(__file__).parent.parent
sys.path.insert(0, str(service_dir))

from stroke_seg.dao.database import database, close_pool
from stroke_seg.dao.models import ModelRecord, InferenceRecord

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Setup test database configuration with testcontainers."""
    import docker
    from testcontainers.postgres import PostgresContainer
    
    if 'TESTCONTAINERS_REUSE_ENABLE' not in os.environ:
        os.environ['TESTCONTAINERS_REUSE_ENABLE'] = 'false'
    
    # Start PostgreSQL container
    postgres = PostgresContainer("postgres:15-alpine")
    postgres.with_env("POSTGRES_DB", "pic_db")
    postgres.with_env("POSTGRES_USER", "pic_user") 
    postgres.with_env("POSTGRES_PASSWORD", "pic_password")
    
    postgres.start()
    
    # Configure database connection for testing
    os.environ['DB_NAME'] = postgres.dbname
    os.environ['DB_HOST'] = postgres.get_container_host_ip()
    os.environ['DB_PORT'] = str(postgres.get_exposed_port(5432))
    os.environ['DB_USER'] = postgres.username
    os.environ['DB_PASSWORD'] = postgres.password
    # Use smaller pool for testing
    os.environ['DB_MAX_CONNECTIONS'] = '3'
    os.environ['DB_STALE_TIMEOUT'] = '60'
    
    # Reinitialize database connection with new config
    from playhouse.pool import PooledPostgresqlDatabase
    from stroke_seg.dao.database import database
    
    # Initialize the pool with test configuration
    database.init(
        postgres.dbname,
        user=postgres.username,
        password=postgres.password,
        host=postgres.get_container_host_ip(),
        port=postgres.get_exposed_port(5432),
        max_connections=3,
        stale_timeout=60,
        timeout=10
    )
    
    # Create tables using SQL initialization script
    init_script_path = Path(__file__).parent.parent.parent / "db" / "init" / "01_init_schema.sql"
    with open(init_script_path, 'r') as f:
        init_sql = f.read()
    database.execute_sql(init_sql)
    
    yield
    
    # Close the connection pool properly
    close_pool()
    postgres.stop()

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