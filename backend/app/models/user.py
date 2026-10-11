from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """Модель пользователя платформы TeachLab."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="student")  # 'tutor', 'student', 'admin'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Связи (Relationships)
    taught_classes = relationship(
        "StudyGroup", back_populates="teacher", cascade="all, delete-orphan"
    )
    group_memberships = relationship(
        "GroupMember", back_populates="student", cascade="all, delete-orphan"
    )
    subjects = relationship(
        "Subject", back_populates="author", cascade="all, delete-orphan"
    )
    tests = relationship(
        "Test", back_populates="author", cascade="all, delete-orphan"
    )
    submissions = relationship(
        "Submission", back_populates="student", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
