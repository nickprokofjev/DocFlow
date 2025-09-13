"""
Пользовательские классы исключений и обработчики ошибок для DocFlow API.

Определяет:
- Базовые классы исключений для различных типов ошибок
- Обработчики исключений для преобразования в HTTP ответы
- Стандартизированные ответы об ошибках

Типы ошибок:
- ValidationError: Ошибки валидации входных данных
- DatabaseError: Ошибки работы с базой данных
- FileProcessingError: Ошибки обработки файлов (OCR/NLP)
- NotFoundError: Ошибки поиска ресурсов
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class DocFlowException(Exception):
    """Базовый класс исключений для приложения DocFlow."""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(DocFlowException):
    """Возникает при неудачной валидации входных данных."""
    pass

class DatabaseError(DocFlowException):
    """Возникает при неудачных операциях с базой данных."""
    pass

class FileProcessingError(DocFlowException):
    """Возникает при неудачной обработке файлов (OCR/NLP)."""
    pass

class NotFoundError(DocFlowException):
    """Возникает, когда запрашиваемый ресурс не найден."""
    pass

async def docflow_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Пользовательский обработчик исключений для DocFlow.
    
    Преобразует внутренние исключения в соответствующие HTTP ответы.
    """
    # Handle DocFlow specific exceptions
    if isinstance(exc, DocFlowException):
        logger.error(f"DocFlow ошибка: {exc.message} (код: {exc.error_code})")
        
        # Сопоставляем типы исключений с HTTP кодами состояния
        status_code_map = {
            ValidationError: 400,
            NotFoundError: 404,
            DatabaseError: 500,
            FileProcessingError: 500,
        }
        
        status_code = status_code_map.get(type(exc), 500)
        
        return JSONResponse(
            status_code=status_code,
            content={
                "detail": exc.message,
                "error_code": exc.error_code,
                "type": type(exc).__name__
            }
        )
    else:
        # Handle other exceptions generically
        logger.error(f"Общая ошибка: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Внутренняя ошибка сервера",
                "error_code": "INTERNAL_ERROR",
                "type": "Exception"
            }
        )

async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Обрабатывает ошибки валидации от Pydantic.
    
    Преобразует ошибки валидации схем в понятные HTTP ответы.
    """
    logger.error(f"Ошибка валидации: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Ошибка валидации",
            "errors": str(exc)
        }
    )

def get_error_response(message: str, status_code: int = 400, error_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Вспомогательная функция для создания стандартизированных ответов об ошибках.
    
    Используется для единообразного форматирования ответов об ошибках.
    """
    return {
        "error": True,
        "message": message,
        "error_code": error_code,
        "status_code": status_code
    }