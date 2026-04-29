from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DBSession, OptionalCurrentUser, Pagination
from app.core.response import success
from app.modules.content.schemas import ContentCreateRequest, ContentUpdateRequest, FeedQueryParams
from app.modules.content.service import ContentService

contents_router = APIRouter()
feed_router = APIRouter()


@feed_router.get("/videos")
async def list_feed_videos(
    session: DBSession,
    current_user: OptionalCurrentUser,
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
    category_id: Annotated[int | None, Query(gt=0)] = None,
    recommend_type: Annotated[str, Query()] = "for_you",
):
    service = ContentService()
    data = await service.list_feed_videos(
        session,
        viewer_user_id=int(current_user.sub) if current_user is not None else None,
        query=FeedQueryParams(
            cursor=cursor,
            limit=limit,
            category_id=category_id,
            recommend_type=recommend_type,
        ),
    )
    return success(data=data.model_dump(mode="json"))


@contents_router.post("")
async def create_content(
    payload: ContentCreateRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = ContentService()
    data = await service.create_content(session, user_id=int(current_user.sub), payload=payload)
    return success(data=data.model_dump(mode="json"))


@contents_router.get("/{content_id}")
async def get_content_detail(
    content_id: int,
    session: DBSession,
    current_user: OptionalCurrentUser,
):
    service = ContentService()
    data = await service.get_content_detail(
        session,
        content_id=content_id,
        viewer_user_id=int(current_user.sub) if current_user is not None else None,
    )
    return success(data=data.model_dump(mode="json"))


@contents_router.put("/{content_id}")
async def update_content(
    content_id: int,
    payload: ContentUpdateRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = ContentService()
    data = await service.update_content(
        session,
        user_id=int(current_user.sub),
        content_id=content_id,
        payload=payload,
    )
    return success(data=data.model_dump(mode="json"))
