from datetime import datetime

from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notification.models import Notification


class NotificationRepository:
    async def list_user_notifications(
        self,
        session: AsyncSession,
        user_id: int,
        read_status: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Notification], int]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        
        if read_status is not None:
            stmt = stmt.where(Notification.read_status == read_status)
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await session.scalar(count_stmt) or 0
        
        stmt = stmt.order_by(desc(Notification.created_at)).offset(offset).limit(limit)
        
        result = await session.execute(stmt)
        notifications = list(result.scalars().all())
        
        return notifications, total

    async def get_notification_by_id(
        self,
        session: AsyncSession,
        notification_id: int,
    ) -> Notification | None:
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_notification(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        notification_type: str,
        title: str,
        body: str,
        biz_type: str | None = None,
        biz_id: int | None = None,
        created_at: datetime,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            body=body,
            biz_type=biz_type,
            biz_id=biz_id,
            read_status=False,
            created_at=created_at,
        )
        session.add(notification)
        await session.flush()
        await session.refresh(notification)
        return notification

    async def mark_as_read(
        self,
        session: AsyncSession,
        notification_id: int,
        read_at: datetime,
    ) -> None:
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id)
            .values(read_status=True, read_at=read_at)
        )
        await session.execute(stmt)

    async def mark_all_as_read(
        self,
        session: AsyncSession,
        user_id: int,
        read_at: datetime,
    ) -> int:
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.read_status == False)
            .values(read_status=True, read_at=read_at)
        )
        result = await session.execute(stmt)
        return result.rowcount

    async def get_unread_count(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> int:
        stmt = select(func.count()).where(
            Notification.user_id == user_id,
            Notification.read_status == False,
        )
        return await session.scalar(stmt) or 0
