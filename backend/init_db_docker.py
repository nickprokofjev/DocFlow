#!/usr/bin/env python3
"""
Database initialization script for Docker containers.
This script ensures all tables are created and the admin user exists.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Base, User

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database: create tables and admin user."""
    # Get database URL from environment variable
    database_url = os.getenv('DATABASE_URL', 'postgresql://docflow_user:docflow_password@postgres:5432/docflow')
    
    # Replace asyncpg with psycopg2 for synchronous operations
    sync_database_url = database_url.replace('+asyncpg', '')
    
    try:
        # Create synchronous engine
        engine = create_engine(sync_database_url, echo=True)
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(engine)
        logger.info("All tables created successfully")
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if admin user already exists and verify password
        result = session.execute(text("SELECT id, hashed_password FROM users WHERE username = 'admin'"))
        existing_user = result.fetchone()
        
        admin_needs_creation = True
        if existing_user:
            # Test if existing password is correct
            from auth import verify_password
            if verify_password("admin123", existing_user[1]):
                logger.info("Admin user already exists with correct password")
                admin_needs_creation = False
            else:
                logger.warning("Admin user exists but password is incorrect, recreating...")
                # Delete the existing user with wrong password
                session.execute(text("DELETE FROM users WHERE username = 'admin'"))
                session.commit()
        
        if admin_needs_creation:
            # Create admin user
            from auth import get_password_hash
            hashed_password = get_password_hash("admin123")
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=True
            )
            
            session.add(admin_user)
            session.commit()
            logger.info("Admin user created successfully: admin@example.com / admin123")
        
        session.close()
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        return False

def main():
    """Main function."""
    logger.info("Starting Docker database initialization...")
    
    if init_database():
        logger.info("Docker database initialization completed successfully")
        sys.exit(0)
    else:
        logger.error("Docker database initialization failed")
        sys.exit(1)

if __name__ == "__main__":
    main()