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
from schemas import ExtendedContractUploadRequest, APIResponse, ErrorResponse
import json

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
        "api_base": "/api/v1",
        "test_pages": {
            "ocr_test": "/test",
            "contract_form_test": "/test-form",
            "contracts_list": "/test-contracts"
        },
        "available_endpoints": [
            "POST /test-ocr - Тестирование OCR",
            "POST /test-contract-save - Сохранение договора",
            "GET /test-contracts - Список сохраненных договоров",
            "GET /test-contract/{number} - Детали договора"
        ]
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

@app.post("/test-contract-save")
async def test_contract_save(contract_data: ExtendedContractUploadRequest):
    """
    Тестовый эндпоинт для сохранения данных договора без авторизации.
    Принимает данные договора и сохраняет их в JSON файл для тестирования.
    """
    logger.info(f"Тестирование сохранения договора: {contract_data.number}")
    
    try:
        # Преобразуем данные в словарь
        contract_dict = contract_data.model_dump()
        
        # Преобразуем даты в строки для JSON
        for key, value in contract_dict.items():
            if hasattr(value, 'isoformat'):
                contract_dict[key] = value.isoformat()
        
        # Сохраняем в JSON файл для тестирования
        filename = f"test_contracts/contract_{contract_data.number.replace('/', '_')}.json"
        os.makedirs("test_contracts", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(contract_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Договор сохранен в файл: {filename}")
        
        return APIResponse(
            success=True,
            message=f"Договор {contract_data.number} успешно сохранен для тестирования",
            data={
                "contract_number": contract_data.number,
                "filename": filename,
                "saved_fields": len([k for k, v in contract_dict.items() if v is not None])
            }
        )
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении договора: {e}")
        return ErrorResponse(
            success=False,
            message=f"Ошибка сохранения: {str(e)}",
            error_code="SAVE_ERROR"
        )

@app.get("/test-contracts")
async def get_test_contracts():
    """
    Получить список всех тестовых договоров.
    """
    try:
        contracts = []
        test_dir = "test_contracts"
        
        if os.path.exists(test_dir):
            for filename in os.listdir(test_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(test_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            contract_data = json.load(f)
                            contracts.append({
                                "filename": filename,
                                "contract_number": contract_data.get("number", "Unknown"),
                                "contract_date": contract_data.get("contract_date"),
                                "customer_name": contract_data.get("customer_name"),
                                "contractor_name": contract_data.get("contractor_name"),
                                "amount": contract_data.get("amount")
                            })
                    except Exception as e:
                        logger.error(f"Ошибка чтения файла {filename}: {e}")
        
        return APIResponse(
            success=True,
            message=f"Найдено {len(contracts)} тестовых договоров",
            data={"contracts": contracts}
        )
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка договоров: {e}")
        return ErrorResponse(
            success=False,
            message=f"Ошибка получения списка: {str(e)}",
            error_code="LIST_ERROR"
        )

@app.get("/test-contract/{contract_number}")
async def get_test_contract(contract_number: str):
    """
    Получить данные конкретного тестового договора.
    """
    try:
        filename = f"test_contracts/contract_{contract_number.replace('/', '_')}.json"
        
        if not os.path.exists(filename):
            return ErrorResponse(
                success=False,
                message=f"Договор {contract_number} не найден",
                error_code="NOT_FOUND"
            )
        
        with open(filename, 'r', encoding='utf-8') as f:
            contract_data = json.load(f)
        
        return APIResponse(
            success=True,
            message=f"Данные договора {contract_number}",
            data=contract_data
        )
        
    except Exception as e:
        logger.error(f"Ошибка при получении договора {contract_number}: {e}")
        return ErrorResponse(
            success=False,
            message=f"Ошибка получения договора: {str(e)}",
            error_code="GET_ERROR"
        )
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

@app.get("/test-form", response_class=HTMLResponse)
async def test_form_page():
    """
    HTML страница для тестирования сохранения договоров без авторизации.
    """
    try:
        with open("test_contract_form.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body>
                <h1>Тестовая форма не найдена</h1>
                <p>Файл test_contract_form.html не найден в директории backend.</p>
                <p><a href="/test">Перейти к OCR тестированию</a></p>
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
