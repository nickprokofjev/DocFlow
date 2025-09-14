#!/usr/bin/env python3
"""
Script to check users in the database
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal
from models import User
from sqlalchemy import select

async def check_users():
    """Check all users in the database"""
    try:
        async with SessionLocal() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"- ID: {user.id}")
                print(f"  Username: {user.username}")
                print(f"  Email: {user.email}")
                print(f"  Active: {user.is_active}")
                print(f"  Superuser: {user.is_superuser}")
                print(f"  Created: {user.created_at}")
                print("---")
                
    except Exception as e:
        print(f"Error checking users: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_users())