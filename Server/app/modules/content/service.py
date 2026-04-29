from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginationParams, build_page_response
from app.common.utils import utc_now_naive
from app.core.exceptions import AuthorizationError, BadRequestError, NotFoundError
from app.infra.storage.service import StorageService
from app.modules.content.repository import ContentRepository
from app.modules.content.schemas import (
    ContentAuthorResponse,
    ContentCategoryResponse,
    ContentCreateRequest,
    ContentInteractionResponse,
    ContentUpdateRequest,
    ContentVideoResponse,
    FeedQueryParams,
    FeedVideosResponse,
)
from app.modules.user.schemas import UserWorkListItemResponse


class ContentService:
    def __init__(
        self,
        *,
        repository: ContentRepository | None = None,
        storage_service: StorageService | None = None,
    ) -> None:
        self.repository = repository or ContentRepository()
        self.storage_service = storage_service or StorageService()

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
        if normalized_type not in {"for_you", "following"}:
            raise BadRequestError(message="Unsupported recommend_type.")

        cursor = self._parse_cursor(query.cursor)
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
