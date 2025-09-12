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
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """
    Модель пользователя системы.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Party(Base):
    """
    Модель стороны договора (заказчик или подрядчик).
    """
    __tablename__ = 'parties'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    inn = Column(String, nullable=True)
    kpp = Column(String, nullable=True)
    address = Column(String, nullable=True)
    role = Column(String, nullable=False)  # заказчик/подрядчик

class Contract(Base):
    """
    Модель договора (основные реквизиты, ссылки на стороны).
    """
    __tablename__ = 'contracts'
    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    subject = Column(Text, nullable=True)
    amount = Column(Numeric, nullable=True)
    deadline = Column(Date, nullable=True)
    penalties = Column(Text, nullable=True)
    customer_id = Column(Integer, ForeignKey('parties.id'))
    contractor_id = Column(Integer, ForeignKey('parties.id'))
    customer = relationship('Party', foreign_keys=[customer_id])
    contractor = relationship('Party', foreign_keys=[contractor_id])

class ContractDocument(Base):
    """
    Модель документа, связанного с договором (акт, доп. соглашение, основной договор).
    """
    __tablename__ = 'contract_documents'
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    doc_type = Column(String, nullable=False)  # акт, доп. соглашение
    file_path = Column(String, nullable=False)
    date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    contract = relationship('Contract', backref='documents')

class DocumentLink(Base):
    """
    Модель связи между документами (например, акт привязан к договору).
    """
    __tablename__ = 'document_links'
    id = Column(Integer, primary_key=True)
    parent_document_id = Column(Integer, ForeignKey('contract_documents.id'))
    child_document_id = Column(Integer, ForeignKey('contract_documents.id'))
    link_type = Column(String, nullable=False)  # связь (акт к договору, доп к договору и т.д.)
