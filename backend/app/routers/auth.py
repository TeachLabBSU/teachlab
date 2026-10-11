from typing import cast
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["Аутентификация и Авторизация"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового преподавателя или ученика."""
    # 1. Проверяем, нет ли уже пользователя с таким email
    existing_user = db.query(User).filter_by(email=user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    # 2. Хэшируем пароль с солью
    hashed_pwd = hash_password(user_data.password)

    # 3. Сохраняем в PostgreSQL
    new_user = User(
        email=user_data.email,
        password_hash=hashed_pwd,
        full_name=user_data.full_name,
        role=user_data.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход по логину и паролю",
)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Вход по email и паролю с выдачей JWT-токена."""
    user = db.query(User).filter_by(email=login_data.email).first()
    if not user or not verify_password(login_data.password, cast(str, user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    # Создаем JWT токен с полезной нагрузкой (payload)
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    return {"access_token": token, "token_type": "bearer", "user": user}


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Dependency для защиты маршрутов: проверяет JWT токен и достает пользователя из базы."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not isinstance(user_id, str):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный токен",
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен истек или подделан",
        )

    user = db.query(User).filter_by(id=int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return user


def require_tutor(current_user: User = Depends(get_current_user)) -> User:
    """Dependency: разрешает доступ только преподавателям."""
    if current_user.role not in ("tutor", "teacher", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Данное действие доступно только преподавателям",
        )
    return current_user


def require_student(current_user: User = Depends(get_current_user)) -> User:
    """Dependency: разрешает доступ только ученикам."""
    if current_user.role not in ("student", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Данное действие доступно только ученикам",
        )
    return current_user


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Получение профиля текущего пользователя",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Защищенный маршрут: возвращает профиль вошедшего пользователя."""
    return current_user
