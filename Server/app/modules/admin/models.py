from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class AdminUser(Base, TimestampMixin):
    """管理员用户表"""

    __tablename__ = "admin_users"
    __table_args__ = (
        UniqueConstraint("username", name="uk_admin_username"),
        UniqueConstraint("email", name="uk_admin_email"),
        Index("idx_admin_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str] = mapped_column(String(128), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    real_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("admin_roles.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)

    role = relationship("AdminRole", back_populates="users")
    operation_logs = relationship("AdminOperationLog", back_populates="admin_user")


class AdminRole(Base, TimestampMixin):
    """管理员角色表"""

    __tablename__ = "admin_roles"
    __table_args__ = (
        UniqueConstraint("name", name="uk_admin_role_name"),
        Index("idx_admin_role_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    permissions: Mapped[str] = mapped_column(String(2000), nullable=False)  # JSON string
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    is_super: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    users = relationship("AdminUser", back_populates="role")


class AdminOperationLog(Base):
    """管理员操作日志表"""

    __tablename__ = "admin_operation_logs"
    __table_args__ = (
        Index("idx_admin_log_user_time", "admin_user_id", "created_at"),
        Index("idx_admin_log_module_action", "module", "action", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    admin_user_id: Mapped[int] = mapped_column(ForeignKey("admin_users.id"), nullable=False)
    module: Mapped[str] = mapped_column(String(64), nullable=False)  # user, content, category, etc.
    action: Mapped[str] = mapped_column(String(64), nullable=False)  # create, update, delete, etc.
    target_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    target_id: Mapped[int | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    request_data: Mapped[str | None] = mapped_column(String(2000), nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)

    admin_user = relationship("AdminUser", back_populates="operation_logs")
