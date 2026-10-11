from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class ClassroomCreate(BaseModel):
    """Схема создания учебного класса."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название учебной группы/класса",
    )


class ClassroomUpdate(BaseModel):
    """Схема обновления данных класса."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Новое название учебной группы/класса",
    )


class EnrolledStudent(BaseModel):
    """Краткая информация об ученике, состоящем в классе."""
    id: int
    full_name: str
    email: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClassroomResponse(BaseModel):
    """Базовый ответ с информацией о классе."""
    id: int
    title: str
    invite_code: str
    teacher_id: int
    created_at: datetime
    students_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ClassroomDetailResponse(BaseModel):
    """Детальная информация о классе со списком учеников."""
    id: int
    title: str
    invite_code: str
    teacher_id: int
    created_at: datetime
    students: List[EnrolledStudent] = []

    model_config = ConfigDict(from_attributes=True)


class JoinClassroomRequest(BaseModel):
    """Запрос на вступление в класс по инвайт-коду."""
    invite_code: str = Field(
        ...,
        min_length=4,
        max_length=32,
        description="Уникальный инвайт-код класса",
    )


class RegenerateInviteCodeResponse(BaseModel):
    """Ответ при генерации нового инвайт-кода."""
    classroom_id: int
    invite_code: str
    message: str = "Инвайт-код успешно обновлен"
