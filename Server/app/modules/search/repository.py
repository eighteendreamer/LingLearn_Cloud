from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.content.repository import ContentRepository


class SearchRepository:
    def __init__(self, *, content_repository: ContentRepository | None = None) -> None:
        self.content_repository = content_repository or ContentRepository()

    async def search_contents(
        self,
        session: AsyncSession,
        *,
        viewer_user_id: int | None,
        keyword: str | None,
        category_id: int | None,
        offset: int,
        limit: int,
    ) -> tuple[list[dict], int]:
        return await self.content_repository.search_content_rows(
            session,
            viewer_user_id=viewer_user_id,
            keyword=keyword,
            category_id=category_id,
            offset=offset,
            limit=limit,
        )
