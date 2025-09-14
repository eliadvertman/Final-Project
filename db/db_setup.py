#!/usr/bin/env python3
"""
Database setup script for PIC (Prediction and Model Management) service.

This script creates a PostgreSQL database if it doesn't exist and runs
the initialization SQL scripts to set up the schema.

Usage:
    python db_setup.py --db_name <name> --db_user <user> --db_password <password> --db_port <port> [--db_host <host>]
    
Or with environment variables:
    DB_NAME=pic_db DB_USER=pic_user DB_PASSWORD=pic_password DB_PORT=5432 python db_setup.py
"""

import argparse
import os
import sys
import logging
from pathlib import Path
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_config():
    """Get database configuration from command line arguments or environment variables."""
    parser = argparse.ArgumentParser(description='Setup PostgreSQL database and run initialization scripts')
    
    parser.add_argument('--db_name', default=os.getenv('DB_NAME', 'pic_db'),
                       help='Database name (default: pic_db)')
    parser.add_argument('--db_user', default=os.getenv('DB_USER', 'pic_user'),
                       help='Database user (default: pic_user)')
    parser.add_argument('--db_password', default=os.getenv('DB_PASSWORD', 'pic_password'),
                       help='Database password (default: pic_password)')
    parser.add_argument('--db_port', type=int, default=int(os.getenv('DB_PORT', '5432')),
                       help='Database port (default: 5432)')
    parser.add_argument('--db_host', default=os.getenv('DB_HOST', 'localhost'),
                       help='Database host (default: localhost)')
    parser.add_argument('--cleanup', action='store_true',
                       help='Drop existing tables before creating new ones')
    
    return parser.parse_args()


def connect_to_postgres(host, port, user, password, database=None):
    """Connect to PostgreSQL server."""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database or 'postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise


def database_exists(cursor, db_name):
    """Check if database exists."""
    cursor.execute(
        "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
        (db_name,)
    )
    return cursor.fetchone() is not None


def create_database(cursor, db_name):
    """Create database if it doesn't exist."""
    if database_exists(cursor, db_name):
        logger.info(f"Database '{db_name}' already exists")
        return False
    
    logger.info(f"Creating database '{db_name}'...")
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
    logger.info(f"Database '{db_name}' created successfully")
    return True


def run_sql_file(cursor, sql_file_path):
    """Execute SQL commands from a file."""
    try:
        with open(sql_file_path, 'r') as file:
            sql_content = file.read()
        
        if sql_content.strip():
            cursor.execute(sql_content)
            logger.info(f"Successfully executed SQL file: {sql_file_path}")
        else:
            logger.warning(f"SQL file is empty: {sql_file_path}")
            
    except FileNotFoundError:
        logger.error(f"SQL file not found: {sql_file_path}")
        raise
    except psycopg2.Error as e:
        logger.error(f"Error executing SQL file {sql_file_path}: {e}")
        raise


def cleanup_tables(cursor):
    """Drop existing tables in reverse dependency order."""
    tables_to_drop = ['inference', 'model', 'training', 'jobs']
    
    logger.info("Starting table cleanup...")
    for table_name in tables_to_drop:
        try:
            cursor.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(sql.Identifier(table_name)))
            logger.info(f"Dropped table '{table_name}'")
        except psycopg2.Error as e:
            logger.error(f"Error dropping table '{table_name}': {e}")
            raise
    
    logger.info("Table cleanup completed")


def find_init_scripts():
    """Find all SQL initialization scripts in the init directory."""
    script_dir = Path(__file__).parent
    init_dir = script_dir / 'init'
    
    if not init_dir.exists():
        logger.warning(f"Init directory not found: {init_dir}")
        return []
    
    sql_files = sorted(init_dir.glob('*.sql'))
    logger.info(f"Found {len(sql_files)} SQL initialization scripts")
    
    return sql_files


def main():
    """Main function to setup database and run initialization scripts."""
    config = get_config()
    
    logger.info("Starting database setup...")
    logger.info(f"Configuration: host={config.db_host}, port={config.db_port}, "
                f"database={config.db_name}, user={config.db_user}")
    
    try:
        # Connect to PostgreSQL server (not specific database)
        logger.info("Connecting to PostgreSQL server...")
        conn = connect_to_postgres(
            config.db_host, 
            config.db_port, 
            config.db_user, 
            config.db_password
        )
        
        with conn.cursor() as cursor:
            # Create database if it doesn't exist
            create_database(cursor, config.db_name)
        
        conn.close()
        
        # Connect to the target database for initialization
        logger.info(f"Connecting to database '{config.db_name}'...")
        db_conn = connect_to_postgres(
            config.db_host,
            config.db_port,
            config.db_user,
            config.db_password,
            config.db_name
        )
        
        with db_conn.cursor() as cursor:
            # Cleanup tables if requested
            if config.cleanup:
                cleanup_tables(cursor)
            
            # Run initialization scripts
            init_scripts = find_init_scripts()
            
            if not init_scripts:
                logger.warning("No initialization scripts found")
            else:
                logger.info("Running initialization scripts...")
                for script in init_scripts:
                    run_sql_file(cursor, script)
        
        db_conn.close()
        
        logger.info("Database setup completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())