from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response

from app.api.deps import CurrentUser, DBSession, OptionalCurrentUser, Pagination
from app.core.response import success
from app.modules.content.schemas import (
    ContentCommentCreateRequest,
    ContentCreateRequest,
    ContentInteractionBatchSyncRequest,
    ContentShareRequest,
    ContentUpdateRequest,
    ContentWatchProgressRequest,
    FeedQueryParams,
)
from app.modules.content.service import ContentService
from app.modules.quiz.service import QuizService

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


@contents_router.get("/{content_id}/stream.m3u8", include_in_schema=False)
async def get_content_hls_manifest(
    content_id: int,
    session: DBSession,
):
    service = ContentService()
    manifest = await service.get_hls_manifest(session, content_id=content_id)
    return Response(content=manifest, media_type="application/vnd.apple.mpegurl")


@contents_router.get("/{content_id}/quizzes")
async def list_content_quizzes(
    content_id: int,
    session: DBSession,
    current_user: OptionalCurrentUser,
):
    service = QuizService()
    data = await service.list_content_quizzes(
        session,
        content_id=content_id,
        viewer_user_id=int(current_user.sub) if current_user is not None else None,
    )
    return success(data=[item.model_dump(mode="json") for item in data])


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


@contents_router.post("/{content_id}/like")
async def like_content(
    content_id: int,
    session: DBSession,
    current_user: CurrentUser,
):
    service = ContentService()
    data = await service.like_content(session, content_id=content_id, user_id=int(current_user.sub))
    return success(data=data.model_dump(mode="json"))


@contents_router.delete("/{content_id}/like")
async def unlike_content(
    content_id: int,
    session: DBSession,
    current_user: CurrentUser,
):
    service = ContentService()
    data = await service.unlike_content(session, content_id=content_id, user_id=int(current_user.sub))
    return success(data=data.model_dump(mode="json"))


@contents_router.post("/{content_id}/favorite")
async def favorite_content(
    content_id: int,
    session: DBSession,
    current_user: CurrentUser,
):
    service = ContentService()
    data = await service.favorite_content(session, content_id=content_id, user_id=int(current_user.sub))
    return success(data=data.model_dump(mode="json"))


@contents_router.delete("/{content_id}/favorite")
async def unfavorite_content(
    content_id: int,
    session: DBSession,
    current_user: CurrentUser,
):
    service = ContentService()
    data = await service.unfavorite_content(session, content_id=content_id, user_id=int(current_user.sub))
    return success(data=data.model_dump(mode="json"))


@contents_router.post("/{content_id}/share")
async def share_content(
    content_id: int,
    payload: ContentShareRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = ContentService()
    data = await service.share_content(
        session,
        content_id=content_id,
        user_id=int(current_user.sub),
        payload=payload,
    )
    return success(data=data.model_dump(mode="json"))


@contents_router.get("/{content_id}/comments")
async def list_comments(
    content_id: int,
    session: DBSession,
    pagination: Pagination,
):
    service = ContentService()
    data = await service.list_comments(session, content_id=content_id, pagination=pagination)
    return success(data=data.model_dump(mode="json"))


@contents_router.post("/{content_id}/comments")
async def create_comment(
    content_id: int,
    payload: ContentCommentCreateRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = ContentService()
    data = await service.create_comment(
        session,
        content_id=content_id,
        user_id=int(current_user.sub),
        payload=payload,
    )
    return success(data=data.model_dump(mode="json"))


@contents_router.post("/{content_id}/watch-progress")
async def report_watch_progress(
    content_id: int,
    payload: ContentWatchProgressRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = ContentService()
    data = await service.report_watch_progress(
        session,
        content_id=content_id,
        user_id=int(current_user.sub),
        payload=payload,
    )
    return success(data=data.model_dump(mode="json"))


@contents_router.post("/interactions/batch-sync")
async def sync_content_interactions_batch(
    payload: ContentInteractionBatchSyncRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = ContentService()
    data = await service.sync_interactions_batch(
        session,
        user_id=int(current_user.sub),
        payload=payload,
    )
    return success(data=data.model_dump(mode="json"))
