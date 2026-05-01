from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MonthlyReport(Base):
    __tablename__ = "monthly_reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    report_month: Mapped[str] = mapped_column(String(7), nullable=False)
    assessment_snapshot_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("assessment_snapshots.id"), nullable=True)
    report_status: Mapped[str] = mapped_column(String(20), nullable=False, default="generated")
    total_learning_minutes: Mapped[int] = mapped_column(nullable=False, default=0)
    completed_courses: Mapped[int] = mapped_column(nullable=False, default=0)
    average_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    site_rank: Mapped[int | None] = mapped_column(nullable=True)
    strengths_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    improvements_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    exported_pdf_asset_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("media_assets.id"), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ReportAchievement(Base):
    __tablename__ = "report_achievements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    report_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("monthly_reports.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    color_token: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
