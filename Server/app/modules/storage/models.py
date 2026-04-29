from sqlalchemy import BigInteger, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class MediaAsset(Base, TimestampMixin):
    __tablename__ = "media_assets"
    __table_args__ = (
        UniqueConstraint("bucket_name", "object_key", name="uk_media_bucket_object"),
        Index("idx_media_asset_type_status", "asset_type", "status"),
        Index("idx_media_uploaded_by_type", "uploaded_by", "asset_type", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bucket_name: Mapped[str] = mapped_column(String(64), nullable=False)
    object_key: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    extension: Mapped[str | None] = mapped_column(String(20), nullable=True)
    asset_type: Mapped[str] = mapped_column(String(32), nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(32), nullable=False, default="minio")
    file_size: Mapped[int] = mapped_column(BigInteger(), nullable=False, default=0)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    public_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    width: Mapped[int | None] = mapped_column(nullable=True)
    height: Mapped[int | None] = mapped_column(nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(nullable=True)
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
