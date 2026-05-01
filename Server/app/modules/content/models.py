from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import SoftDeleteMixin, TimestampMixin


class ContentCategory(Base, TimestampMixin):
    __tablename__ = "content_categories"
    __table_args__ = (
        UniqueConstraint("slug", name="uk_categories_slug"),
        UniqueConstraint("name", name="uk_categories_name"),
        Index("idx_categories_parent_sort", "parent_id", "sort_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("content_categories.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("name", name="uk_tags_name"),
        UniqueConstraint("slug", name="uk_tags_slug"),
        Index("idx_tags_type_use_count", "tag_type", "use_count"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    tag_type: Mapped[str] = mapped_column(String(20), nullable=False, default="topic")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    use_count: Mapped[int] = mapped_column(BigInteger(), nullable=False, default=0)


class ContentItem(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "content_items"
    __table_args__ = (
        UniqueConstraint("bvid", name="uk_content_items_bvid"),
        Index("idx_content_author_status_publish", "author_id", "publish_status", "published_at"),
        Index("idx_content_category_status_publish", "category_id", "publish_status", "published_at"),
        Index("idx_content_type_status_publish", "content_type", "publish_status", "published_at"),
        Index("idx_content_hot_score", "publish_status", "hot_score", "published_at"),
        Index("idx_content_audit_status", "audit_status", "publish_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("content_categories.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_type: Mapped[str] = mapped_column(String(32), nullable=False, default="short_video")
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, default="original")
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="public")
    audit_status: Mapped[str] = mapped_column(String(20), nullable=False, default="approved")
    publish_status: Mapped[str] = mapped_column(String(20), nullable=False, default="published")
    cover_asset_id: Mapped[int | None] = mapped_column(ForeignKey("media_assets.id"), nullable=True)
    primary_media_asset_id: Mapped[int | None] = mapped_column(
        ForeignKey("media_assets.id"),
        nullable=True,
    )
    external_video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bvid: Mapped[str | None] = mapped_column(String(64), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(nullable=True)
    hashtags_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    allow_comment: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_duet: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_quiz: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    quiz_count: Mapped[int] = mapped_column(nullable=False, default=0)
    views_count: Mapped[int] = mapped_column(BigInteger(), nullable=False, default=0)
    likes_count: Mapped[int] = mapped_column(BigInteger(), nullable=False, default=0)
    comments_count: Mapped[int] = mapped_column(BigInteger(), nullable=False, default=0)
    favorites_count: Mapped[int] = mapped_column(BigInteger(), nullable=False, default=0)
    shares_count: Mapped[int] = mapped_column(BigInteger(), nullable=False, default=0)
    hot_score: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)


class ContentItemTag(Base):
    __tablename__ = "content_item_tags"
    __table_args__ = (Index("idx_content_item_tags_tag_id", "tag_id", "content_item_id"),)

    content_item_id: Mapped[int] = mapped_column(
        ForeignKey("content_items.id"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=func.now(),
    )


class ContentLike(Base):
    __tablename__ = "content_likes"
    __table_args__ = (
        UniqueConstraint("user_id", "content_item_id", name="uk_content_like"),
        Index("idx_likes_content_created", "content_item_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content_item_id: Mapped[int] = mapped_column(ForeignKey("content_items.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())


class ContentFavorite(Base):
    __tablename__ = "content_favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "content_item_id", name="uk_content_favorite"),
        Index("idx_favorites_content_created", "content_item_id", "created_at"),
        Index("idx_favorites_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content_item_id: Mapped[int] = mapped_column(ForeignKey("content_items.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())


class ContentComment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "content_comments"
    __table_args__ = (
        Index("idx_comments_content_parent_created", "content_item_id", "parent_id", "created_at"),
        Index("idx_comments_root_created", "root_id", "created_at"),
        Index("idx_comments_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content_item_id: Mapped[int] = mapped_column(ForeignKey("content_items.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("content_comments.id"), nullable=True)
    root_id: Mapped[int | None] = mapped_column(ForeignKey("content_comments.id"), nullable=True)
    reply_to_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    content: Mapped[str] = mapped_column(String(1000), nullable=False)
    like_count: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")


class ContentShare(Base):
    __tablename__ = "content_shares"
    __table_args__ = (
        Index("idx_shares_content_created", "content_item_id", "created_at"),
        Index("idx_shares_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content_item_id: Mapped[int] = mapped_column(ForeignKey("content_items.id"), nullable=False)
    share_channel: Mapped[str] = mapped_column(String(32), nullable=False, default="internal")
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())


class ContentViewHistory(Base, TimestampMixin):
    __tablename__ = "content_view_histories"
    __table_args__ = (
        UniqueConstraint("user_id", "content_item_id", "view_date", name="uk_view_history_day"),
        Index("idx_view_history_user_last", "user_id", "last_viewed_at"),
        Index("idx_view_history_content_date", "content_item_id", "view_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content_item_id: Mapped[int] = mapped_column(ForeignKey("content_items.id"), nullable=False)
    view_date: Mapped[date] = mapped_column(nullable=False)
    view_count: Mapped[int] = mapped_column(nullable=False, default=1)
    watch_seconds: Mapped[int] = mapped_column(nullable=False, default=0)
    watch_progress: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    last_position_seconds: Mapped[int] = mapped_column(nullable=False, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    liked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    favorited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_viewed_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())


class ContentQuiz(Base, TimestampMixin):
    __tablename__ = "content_quizzes"
    __table_args__ = (
        UniqueConstraint("content_item_id", "sort_order", name="uk_content_quiz_sort"),
        Index("idx_quizzes_content_status", "content_item_id", "status", "sort_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content_item_id: Mapped[int] = mapped_column(ForeignKey("content_items.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    quiz_type: Mapped[str] = mapped_column(String(32), nullable=False, default="single_choice_poll")
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="published")
    total_votes: Mapped[int] = mapped_column(BigInteger(), nullable=False, default=0)


class ContentQuizOption(Base):
    __tablename__ = "content_quiz_options"
    __table_args__ = (
        UniqueConstraint("quiz_id", "option_order", name="uk_quiz_option_order"),
        Index("idx_quiz_options_quiz_order", "quiz_id", "option_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("content_quizzes.id"), nullable=False)
    option_text: Mapped[str] = mapped_column(String(255), nullable=False)
    option_order: Mapped[int] = mapped_column(nullable=False, default=0)
    vote_count: Mapped[int] = mapped_column(BigInteger(), nullable=False, default=0)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())


class ContentQuizAttempt(Base):
    __tablename__ = "content_quiz_attempts"
    __table_args__ = (
        UniqueConstraint("quiz_id", "user_id", name="uk_quiz_attempt_user"),
        Index("idx_quiz_attempts_user_submitted", "user_id", "submitted_at"),
        Index("idx_quiz_attempts_option_id", "selected_option_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("content_quizzes.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    selected_option_id: Mapped[int] = mapped_column(ForeignKey("content_quiz_options.id"), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())
    client_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
