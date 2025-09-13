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
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import tempfile
import os
# from api import router
# from auth_api import router as auth_router
from exceptions import (
    DocFlowException, 
    docflow_exception_handler, 
    validation_exception_handler
)
from pydantic import ValidationError
from ocr_nlp import extract_text_from_file, extract_contract_entities

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

# Include API routers - временно отключено для тестирования OCR
# app.include_router(auth_router)  # No prefix for auth routes
# app.include_router(router, prefix="/api/v1")

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
        # Test database connection - временно отключено для тестирования
        # from db import engine
        # from sqlalchemy import text
        # 
        # async with engine.begin() as conn:
        #     await conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "not_checked",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Database check disabled for OCR testing"
        }
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.post("/test-ocr")
async def test_ocr(file: UploadFile = File(...)):
    """
    Тестовый эндпоинт для демонстрации OCR без авторизации.
    Принимает файл (PDF или изображение) и возвращает извлеченный текст и сущности.
    """
    logger.info(f"Тестирование OCR для файла: {file.filename}")
    
    # Проверяем тип файла
    allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Неподдерживаемый тип файла. Поддерживаются: {', '.join(allowed_types)}"
        )
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename or '')[1]) as temp_file:
        try:
            # Записываем содержимое в временный файл
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Извлекаем текст с помощью OCR
            extracted_text = extract_text_from_file(temp_file.name)
            
            # Извлекаем сущности с помощью NLP
            entities = extract_contract_entities(extracted_text) if extracted_text else {}
            
            return {
                "filename": file.filename,
                "file_size": len(content),
                "content_type": file.content_type,
                "extracted_text": extracted_text,
                "entities": entities,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Ошибка при обработке файла {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")
        
        finally:
            # Удаляем временный файл
            try:
                os.unlink(temp_file.name)
            except:
                pass

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """
    Простая HTML страница для тестирования OCR функциональности.
    """
    try:
        with open("test_ocr.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body>
                <h1>Тестовая страница не найдена</h1>
                <p>Файл test_ocr.html не найден в директории backend.</p>
                <p><a href="/docs">Перейти к API документации</a></p>
            </body>
        </html>
        """

if __name__ == "__main__":
    import uvicorn
    try:
        logger.info("Запуск FastAPI приложения через uvicorn...")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")
