from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Literal

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

# Схема ответа (без пароля!)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

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