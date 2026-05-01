from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_chat.models import AIChatMessage, AIChatSession


class AIChatRepository:
    async def list_user_sessions(
        self,
        session: AsyncSession,
        user_id: int,
        limit: int = 50,
    ) -> list[AIChatSession]:
        stmt = (
            select(AIChatSession)
            .where(AIChatSession.user_id == user_id)
            .order_by(desc(AIChatSession.updated_at))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_session_by_id(
        self,
        session: AsyncSession,
        session_id: int,
    ) -> AIChatSession | None:
        stmt = select(AIChatSession).where(AIChatSession.id == session_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_session(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        session_name: str | None,
        scene_code: str,
        model_name: str,
        created_at: datetime,
    ) -> AIChatSession:
        chat_session = AIChatSession(
            user_id=user_id,
            session_name=session_name,
            scene_code=scene_code,
            model_name=model_name,
            status="active",
            created_at=created_at,
            updated_at=created_at,
        )
        session.add(chat_session)
        await session.flush()
        await session.refresh(chat_session)
        return chat_session

    async def update_session_timestamp(
        self,
        session: AsyncSession,
        session_id: int,
        last_message_at: datetime,
    ) -> None:
        chat_session = await self.get_session_by_id(session, session_id)
        if chat_session:
            chat_session.last_message_at = last_message_at
            chat_session.updated_at = last_message_at

    async def list_session_messages(
        self,
        session: AsyncSession,
        session_id: int,
        limit: int = 100,
    ) -> list[AIChatMessage]:
        stmt = (
            select(AIChatMessage)
            .where(AIChatMessage.session_id == session_id)
            .order_by(AIChatMessage.created_at)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def create_message(
        self,
        session: AsyncSession,
        *,
        session_id: int,
        role: str,
        message_type: str,
        content: str,
        token_count: int = 0,
        latency_ms: int | None = None,
        error_code: str | None = None,
        trace_id: str | None = None,
        created_at: datetime,
    ) -> AIChatMessage:
        message = AIChatMessage(
            session_id=session_id,
            role=role,
            message_type=message_type,
            content=content,
            token_count=token_count,
            latency_ms=latency_ms,
            error_code=error_code,
            trace_id=trace_id,
            created_at=created_at,
        )
        session.add(message)
        await session.flush()
        await session.refresh(message)
        return message
