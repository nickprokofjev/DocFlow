"""
Утилиты аутентификации для DocFlow API.

Включает обработку JWT токенов, хеширование паролей и аутентификацию пользователей.

Основные функции:
- Проверка и хеширование паролей
- Создание и проверка JWT токенов
- Получение текущего пользователя из токена
- Аутентификация по имени пользователя/email и паролю
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

from models import User
from db import SessionLocal

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие обычного пароля с его хешем.
    
    Args:
        plain_password: Обычный пароль в виде строки
        hashed_password: Хешированный пароль из базы данных
    
    Returns:
        bool: True если пароль соответствует хешу
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Генерирует безопасный хеш пароля с использованием bcrypt.
    
    Args:
        password: Обычный пароль для хеширования
    
    Returns:
        str: Хешированный пароль
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает JWT токен доступа с заданными данными.
    
    Args:
        data: Данные для включения в токен (обычно имя пользователя)
        expires_delta: Опциональное время истечения токена
    
    Returns:
        str: Подписанный JWT токен
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None

async def get_db():
    """Get database session."""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Union[User, bool]:
    """Authenticate user with username/email and password."""
    # Try to find user by email first, then by username
    user = await get_user_by_email(db, username)
    if not user:
        user = await get_user_by_username(db, username)
    
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def create_default_user(db: AsyncSession) -> User:
    """Create default admin user if none exists."""
    hashed_password = get_password_hash("admin123")
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=hashed_password,
        is_superuser=True
    )
    return user