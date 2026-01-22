"""
Create PostgreSQL database for Saylo Interview Platform
Run this script to create the database if it doesn't exist
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

# Database configuration
DB_NAME = "saylo_interview"
DB_USER = "postgres"
DB_PASSWORD = "Admin@123"
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Connect to PostgreSQL server (default database)
        print(f"Connecting to PostgreSQL server at {DB_HOST}:{DB_PORT}...")
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        # Set isolation level for database creation
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"✓ Database '{DB_NAME}' already exists")
        else:
            # Create database
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(DB_NAME)
                )
            )
            print(f"✓ Database '{DB_NAME}' created successfully!")
        
        cursor.close()
        conn.close()
        
        # Test connection to new database
        print(f"\nTesting connection to '{DB_NAME}'...")
        test_conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        test_conn.close()
        print(f"✓ Successfully connected to '{DB_NAME}'")
        
        print("\n" + "="*50)
        print("Database setup complete!")
        print("="*50)
        print(f"\nConnection string:")
        print(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n✗ Database error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check that the password is correct (Admin@123)")
        print("3. Verify PostgreSQL is accessible on localhost:5432")
        return False
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("="*50)
    print("Saylo Interview Platform - Database Setup")
    print("="*50)
    print()
    
    success = create_database()
    
    if success:
        print("\nNext steps:")
        print("1. Download Ollama models: ollama pull llama3.1:8b-instruct-q4_K_M")
        print("2. Start backend: python -m uvicorn app.main:app --reload")
        sys.exit(0)
    else:
        print("\nPlease fix the errors above and try again.")
        sys.exit(1)
