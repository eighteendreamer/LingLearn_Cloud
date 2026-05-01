from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import SoftDeleteMixin, TimestampMixin


class Course(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "courses"
    __table_args__ = (
        Index("idx_courses_category_status", "category_id", "status"),
        Index("idx_courses_instructor_status", "instructor_id", "status"),
        Index("idx_courses_status_created", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("content_categories.id"), nullable=True)
    cover_asset_id: Mapped[int | None] = mapped_column(ForeignKey("media_assets.id"), nullable=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="beginner")
    duration_minutes: Mapped[int] = mapped_column(nullable=False, default=0)
    lesson_count: Mapped[int] = mapped_column(nullable=False, default=0)
    enrollment_count: Mapped[int] = mapped_column(BigInteger(), nullable=False, default=0)
    rating: Mapped[float] = mapped_column(nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")


class CourseLesson(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "course_lessons"
    __table_args__ = (
        Index("idx_lessons_course_order", "course_id", "sort_order"),
        Index("idx_lessons_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_item_id: Mapped[int | None] = mapped_column(ForeignKey("content_items.id"), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(nullable=False, default=0)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    is_free: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="published")


class UserCourseEnrollment(Base, TimestampMixin):
    __tablename__ = "user_course_enrollments"
    __table_args__ = (
        Index("idx_enrollments_user_enrolled", "user_id", "enrolled_at"),
        Index("idx_enrollments_course_user", "course_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    progress_percent: Mapped[float] = mapped_column(nullable=False, default=0.0)
    completed_lessons: Mapped[int] = mapped_column(nullable=False, default=0)
    last_lesson_id: Mapped[int | None] = mapped_column(ForeignKey("course_lessons.id"), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)


class UserLessonProgress(Base, TimestampMixin):
    __tablename__ = "user_lesson_progress"
    __table_args__ = (
        Index("idx_lesson_progress_user_lesson", "user_id", "lesson_id"),
        Index("idx_lesson_progress_enrollment", "enrollment_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    enrollment_id: Mapped[int] = mapped_column(ForeignKey("user_course_enrollments.id"), nullable=False)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("course_lessons.id"), nullable=False)
    progress_percent: Mapped[float] = mapped_column(nullable=False, default=0.0)
    watch_seconds: Mapped[int] = mapped_column(nullable=False, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
