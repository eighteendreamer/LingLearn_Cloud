from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginationParams, build_page_response
from app.common.utils import utc_now_naive
from app.core.exceptions import AuthorizationError, NotFoundError
from app.modules.notification.repository import NotificationRepository
from app.modules.notification.schemas import NotificationCreateRequest, NotificationResponse


class NotificationService:
    def __init__(self, *, repository: NotificationRepository | None = None) -> None:
        self.repository = repository or NotificationRepository()

    async def list_user_notifications(
        self,
        session: AsyncSession,
        user_id: int,
        read_status: bool | None,
        pagination: PaginationParams,
    ):
        notifications, total = await self.repository.list_user_notifications(
            session,
            user_id=user_id,
            read_status=read_status,
            offset=pagination.offset,
            limit=pagination.page_size,
        )

        items = [
            NotificationResponse(
                id=notif.id,
                notification_type=notif.notification_type,
                title=notif.title,
                body=notif.body,
                biz_type=notif.biz_type,
                biz_id=notif.biz_id,
                read_status=notif.read_status,
                read_at=notif.read_at,
                created_at=notif.created_at,
            )
            for notif in notifications
        ]

        return build_page_response(items, total, pagination)

    async def create_notification(
        self,
        session: AsyncSession,
        payload: NotificationCreateRequest,
    ) -> NotificationResponse:
        """Create a new notification (typically called by system/background jobs)"""
        async with session.begin():
            notification = await self.repository.create_notification(
                session,
                user_id=payload.user_id,
                notification_type=payload.notification_type,
                title=payload.title,
                body=payload.body,
                biz_type=payload.biz_type,
                biz_id=payload.biz_id,
                created_at=utc_now_naive(),
            )

        return NotificationResponse(
            id=notification.id,
            notification_type=notification.notification_type,
            title=notification.title,
            body=notification.body,
            biz_type=notification.biz_type,
            biz_id=notification.biz_id,
            read_status=notification.read_status,
            read_at=notification.read_at,
            created_at=notification.created_at,
        )

    async def mark_notification_as_read(
        self,
        session: AsyncSession,
        user_id: int,
        notification_id: int,
    ) -> None:
        notification = await self.repository.get_notification_by_id(session, notification_id)
        if not notification:
            raise NotFoundError(message="Notification not found.")

        if notification.user_id != user_id:
            raise AuthorizationError(message="Not your notification.")

        if notification.read_status:
            return  # Already read, idempotent

        async with session.begin():
            await self.repository.mark_as_read(session, notification_id, utc_now_naive())

    async def mark_all_as_read(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> int:
        """Mark all unread notifications as read, return count of updated notifications"""
        async with session.begin():
            count = await self.repository.mark_all_as_read(session, user_id, utc_now_naive())
        return count

    async def get_unread_count(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> int:
        return await self.repository.get_unread_count(session, user_id)
