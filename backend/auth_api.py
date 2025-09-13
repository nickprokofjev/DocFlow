"""
Authentication API endpoints for DocFlow.

Обрабатывает все эндпоинты аутентификации:
- Регистрация новых пользователей
- Вход в систему и создание JWT токенов
- Получение информации о текущем пользователе
- Выход из системы
"""
import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional

from auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    get_user_by_email,
    get_user_by_username,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_db
)
from models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool

@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    logger.info(f"Registration attempt for email: {user.email}")
    
    # Check if user already exists
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    existing_username = await get_user_by_username(db, user.username)
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    logger.info(f"User registered successfully: {user.email}")
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        username=db_user.username,
        is_active=db_user.is_active,
        created_at=db_user.created_at.isoformat()
    )

@router.post("/login", response_model=dict)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login user and return access token."""
    logger.info(f"Login attempt for: {form_data.username}")
    
    user = await authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        logger.warning(f"Failed login attempt for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in successfully: {user.email}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at.isoformat()
        )
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat()
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout user (client should remove token)."""
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}