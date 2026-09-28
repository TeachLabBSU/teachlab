from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logger import logger
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# 1. CREATE - Создание пользователя
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Запрос на создание пользователя: {user_in.email}")
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        logger.warning(f"Ошибка: Email {user_in.email} уже занят")
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        password_hash=hash_password(user_in.password),
        role=user_in.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Пользователь создан успешно с ID: {user.id}")
    return user


# 2. READ ALL - Получение всех пользователей из БД
@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info(f"Запрос списка пользователей (skip={skip}, limit={limit})")
    users = db.query(User).offset(skip).limit(limit).all()
    return users


# 3. READ ONE - Получение одного пользователя по ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Поиск пользователя с ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Пользователь ID {user_id} не найден")
        raise HTTPException(status_code=404, detail="User not found")
    return user


# 4. UPDATE - Обновление данных пользователя
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    logger.info(f"Запрос на обновление пользователя ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Пользователь ID {user_id} для обновления не найден")
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    logger.info(f"Пользователь ID {user.id} успешно обновлен")
    return user


# 5. DELETE - Удаление пользователя
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Запрос на удаление пользователя ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Пользователь ID {user_id} не найден для удаления")
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    logger.info(f"Пользователь ID {user_id} успешно удален")
    return None