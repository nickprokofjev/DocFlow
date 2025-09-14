#!/usr/bin/env python3
"""
Скрипт для создания демо-пользователя и проверки настройки базы данных.
Решает проблему "User not found" для демонстрационных целей.
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Add backend directory to path for imports
backend_path = str(Path(__file__).parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Now import from backend modules
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, text
from models import User, Base
from auth import get_password_hash
from db import DATABASE_URL

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def check_database_connection():
    """Проверяет подключение к базе данных."""
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("✅ Подключение к базе данных успешно")
        await engine.dispose()
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к базе данных: {e}")
        return False

async def create_tables():
    """Создает таблицы если они не существуют."""
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Таблицы созданы/проверены")
        await engine.dispose()
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка создания таблиц: {e}")
        return False

async def create_demo_users():
    """Создает демо-пользователей если их нет."""
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
        
        demo_users = [
            {
                "email": "admin@example.com",
                "username": "admin",
                "password": "admin123",
                "is_superuser": True,
                "description": "Администратор системы"
            },
            {
                "email": "demo@example.com", 
                "username": "demo",
                "password": "demo123",
                "is_superuser": False,
                "description": "Демо-пользователь"
            },
            {
                "email": "user@example.com",
                "username": "user", 
                "password": "user123",
                "is_superuser": False,
                "description": "Обычный пользователь"
            }
        ]
        
        async with async_session() as session:
            users_created = 0
            
            for user_data in demo_users:
                # Проверяем существование пользователя
                result = await session.execute(
                    select(User).where(
                        (User.email == user_data["email"]) | 
                        (User.username == user_data["username"])
                    )
                )
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    logger.info(f"⚠️  Пользователь уже существует: {user_data['email']}")
                    # Обновляем пароль на всякий случай
                    existing_user.hashed_password = get_password_hash(user_data["password"])
                    users_created += 1
                else:
                    # Создаем нового пользователя
                    hashed_password = get_password_hash(user_data["password"])
                    new_user = User(
                        email=user_data["email"],
                        username=user_data["username"],
                        hashed_password=hashed_password,
                        is_superuser=user_data["is_superuser"],
                        is_active=True
                    )
                    session.add(new_user)
                    logger.info(f"✅ Создан пользователь: {user_data['email']} ({user_data['description']})")
                    users_created += 1
            
            await session.commit()
            logger.info(f"✅ Обработано пользователей: {users_created}")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания демо-пользователей: {e}")
        return False

async def list_all_users():
    """Выводит список всех пользователей в базе данных."""
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
        
        async with async_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            logger.info(f"📋 Всего пользователей в базе: {len(users)}")
            for user in users:
                status = "✅ Активен" if user.is_active else "❌ Неактивен"
                role = "👑 Админ" if user.is_superuser else "👤 Пользователь"
                logger.info(f"  • {user.email} (логин: {user.username}) - {role} - {status}")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения списка пользователей: {e}")
        return False

def print_demo_credentials():
    """Выводит учетные данные для демонстрации."""
    print("\n" + "="*60)
    print("🔑 УЧЕТНЫЕ ДАННЫЕ ДЛЯ ВХОДА В СИСТЕМУ:")
    print("="*60)
    print("👑 АДМИНИСТРАТОР:")
    print("   Email: admin@example.com")
    print("   Password: admin123")
    print("")
    print("👤 ДЕМО-ПОЛЬЗОВАТЕЛЬ:")
    print("   Email: demo@example.com") 
    print("   Password: demo123")
    print("")
    print("👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ:")
    print("   Email: user@example.com")
    print("   Password: user123")
    print("="*60)

async def main():
    """Главная функция настройки демо-пользователей."""
    print("🚀 === НАСТРОЙКА ДЕМО-ПОЛЬЗОВАТЕЛЕЙ DOCFLOW ===\n")
    
    # Проверяем подключение к БД
    print("🔍 Проверка подключения к базе данных...")
    if not await check_database_connection():
        print("❌ Не удается подключиться к базе данных")
        print(f"🔧 DATABASE_URL: {DATABASE_URL}")
        return False
    
    # Создаем таблицы
    print("\n🏗️  Создание/проверка таблиц...")
    if not await create_tables():
        print("❌ Ошибка при создании таблиц")
        return False
    
    # Создаем демо-пользователей
    print("\n👥 Создание демо-пользователей...")
    if not await create_demo_users():
        print("❌ Ошибка при создании пользователей")
        return False
    
    # Выводим список пользователей
    print("\n📋 Текущие пользователи в системе:")
    await list_all_users()
    
    # Выводим учетные данные
    print_demo_credentials()
    
    print("\n🎉 Настройка завершена успешно!")
    print("💡 Теперь вы можете войти в систему используя любые из указанных учетных данных.")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Операция прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)