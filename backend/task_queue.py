"""
Система фоновых задач для DocFlow.

Обеспечивает асинхронную обработку OCR/NLP для больших файлов,
предотвращая таймауты и улучшая пользовательский опыт.
"""
import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional
from uuid import uuid4, UUID
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Статусы выполнения задач."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class JobResult:
    """Результат выполнения задачи."""
    job_id: str
    status: JobStatus
    progress: int  # 0-100
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует результат в словарь для JSON сериализации."""
        result_dict = asdict(self)
        result_dict['status'] = self.status.value
        # Конвертируем datetime в строки
        for field in ['created_at', 'started_at', 'completed_at']:
            if result_dict[field]:
                result_dict[field] = result_dict[field].isoformat()
        return result_dict

class TaskQueue:
    """
    Простая система фоновых задач в памяти.
    
    В продакшене рекомендуется использовать Redis или RabbitMQ,
    но для MVP достаточно хранения в памяти.
    """
    
    def __init__(self):
        self.jobs: Dict[str, JobResult] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self._cleanup_interval = 3600  # Очищаем завершённые задачи каждый час
        self._max_completed_jobs = 100  # Максимум завершённых задач в памяти
        
    async def submit_job(self, job_id: str, coro_func, *args, **kwargs) -> str:
        """
        Отправляет задачу на выполнение.
        
        Args:
            job_id: Уникальный идентификатор задачи
            coro_func: Корутина для выполнения
            *args, **kwargs: Аргументы для передачи в корутину
            
        Returns:
            str: ID задачи
        """
        logger.info(f"Submitting job {job_id}")
        
        # Создаём запись о задаче
        job_result = JobResult(
            job_id=job_id,
            status=JobStatus.PENDING,
            progress=0,
            message="Задача добавлена в очередь"
        )
        self.jobs[job_id] = job_result
        
        # Запускаем задачу асинхронно
        task = asyncio.create_task(self._execute_job(job_id, coro_func, *args, **kwargs))
        self.running_tasks[job_id] = task
        
        return job_id
    
    async def _execute_job(self, job_id: str, coro_func, *args, **kwargs):
        """Выполняет задачу и обновляет её статус."""
        job_result = self.jobs[job_id]
        
        try:
            # Отмечаем начало выполнения
            job_result.status = JobStatus.PROCESSING
            job_result.started_at = datetime.now()
            job_result.progress = 10
            job_result.message = "Обработка начата"
            
            logger.info(f"Starting job {job_id}")
            
            # Выполняем задачу
            result = await coro_func(job_id, *args, **kwargs)
            
            # Успешное завершение
            job_result.status = JobStatus.COMPLETED
            job_result.progress = 100
            job_result.message = "Обработка завершена успешно"
            job_result.result = result
            job_result.completed_at = datetime.now()
            
            logger.info(f"Job {job_id} completed successfully")
            
        except asyncio.CancelledError:
            job_result.status = JobStatus.CANCELLED
            job_result.message = "Задача была отменена"
            job_result.completed_at = datetime.now()
            logger.info(f"Job {job_id} was cancelled")
            
        except Exception as e:
            job_result.status = JobStatus.FAILED
            job_result.progress = 0
            job_result.message = f"Ошибка при обработке: {str(e)}"
            job_result.error = str(e)
            job_result.completed_at = datetime.now()
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            
        finally:
            # Удаляем из списка выполняемых задач
            if job_id in self.running_tasks:
                del self.running_tasks[job_id]
    
    def get_job_status(self, job_id: str) -> Optional[JobResult]:
        """Получает статус задачи по ID."""
        return self.jobs.get(job_id)
    
    def update_job_progress(self, job_id: str, progress: int, message: Optional[str] = None):
        """Обновляет прогресс выполнения задачи."""
        if job_id in self.jobs:
            self.jobs[job_id].progress = progress
            if message:
                self.jobs[job_id].message = message
            logger.debug(f"Job {job_id} progress updated: {progress}%")
    
    async def cancel_job(self, job_id: str) -> bool:
        """Отменяет выполнение задачи."""
        if job_id in self.running_tasks:
            task = self.running_tasks[job_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            logger.info(f"Job {job_id} cancelled")
            return True
        return False
    
    def cleanup_completed_jobs(self):
        """Очищает старые завершённые задачи."""
        completed_jobs = [
            job_id for job_id, job in self.jobs.items()
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
        ]
        
        if len(completed_jobs) > self._max_completed_jobs:
            # Сортируем по времени завершения и удаляем самые старые
            completed_jobs.sort(
                key=lambda jid: self.jobs[jid].completed_at or datetime.min
            )
            jobs_to_remove = completed_jobs[:-self._max_completed_jobs]
            
            for job_id in jobs_to_remove:
                del self.jobs[job_id]
                logger.debug(f"Cleaned up old job {job_id}")
    
    async def process_ocr_nlp_task(self, job_id: str, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Обрабатывает OCR/NLP задачу асинхронно.
        
        Args:
            job_id: ID задачи
            file_path: Путь к файлу для обработки
            filename: Оригинальное имя файла
            
        Returns:
            Dict[str, Any]: Результат обработки
        """
        from ocr_nlp import extract_text_from_file, extract_contract_entities
        import os
        
        try:
            # Проверяем файл
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Файл не найден: {file_path}")
            
            # Обновляем прогресс - начинаем OCR
            self.update_job_progress(job_id, 20, "Начинается распознавание текста (OCR)")
            
            # Извлекаем текст
            logger.info(f"Job {job_id}: Starting OCR for {filename}")
            extracted_text = extract_text_from_file(file_path)
            
            if "Ошибка" in extracted_text:
                raise ValueError(f"OCR error: {extracted_text}")
            
            # Обновляем прогресс - OCR завершён
            self.update_job_progress(job_id, 60, "OCR завершён, начинается анализ сущностей (NLP)")
            
            # Извлекаем сущности
            logger.info(f"Job {job_id}: Starting NLP for {filename}")
            entities = extract_contract_entities(extracted_text)
            
            if "error" in entities:
                logger.warning(f"Job {job_id}: NLP returned error: {entities['error']}")
                # Продолжаем с пустыми сущностями, если NLP не сработал
                entities = {}
            
            # Обновляем прогресс - NLP завершён
            self.update_job_progress(job_id, 90, "Анализ завершён, формируется результат")
            
            # Формируем результат
            result = {
                "file_info": {
                    "filename": filename,
                    "file_path": file_path,
                    "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
                },
                "extracted_text": extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text,
                "full_text_length": len(extracted_text),
                "contract_data": {
                    # Основные поля
                    "number": entities.get("contract_number", ""),
                    "contract_date": entities.get("contract_date", ""),
                    "customer_name": entities.get("customer_name", ""),
                    "contractor_name": entities.get("contractor_name", ""),
                    "subject": entities.get("work_object_name", ""),
                    "amount": entities.get("amount_including_vat", ""),
                    "amount_including_vat": entities.get("amount_including_vat", ""),
                    "vat_rate": entities.get("vat_rate", ""),
                    "vat_amount": entities.get("vat_amount", ""),
                    "deadline": entities.get("deadline", ""),
                    "penalties": self._format_penalties(entities),
                    
                    # Расширенные поля
                    "contract_type": entities.get("contract_type", ""),
                    "work_object_name": entities.get("work_object_name", ""),
                    "work_object_address": entities.get("work_object_address", ""),
                    "cadastral_number": entities.get("cadastral_number", ""),
                    "construction_permit": entities.get("construction_permit", ""),
                    "permit_date": entities.get("permit_date", ""),
                    "warranty_period_months": entities.get("warranty_period_months", ""),
                    "payment_terms_days": entities.get("payment_terms_days", ""),
                    "retention_percentage": entities.get("retention_percentage", ""),
                    "land_area": entities.get("land_area", ""),
                    
                    # Банковские данные
                    "customer_inn": entities.get("customer_inn", ""),
                    "customer_ogrn": entities.get("customer_ogrn", ""),
                    "customer_bank_name": entities.get("customer_bank_name", ""),
                    "customer_bank_account": entities.get("customer_bank_account", ""),
                    "customer_bik": entities.get("customer_bik", ""),
                    
                    "contractor_bank_name": entities.get("contractor_bank_name", ""),
                    "contractor_bank_account": entities.get("contractor_bank_account", ""),
                    "contractor_bik": entities.get("contractor_bik", ""),
                    
                    # Штрафы
                    "delay_penalty_first_week": entities.get("delay_penalty_first_week", ""),
                    "delay_penalty_after_week": entities.get("delay_penalty_after_week", ""),
                    "document_penalty_amount": entities.get("document_penalty_amount", ""),
                    "site_violation_penalty": entities.get("site_violation_penalty", ""),
                    
                    # Приложения
                    "attachments": entities.get("attachments", []),
                    "project_documentation": entities.get("project_documentation", "")
                },
                "extraction_stats": {
                    "text_length": len(extracted_text),
                    "fields_extracted": len([v for v in entities.values() if v and v != ""]),
                    "total_fields": len(entities)
                }
            }
            
            logger.info(f"Job {job_id}: Processing completed successfully. Extracted {result['extraction_stats']['fields_extracted']} fields")
            return result
            
        except Exception as e:
            logger.error(f"Job {job_id}: Error during processing: {e}", exc_info=True)
            raise
    
    def _format_penalties(self, entities: Dict[str, Any]) -> str:
        """Форматирует информацию о штрафах."""
        penalties = []
        
        if entities.get('delay_penalty_first_week'):
            penalties.append(f"Первые 7 дней: {entities['delay_penalty_first_week']}%")
        
        if entities.get('delay_penalty_after_week'):
            penalties.append(f"После 7 дней: {entities['delay_penalty_after_week']}%")
        
        if entities.get('document_penalty_amount'):
            penalties.append(f"За документы: {entities['document_penalty_amount']} руб.")
            
        if entities.get('site_violation_penalty'):
            penalties.append(f"За нарушения на стройплощадке: {entities['site_violation_penalty']} руб.")
        
        return "; ".join(penalties) if penalties else ""

# Глобальный экземпляр очереди задач
task_queue = TaskQueue()

async def start_background_cleanup():
    """Запускает фоновую очистку завершённых задач."""
    while True:
        try:
            await asyncio.sleep(3600)  # Каждый час
            task_queue.cleanup_completed_jobs()
        except Exception as e:
            logger.error(f"Error during background cleanup: {e}")