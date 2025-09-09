import os

from dotenv import load_dotenv
from peewee import Model
from playhouse.pool import PooledPostgresqlDatabase

load_dotenv()

def get_database_config():
    """Get database configuration from environment variables with defaults."""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'pic_db'),
        'user': os.getenv('DB_USER', 'pic_user'),
        'password': os.getenv('DB_PASSWORD', 'pic_password'),
        'max_connections': int(os.getenv('DB_MAX_CONNECTIONS', 5)),
        'stale_timeout': int(os.getenv('DB_STALE_TIMEOUT', 300)),
        'timeout': int(os.getenv('DB_CONNECTION_TIMEOUT', 10)),
    }

db_config = get_database_config()

database = PooledPostgresqlDatabase(
    db_config['database'],
    user=db_config['user'],
    password=db_config['password'],
    host=db_config['host'],
    port=db_config['port'],
    max_connections=db_config['max_connections'],
    stale_timeout=db_config['stale_timeout'],
    timeout=db_config['timeout']
)


def verify_connection():
    """Verify database connection is working."""
    try:
        database.execute_sql("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

class BaseModel(Model):
    """Base model class that all models inherit from."""
    class Meta:
        database = database

def get_pool_status():
    """Get connection pool status for monitoring."""
    try:
        return {
            'max_connections': database._max_connections,
            'active_connections': len(database._in_use),
            'available_connections': len(database._connections),
            'is_closed': database.is_closed()
        }
    except AttributeError:
        return {'status': 'Pool information not available'}

def close_pool():
    """Close all connections in the pool. Use only for application shutdown."""
    if hasattr(database, 'close_all'):
        database.close_all()
    elif not database.is_closed():
        database.close()