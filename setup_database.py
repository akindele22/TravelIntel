"""
Database Setup Script
Creates the database and tables if they don't exist
"""
import psycopg2
from database import DatabaseHandler
import config


def setup_database():
    """Setup database and tables"""
    try:
        # Connect to PostgreSQL server (not specific database)
        conn = psycopg2.connect(
            host=config.DATABASE_CONFIG['host'],
            port=config.DATABASE_CONFIG['port'],
            user=config.DATABASE_CONFIG['user'],
            password=config.DATABASE_CONFIG['password'],
            database='postgres'  # Connect to default database
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (config.DATABASE_CONFIG['database'],)
        )
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(
                f"CREATE DATABASE {config.DATABASE_CONFIG['database']}"
            )
            print(f"Database '{config.DATABASE_CONFIG['database']}' created successfully")
        else:
            print(f"Database '{config.DATABASE_CONFIG['database']}' already exists")
        
        cursor.close()
        conn.close()
        
        # Now create tables
        print("Creating tables...")
        db = DatabaseHandler()
        db.close()
        print("Database setup completed!")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        print("\nMake sure PostgreSQL is running and credentials are correct.")
        raise


if __name__ == '__main__':
    setup_database()
