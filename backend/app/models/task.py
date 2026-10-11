from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

# Универсальный тип для JSON/JSONB с поддержкой PostgreSQL и SQLite
JSONType = JSON().with_variant(JSONB, "postgresql")


class Task(Base):
    """Модель задания из банка задач с поддержкой LaTeX и автопроверки."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    parent_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    task_type = Column(
        String(50), nullable=False
    )  # 'single_choice', 'numeric', 'code', 'open_answer'
    difficulty = Column(String(20), default="medium")  # 'easy', 'medium', 'hard'
    points = Column(Integer, default=1)
    content = Column(JSONType, nullable=False)
    validation_schema = Column(JSONType, nullable=False)
    is_ai_generated = Column(Boolean, default=False)
    ai_metadata = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Связи
    topic = relationship("Topic", back_populates="tasks")
    parent_task = relationship(
        "Task", remote_side=[id], foreign_keys=[parent_task_id]
    )
    test_tasks = relationship(
        "TestTask", back_populates="task", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', type='{self.task_type}')>"
