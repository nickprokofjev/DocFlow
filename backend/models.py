"""
Модели базы данных для системы DocFlow.

этот модуль определяет все модели базы данных для:
- Пользователей системы
- Сторон договоров (заказчики и подрядчики)
- Договоров с основными реквизитами
- Документов, связанных с договорами
- Связей между документами
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Numeric, Text, Boolean, DateTime
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column
from datetime import datetime
from typing import Optional
from decimal import Decimal

Base = declarative_base()

class User(Base):
    """
    Модель пользователя системы.
    """
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Party(Base):
    """
    Модель стороны договора (заказчик или подрядчик).
    """
    __tablename__ = 'parties'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    inn: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    kpp: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=False)  # заказчик/подрядчик

class Contract(Base):
    """
    Модель договора (основные реквизиты, ссылки на стороны).
    """
    __tablename__ = 'contracts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    penalties: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('parties.id'))
    contractor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('parties.id'))
    customer = relationship('Party', foreign_keys=[customer_id])
    contractor = relationship('Party', foreign_keys=[contractor_id])

class ContractDocument(Base):
    """
    Модель документа, связанного с договором (акт, доп. соглашение, основной договор).
    """
    __tablename__ = 'contract_documents'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_id: Mapped[int] = mapped_column(Integer, ForeignKey('contracts.id'))
    doc_type: Mapped[str] = mapped_column(String, nullable=False)  # акт, доп. соглашение
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contract = relationship('Contract', backref='documents')

class DocumentLink(Base):
    """
    Модель связи между документами (например, акт привязан к договору).
    """
    __tablename__ = 'document_links'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_document_id: Mapped[int] = mapped_column(Integer, ForeignKey('contract_documents.id'))
    child_document_id: Mapped[int] = mapped_column(Integer, ForeignKey('contract_documents.id'))
    link_type: Mapped[str] = mapped_column(String, nullable=False)  # связь (акт к договору, доп к договору и т.д.)
