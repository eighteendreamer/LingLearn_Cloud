from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    notification_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="通知类型")
    title: Mapped[str] = mapped_column(String(120), nullable=False, comment="标题")
    body: Mapped[str] = mapped_column(String(1000), nullable=False, comment="通知内容")
    
    # Optional link to related resource
    biz_type: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="业务类型")
    biz_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="业务ID")
    
    read_status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="已读状态")
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="已读时间")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
