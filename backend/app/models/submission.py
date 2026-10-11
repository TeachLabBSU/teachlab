from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

JSONType = JSON().with_variant(JSONB, "postgresql")


class Submission(Base):
    """Модель сдачи контрольной работы учеником."""
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(
        String(50), default="in_progress"
    )  # 'in_progress', 'submitted', 'graded'
    total_score = Column(Numeric(5, 2), default=0.0)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    submitted_at = Column(DateTime, nullable=True)

    # Связи
    test = relationship("Test", back_populates="submissions")
    student = relationship("User", back_populates="submissions")
    answers = relationship(
        "StudentAnswer", back_populates="submission", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Submission(id={self.id}, test_id={self.test_id}, "
            f"student_id={self.student_id}, status='{self.status}')>"
        )


class StudentAnswer(Base):
    """Модель ответа ученика на конкретное задание с автопроверкой и комментарием."""
    __tablename__ = "student_answers"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(
        Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False
    )
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    student_response = Column(JSONType, nullable=False)
    earned_points = Column(Numeric(5, 2), default=0.0)
    teacher_comment = Column(Text, nullable=True)

    # Связи
    submission = relationship("Submission", back_populates="answers")
    task = relationship("Task")

    def __repr__(self) -> str:
        return (
            f"<StudentAnswer(submission_id={self.submission_id}, "
            f"task_id={self.task_id}, points={self.earned_points})>"
        )
