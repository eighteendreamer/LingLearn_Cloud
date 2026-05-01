from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AssessmentSnapshot(Base):
    __tablename__ = "assessment_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    assessment_type: Mapped[str] = mapped_column(String(32), nullable=False, default="weekly", comment="评估类型：日、周、月")
    period_start: Mapped[date] = mapped_column(Date, nullable=False, comment="周期开始日期")
    period_end: Mapped[date] = mapped_column(Date, nullable=False, comment="周期结束日期")
    
    # Learning metrics
    total_learning_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="累计学习分钟数")
    completed_courses: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="完成课程数")
    average_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="平均分")
    
    # Additional metrics
    rank_percent: Mapped[float | None] = mapped_column(Float, nullable=True, comment="排名百分位")
    correct_rate: Mapped[float | None] = mapped_column(Float, nullable=True, comment="正确率")
    focus_rate: Mapped[float | None] = mapped_column(Float, nullable=True, comment="专注度")
    
    # JSON metrics
    metrics_json: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="指标汇总JSON")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
