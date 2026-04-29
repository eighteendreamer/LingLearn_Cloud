from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"
    __table_args__ = (
        Index("idx_profiles_display_name", "display_name"),
        Index("idx_profiles_avatar_asset_id", "avatar_asset_id"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    avatar_asset_id: Mapped[int | None] = mapped_column(nullable=True)
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(16), nullable=True)
    birthday: Mapped[date | None] = mapped_column(Date(), nullable=True)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    profession: Mapped[str | None] = mapped_column(String(64), nullable=True)
    learning_goal: Mapped[str | None] = mapped_column(String(500), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Shanghai")
    locale: Mapped[str] = mapped_column(String(16), nullable=False, default="zh-CN")
    total_learning_minutes: Mapped[int] = mapped_column(nullable=False, default=0)
    streak_days: Mapped[int] = mapped_column(nullable=False, default=0)
    followers_count: Mapped[int] = mapped_column(nullable=False, default=0)
    following_count: Mapped[int] = mapped_column(nullable=False, default=0)
    likes_received_count: Mapped[int] = mapped_column(nullable=False, default=0)
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="profile")


class UserSettings(Base, TimestampMixin):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    theme: Mapped[str] = mapped_column(String(20), nullable=False, default="light")
    language: Mapped[str] = mapped_column(String(16), nullable=False, default="zh-CN")
    daily_reminder_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    progress_notice_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    badge_notice_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    weekly_report_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    profile_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    learning_data_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="settings")


class UserFollowRelation(Base):
    __tablename__ = "user_follow_relations"
    __table_args__ = (
        UniqueConstraint("follower_user_id", "followee_user_id", name="uk_follow_relation"),
        Index("idx_followee_created_at", "followee_user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    follower_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    followee_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
