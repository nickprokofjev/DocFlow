#!/usr/bin/env python3
"""
Скрипт запуска backend для development окружения.
Автоматически инициализирует базу данных и создает admin пользователя.
"""
import os
import sys
import asyncio
import logging
import subprocess
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from init_db import init_database, check_database_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def wait_for_db():
    """Ждем пока база данных будет готова."""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        if await check_database_connection():
            logger.info("База данных готова!")
            return True
        
        logger.info(f"Ожидание базы данных... ({retry_count + 1}/{max_retries})")
        await asyncio.sleep(2)
        retry_count += 1
    
    logger.error("Не удалось подключиться к базе данных после всех попыток")
    return False

async def main():
    """Главная функция запуска development сервера."""
    logger.info("🚀 Запуск DocFlow Backend Development Server")
    
    # Ждем базу данных
    if not await wait_for_db():
        sys.exit(1)
    
    # Инициализируем базу данных
    try:
        logger.info("📦 Инициализация базы данных...")
        await init_database()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации базы данных: {e}")
        # Продолжаем работу даже если инициализация не удалась
    
    # Запускаем Uvicorn сервер
    logger.info("🌐 Запуск Uvicorn сервера...")
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())