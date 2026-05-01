from datetime import datetime

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    title: str
    body: str
    biz_type: str | None
    biz_id: int | None
    read_status: bool
    read_at: datetime | None
    created_at: datetime


class NotificationCreateRequest(BaseModel):
    user_id: int
    notification_type: str = Field(..., description="system / course / practice / achievement / reminder")
    title: str = Field(..., max_length=120)
    body: str = Field(..., max_length=1000)
    biz_type: str | None = None
    biz_id: int | None = None


class NotificationMarkReadRequest(BaseModel):
    notification_id: int
