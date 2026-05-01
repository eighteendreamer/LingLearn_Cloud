from __future__ import annotations

from datetime import datetime

from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class QuestionBank(Base, TimestampMixin):
    __tablename__ = "question_banks"
    __table_args__ = (
        Index("idx_banks_category_type_status", "category_id", "bank_type", "status"),
        Index("idx_banks_created_by", "created_by", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column("name", String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("content_categories.id"), nullable=True)
    bank_type: Mapped[str] = mapped_column(String(32), nullable=False, default="practice")
    question_count: Mapped[int] = mapped_column(nullable=False, default=0)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="mixed")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="published")
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class Question(Base, TimestampMixin):
    __tablename__ = "questions"
    __table_args__ = (
        Index("idx_questions_bank_status_difficulty", "bank_id", "status", "difficulty"),
        Index("idx_questions_course_lesson", "course_id", "lesson_id"),
        Index("idx_questions_category_type", "category_id", "question_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bank_id: Mapped[int] = mapped_column(ForeignKey("question_banks.id"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("content_categories.id"), nullable=True)
    course_id: Mapped[int | None] = mapped_column(ForeignKey("courses.id"), nullable=True)
    lesson_id: Mapped[int | None] = mapped_column(nullable=True)
    question_type: Mapped[str] = mapped_column(String(32), nullable=False, default="single_choice")
    content: Mapped[str] = mapped_column("stem", Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    correct_answer_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="published")
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)


class QuestionOption(Base):
    __tablename__ = "question_options"
    __table_args__ = (Index("idx_options_question_order", "question_id", "sort_order"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    option_key: Mapped[str] = mapped_column(String(1), nullable=False)
    content: Mapped[str] = mapped_column("option_text", Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)


class PracticeSession(Base, TimestampMixin):
    __tablename__ = "practice_sessions"
    __table_args__ = (
        Index("idx_sessions_user_created", "user_id", "created_at"),
        Index("idx_sessions_bank_user", "bank_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    bank_id: Mapped[int | None] = mapped_column(ForeignKey("question_banks.id"), nullable=True)
    session_type: Mapped[str] = mapped_column(String(32), nullable=False, default="practice")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="started")
    started_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(nullable=False, default=0)
    total_questions: Mapped[int] = mapped_column(nullable=False, default=0)
    answered_questions: Mapped[int] = mapped_column(nullable=False, default=0)
    correct_answers: Mapped[int] = mapped_column("correct_questions", nullable=False, default=0)
    earned_score: Mapped[Decimal] = mapped_column("score", Numeric(5, 2), nullable=False, default=0)


class PracticeAnswer(Base):
    __tablename__ = "practice_answers"
    __table_args__ = (
        Index("uk_practice_answer", "session_id", "question_id", unique=True),
        Index("idx_practice_answers_question_answered", "question_id", "answered_at"),
        Index("fk_practice_answers_selected_option_id", "selected_option_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("practice_sessions.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    selected_option_id: Mapped[int | None] = mapped_column(ForeignKey("question_options.id"), nullable=True)
    answer_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    earned_score: Mapped[Decimal] = mapped_column("score", Numeric(5, 2), nullable=False, default=0)
    answered_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
