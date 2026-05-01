from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DBSession, Pagination
from app.core.response import success
from app.modules.notification.service import NotificationService

router = APIRouter()


@router.get("/users/me/notifications")
async def list_notifications(
    current_user: CurrentUser,
    session: DBSession,
    pagination: Pagination,
    read_status: bool | None = Query(None, description="Filter by read status"),
):
    """List user notifications with optional read status filter"""
    service = NotificationService()
    result = await service.list_user_notifications(
        session,
        user_id=int(current_user.sub),
        read_status=read_status,
        pagination=pagination,
    )
    return success(data=result)


@router.get("/users/me/notifications/unread-count")
async def get_unread_count(
    current_user: CurrentUser,
    session: DBSession,
):
    """Get count of unread notifications"""
    service = NotificationService()
    count = await service.get_unread_count(session, int(current_user.sub))
    return success(data={"unread_count": count})


@router.patch("/users/me/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: CurrentUser,
    session: DBSession,
):
    """Mark a single notification as read"""
    service = NotificationService()
    await service.mark_notification_as_read(session, int(current_user.sub), notification_id)
    return success(message="Notification marked as read.")


@router.patch("/users/me/notifications/read-all")
async def mark_all_as_read(
    current_user: CurrentUser,
    session: DBSession,
):
    """Mark all unread notifications as read"""
    service = NotificationService()
    count = await service.mark_all_as_read(session, int(current_user.sub))
    return success(data={"updated_count": count}, message="All notifications marked as read.")
