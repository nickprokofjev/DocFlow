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
    # Расширенные реквизиты организации
    ogrn: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # ОГРН
    okpo: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # ОКПО
    okved: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # ОКВЭД
    bank_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Банк
    bank_account: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Расчетный счет
    correspondent_account: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Корреспондентский счет
    bik: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # БИК
    # Руководство
    director_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # ФИО директора
    director_position: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Должность
    acting_basis: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Основание действий
    # Дополнительная информация
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Телефон
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Email
    legal_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Юридический адрес
    postal_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Почтовый адрес

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
    
    # Расширенные поля для типового договора
    contract_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Тип договора (подряда, поставки и т.д.)
    place_of_conclusion: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Место заключения
    
    # Объект работ/строительства
    work_object_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Наименование объекта
    work_object_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Адрес объекта
    cadastral_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Кадастровый номер
    land_area: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)  # Площадь участка
    construction_permit: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Разрешение на строительство
    permit_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)  # Дата разрешения
    
    # Финансовые условия
    amount_including_vat: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)  # Сумма с НДС
    vat_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)  # Сумма НДС
    vat_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)  # Ставка НДС (%)
    retention_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)  # % удержания
    payment_terms_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Срок оплаты (дни)
    
    # Сроки выполнения работ
    work_start_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)  # Дата начала работ
    work_completion_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)  # Дата окончания работ
    
    # Гарантии
    warranty_period_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Гарантийный период (месяцы)
    warranty_start_basis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Основание начала гарантии
    
    # Штрафы и неустойки
    delay_penalty_first_week: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)  # Штраф за просрочку 1-я неделя (%)
    delay_penalty_after_week: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)  # Штраф за просрочку после недели (%)
    late_payment_penalty: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)  # Штраф за просрочку оплаты (%)
    document_penalty_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)  # Штраф за документы (руб.)
    site_violation_penalty: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)  # Штраф за нарушения на стройплощадке (руб.)
    
    # Проектная документация
    project_documentation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Номера проектной документации
    
    # Статус договора
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True, default='active')  # Статус: active, completed, terminated, etc.
    
    # Дополнительные поля
    currency: Mapped[Optional[str]] = mapped_column(String, nullable=True, default='RUB')  # Валюта
    force_majeure_clause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Условия форс-мажора
    dispute_resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Порядок разрешения споров
    governing_law: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Применимое право
    
    # Метаданные
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)

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

class ContractAttachment(Base):
    """
    Модель приложений к договору (сметы, графики, спецификации и т.д.)
    """
    __tablename__ = 'contract_attachments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_id: Mapped[int] = mapped_column(Integer, ForeignKey('contracts.id'))
    attachment_type: Mapped[str] = mapped_column(String, nullable=False)  # Тип: estimate, schedule, specification, technical_map, etc.
    title: Mapped[str] = mapped_column(Text, nullable=False)  # Название приложения
    number: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Номер приложения
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Описание
    file_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Путь к файлу
    is_integral_part: Mapped[bool] = mapped_column(Boolean, default=True)  # Является ли неотъемлемой частью
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    contract = relationship('Contract', backref='attachments')

class ContractPenalty(Base):
    """
    Модель штрафов и неустоек по договору.
    """
    __tablename__ = 'contract_penalties'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_id: Mapped[int] = mapped_column(Integer, ForeignKey('contracts.id'))
    penalty_type: Mapped[str] = mapped_column(String, nullable=False)  # Тип: delay, late_payment, document_violation, site_violation, etc.
    description: Mapped[str] = mapped_column(Text, nullable=False)  # Описание нарушения
    penalty_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)  # Ставка штрафа (%)
    penalty_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)  # Фиксированная сумма штрафа
    period_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Период действия штрафа (дни)
    calculation_basis: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Основа расчета (contract_price, task_price, etc.)
    contract = relationship('Contract', backref='penalty_terms')

class ContractMilestone(Base):
    """
    Модель этапов выполнения договора.
    """
    __tablename__ = 'contract_milestones'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_id: Mapped[int] = mapped_column(Integer, ForeignKey('contracts.id'))
    milestone_name: Mapped[str] = mapped_column(String, nullable=False)  # Название этапа
    planned_start_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)  # Плановая дата начала
    planned_end_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)  # Плановая дата окончания
    actual_start_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)  # Фактическая дата начала
    actual_end_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)  # Фактическая дата окончания
    status: Mapped[str] = mapped_column(String, nullable=False, default='planned')  # Статус: planned, in_progress, completed, delayed
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Описание этапа
    milestone_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)  # Стоимость этапа
    contract = relationship('Contract', backref='milestones')

class ContactPerson(Base):
    """
    Модель контактных лиц по договору.
    """
    __tablename__ = 'contact_persons'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_id: Mapped[int] = mapped_column(Integer, ForeignKey('contracts.id'))
    party_id: Mapped[int] = mapped_column(Integer, ForeignKey('parties.id'))  # Компания, к которой относится лицо
    name: Mapped[str] = mapped_column(String, nullable=False)  # ФИО
    position: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Должность
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Телефон
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Email
    role: Mapped[str] = mapped_column(String, nullable=False)  # Роль: project_manager, technical_supervisor, authorized_representative, etc.
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)  # Основное контактное лицо
    contract = relationship('Contract', backref='contact_persons')
    party = relationship('Party', backref='contact_persons')
