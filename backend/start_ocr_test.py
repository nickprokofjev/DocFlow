#!/usr/bin/env python3
"""
Simple startup script for DocFlow backend OCR testing.
Runs without database dependencies.
"""
import os
import sys
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main startup function for OCR testing."""
    logger.info("Starting DocFlow backend for OCR testing...")
    
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