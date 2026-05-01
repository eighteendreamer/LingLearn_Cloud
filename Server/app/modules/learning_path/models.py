from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SkillDimension(Base):
    __tablename__ = "skill_dimensions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class UserSkillSnapshot(Base):
    __tablename__ = "user_skill_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, default="assessment")
    source_ref_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    snapshot_version: Mapped[int] = mapped_column(nullable=False, default=1)
    total_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    rank_percent: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    generated_by: Mapped[str] = mapped_column(String(32), nullable=False, default="system")
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class UserSkillScore(Base):
    __tablename__ = "user_skill_scores"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user_skill_snapshots.id"), nullable=False)
    dimension_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("skill_dimensions.id"), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    percentile: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    insight: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    path_type: Mapped[str] = mapped_column(String(20), nullable=False, default="template")
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    target_role: Mapped[str | None] = mapped_column(String(64), nullable=True)
    based_on_snapshot_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user_skill_snapshots.id"), nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    is_default: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class LearningPathNode(Base):
    __tablename__ = "learning_path_nodes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    path_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("learning_paths.id"), nullable=False)
    course_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("courses.id"), nullable=True)
    node_type: Mapped[str] = mapped_column(String(32), nullable=False, default="course")
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    default_status: Mapped[str] = mapped_column(String(20), nullable=False, default="locked")
    recommended_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    estimated_minutes: Mapped[int] = mapped_column(nullable=False, default=0)
    prerequisite_node_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("learning_path_nodes.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class LearningPathNodeDimensionLink(Base):
    __tablename__ = "learning_path_node_dimension_links"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    node_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("learning_path_nodes.id"), nullable=False)
    dimension_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("skill_dimensions.id"), nullable=False)
    match_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class UserLearningPath(Base):
    __tablename__ = "user_learning_paths"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    path_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("learning_paths.id"), nullable=False)
    snapshot_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user_skill_snapshots.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    progress_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    current_node_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("learning_path_nodes.id"), nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class UserLearningPathNode(Base):
    __tablename__ = "user_learning_path_nodes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_path_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user_learning_paths.id"), nullable=False)
    node_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("learning_path_nodes.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="locked")
    progress_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    unlocked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ai_feedback: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
