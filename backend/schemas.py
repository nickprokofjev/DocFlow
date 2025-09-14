# -*- coding: utf-8 -*-
"""
Pydantic schemas for DocFlow API request/response validation.

Defines data structures for:
- Contract parties (customers/contractors)
- Contracts with main attributes
- Documents and their relationships
- API responses with error handling

Includes validation for:
- Tax numbers (INN/KPP) for organizations
- Dates and deadlines
- Party roles and document types
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date as Date
import re

class PartyCreate(BaseModel):
    """
    Schema for creating a new contract party.
    Supports validation of INN (10 or 12 digits) and KPP (9 digits).
    """
    name: str = Field(..., min_length=1, max_length=500, description="Party name")
    inn: Optional[str] = Field(None, min_length=10, max_length=12, description="Tax identification number")
    kpp: Optional[str] = Field(None, min_length=9, max_length=9, description="Tax registration code")
    address: Optional[str] = Field(None, max_length=1000, description="Address")
    role: str = Field(..., description="Party role: customer or contractor")
    
    # Расширенные реквизиты организации
    ogrn: Optional[str] = Field(None, description="ОГРН")
    okpo: Optional[str] = Field(None, description="ОКПО")
    okved: Optional[str] = Field(None, description="ОКВЭД")
    bank_name: Optional[str] = Field(None, description="Название банка")
    bank_account: Optional[str] = Field(None, description="Расчетный счет")
    correspondent_account: Optional[str] = Field(None, description="Корреспондентский счет")
    bik: Optional[str] = Field(None, description="БИК")
    
    # Руководство
    director_name: Optional[str] = Field(None, description="ФИО директора")
    director_position: Optional[str] = Field(None, description="Должность директора")
    acting_basis: Optional[str] = Field(None, description="Основание действий")
    
    # Контактная информация
    phone: Optional[str] = Field(None, description="Телефон")
    email: Optional[str] = Field(None, description="Email")
    legal_address: Optional[str] = Field(None, description="Юридический адрес")
    postal_address: Optional[str] = Field(None, description="Почтовый адрес")
    
    @validator('role')
    def validate_role(cls, v):
        """Validates that role is either customer or contractor."""
        if v not in ['customer', 'contractor']:
            raise ValueError('Role must be either "customer" or "contractor"')
        return v
    
    @validator('inn')
    def validate_inn(cls, v):
        """Validates INN format (10 or 12 digits)."""
        if v is not None:
            # Remove spaces and validate INN format
            v = re.sub(r'\s+', '', v)
            if not re.match(r'^\d{10}$|^\d{12}$', v):
                raise ValueError('INN must contain 10 or 12 digits')
        return v
    
    @validator('kpp')
    def validate_kpp(cls, v):
        """Validates KPP format (9 digits)."""
        if v is not None:
            # Remove spaces and validate KPP format
            v = re.sub(r'\s+', '', v)
            if not re.match(r'^\d{9}$', v):
                raise ValueError('KPP must contain 9 digits')
        return v

class PartyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    inn: Optional[str] = Field(None, min_length=10, max_length=12)
    kpp: Optional[str] = Field(None, min_length=9, max_length=9)
    address: Optional[str] = Field(None, max_length=1000)
    role: Optional[str] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None and v not in ['customer', 'contractor']:
            raise ValueError('Role must be either "customer" or "contractor"')
        return v

class PartyResponse(BaseModel):
    id: int
    name: str
    inn: Optional[str]
    kpp: Optional[str]
    address: Optional[str]
    role: str
    
    # Расширенные реквизиты
    ogrn: Optional[str] = None
    okpo: Optional[str] = None
    okved: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    correspondent_account: Optional[str] = None
    bik: Optional[str] = None
    
    # Руководство
    director_name: Optional[str] = None
    director_position: Optional[str] = None
    acting_basis: Optional[str] = None
    
    # Контактная информация
    phone: Optional[str] = None
    email: Optional[str] = None
    legal_address: Optional[str] = None
    postal_address: Optional[str] = None
    
    class Config:
        from_attributes = True

class ContractCreate(BaseModel):
    number: str = Field(..., min_length=1, max_length=100, description="Contract number")
    date: Date = Field(..., description="Contract date")
    subject: Optional[str] = Field(None, max_length=2000, description="Contract subject")
    amount: Optional[float] = Field(None, gt=0, description="Contract amount")
    deadline: Optional[Date] = Field(None, description="Contract deadline")
    penalties: Optional[str] = Field(None, max_length=2000, description="Penalty terms")
    customer_id: int = Field(..., gt=0, description="Customer party ID")
    contractor_id: int = Field(..., gt=0, description="Contractor party ID")
    
    # Расширенные поля
    contract_type: Optional[str] = Field(None, description="Тип договора")
    place_of_conclusion: Optional[str] = Field(None, description="Место заключения")
    
    # Объект работ
    work_object_name: Optional[str] = Field(None, description="Наименование объекта")
    work_object_address: Optional[str] = Field(None, description="Адрес объекта")
    cadastral_number: Optional[str] = Field(None, description="Кадастровый номер")
    land_area: Optional[float] = Field(None, description="Площадь участка")
    construction_permit: Optional[str] = Field(None, description="Разрешение на строительство")
    permit_date: Optional[Date] = Field(None, description="Дата разрешения")
    
    # Финансовые условия
    amount_including_vat: Optional[float] = Field(None, description="Сумма с НДС")
    vat_amount: Optional[float] = Field(None, description="Сумма НДС")
    vat_rate: Optional[float] = Field(None, description="Ставка НДС (%)")
    retention_percentage: Optional[float] = Field(None, description="% удержания")
    payment_terms_days: Optional[int] = Field(None, description="Срок оплаты (дни)")
    
    # Сроки
    work_start_date: Optional[Date] = Field(None, description="Дата начала работ")
    work_completion_date: Optional[Date] = Field(None, description="Дата окончания работ")
    
    # Гарантии
    warranty_period_months: Optional[int] = Field(None, description="Гарантийный период (месяцы)")
    warranty_start_basis: Optional[str] = Field(None, description="Основание начала гарантии")
    
    # Штрафы
    delay_penalty_first_week: Optional[float] = Field(None, description="Штраф за просрочку 1-я неделя (%)")
    delay_penalty_after_week: Optional[float] = Field(None, description="Штраф за просрочку после недели (%)")
    late_payment_penalty: Optional[float] = Field(None, description="Штраф за просрочку оплаты (%)")
    document_penalty_amount: Optional[float] = Field(None, description="Штраф за документы (руб.)")
    site_violation_penalty: Optional[float] = Field(None, description="Штраф за нарушения на стройплощадке (руб.)")
    
    # Прочее
    project_documentation: Optional[str] = Field(None, description="Проектная документация")
    status: Optional[str] = Field('active', description="Статус договора")
    currency: Optional[str] = Field('RUB', description="Валюта")
    
    @validator('deadline')
    def validate_deadline(cls, v, values):
        if v is not None and 'date' in values and v < values['date']:
            raise ValueError('Deadline cannot be before contract date')
        return v
    
    @validator('contractor_id')
    def validate_different_parties(cls, v, values):
        if 'customer_id' in values and v == values['customer_id']:
            raise ValueError('Customer and contractor must be different parties')
        return v

class ContractResponse(BaseModel):
    id: int
    number: str
    date: Date
    subject: Optional[str]
    amount: Optional[float]
    deadline: Optional[Date]
    penalties: Optional[str]
    customer_id: int
    contractor_id: int
    
    # Расширенные поля
    contract_type: Optional[str] = None
    place_of_conclusion: Optional[str] = None
    
    # Объект работ
    work_object_name: Optional[str] = None
    work_object_address: Optional[str] = None
    cadastral_number: Optional[str] = None
    land_area: Optional[float] = None
    construction_permit: Optional[str] = None
    permit_date: Optional[Date] = None
    
    # Финансовые условия
    amount_including_vat: Optional[float] = None
    vat_amount: Optional[float] = None
    vat_rate: Optional[float] = None
    retention_percentage: Optional[float] = None
    payment_terms_days: Optional[int] = None
    
    # Сроки
    work_start_date: Optional[Date] = None
    work_completion_date: Optional[Date] = None
    
    # Гарантии
    warranty_period_months: Optional[int] = None
    warranty_start_basis: Optional[str] = None
    
    # Штрафы
    delay_penalty_first_week: Optional[float] = None
    delay_penalty_after_week: Optional[float] = None
    late_payment_penalty: Optional[float] = None
    document_penalty_amount: Optional[float] = None
    site_violation_penalty: Optional[float] = None
    
    # Прочее
    project_documentation: Optional[str] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    
    # Метаданные
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True

class ContractWithPartiesResponse(ContractResponse):
    customer: PartyResponse
    contractor: PartyResponse

class ContractDocumentCreate(BaseModel):
    contract_id: int = Field(..., gt=0, description="Contract ID")
    doc_type: str = Field(..., description="Document type")
    date: Optional[Date] = Field(None, description="Document date")
    description: Optional[str] = Field(None, max_length=2000, description="Document description")
    
    @validator('doc_type')
    def validate_doc_type(cls, v):
        allowed_types = ['contract', 'act', 'addendum', 'supplement']
        if v not in allowed_types:
            raise ValueError(f'Document type must be one of: {", ".join(allowed_types)}')
        return v

class ContractDocumentResponse(BaseModel):
    id: int
    contract_id: int
    doc_type: str
    file_path: str
    date: Optional[Date]
    description: Optional[str]
    
    class Config:
        from_attributes = True

class DocumentLinkCreate(BaseModel):
    parent_document_id: int = Field(..., gt=0)
    child_document_id: int = Field(..., gt=0)
    link_type: str = Field(..., max_length=100)
    
    @validator('child_document_id')
    def validate_different_documents(cls, v, values):
        if 'parent_document_id' in values and v == values['parent_document_id']:
            raise ValueError('Parent and child documents must be different')
        return v

class DocumentLinkResponse(BaseModel):
    id: int
    parent_document_id: int
    child_document_id: int
    link_type: str
    
    class Config:
        from_attributes = True

class UploadContractRequest(BaseModel):
    number: str = Field(..., min_length=1, max_length=100)
    contract_date: Date
    subject: Optional[str] = Field(None, max_length=2000)
    amount: Optional[float] = Field(None, gt=0)
    deadline: Optional[Date] = None
    penalties: Optional[str] = Field(None, max_length=2000)
    customer_name: str = Field(..., min_length=1, max_length=500)
    contractor_name: str = Field(..., min_length=1, max_length=500)

class APIResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None

# Новые схемы для дополнительных моделей

class ContractAttachmentCreate(BaseModel):
    contract_id: int = Field(..., gt=0, description="ID договора")
    attachment_type: str = Field(..., description="Тип приложения")
    title: str = Field(..., description="Название")
    number: Optional[str] = Field(None, description="Номер")
    description: Optional[str] = Field(None, description="Описание")
    is_integral_part: bool = Field(True, description="Неотъемлемая часть")
    
    @validator('attachment_type')
    def validate_attachment_type(cls, v):
        allowed_types = ['estimate', 'schedule', 'specification', 'technical_map', 'consent_form', 'material_protocol']
        if v not in allowed_types:
            raise ValueError(f'Attachment type must be one of: {", ".join(allowed_types)}')
        return v

class ContractAttachmentResponse(BaseModel):
    id: int
    contract_id: int
    attachment_type: str
    title: str
    number: Optional[str]
    description: Optional[str]
    file_path: Optional[str]
    is_integral_part: bool
    created_at: str
    
    class Config:
        from_attributes = True

class ContractPenaltyCreate(BaseModel):
    contract_id: int = Field(..., gt=0, description="ID договора")
    penalty_type: str = Field(..., description="Тип штрафа")
    description: str = Field(..., description="Описание")
    penalty_rate: Optional[float] = Field(None, description="Ставка (%)")
    penalty_amount: Optional[float] = Field(None, description="Фиксированная сумма")
    period_days: Optional[int] = Field(None, description="Период (дни)")
    calculation_basis: Optional[str] = Field(None, description="Основа расчета")
    
    @validator('penalty_type')
    def validate_penalty_type(cls, v):
        allowed_types = ['delay', 'late_payment', 'document_violation', 'site_violation', 'non_appearance']
        if v not in allowed_types:
            raise ValueError(f'Penalty type must be one of: {", ".join(allowed_types)}')
        return v

class ContractPenaltyResponse(BaseModel):
    id: int
    contract_id: int
    penalty_type: str
    description: str
    penalty_rate: Optional[float]
    penalty_amount: Optional[float]
    period_days: Optional[int]
    calculation_basis: Optional[str]
    
    class Config:
        from_attributes = True

class ContractMilestoneCreate(BaseModel):
    contract_id: int = Field(..., gt=0, description="ID договора")
    milestone_name: str = Field(..., description="Название этапа")
    planned_start_date: Optional[Date] = Field(None, description="Плановая дата начала")
    planned_end_date: Optional[Date] = Field(None, description="Плановая дата окончания")
    description: Optional[str] = Field(None, description="Описание")
    milestone_amount: Optional[float] = Field(None, description="Стоимость")
    status: Optional[str] = Field('planned', description="Статус")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['planned', 'in_progress', 'completed', 'delayed']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

class ContractMilestoneResponse(BaseModel):
    id: int
    contract_id: int
    milestone_name: str
    planned_start_date: Optional[Date]
    planned_end_date: Optional[Date]
    actual_start_date: Optional[Date]
    actual_end_date: Optional[Date]
    status: str
    description: Optional[str]
    milestone_amount: Optional[float]
    
    class Config:
        from_attributes = True

class ContactPersonCreate(BaseModel):
    contract_id: int = Field(..., gt=0, description="ID договора")
    party_id: int = Field(..., gt=0, description="ID компании")
    name: str = Field(..., description="ФИО")
    position: Optional[str] = Field(None, description="Должность")
    phone: Optional[str] = Field(None, description="Телефон")
    email: Optional[str] = Field(None, description="Email")
    role: str = Field(..., description="Роль")
    is_primary: bool = Field(False, description="Основное лицо")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['project_manager', 'technical_supervisor', 'authorized_representative', 'financial_manager']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v

class ContactPersonResponse(BaseModel):
    id: int
    contract_id: int
    party_id: int
    name: str
    position: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    role: str
    is_primary: bool
    
    class Config:
        from_attributes = True

# Расширенная схема для загрузки договора
class ExtendedContractUploadRequest(BaseModel):
    # Основные поля
    number: str = Field(..., min_length=1, max_length=100)
    contract_date: Date
    subject: Optional[str] = Field(None, max_length=2000)
    amount: Optional[float] = Field(None, gt=0)
    deadline: Optional[Date] = None
    penalties: Optional[str] = Field(None, max_length=2000)
    customer_name: str = Field(..., min_length=1, max_length=500)
    contractor_name: str = Field(..., min_length=1, max_length=500)
    
    # Объект работ
    work_object_name: Optional[str] = None
    work_object_address: Optional[str] = None
    cadastral_number: Optional[str] = None
    construction_permit: Optional[str] = None
    
    # Финансовые условия
    vat_rate: Optional[float] = None
    retention_percentage: Optional[float] = None
    payment_terms_days: Optional[int] = None
    
    # Гарантии
    warranty_period_months: Optional[int] = None