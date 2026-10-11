from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr


# Схема для регистрации
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Literal["tutor", "student"]


# Схема для входа
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Схема ответа (без пароля)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Схема токена
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Схема обновления
class UserUpdate(BaseModel):
    full_name: str
    email: EmailStr
    role: Literal["tutor", "student"]
