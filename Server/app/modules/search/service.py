import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginationParams, build_page_response
from app.infra.storage.service import StorageService
from app.modules.content.schemas import (
    ContentAuthorResponse,
    ContentCategoryResponse,
    ContentInteractionResponse,
    ContentVideoResponse,
)
from app.modules.search.repository import SearchRepository


class SearchService:
    def __init__(
        self,
        *,
        repository: SearchRepository | None = None,
        storage_service: StorageService | None = None,
    ) -> None:
        self.repository = repository or SearchRepository()
        self.storage_service = storage_service or StorageService()

    async def search_contents(
        self,
        session: AsyncSession,
        *,
        viewer_user_id: int | None,
        keyword: str | None,
        category_id: int | None,
        pagination: PaginationParams,
    ):
        rows, total = await self.repository.search_contents(
            session,
            viewer_user_id=viewer_user_id,
            keyword=keyword,
            category_id=category_id,
            offset=pagination.offset,
            limit=pagination.page_size,
        )
        items = await asyncio.gather(*(self._build_content_video_response(row) for row in rows))
        return build_page_response(items, total, pagination)

    async def _build_content_video_response(self, row) -> ContentVideoResponse:
        cover_url = await self.storage_service.build_access_url(
            object_key=row["cover_object_key"],
            public_url=row["cover_public_url"],
        )
        avatar_url = await self.storage_service.build_access_url(
            object_key=row["avatar_object_key"],
            public_url=row["avatar_public_url"],
        )
        video_url = row["external_video_url"] or await self.storage_service.build_access_url(
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
