from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class StudyGroup(Base):
    """Модель учебной группы (класса) преподавателя с инвайт-кодом."""
    __tablename__ = "study_groups"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    invite_code = Column(String(32), unique=True, index=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Связи
    teacher = relationship("User", back_populates="taught_classes")
    members = relationship(
        "GroupMember", back_populates="group", cascade="all, delete-orphan"
    )
    tests = relationship("Test", back_populates="group")

    def __repr__(self) -> str:
        return f"<StudyGroup(id={self.id}, title='{self.title}', code='{self.invite_code}')>"


class GroupMember(Base):
    """Связующая модель: Студенты в учебных группах."""
    __tablename__ = "group_members"
    __table_args__ = (
        UniqueConstraint("group_id", "student_id", name="uq_group_student"),
    )

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(
        Integer, ForeignKey("study_groups.id", ondelete="CASCADE"), nullable=False
    )
    student_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Связи
    group = relationship("StudyGroup", back_populates="members")
    student = relationship("User", back_populates="group_memberships")

    def __repr__(self) -> str:
        return f"<GroupMember(group_id={self.group_id}, student_id={self.student_id})>"
