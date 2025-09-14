#!/usr/bin/env python3
"""
Скрипт для создания администратора по умолчанию.
Используется для решения проблем с входом в систему.
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from models import User
from auth import get_password_hash
from db import DATABASE_URL

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def create_admin_user():
    """Create admin user if it doesn't exist."""
    try:
        engine = create_async_engine(DATABASE_URL, echo=True)
        async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
        
        async with async_session() as session:
            # Check if admin user exists
            result = await session.execute(
                select(User).where(User.email == "admin@example.com")
            )
            admin_user = result.scalar_one_or_none()
            
            if admin_user:
                logger.info("Admin user already exists: admin@example.com")
                # Update password just in case
                admin_user.hashed_password = get_password_hash("admin123")
                await session.commit()
                logger.info("Admin password updated successfully")
            else:
                # Create new admin user
                hashed_password = get_password_hash("admin123")
                admin_user = User(
                    email="admin@example.com",
                    username="admin",
                    hashed_password=hashed_password,
                    is_superuser=True,
                    is_active=True
                )
                session.add(admin_user)
                await session.commit()
                logger.info("Admin user created successfully!")
                logger.info("Email: admin@example.com")
                logger.info("Password: admin123")
        
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise

async def list_users():
    """List all users in the database."""
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
        
        async with async_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            logger.info(f"Found {len(users)} users in database:")
            for user in users:
                logger.info(f"  - {user.email} (username: {user.username}, active: {user.is_active})")
        
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise

def main():
    """Main function."""
    logger.info("Starting admin user creation...")
    
    try:
        # List existing users first
        asyncio.run(list_users())
        
        # Create/update admin user
        asyncio.run(create_admin_user())
        
        # List users again to confirm
        logger.info("Final user list:")
        asyncio.run(list_users())
        
        logger.info("Admin user setup completed successfully!")
        logger.info("You can now login with:")
        logger.info("  Email: admin@example.com")
        logger.info("  Password: admin123")
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()