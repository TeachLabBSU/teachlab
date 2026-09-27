from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import cast
import jwt

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["Аутентификация и Авторизация"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового преподавателя или ученика"""
    # 1. Проверяем, нет ли уже пользователя с таким email
    existing_user = db.query(User).filter_by(email=user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    # 2. Хэшируем пароль с солью
    hashed_pwd = hash_password(user_data.password)

    # 3. Сохраняем в PostgreSQL
    new_user = User(
        email=user_data.email,
        password_hash=hashed_pwd,
        full_name=user_data.full_name,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Вход по email и паролю с выдачей JWT-токена"""
    user = db.query(User).filter_by(email=login_data.email).first()
    if not user or not verify_password(login_data.password, cast(str, user.password_hash)):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    # Создаем JWT токен с полезной нагрузкой (payload)
    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Dependency для защиты маршрутов: проверяет JWT токен и достает пользователя из базы"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not isinstance(user_id, str):
            raise HTTPException(status_code=401, detail="Невалидный токен")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Токен истек или подделан")

    user = db.query(User).filter_by(id=int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Защищенный маршрут: возвращает профиль вошедшего пользователя"""
    return current_user