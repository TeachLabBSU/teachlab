from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Subject(Base):
    """Модель учебного предмета / курса (например, Математика, Физика)."""
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Связи
    author = relationship("User", back_populates="subjects")
    topics = relationship(
        "Topic", back_populates="subject", cascade="all, delete-orphan"
    )
    tests = relationship(
        "Test", back_populates="subject", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, title='{self.title}')>"


class Topic(Base):
    """Модель темы внутри предмета."""
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    order_index = Column(Integer, default=0)

    # Связи
    subject = relationship("Subject", back_populates="topics")
    tasks = relationship(
        "Task", back_populates="topic", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Topic(id={self.id}, title='{self.title}')>"
