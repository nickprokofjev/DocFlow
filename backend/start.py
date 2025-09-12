#!/usr/bin/env python3
"""
Startup script for DocFlow backend.
Handles database initialization and starts the FastAPI server.
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from init_db import check_database_connection, init_database

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def startup_checks():
    """Perform startup checks and initialization."""
    logger.info("Starting DocFlow backend...")
    
    # Check database connection
    logger.info("Checking database connection...")
    if not await check_database_connection():
        logger.error("Database connection failed. Please check your DATABASE_URL.")
        logger.error("Make sure PostgreSQL is running and DATABASE_URL is set correctly.")
        return False
    
    # Initialize database if needed
    logger.info("Initializing database...")
    try:
        await init_database()
        logger.info("Database initialization completed.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False
    
    return True

def main():
    """Main startup function."""
    # Perform startup checks
    if not asyncio.run(startup_checks()):
        logger.error("Startup checks failed. Exiting.")
        sys.exit(1)
    
    # Start the FastAPI server
    import uvicorn
    try:
        logger.info("Starting FastAPI server...")
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            reload_dirs=["./"],
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()