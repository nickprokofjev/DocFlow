"""
Скрипт инициализации базы данных для DocFlow backend.

Отвечает за:
- Создание всех таблиц в базе данных
- Запуск начальных миграций
- Создание администратора по умолчанию
- Проверку подключения к базе данных

Использование:
    python init_db.py
"""
import os
import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import logging

# Добавляем текущую директорию в путь для импорта наших моделей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Base
from db import DATABASE_URL
from auth import create_default_user

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def init_database():
    """
    Инициализация базы данных путем создания всех таблиц.
    
    Создает все необходимые таблицы и создает пользователя-администратора по умолчанию.
    """
    try:
        # Удаляем +asyncpg из URL для создания таблиц (если присутствует)
        sync_url = DATABASE_URL.replace("+asyncpg", "")
        logger.info(f"Подключение к базе данных: {sync_url}")
        
        # Создаем асинхронный движок
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        async with engine.begin() as conn:
            # Создаем все таблицы
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Все таблицы успешно созданы")
            
        # Create default user if none exists
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        from sqlalchemy import select
        from models import User
        async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
        async with async_session() as session:
            # Check if any users exist
            result = await session.execute(select(User))
            existing_users = result.scalars().all()
            
            if not existing_users:
                default_user = create_default_user(session)
                session.add(default_user)
                await session.commit()
                logger.info("Default admin user created: admin@example.com / admin123")
            else:
                logger.info("Users already exist, skipping default user creation")
            
        await engine.dispose()
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise

async def check_database_connection():
    """Check if database connection is working."""
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        await engine.dispose()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def main():
    """Main function to run database initialization."""
    logger.info("Starting DocFlow database initialization...")
    
    # Check connection first
    if not asyncio.run(check_database_connection()):
        logger.error("Cannot connect to database. Please check your DATABASE_URL environment variable.")
        logger.error(f"Current DATABASE_URL: {DATABASE_URL}")
        sys.exit(1)
    
    # Initialize database
    asyncio.run(init_database())
    logger.info("Database initialization finished successfully!")

if __name__ == "__main__":
    main()