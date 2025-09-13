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