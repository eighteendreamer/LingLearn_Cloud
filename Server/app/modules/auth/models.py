from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import SoftDeleteMixin, TimestampMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uk_users_username"),
        UniqueConstraint("email", name="uk_users_email"),
        UniqueConstraint("phone", name="uk_users_phone"),
        Index("idx_users_status_created_at", "status", "created_at"),
        Index("idx_users_last_login_at", "last_login_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str] = mapped_column(String(128), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    register_source: Mapped[str] = mapped_column(String(32), nullable=False, default="password")
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    phone_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    settings = relationship("UserSettings", back_populates="user", uselist=False)


class UserRefreshToken(Base):
    __tablename__ = "user_refresh_tokens"
    __table_args__ = (
        UniqueConstraint("refresh_token_hash", name="uk_refresh_token_hash"),
        Index("idx_refresh_user_expire", "user_id", "revoked_at", "expired_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"),
        ForeignKey("users.id"),
        nullable=False,
    )
    device_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    refresh_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expired_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)

    user = relationship("User")


class PasswordResetCode(Base, TimestampMixin):
    __tablename__ = "password_reset_codes"
    __table_args__ = (
        Index("idx_password_reset_user_status", "user_id", "used_at", "expired_at"),
        Index("idx_password_reset_email_created_at", "email", "created_at"),
        Index("idx_password_reset_ip_created_at", "request_ip", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(128), nullable=False)
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    request_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    failed_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expired_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)

    user = relationship("User")
