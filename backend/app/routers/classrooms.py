from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.logger import logger
from app.core.security import generate_invite_code
from app.models.study_group import GroupMember, StudyGroup
from app.models.user import User
from app.routers.auth import get_current_user, require_student, require_tutor
from app.schemas.classroom import (
    ClassroomCreate,
    ClassroomDetailResponse,
    ClassroomResponse,
    ClassroomUpdate,
    EnrolledStudent,
    JoinClassroomRequest,
    RegenerateInviteCodeResponse,
)

router = APIRouter(prefix="/classrooms", tags=["Управление классами (Classrooms)"])


def _generate_unique_invite_code(db: Session) -> str:
    """Генерация уникального инвайт-кода с проверкой коллизий в БД."""
    for _ in range(10):
        code = generate_invite_code(length=6)
        exists = db.query(StudyGroup).filter_by(invite_code=code).first()
        if not exists:
            return code
    # Крайний случай коллизии: увеличиваем длину до 8
    return generate_invite_code(length=8)


@router.post(
    "/",
    response_model=ClassroomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового учебного класса (Преподаватель)",
)
def create_classroom(
    classroom_data: ClassroomCreate,
    current_user: User = Depends(require_tutor),
    db: Session = Depends(get_db),
):
    """
    Создает новый класс и автоматически генерирует уникальный инвайт-код для учеников.
    Доступно только преподавателям (роль 'tutor').
    """
    logger.info(f"Преподаватель {current_user.email} создает класс: {classroom_data.title}")
    invite_code = _generate_unique_invite_code(db)

    new_classroom = StudyGroup(
        title=classroom_data.title.strip(),
        invite_code=invite_code,
        teacher_id=current_user.id,
    )
    db.add(new_classroom)
    db.commit()
    db.refresh(new_classroom)

    logger.info(f"Класс создан с ID {new_classroom.id}, инвайт-код: {invite_code}")
    return ClassroomResponse(
        id=new_classroom.id,
        title=new_classroom.title,
        invite_code=new_classroom.invite_code,
        teacher_id=new_classroom.teacher_id,
        created_at=new_classroom.created_at,
        students_count=0,
    )


@router.get(
    "/",
    response_model=List[ClassroomResponse],
    summary="Получение списка классов текущего пользователя",
)
def get_my_classrooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Возвращает список классов пользователя:
    - Для преподавателя: все созданные им классы.
    - Для ученика: все классы, в которые он вступил по инвайт-коду.
    """
    if current_user.role in ("tutor", "teacher"):
        groups = (
            db.query(StudyGroup)
            .filter_by(teacher_id=current_user.id)
            .options(joinedload(StudyGroup.members))
            .all()
        )
        return [
            ClassroomResponse(
                id=g.id,
                title=g.title,
                invite_code=g.invite_code,
                teacher_id=g.teacher_id,
                created_at=g.created_at,
                students_count=len(g.members),
            )
            for g in groups
        ]

    # Для учеников
    memberships = (
        db.query(GroupMember)
        .filter_by(student_id=current_user.id)
        .options(joinedload(GroupMember.group).joinedload(StudyGroup.members))
        .all()
    )
    result = []
    for m in memberships:
        group = m.group
        if group:
            result.append(
                ClassroomResponse(
                    id=group.id,
                    title=group.title,
                    invite_code=group.invite_code,
                    teacher_id=group.teacher_id,
                    created_at=group.created_at,
                    students_count=len(group.members),
                )
            )
    return result


@router.get(
    "/{classroom_id}",
    response_model=ClassroomDetailResponse,
    summary="Детальная информация о классе со списком учеников",
)
def get_classroom_detail(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Возвращает информацию о классе и список записавшихся учеников.
    Доступ имеют: преподаватель-владелец или ученики данного класса.
    """
    group = (
        db.query(StudyGroup)
        .filter_by(id=classroom_id)
        .options(joinedload(StudyGroup.members).joinedload(GroupMember.student))
        .first()
    )
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Класс не найден",
        )

    # Проверка прав доступа
    is_teacher = group.teacher_id == current_user.id
    is_member = any(m.student_id == current_user.id for m in group.members)
    if not is_teacher and not is_member and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к данному классу",
        )

    enrolled = [
        EnrolledStudent(
            id=m.student.id,
            full_name=m.student.full_name,
            email=m.student.email,
            joined_at=m.joined_at,
        )
        for m in group.members
        if m.student
    ]

    return ClassroomDetailResponse(
        id=group.id,
        title=group.title,
        invite_code=group.invite_code,
        teacher_id=group.teacher_id,
        created_at=group.created_at,
        students=enrolled,
    )


@router.put(
    "/{classroom_id}",
    response_model=ClassroomResponse,
    summary="Обновление названия класса (Преподаватель)",
)
def update_classroom(
    classroom_id: int,
    classroom_data: ClassroomUpdate,
    current_user: User = Depends(require_tutor),
    db: Session = Depends(get_db),
):
    """Обновляет название учебного класса. Доступно только владельцу."""
    group = db.query(StudyGroup).filter_by(id=classroom_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Класс не найден")

    if group.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь владельцем этого класса",
        )

    group.title = classroom_data.title.strip()
    db.commit()
    db.refresh(group)

    students_count = db.query(GroupMember).filter_by(group_id=group.id).count()
    return ClassroomResponse(
        id=group.id,
        title=group.title,
        invite_code=group.invite_code,
        teacher_id=group.teacher_id,
        created_at=group.created_at,
        students_count=students_count,
    )


@router.delete(
    "/{classroom_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление класса (Преподаватель)",
)
def delete_classroom(
    classroom_id: int,
    current_user: User = Depends(require_tutor),
    db: Session = Depends(get_db),
):
    """Удаляет учебный класс. Доступно только преподавателю-владельцу."""
    group = db.query(StudyGroup).filter_by(id=classroom_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Класс не найден")

    if group.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь владельцем этого класса",
        )

    db.delete(group)
    db.commit()
    logger.info(f"Класс ID {classroom_id} успешно удален преподавателем {current_user.email}")
    return None


@router.post(
    "/{classroom_id}/regenerate-code",
    response_model=RegenerateInviteCodeResponse,
    summary="Перегенерация инвайт-кода класса (Преподаватель)",
)
def regenerate_invite_code(
    classroom_id: int,
    current_user: User = Depends(require_tutor),
    db: Session = Depends(get_db),
):
    """
    Генерирует новый уникальный инвайт-код для класса (старый код аннулируется).
    Полезно, если код попал в публичный доступ.
    """
    group = db.query(StudyGroup).filter_by(id=classroom_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Класс не найден")

    if group.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь владельцем этого класса",
        )

    new_code = _generate_unique_invite_code(db)
    group.invite_code = new_code
    db.commit()

    logger.info(f"Инвайт-код класса ID {classroom_id} обновлен на {new_code}")
    return RegenerateInviteCodeResponse(
        classroom_id=group.id,
        invite_code=new_code,
    )


@router.post(
    "/join",
    response_model=ClassroomResponse,
    status_code=status.HTTP_200_OK,
    summary="Вступление в класс по инвайт-коду (Ученик)",
)
def join_classroom(
    join_data: JoinClassroomRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ученик вводит инвайт-код преподавателя и добавляется в группу.
    """
    clean_code = join_data.invite_code.strip().upper()
    group = db.query(StudyGroup).filter_by(invite_code=clean_code).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Класс с таким инвайт-кодом не найден",
        )

    if group.teacher_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Преподаватель не может вступить в свой собственный класс как ученик",
        )

    # Проверка, не состоит ли уже в этом классе
    existing_member = (
        db.query(GroupMember)
        .filter_by(group_id=group.id, student_id=current_user.id)
        .first()
    )
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже состоите в этом классе",
        )

    membership = GroupMember(group_id=group.id, student_id=current_user.id)
    db.add(membership)
    db.commit()

    students_count = db.query(GroupMember).filter_by(group_id=group.id).count()
    logger.info(
        f"Ученик {current_user.email} успешно вступил в класс '{group.title}' (ID: {group.id})"
    )

    return ClassroomResponse(
        id=group.id,
        title=group.title,
        invite_code=group.invite_code,
        teacher_id=group.teacher_id,
        created_at=group.created_at,
        students_count=students_count,
    )


@router.delete(
    "/{classroom_id}/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Исключение ученика из класса (Преподаватель)",
)
def remove_student_from_classroom(
    classroom_id: int,
    student_id: int,
    current_user: User = Depends(require_tutor),
    db: Session = Depends(get_db),
):
    """Исключает ученика из класса. Доступно только преподавателю класса."""
    group = db.query(StudyGroup).filter_by(id=classroom_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Класс не найден")

    if group.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь владельцем этого класса",
        )

    membership = (
        db.query(GroupMember)
        .filter_by(group_id=classroom_id, student_id=student_id)
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден в данном классе",
        )

    db.delete(membership)
    db.commit()
    logger.info(f"Ученик ID {student_id} удален из класса ID {classroom_id}")
    return None


@router.post(
    "/{classroom_id}/leave",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход ученика из класса (Ученик)",
)
def leave_classroom(
    classroom_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    """Позволяет ученику самостоятельно покинуть учебный класс."""
    membership = (
        db.query(GroupMember)
        .filter_by(group_id=classroom_id, student_id=current_user.id)
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вы не состоите в этом классе",
        )

    db.delete(membership)
    db.commit()
    logger.info(f"Ученик {current_user.email} покинул класс ID {classroom_id}")
    return None
