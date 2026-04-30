from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class UserCategoryInterestProfile(Base, TimestampMixin):
    __tablename__ = "user_category_interest_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", "category_id", name="uk_user_category_interest"),
        Index("idx_user_category_interest_score", "user_id", "interest_score", "updated_at"),
        Index("idx_category_interest_category_score", "category_id", "interest_score"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("content_categories.id"), nullable=False)
    interest_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    watch_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    like_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    favorite_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    comment_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    share_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    complete_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    negative_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    last_interaction_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)


class UserTagInterestProfile(Base, TimestampMixin):
    __tablename__ = "user_tag_interest_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", "tag_id", name="uk_user_tag_interest"),
        Index("idx_user_tag_interest_score", "user_id", "interest_score", "updated_at"),
        Index("idx_tag_interest_tag_score", "tag_id", "interest_score"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), nullable=False)
    interest_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    watch_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    like_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    favorite_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    comment_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    share_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    complete_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    negative_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    last_interaction_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)


class UserAuthorInterestProfile(Base, TimestampMixin):
    __tablename__ = "user_author_interest_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", "author_id", name="uk_user_author_interest"),
        Index("idx_user_author_interest_score", "user_id", "interest_score", "updated_at"),
        Index("idx_author_interest_author_score", "author_id", "interest_score"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    interest_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    watch_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    like_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    favorite_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    comment_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    share_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    complete_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    negative_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    last_interaction_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)


class ContentRecommendationImpression(Base, TimestampMixin):
    __tablename__ = "content_recommendation_impressions"
    __table_args__ = (
        Index("idx_reco_impression_user_scene_time", "user_id", "scene_code", "shown_at"),
        Index("idx_reco_impression_content_time", "content_item_id", "shown_at"),
        Index("idx_reco_impression_session_pos", "session_id", "position_no"),
        Index("idx_reco_impression_recall_source", "recall_source", "shown_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content_item_id: Mapped[int] = mapped_column(ForeignKey("content_items.id"), nullable=False)
    scene_code: Mapped[str] = mapped_column(String(32), nullable=False, default="for_you")
    recommend_type: Mapped[str] = mapped_column(String(32), nullable=False, default="for_you")
    recall_source: Mapped[str] = mapped_column(String(32), nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    position_no: Mapped[int] = mapped_column(nullable=False, default=0)
    rank_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    shown_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())
    clicked_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    watch_seconds: Mapped[int] = mapped_column(nullable=False, default=0)
    watch_progress: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    completed: Mapped[bool] = mapped_column(nullable=False, default=False)
    liked: Mapped[bool] = mapped_column(nullable=False, default=False)
    favorited: Mapped[bool] = mapped_column(nullable=False, default=False)
    commented: Mapped[bool] = mapped_column(nullable=False, default=False)
    shared: Mapped[bool] = mapped_column(nullable=False, default=False)
