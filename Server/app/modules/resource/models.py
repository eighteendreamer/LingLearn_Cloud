from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import SoftDeleteMixin, TimestampMixin


class Resource(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "resources"
    __table_args__ = (
        Index("idx_resources_type_status", "resource_type", "status"),
        Index("idx_resources_category_status", "category_id", "status"),
        Index("idx_resources_status_created", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    resource_type: Mapped[str] = mapped_column(String(32), nullable=False, default="document")
    category_id: Mapped[int | None] = mapped_column(ForeignKey("content_categories.id"), nullable=True)
    file_asset_id: Mapped[int | None] = mapped_column(ForeignKey("media_assets.id"), nullable=True)
    file_size: Mapped[int] = mapped_column(BigInteger(), nullable=False, default=0)
    download_count: Mapped[int] = mapped_column(BigInteger(), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="published")


class UserResourceAccess(Base):
    __tablename__ = "user_resource_access"
    __table_args__ = (
        Index("idx_resource_access_user_time", "user_id", "accessed_at"),
        Index("idx_resource_access_resource", "resource_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"), nullable=False)
    accessed_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
