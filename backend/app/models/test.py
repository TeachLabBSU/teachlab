from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class Test(Base):
    """Модель проверочной / контрольной работы."""
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(Integer, ForeignKey("study_groups.id", ondelete="SET NULL"), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    time_limit_minutes = Column(Integer, nullable=True)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Связи
    subject = relationship("Subject", back_populates="tests")
    group = relationship("StudyGroup", back_populates="tests")
    author = relationship("User", back_populates="tests")
    test_tasks = relationship(
        "TestTask",
        back_populates="test",
        cascade="all, delete-orphan",
        order_by="TestTask.order_index",
    )
    submissions = relationship(
        "Submission", back_populates="test", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Test(id={self.id}, title='{self.title}')>"


class TestTask(Base):
    """Связующая модель: Задачи в тесте с фиксацией порядка."""
    __tablename__ = "test_tasks"
    __table_args__ = (
        UniqueConstraint("test_id", "task_id", name="uq_test_task"),
    )

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    order_index = Column(Integer, default=0)

    # Связи
    test = relationship("Test", back_populates="test_tasks")
    task = relationship("Task", back_populates="test_tasks")

    def __repr__(self) -> str:
        return (
            f"<TestTask(test_id={self.test_id}, task_id={self.task_id}, "
            f"order={self.order_index})>"
        )
