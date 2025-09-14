"""
Модуль конфигурации базы данных для системы DocFlow.

Обеспечивает:
- Настройку асинхронного подключения к PostgreSQL
- Создание сессий для работы с базой данных
- Поддержка как асинхронных, так и синхронных операций

Используемые технологии:
- SQLAlchemy с поддержкой asyncio
- PostgreSQL с драйвером asyncpg
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import os

# URL подключения к базе данных из переменных окружения
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://docflow_user:docflow_password@localhost/docflow')
# Синхронная версия для совместимости
SYNC_DATABASE_URL = DATABASE_URL.replace('+asyncpg', '')

# Асинхронный движок и сессия для основной работы
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Синхронный движок и сессия для смешанного использования
sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)