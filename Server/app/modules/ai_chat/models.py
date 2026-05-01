from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AIChatSession(Base):
    __tablename__ = "ai_chat_sessions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    session_name: Mapped[str | None] = mapped_column(String(120), nullable=True, comment="会话名称")
    scene_code: Mapped[str] = mapped_column(String(32), nullable=False, default="study_assistant", comment="场景编码")
    model_name: Mapped[str] = mapped_column(String(64), nullable=False, default="glm-4-flash", comment="模型名称")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", comment="状态")
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="摘要")
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="最后消息时间")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class AIChatMessage(Base):
    __tablename__ = "ai_chat_messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False, comment="消息角色：系统、用户、助手、工具")
    message_type: Mapped[str] = mapped_column(String(32), nullable=False, default="text", comment="消息类型")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="内容正文")
    
    # Optional metadata
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="Token数量")
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="耗时（毫秒）")
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="错误码")
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="追踪ID")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
