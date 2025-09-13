"""
Основное приложение FastAPI для системы DocFlow.

Отвечает за:
- Настройку главного приложения FastAPI
- Подключение CORS миддлвари для кросс-доменных запросов
- Обработку пользовательских исключений
- Подключение маршрутов API и аутентификации
- Эндпоинты проверки здоровья

Поддерживаемые эндпоинты:
- / - Основная страница с информацией о API
- /health - Проверка состояния и подключения к базе данных
- /api/v1/* - Основные API маршруты
- /auth/* - Маршруты аутентификации
"""
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router
from auth_api import router as auth_router
from exceptions import (
    DocFlowException, 
    docflow_exception_handler, 
    validation_exception_handler
)
from pydantic import ValidationError

# Настройка логгирования для основного приложения
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Создание экземпляра FastAPI
app = FastAPI(
    title="DocFlow API",
    description="API for managing contracts, acts, and additional agreements",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom exception handlers
# Note: Using Exception base class for broader compatibility
app.add_exception_handler(Exception, docflow_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)

# Include API routers
app.include_router(auth_router)  # No prefix for auth routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    """
    Базовый эндпоинт для проверки работоспособности backend.
    """
    logger.info("Запрос к корневому эндпоинту: /")
    return {
        "message": "DocFlow backend is running",
        "version": "1.0.0",
        "status": "healthy",
        "api_docs": "/docs",
        "api_base": "/api/v1"
    }

@app.get("/health")
async def health_check():
    """
    Проверка здоровья приложения и подключения к базе данных.
    """
    try:
        # Test database connection
        from db import engine
        from sqlalchemy import text
        
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    try:
        logger.info("Запуск FastAPI приложения через uvicorn...")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")
