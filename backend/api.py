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
from datetime import date
from uuid import uuid4
from typing import List, Optional
from schemas import (
    PartyCreate, PartyUpdate, PartyResponse,
    ContractCreate, ContractResponse, ContractWithPartiesResponse,
    ContractDocumentCreate, ContractDocumentResponse,
    UploadContractRequest, APIResponse, ErrorResponse
)
from exceptions import ValidationError, DatabaseError, FileProcessingError, NotFoundError
from models import Party, Contract, ContractDocument, DocumentLink, User
from auth import get_current_active_user, get_db

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Загружает договор, сохраняет файл, извлекает текст и сущности, сохраняет данные в БД.
    
    Основной эндпоинт для загрузки договоров с полной обработкой:
    1. Сохраняет загруженный файл на диск
    2. Создает стороны договора (заказчик/подрядчик)
    3. Создает запись договора с основными реквизитами
    4. Обрабатывает файл через OCR (распознавание текста)
    5. Анализирует текст через NLP (извлечение сущностей)
    
    Возвращает ID договора, путь к файлу, извлечённый текст и сущности.
    """
    logger.info("Начало загрузки договора: %s", number)
    # Сохраняем файл
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
    logger.info("Стороны добавлены: заказчик=%s, подрядчик=%s", customer_name, contractor_name)

    # Создаём договор
    contract = Contract(
        number=number,
        date=contract_date,
        subject=subject,
        amount=amount,
        deadline=deadline,
        penalties=penalties,
        customer_id=customer.id,
        contractor_id=contractor.id
    )
    db.add(contract)
    await db.flush()
    logger.info("Договор добавлен: id=%s", contract.id)

    # Документ
    doc = ContractDocument(
        contract_id=contract.id,
        doc_type="contract",
        file_path=file_path,
        date=contract_date
    )
    db.add(doc)
    await db.commit()
    logger.info("Документ договора сохранён: id=%s", doc.id)

    # OCR + NLP
    from ocr_nlp import extract_text_from_file, extract_contract_entities
    try:
        text = extract_text_from_file(file_path)
        logger.info("Текст успешно извлечён из файла (%d символов)", len(text))
    except Exception as e:
        logger.error("Ошибка OCR: %s", e)
        text = ""
    try:
        entities = extract_contract_entities(text)
        logger.info("Сущности успешно извлечены: %s", entities)
    except Exception as e:
        logger.error("Ошибка NLP: %s", e)
        entities = {}

    return JSONResponse({
        "contract_id": contract.id,
        "file": file_path,
        "ocr_text": text[:1000],  # первые 1000 символов
        "entities": entities
    })

# Pydantic models for API requests/responses
class PartyCreate(BaseModel):
    name: str
    inn: Optional[str] = None
    kpp: Optional[str] = None
    address: Optional[str] = None
    role: str  # "customer" or "contractor"

class PartyResponse(BaseModel):
    id: int
    name: str
    inn: Optional[str]
    kpp: Optional[str]
    address: Optional[str]
    role: str
    
    class Config:
        from_attributes = True

class ContractResponse(BaseModel):
    id: int
    number: str
    date: date
    subject: Optional[str]
    amount: Optional[float]
    deadline: Optional[date]
    penalties: Optional[str]
    customer_id: int
    contractor_id: int
    
    class Config:
        from_attributes = True

class ContractDocumentResponse(BaseModel):
    id: int
    contract_id: int
    doc_type: str
    file_path: str
    date: Optional[date]
    description: Optional[str]
    
    class Config:
        from_attributes = True

# CRUD endpoints for Parties
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
