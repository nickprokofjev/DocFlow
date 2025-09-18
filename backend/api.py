"""
API эндпоинты для системы DocFlow.

этот модуль содержит все основные API эндпоинты для:
- Управления договорами (загрузка, просмотр, обработка OCR/NLP)
- CRUD операций со сторонами (заказчики/подрядчики)
- Получения списков документов с фильтрацией и пагинацией

Все эндпоинты защищены JWT аутентификацией.
"""
import logging
from fastapi import UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import APIRouter
import os
from datetime import date, datetime
from uuid import uuid4
from typing import List, Optional
from schemas import (
    PartyCreate, PartyUpdate, PartyResponse,
    ContractCreate, ContractResponse, ContractWithPartiesResponse,
    ContractDocumentCreate, ContractDocumentResponse,
    UploadContractRequest, APIResponse, ErrorResponse
)
from exceptions import ValidationError, DatabaseError, FileProcessingError, NotFoundError
from models import Party, Contract, ContractDocument, DocumentLink, ContractAttachment, User
from auth import get_current_active_user, get_db

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/contracts/extract")
async def extract_contract_data(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Запускает асинхронную обработку файла договора с помощью OCR/NLP.
    Возвращает ID задачи для отслеживания прогресса.
    """
    from task_queue import task_queue
    
    logger.info(f"Начало обработки файла: {file.filename}")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Ошибка: имя файла не указано")
    
    # Проверяем размер файла (50MB)
    max_size = 50 * 1024 * 1024  # 50MB
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой. Максимальный размер: {max_size // 1024 // 1024}MB"
        )
    
    # Проверяем тип файла
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(allowed_extensions)}"
        )
    
    # Создаём файл
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"contract_{file_id}{ext}")
    
    try:
        # Сохраняем файл
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"Файл сохранён: {file_path}")
        
        # Создаём задачу для асинхронной обработки
        job_id = str(uuid4())
        await task_queue.submit_job(
            job_id,
            task_queue.process_ocr_nlp_task,
            file_path,
            file.filename
        )
        
        logger.info(f"Задача {job_id} создана для файла {file.filename}")
        
        return APIResponse(
            success=True,
            message=f"Обработка файла {file.filename} начата",
            data={
                "job_id": job_id,
                "filename": file.filename,
                "file_size": file.size,
                "status": "processing",
                "message": "Файл загружен и отправлен на обработку. Используйте job_id для отслеживания прогресса."
            }
        )
        
    except Exception as e:
        logger.error(f"Ошибка при создании задачи: {e}")
        # Удаляем файл в случае ошибки
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        return APIResponse(
            success=False,
            message=f"Ошибка при обработке файла: {str(e)}",
            data={"error": str(e)}
        )

@router.get("/jobs/{job_id}/status")
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Получает статус выполнения задачи по её ID.
    """
    from task_queue import task_queue
    
    job_result = task_queue.get_job_status(job_id)
    
    if not job_result:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return APIResponse(
        success=True,
        message="Статус задачи получен",
        data=job_result.to_dict()
    )

@router.post("/jobs/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Отменяет выполнение задачи.
    """
    from task_queue import task_queue
    
    cancelled = await task_queue.cancel_job(job_id)
    
    if not cancelled:
        raise HTTPException(status_code=404, detail="Задача не найдена или уже завершена")
    
    return APIResponse(
        success=True,
        message="Задача отменена",
        data={"job_id": job_id, "status": "cancelled"}
    )

@router.post("/contracts/save-extracted")
async def save_extracted_contract(
    contract_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Сохраняет извлеченные данные договора.
    """
    logger.info("Начало сохранения извлеченных данных договора")
    
    try:
        # Создаём стороны если они не существуют
        customer_name = contract_data.get("customer_name", "Заказчик не указан")
        contractor_name = contract_data.get("contractor_name", "Подрядчик не указан")
        
        # Проверяем существование заказчика
        result = await db.execute(select(Party).where(Party.name == customer_name, Party.role == "customer"))
        customer = result.scalar_one_or_none()
        if not customer:
            customer = Party(name=customer_name, role="customer")
            db.add(customer)
            await db.flush()
        
        # Проверяем существование подрядчика
        result = await db.execute(select(Party).where(Party.name == contractor_name, Party.role == "contractor"))
        contractor = result.scalar_one_or_none()
        if not contractor:
            contractor = Party(name=contractor_name, role="contractor")
            db.add(contractor)
            await db.flush()
        
        # Создаём договор
        contract_date_str = contract_data.get("contract_date")
        if contract_date_str:
            if isinstance(contract_date_str, str):
                contract_date = datetime.fromisoformat(contract_date_str.replace('Z', '+00:00')).date()
            else:
                contract_date = contract_date_str
        else:
            contract_date = date.today()
        
        contract = Contract(
            number=contract_data.get("number", "Без номера"),
            date=contract_date,
            subject=contract_data.get("subject"),
            amount=contract_data.get("amount"),
            deadline=contract_data.get("deadline"),
            penalties=contract_data.get("penalties"),
            customer_id=customer.id,
            contractor_id=contractor.id,
            contract_type=contract_data.get("contract_type"),
            work_object_name=contract_data.get("work_object_name"),
            work_object_address=contract_data.get("work_object_address"),
            cadastral_number=contract_data.get("cadastral_number"),
            construction_permit=contract_data.get("construction_permit"),
            amount_including_vat=contract_data.get("amount_including_vat"),
            vat_rate=contract_data.get("vat_rate"),
            warranty_period_months=contract_data.get("warranty_period_months"),
            status="active",
            created_by_user_id=current_user.id
        )
        db.add(contract)
        await db.flush()
        
        # Сохраняем приложения если они есть
        attachments = contract_data.get("attachments", [])
        if isinstance(attachments, list):
            for attachment_data in attachments:
                if isinstance(attachment_data, dict):
                    attachment = ContractAttachment(
                        contract_id=contract.id,
                        attachment_type=attachment_data.get("type", "specification"),
                        title=attachment_data.get("title", "Без названия"),
                        number=attachment_data.get("number"),
                        is_integral_part=True
                    )
                    db.add(attachment)
        
        await db.commit()
        await db.refresh(contract)
        
        logger.info(f"Договор сохранен с ID: {contract.id}")
        
        return APIResponse(
            success=True,
            message="Договор успешно сохранен",
            data={"contract_id": contract.id}
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при сохранении договора: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении договора: {str(e)}")

@router.post("/contracts/")
async def create_contract(
    number: str = Form(...),
    contract_date: date = Form(...),
    subject: str = Form(None),
    amount: float = Form(None),
    deadline: date = Form(None),
    penalties: str = Form(None),
    customer_name: str = Form(...),
    contractor_name: str = Form(...),
    file: UploadFile = File(...),
    # Новые поля
    contract_type: str = Form(None),
    work_object_name: str = Form(None),
    cadastral_number: str = Form(None),
    construction_permit: str = Form(None),
    amount_including_vat: float = Form(None),
    vat_rate: float = Form(None),
    warranty_period_months: int = Form(None),
    status: str = Form('active'),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Загружает договор с расширенными полями.
    """
    logger.info("Начало загрузки договора: %s", number)
    # Сохраняем файл
    if not file.filename:
        raise HTTPException(status_code=400, detail="Ошибка: имя файла не указано")
    
    ext = os.path.splitext(file.filename)[1]
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info("Файл сохранён: %s", file_path)
    except Exception as e:
        logger.error("Ошибка при сохранении файла: %s", e)
        raise HTTPException(status_code=500, detail="Ошибка при сохранении файла")

    # Создаём стороны
    customer = Party(name=customer_name, role="customer")
    contractor = Party(name=contractor_name, role="contractor")
    db.add_all([customer, contractor])
    await db.flush()

    # Создаём договор с новыми полями
    contract = Contract(
        number=number, date=contract_date, subject=subject, amount=amount,
        deadline=deadline, penalties=penalties, customer_id=customer.id,
        contractor_id=contractor.id, contract_type=contract_type,
        work_object_name=work_object_name, cadastral_number=cadastral_number,
        construction_permit=construction_permit, amount_including_vat=amount_including_vat,
        vat_rate=vat_rate, warranty_period_months=warranty_period_months,
        status=status, created_by_user_id=current_user.id
    )
    db.add(contract)
    await db.flush()

    # Документ
    doc = ContractDocument(
        contract_id=contract.id, doc_type="contract",
        file_path=file_path, date=contract_date
    )
    db.add(doc)
    await db.commit()

    # OCR + NLP
    from ocr_nlp import extract_text_from_file, extract_contract_entities
    try:
        text = extract_text_from_file(file_path)
        entities = extract_contract_entities(text)
        logger.info("Обработка завершена")
    except Exception as e:
        logger.error("Ошибка: %s", e)
        text, entities = "", {}

    # Process extracted entities and save attachments if they exist
    if entities and isinstance(entities, dict) and "attachments" in entities:
        try:
            attachments_data = entities["attachments"]
            if isinstance(attachments_data, list):
                for attachment_data in attachments_data:
                    if isinstance(attachment_data, dict):
                        attachment = ContractAttachment(
                            contract_id=contract.id,
                            attachment_type=attachment_data.get("type", "specification"),
                            title=attachment_data.get("title", "Без названия"),
                            number=attachment_data.get("number"),
                            is_integral_part=True
                        )
                        db.add(attachment)
                await db.commit()
                logger.info(f"Сохранено {len(attachments_data)} приложений")
        except Exception as e:
            logger.error(f"Ошибка при сохранении приложений: {e}")
            await db.rollback()

    return JSONResponse({
        "contract_id": contract.id, "file": file_path,
        "ocr_text": text[:500], "entities": entities
    })

# CRUD endpoints for Parties - Эндпоинты для работы со сторонами договоров
@router.post("/parties/", response_model=PartyResponse)
async def create_party(
    party: PartyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new party (customer or contractor)."""
    logger.info(f"Creating party: {party.name}")
    try:
        db_party = Party(**party.dict())
        db.add(db_party)
        await db.commit()
        await db.refresh(db_party)
        logger.info(f"Party created with id: {db_party.id}")
        return db_party
    except Exception as e:
        logger.error(f"Error creating party: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error creating party")

@router.get("/parties/", response_model=List[PartyResponse])
async def get_parties(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of parties with optional filtering by role."""
    logger.info(f"Getting parties: skip={skip}, limit={limit}, role={role}")
    try:
        query = select(Party)
        if role:
            query = query.where(Party.role == role)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        parties = result.scalars().all()
        logger.info(f"Found {len(parties)} parties")
        return parties
    except Exception as e:
        logger.error(f"Error getting parties: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving parties")

@router.get("/parties/{party_id}", response_model=PartyResponse)
async def get_party(
    party_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific party by ID."""
    logger.info(f"Getting party with id: {party_id}")
    try:
        result = await db.execute(select(Party).where(Party.id == party_id))
        party = result.scalar_one_or_none()
        if not party:
            raise HTTPException(status_code=404, detail="Party not found")
        return party
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting party: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving party")

@router.put("/parties/{party_id}", response_model=PartyResponse)
async def update_party(
    party_id: int,
    party_update: PartyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a party."""
    logger.info(f"Updating party with id: {party_id}")
    try:
        result = await db.execute(select(Party).where(Party.id == party_id))
        party = result.scalar_one_or_none()
        if not party:
            raise HTTPException(status_code=404, detail="Party not found")
        
        for field, value in party_update.dict().items():
            setattr(party, field, value)
        
        await db.commit()
        await db.refresh(party)
        logger.info(f"Party updated: {party.id}")
        return party
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating party: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error updating party")

@router.delete("/parties/{party_id}")
async def delete_party(
    party_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a party."""
    logger.info(f"Deleting party with id: {party_id}")
    try:
        result = await db.execute(select(Party).where(Party.id == party_id))
        party = result.scalar_one_or_none()
        if not party:
            raise HTTPException(status_code=404, detail="Party not found")
        
        await db.delete(party)
        await db.commit()
        logger.info(f"Party deleted: {party_id}")
        return {"message": "Party deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting party: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting party")

# CRUD endpoints for Contracts
@router.get("/contracts/", response_model=List[ContractResponse])
async def get_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of contracts."""
    logger.info(f"Getting contracts: skip={skip}, limit={limit}")
    try:
        query = select(Contract).offset(skip).limit(limit)
        result = await db.execute(query)
        contracts = result.scalars().all()
        logger.info(f"Found {len(contracts)} contracts")
        return contracts
    except Exception as e:
        logger.error(f"Error getting contracts: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving contracts")

@router.get("/contracts/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific contract by ID."""
    logger.info(f"Getting contract with id: {contract_id}")
    try:
        result = await db.execute(select(Contract).where(Contract.id == contract_id))
        contract = result.scalar_one_or_none()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        return contract
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contract: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving contract")

# CRUD endpoints for Contract Documents
@router.get("/contracts/{contract_id}/documents", response_model=List[ContractDocumentResponse])
async def get_contract_documents(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all documents for a specific contract."""
    logger.info(f"Getting documents for contract: {contract_id}")
    try:
        query = select(ContractDocument).where(ContractDocument.contract_id == contract_id)
        result = await db.execute(query)
        documents = result.scalars().all()
        logger.info(f"Found {len(documents)} documents for contract {contract_id}")
        return documents
    except Exception as e:
        logger.error(f"Error getting contract documents: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving contract documents")

@router.get("/documents/", response_model=List[ContractDocumentResponse])
async def get_all_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    doc_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all documents with optional filtering by document type."""
    logger.info(f"Getting documents: skip={skip}, limit={limit}, doc_type={doc_type}")
    try:
        query = select(ContractDocument)
        if doc_type:
            query = query.where(ContractDocument.doc_type == doc_type)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        documents = result.scalars().all()
        logger.info(f"Found {len(documents)} documents")
        return documents
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving documents")

