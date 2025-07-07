import os
from peewee import PostgresqlDatabase, Model
from dotenv import load_dotenv

load_dotenv()

def get_database_config():
    """Get database configuration from environment variables with defaults."""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'pic_db'),
        'user': os.getenv('DB_USER', 'pic_user'),
        'password': os.getenv('DB_PASSWORD', 'pic_password'),
    }

db_config = get_database_config()

database = PostgresqlDatabase(
    db_config['database'],
    user=db_config['user'],
    password=db_config['password'],
    host=db_config['host'],
    port=db_config['port']
)

class BaseModel(Model):
    """Base model class that all models inherit from."""
    class Meta:
        database = database

def connect_db():
    """Connect to the database."""
    if database.is_closed():
        database.connect()
    return database

def close_db():
    """Close the database connection."""
    if not database.is_closed():
        database.close()