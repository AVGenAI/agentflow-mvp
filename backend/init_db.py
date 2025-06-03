#!/usr/bin/env python3
"""
Initialize database tables for AgentFlow
"""
import time
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.conversation import Base

def wait_for_db(database_url, max_retries=30, retry_interval=2):
    """Wait for database to be available"""
    engine = create_engine(database_url)
    
    for i in range(max_retries):
        try:
            # Try to connect
            conn = engine.connect()
            conn.close()
            print("✅ Database is ready!")
            return engine
        except OperationalError:
            if i < max_retries - 1:
                print(f"⏳ Waiting for database... ({i+1}/{max_retries})")
                time.sleep(retry_interval)
            else:
                print("❌ Database connection failed after maximum retries")
                raise

def init_database():
    """Initialize database tables"""
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/agentflow")
    print(f"🔧 Initializing database: {database_url}")
    
    # Wait for database to be ready
    engine = wait_for_db(database_url)
    
    # Create all tables
    print("📊 Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    # List created tables
    print("\n✅ Database initialized successfully!")
    print("📋 Created tables:")
    for table in Base.metadata.tables:
        print(f"   - {table}")

if __name__ == "__main__":
    init_database()