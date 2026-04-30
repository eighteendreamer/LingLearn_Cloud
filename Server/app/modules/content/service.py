from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginationParams, build_page_response
from app.common.utils import utc_now_naive
from app.core.exceptions import AuthorizationError, BadRequestError, NotFoundError
from app.infra.cache.redis_client import RedisCacheClient, redis_cache_client
from app.infra.storage.service import StorageService
from app.modules.content.repository import ContentRepository
from app.modules.content.schemas import (
    ContentAuthorResponse,
    ContentCommentCreateRequest,
    ContentCategoryResponse,
    ContentInteractionBatchCommentItemRequest,
    ContentInteractionBatchFavoriteItemRequest,
    ContentInteractionBatchItemResponse,
    ContentInteractionBatchLikeItemRequest,
    ContentInteractionBatchSyncRequest,
    ContentInteractionBatchSyncResponse,
    ContentCommentListResponse,
    ContentCommentResponse,
    ContentCreateRequest,
    ContentInteractionResponse,
    ContentInteractionMutationResponse,
    ContentShareRequest,
    ContentUpdateRequest,
    ContentVideoResponse,
    ContentWatchProgressRequest,
    FeedQueryParams,
    FeedVideosResponse,
)
from app.modules.recommendation.service import RecommendationService
from app.modules.user.schemas import UserWorkListItemResponse


class ContentService:
    def __init__(
        self,
        *,
        repository: ContentRepository | None = None,
        storage_service: StorageService | None = None,
        cache_client: RedisCacheClient | None = None,
        recommendation_service: RecommendationService | None = None,
    ) -> None:
        self.repository = repository or ContentRepository()
        self.storage_service = storage_service or StorageService()
        self.cache_client = cache_client or redis_cache_client
        self.recommendation_service = recommendation_service or RecommendationService(
            content_repository=self.repository,
        )

    async def create_content(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        payload: ContentCreateRequest,
    ) -> ContentVideoResponse:
        normalized_tags = self._normalize_hashtags(payload.hashtags)

        async with session.begin():
            await self._validate_content_assets(
                session,
                user_id=user_id,
                cover_asset_id=payload.cover_asset_id,
                primary_media_asset_id=payload.primary_media_asset_id,
            )

            if payload.category_id is not None:
                category = await self.repository.get_category_by_id(session, payload.category_id)
                if category is None or category.status != "active":
                    raise BadRequestError(message="Category does not exist or is inactive.")

            tag_ids = await self._ensure_tags(session, normalized_tags)
            item = await self.repository.create_content_item(
                session,
                author_id=user_id,
                category_id=payload.category_id,
                title=payload.title.strip(),
                summary=payload.summary.strip() if payload.summary else None,
                content_type=payload.content_type.strip(),
                source_type="original",
                visibility="public",
                audit_status="approved",
                publish_status="published",
                cover_asset_id=payload.cover_asset_id,
                primary_media_asset_id=payload.primary_media_asset_id,
                duration_seconds=payload.duration_seconds,
                hashtags_json=normalized_tags or None,
                allow_comment=payload.allow_comment,
                allow_duet=payload.allow_duet,
                published_at=utc_now_naive(),
            )
            await self.repository.replace_content_tags(
                session,
                content_item_id=item.id,
                tag_ids=tag_ids,
            )
            await self.repository.increment_tag_use_count(session, tag_ids)

        detail = await self.get_content_detail(session, content_id=item.id, viewer_user_id=user_id)
        return detail

    async def get_content_detail(
        self,
        session: AsyncSession,
        *,
        content_id: int,
        viewer_user_id: int | None,
    ) -> ContentVideoResponse:
        row = await self.repository.get_content_detail_row(
            session,
            content_id=content_id,
            viewer_user_id=viewer_user_id,
            include_unpublished_for_author_id=viewer_user_id,
        )
        if row is None:
            raise NotFoundError(message="Content not found.")
        return await self._build_content_video_response(row)

    async def update_content(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        content_id: int,
        payload: ContentUpdateRequest,
    ) -> ContentVideoResponse:
        normalized_tags = self._normalize_hashtags(payload.hashtags) if payload.hashtags is not None else None
        update_values = payload.model_dump(
            exclude_none=True,
            exclude={"hashtags"},
        )
        if "title" in update_values:
            update_values["title"] = update_values["title"].strip()
        if "summary" in update_values and update_values["summary"] is not None:
            update_values["summary"] = update_values["summary"].strip()
        if normalized_tags is not None:
            update_values["hashtags_json"] = normalized_tags or None

        async with session.begin():
            item = await self.repository.get_content_item_by_id(session, content_id)
            if item is None or item.deleted_at is not None:
                raise NotFoundError(message="Content not found.")
            if item.author_id != user_id:
                raise AuthorizationError(message="You can only edit your own content.")

            if payload.category_id is not None:
                category = await self.repository.get_category_by_id(session, payload.category_id)
                if category is None or category.status != "active":
                    raise BadRequestError(message="Category does not exist or is inactive.")

            await self._validate_content_assets(
                session,
                user_id=user_id,
                cover_asset_id=payload.cover_asset_id,
                primary_media_asset_id=payload.primary_media_asset_id,
            )

            await self.repository.update_content_item(
                session,
                content_id=content_id,
                values=update_values,
            )
            if normalized_tags is not None:
                tag_ids = await self._ensure_tags(session, normalized_tags)
                await self.repository.replace_content_tags(
                    session,
                    content_item_id=content_id,
                    tag_ids=tag_ids,
                )
                await self.repository.increment_tag_use_count(session, tag_ids)

        return await self.get_content_detail(session, content_id=content_id, viewer_user_id=user_id)

    async def list_feed_videos(
        self,
        session: AsyncSession,
        *,
        viewer_user_id: int | None,
        query: FeedQueryParams,
    ) -> FeedVideosResponse:
        normalized_type = query.recommend_type.strip().lower()
        if normalized_type not in {"for_you", "following", "hot"}:
            raise BadRequestError(message="Unsupported recommend_type.")

        cursor = self._parse_cursor(query.cursor)
        if normalized_type == "for_you":
            rows, _session_id = await self.recommendation_service.list_for_you_rows(
                session,
                viewer_user_id=viewer_user_id,
                limit=query.limit + 1,
                category_id=query.category_id,
                cursor=cursor,
            )
        else:
            rows = await self.repository.list_feed_rows(
                session,
                viewer_user_id=viewer_user_id,
                limit=query.limit + 1,
                category_id=query.category_id,
                recommend_type=normalized_type,
                cursor=cursor,
            )
        has_more = len(rows) > query.limit
        trimmed = rows[: query.limit]
        items = [await self._build_content_video_response(row) for row in trimmed]
        next_cursor = None
        if has_more and trimmed:
            last_row = trimmed[-1]
            next_cursor = self._build_cursor(last_row["published_at"], last_row["id"])
        return FeedVideosResponse(list=items, next_cursor=next_cursor, has_more=has_more)

    async def list_author_works(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        pagination: PaginationParams,
    ):
        rows, total = await self.repository.list_author_works_rows(
            session,
            user_id=user_id,
            offset=pagination.offset,
            limit=pagination.page_size,
        )
        items: list[UserWorkListItemResponse] = []
        for row in rows:
            cover_url = await self.storage_service.build_access_url(
                object_key=row["cover_object_key"],
                public_url=row["cover_public_url"],
            )
            items.append(
                UserWorkListItemResponse(
                    id=row["id"],
                    title=row["title"],
                    summary=row["summary"],
                    cover_url=cover_url,
                    published_at=row["published_at"],
                )
            )
        return build_page_response(items, total, pagination)

    async def like_content(
        self,
        session: AsyncSession,
        *,
        content_id: int,
        user_id: int,
    ) -> ContentInteractionMutationResponse:
        async with session.begin():
            item = await self._require_interactable_content(session, content_id)
            existing = await self.repository.get_content_like(
                session,
                user_id=user_id,
                content_item_id=content_id,
            )
            if existing is None:
                await self.repository.create_content_like(
                    session,
                    user_id=user_id,
                    content_item_id=content_id,
                )
                await self.repository.increment_content_counters(
                    session,
                    content_id=content_id,
                    likes_delta=1,
                    hot_score_delta=1.0,
                )
                await self.repository.increment_author_likes_received(
                    session,
                    author_user_id=item.author_id,
                    delta=1,
                )
                await self.recommendation_service.record_behavior(
                    session,
                    user_id=user_id,
                    content_id=content_id,
                    event_type="like",
                )
                await self.recommendation_service.update_impression_feedback(
                    session,
                    user_id=user_id,
                    content_id=content_id,
                    liked=True,
                    clicked_at=utc_now_naive(),
                )
        return await self._build_interaction_mutation_response(session, content_id=content_id, user_id=user_id)

    async def sync_interactions_batch(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        payload: ContentInteractionBatchSyncRequest,
    ) -> ContentInteractionBatchSyncResponse:
        items: list[ContentInteractionBatchItemResponse] = []

        for item in payload.items:
            if session.in_transaction():
                await session.commit()

            if isinstance(item, ContentInteractionBatchLikeItemRequest):
                mutation = (
                    await self.like_content(session, content_id=item.content_id, user_id=user_id)
                    if item.liked
                    else await self.unlike_content(session, content_id=item.content_id, user_id=user_id)
                )
                items.append(
                    ContentInteractionBatchItemResponse(
                        client_id=item.client_id,
                        action=item.action,
                        content_id=item.content_id,
                        interaction=mutation.interaction,
                    )
                )
                if session.in_transaction():
                    await session.commit()
                continue

            if isinstance(item, ContentInteractionBatchFavoriteItemRequest):
                mutation = (
                    await self.favorite_content(session, content_id=item.content_id, user_id=user_id)
                    if item.favorited
                    else await self.unfavorite_content(session, content_id=item.content_id, user_id=user_id)
                )
                items.append(
                    ContentInteractionBatchItemResponse(
                        client_id=item.client_id,
                        action=item.action,
                        content_id=item.content_id,
                        interaction=mutation.interaction,
                    )
                )
                if session.in_transaction():
                    await session.commit()
                continue

            if isinstance(item, ContentInteractionBatchCommentItemRequest):
                comment = await self.create_comment(
                    session,
                    content_id=item.content_id,
                    user_id=user_id,
                    payload=ContentCommentCreateRequest(
                        content=item.content,
                        parent_id=item.parent_id,
                    ),
                )
                mutation = await self._build_interaction_mutation_response(
                    session,
                    content_id=item.content_id,
                    user_id=user_id,
                )
                items.append(
                    ContentInteractionBatchItemResponse(
                        client_id=item.client_id,
                        action=item.action,
                        content_id=item.content_id,
                        interaction=mutation.interaction,
                        comment=comment,
                    )
                )
                if session.in_transaction():
                    await session.commit()

        if session.in_transaction():
            await session.commit()
        return ContentInteractionBatchSyncResponse(items=items)

    async def unlike_content(
        self,
        session: AsyncSession,
        *,
        content_id: int,
        user_id: int,
    ) -> ContentInteractionMutationResponse:
        async with session.begin():
            item = await self._require_interactable_content(session, content_id)
            existing = await self.repository.get_content_like(
                session,
                user_id=user_id,
                content_item_id=content_id,
            )
            if existing is not None:
                await self.repository.delete_content_like(session, existing)
                await self.repository.increment_content_counters(
                    session,
                    content_id=content_id,
                    likes_delta=-1,
                    hot_score_delta=-1.0,
                )
                await self.repository.increment_author_likes_received(
                    session,
                    author_user_id=item.author_id,
                    delta=-1,
                )
                await self.recommendation_service.record_behavior(
                    session,
                    user_id=user_id,
                    content_id=content_id,
                    event_type="unlike",
                )
                await self.recommendation_service.update_impression_feedback(
                    session,
                    user_id=user_id,
                    content_id=content_id,
                    liked=False,
                )
        return await self._build_interaction_mutation_response(session, content_id=content_id, user_id=user_id)

    async def favorite_content(
        self,
        session: AsyncSession,
        *,
        content_id: int,
        user_id: int,
    ) -> ContentInteractionMutationResponse:
        async with session.begin():
            await self._require_interactable_content(session, content_id)
            existing = await self.repository.get_content_favorite(
                session,
                user_id=user_id,
                content_item_id=content_id,
            )
            if existing is None:
                await self.repository.create_content_favorite(
                    session,
                    user_id=user_id,
                    content_item_id=content_id,
                )
                await self.repository.increment_content_counters(
                    session,
                    content_id=content_id,
                    favorites_delta=1,
                    hot_score_delta=1.5,
                )
                await self.recommendation_service.record_behavior(
                    session,
                    user_id=user_id,
                    content_id=content_id,
                    event_type="favorite",
                )
                await self.recommendation_service.update_impression_feedback(
                    session,
                    user_id=user_id,
                    content_id=content_id,
                    favorited=True,
                    clicked_at=utc_now_naive(),
                )
        return await self._build_interaction_mutation_response(session, content_id=content_id, user_id=user_id)

    async def unfavorite_content(
        self,
        session: AsyncSession,
        *,
        content_id: int,
        user_id: int,
    ) -> ContentInteractionMutationResponse:
        async with session.begin():
            await self._require_interactable_content(session, content_id)
            existing = await self.repository.get_content_favorite(
                session,
                user_id=user_id,
                content_item_id=content_id,
            )
            if existing is not None:
                await self.repository.delete_content_favorite(session, existing)
                await self.repository.increment_content_counters(
                    session,
                    content_id=content_id,
                    favorites_delta=-1,
                    hot_score_delta=-1.5,
                )
                await self.recommendation_service.record_behavior(
                    session,
                    user_id=user_id,
                    content_id=content_id,
                    event_type="unfavorite",
                )
                await self.recommendation_service.update_impression_feedback(
                    session,
                    user_id=user_id,
                    content_id=content_id,
                    favorited=False,
                )
        return await self._build_interaction_mutation_response(session, content_id=content_id, user_id=user_id)

    async def share_content(
        self,
        session: AsyncSession,
        *,
        content_id: int,
        user_id: int,
        payload: ContentShareRequest,
    ) -> ContentInteractionMutationResponse:
        async with session.begin():
            await self._require_interactable_content(session, content_id)
            await self.repository.create_content_share(
                session,
                user_id=user_id,
                content_item_id=content_id,
                share_channel=payload.share_channel.strip().lower(),
            )
            await self.repository.increment_content_counters(
                session,
                content_id=content_id,
                shares_delta=1,
                hot_score_delta=1.2,
            )
            await self.recommendation_service.record_behavior(
                session,
                user_id=user_id,
                content_id=content_id,
                event_type="share",
            )
            await self.recommendation_service.update_impression_feedback(
                session,
                user_id=user_id,
                content_id=content_id,
                shared=True,
                clicked_at=utc_now_naive(),
            )
        return await self._build_interaction_mutation_response(session, content_id=content_id, user_id=user_id)

    async def list_comments(
        self,
        session: AsyncSession,
        *,
        content_id: int,
        pagination: PaginationParams,
    ) -> ContentCommentListResponse:
        await self._ensure_content_exists(session, content_id)

        cache_key = self._build_comments_cache_key(
            content_id=content_id,
            page=pagination.page,
            page_size=pagination.page_size,
        )
        cached = await self.cache_client.get_json(cache_key)
        if isinstance(cached, dict):
            return ContentCommentListResponse.model_validate(cached)

        rows, total = await self.repository.list_content_comments_rows(
            session,
            content_item_id=content_id,
            offset=pagination.offset,
            limit=pagination.page_size,
        )
        items = [await self._build_comment_response(row) for row in rows]
        response = ContentCommentListResponse(
            list=items,
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
            has_more=(pagination.page * pagination.page_size) < total,
        )
        await self.cache_client.set_json(cache_key, response.model_dump(mode="json"))
        return response

    async def create_comment(
        self,
        session: AsyncSession,
        *,
        content_id: int,
        user_id: int,
        payload: ContentCommentCreateRequest,
    ) -> ContentCommentResponse:
        comment_body = payload.content.strip()
        if not comment_body:
            raise BadRequestError(message="Comment content cannot be empty.")

        async with session.begin():
            item = await self._require_interactable_content(session, content_id)
            if not item.allow_comment:
                raise BadRequestError(message="Comments are disabled for this content.")

            parent_id = None
            root_id = None
            reply_to_user_id = None
            if payload.parent_id is not None:
                parent = await self.repository.get_content_comment_by_id(session, payload.parent_id)
                if parent is None or parent.deleted_at is not None or parent.content_item_id != content_id:
                    raise BadRequestError(message="Parent comment does not exist.")
                parent_id = parent.id
                root_id = parent.root_id or parent.id
                reply_to_user_id = parent.user_id

            comment = await self.repository.create_content_comment(
                session,
                content_item_id=content_id,
                user_id=user_id,
                content=comment_body,
                parent_id=parent_id,
                root_id=root_id,
                reply_to_user_id=reply_to_user_id,
            )
            await self.repository.increment_content_counters(
                session,
                content_id=content_id,
                comments_delta=1,
                hot_score_delta=1.8,
            )
            await self.recommendation_service.record_behavior(
                session,
                user_id=user_id,
                content_id=content_id,
                event_type="comment",
            )
            await self.recommendation_service.update_impression_feedback(
                session,
                user_id=user_id,
                content_id=content_id,
                commented=True,
                clicked_at=utc_now_naive(),
            )

        await self._invalidate_comment_caches(content_id)
        comments = await self.list_comments(
            session,
            content_id=content_id,
            pagination=PaginationParams(page=1, page_size=1),
        )
        for item in comments.list:
            if item.id == comment.id:
                return item
        row = await self.repository.list_content_comments_rows(
            session,
            content_item_id=content_id,
            offset=0,
            limit=1,
        )
        if row[0]:
            return await self._build_comment_response(row[0][0])
        raise NotFoundError(message="Comment not found after creation.")

    async def report_watch_progress(
        self,
        session: AsyncSession,
        *,
        content_id: int,
        user_id: int,
        payload: ContentWatchProgressRequest,
    ) -> ContentInteractionMutationResponse:
        watch_seconds = max(0, int(payload.watch_seconds))
        watch_progress = max(0.0, min(100.0, float(payload.watch_progress)))
        last_position_seconds = max(0, int(payload.last_position_seconds))
        reported_completed = bool(payload.completed or watch_progress >= 95)
        now = utc_now_naive()
        today = now.date()

        async with session.begin():
            await self._require_interactable_content(session, content_id)
            history = await self.repository.get_view_history_for_day(
                session,
                user_id=user_id,
                content_item_id=content_id,
                view_date=today,
            )
            interaction = await self.repository.get_content_detail_row(
                session,
                content_id=content_id,
                viewer_user_id=user_id,
                include_unpublished_for_author_id=user_id,
            )
            liked = bool(interaction["liked"]) if interaction is not None else False
            favorited = bool(interaction["favorited"]) if interaction is not None else False

            if history is None:
                await self.repository.create_view_history(
                    session,
                    user_id=user_id,
                    content_item_id=content_id,
                    view_date=today,
                    watch_seconds=watch_seconds,
                    watch_progress=watch_progress,
                    last_position_seconds=last_position_seconds,
                    completed=reported_completed,
                    liked=liked,
                    favorited=favorited,
                    last_viewed_at=now,
                )
                await self.repository.increment_content_counters(
                    session,
                    content_id=content_id,
                    hot_score_delta=0.2 if watch_progress >= 10 else 0.05,
                )
                await self.repository.increment_views_count(session, content_id=content_id, delta=1)
            else:
                update_values = {
                    "watch_seconds": max(history.watch_seconds, watch_seconds),
                    "watch_progress": max(float(history.watch_progress), watch_progress),
                    "last_position_seconds": max(history.last_position_seconds, last_position_seconds),
                    "completed": bool(history.completed or reported_completed),
                    "liked": liked,
                    "favorited": favorited,
                    "last_viewed_at": now,
                }
                await self.repository.update_view_history(session, history_id=history.id, values=update_values)
            await self.recommendation_service.record_behavior(
                session,
                user_id=user_id,
                content_id=content_id,
                event_type="watch",
                watch_seconds=watch_seconds,
                watch_progress=watch_progress,
                completed=reported_completed,
            )
            await self.recommendation_service.update_impression_feedback(
                session,
                user_id=user_id,
                content_id=content_id,
                watch_seconds=watch_seconds,
                watch_progress=watch_progress,
                completed=reported_completed,
                clicked_at=now,
            )

        return await self._build_interaction_mutation_response(session, content_id=content_id, user_id=user_id)

    async def _validate_content_assets(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        cover_asset_id: int | None,
        primary_media_asset_id: int | None,
    ) -> None:
        asset_ids = [asset_id for asset_id in [cover_asset_id, primary_media_asset_id] if asset_id is not None]
        if not asset_ids:
            return

        assets = await self.repository.get_media_assets_by_ids(session, asset_ids)
        for asset_id in asset_ids:
            asset = assets.get(asset_id)
            if asset is None or asset.status != "active":
                raise BadRequestError(message="Referenced upload asset is missing or inactive.")
            if asset.uploaded_by != user_id:
                raise AuthorizationError(message="You can only use assets uploaded by yourself.")

        if cover_asset_id is not None and assets[cover_asset_id].asset_type not in {"cover", "avatar"}:
            raise BadRequestError(message="cover_asset_id must reference an image asset.")
        if primary_media_asset_id is not None and assets[primary_media_asset_id].asset_type != "video":
            raise BadRequestError(message="primary_media_asset_id must reference a video asset.")

    async def _ensure_tags(self, session: AsyncSession, hashtags: list[str]) -> list[int]:
        if not hashtags:
            return []

        existing = await self.repository.get_tags_by_names(session, hashtags)
        existing_by_name = {tag.name: tag for tag in existing}
        tag_ids: list[int] = []
        for name in hashtags:
            tag = existing_by_name.get(name)
            if tag is None:
                tag = await self.repository.create_tag(
                    session,
                    name=name,
                    slug=self._slugify_tag(name),
                )
                existing_by_name[name] = tag
            tag_ids.append(tag.id)
        return tag_ids

    async def _build_content_video_response(self, row: Any) -> ContentVideoResponse:
        cover_url = await self.storage_service.build_access_url(
            object_key=row["cover_object_key"],
            public_url=row["cover_public_url"],
        )
        avatar_url = await self.storage_service.build_access_url(
            object_key=row["avatar_object_key"],
            public_url=row["avatar_public_url"],
        )
        if row["external_video_url"]:
            video_url = row["external_video_url"]
        else:
            video_url = await self.storage_service.build_access_url(
                object_key=row["video_object_key"],
                public_url=row["video_public_url"],
            )

        category = None
        if row["category_id"] is not None:
            category = ContentCategoryResponse(id=row["category_id"], name=row["category_name"])

        hashtags = row["hashtags_json"] or []
        if not isinstance(hashtags, list):
            hashtags = []

        return ContentVideoResponse(
            id=row["id"],
            title=row["title"],
            summary=row["summary"],
            hashtags=hashtags,
            author=ContentAuthorResponse(
                user_id=row["author_id"],
                display_name=row["author_display_name"],
                avatar_url=avatar_url,
                is_following=bool(row["author_is_following"]),
            ),
            category=category,
            cover_url=cover_url,
            video_url=video_url,
            duration_seconds=row["duration_seconds"],
            bvid=row["bvid"],
            interaction=ContentInteractionResponse(
                views_count=row["views_count"],
                likes_count=row["likes_count"],
                comments_count=row["comments_count"],
                favorites_count=row["favorites_count"],
                shares_count=row["shares_count"],
                liked=bool(row["liked"]),
                favorited=bool(row["favorited"]),
            ),
            has_quiz=bool(row["has_quiz"]),
            quiz_count=row["quiz_count"],
            published_at=row["published_at"],
        )

    async def _build_comment_response(self, row: Any) -> ContentCommentResponse:
        avatar_url = await self.storage_service.build_access_url(
            object_key=row["avatar_object_key"],
            public_url=row["avatar_public_url"],
        )
        return ContentCommentResponse(
            id=row["id"],
            content_item_id=row["content_item_id"],
            user_id=row["user_id"],
            display_name=row["display_name"],
            avatar_url=avatar_url,
            content=row["content"],
            like_count=row["like_count"],
            parent_id=row["parent_id"],
            root_id=row["root_id"],
            reply_to_user_id=row["reply_to_user_id"],
            reply_to_display_name=row["reply_to_display_name"],
            created_at=row["created_at"],
        )

    async def _build_interaction_mutation_response(
        self,
        session: AsyncSession,
        *,
        content_id: int,
        user_id: int,
    ) -> ContentInteractionMutationResponse:
        detail = await self.get_content_detail(session, content_id=content_id, viewer_user_id=user_id)
        return ContentInteractionMutationResponse(content_id=content_id, interaction=detail.interaction)

    async def _require_interactable_content(
        self,
        session: AsyncSession,
        content_id: int,
    ):
        item = await self.repository.get_content_item_by_id_for_update(session, content_id)
        if item is None or item.deleted_at is not None:
            raise NotFoundError(message="Content not found.")
        if item.visibility != "public" or item.audit_status != "approved" or item.publish_status != "published":
            raise AuthorizationError(message="This content is not available for interaction.")
        return item

    async def _ensure_content_exists(self, session: AsyncSession, content_id: int) -> None:
        item = await self.repository.get_content_item_by_id(session, content_id)
        if item is None or item.deleted_at is not None:
            raise NotFoundError(message="Content not found.")

    def _build_comments_cache_key(self, *, content_id: int, page: int, page_size: int) -> str:
        return f"{self.cache_client.settings.redis_prefix}:content:{content_id}:comments:{page}:{page_size}"

    async def _invalidate_comment_caches(self, content_id: int) -> None:
        prefix = f"{self.cache_client.settings.redis_prefix}:content:{content_id}:comments:"
        if not self.cache_client.enabled:
            return
        client = await self.cache_client._get_client()
        if client is None:
            return
        keys = []
        async for key in client.scan_iter(match=f"{prefix}*"):
            keys.append(key)
        if keys:
            await self.cache_client.delete(*keys)

    @staticmethod
    def _normalize_hashtags(hashtags: list[str] | None) -> list[str]:
        if not hashtags:
            return []

        normalized: list[str] = []
        seen: set[str] = set()
        for hashtag in hashtags:
            value = hashtag.strip().lstrip("#")
            if not value:
                continue
            lowered = value.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            normalized.append(value[:64])
        return normalized

    @staticmethod
    def _slugify_tag(value: str) -> str:
        slug_chars = []
        for char in value.strip().lower():
            if char.isalnum():
                slug_chars.append(char)
            elif slug_chars and slug_chars[-1] != "-":
                slug_chars.append("-")
        slug = "".join(slug_chars).strip("-")
        return slug or f"tag-{abs(hash(value)) % 10_000_000}"

    @staticmethod
    def _build_cursor(published_at: datetime | None, content_id: int) -> str | None:
        if published_at is None:
            return None
        return f"{published_at.isoformat()}|{content_id}"

    @staticmethod
    def _parse_cursor(cursor: str | None) -> tuple[datetime, int] | None:
        if not cursor:
            return None
        try:
            published_at_raw, content_id_raw = cursor.split("|", maxsplit=1)
            return datetime.fromisoformat(published_at_raw), int(content_id_raw)
        except (TypeError, ValueError) as exc:
            raise BadRequestError(message="Invalid cursor.") from exc
