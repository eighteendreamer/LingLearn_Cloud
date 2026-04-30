from __future__ import annotations

from app.modules.content.repository import ContentRepository
from app.modules.discover.schemas import (
    DiscoverCategoryResponse,
    DiscoverHotTagResponse,
    DiscoverHotTopicResponse,
)

DEFAULT_CATEGORIES: tuple[dict[str, str | int | None], ...] = (
    {"name": "编程", "slug": "programming", "description": "编程开发相关内容", "icon": "code", "sort_order": 10},
    {"name": "算法", "slug": "algorithm", "description": "算法与数据结构相关内容", "icon": "binary", "sort_order": 20},
    {"name": "前端", "slug": "frontend", "description": "前端工程与页面开发内容", "icon": "layout", "sort_order": 30},
    {"name": "后端", "slug": "backend", "description": "后端服务与架构设计内容", "icon": "server", "sort_order": 40},
    {"name": "数据库", "slug": "database", "description": "数据库与数据建模相关内容", "icon": "database", "sort_order": 50},
    {"name": "AI/ML", "slug": "ai-ml", "description": "人工智能与机器学习内容", "icon": "sparkles", "sort_order": 60},
)


class DiscoverService:
    def __init__(self, *, content_repository: ContentRepository | None = None) -> None:
        self.content_repository = content_repository or ContentRepository()

    async def list_categories(self, session) -> list[DiscoverCategoryResponse]:
        categories = await self.content_repository.list_active_categories(session)
        if not categories:
            for item in DEFAULT_CATEGORIES:
                await self.content_repository.create_category(
                    session,
                    name=str(item["name"]),
                    slug=str(item["slug"]),
                    description=str(item["description"]) if item["description"] is not None else None,
                    icon=str(item["icon"]) if item["icon"] is not None else None,
                    sort_order=int(item["sort_order"]),
                )
            await session.commit()
            categories = await self.content_repository.list_active_categories(session)

        return [DiscoverCategoryResponse(id=item.id, name=item.name) for item in categories]

    async def list_hot_topics(self, session, *, limit: int = 6) -> list[DiscoverHotTopicResponse]:
        rows = await self.content_repository.list_discover_hot_topic_rows(session, limit=limit)
        return [
            DiscoverHotTopicResponse(
                id=int(row["id"]),
                name=str(row["name"]),
                content_count=int(row["content_count"] or 0),
                views_count=int(row["views_count"] or 0),
                likes_count=int(row["likes_count"] or 0),
                trend_score=float(row["trend_score"] or 0),
            )
            for row in rows
        ]

    async def list_hot_tags(self, session, *, limit: int = 10) -> list[DiscoverHotTagResponse]:
        rows = await self.content_repository.list_discover_hot_tag_rows(session, limit=limit)
        return [
            DiscoverHotTagResponse(
                id=int(row["id"]),
                name=str(row["name"]),
                content_count=int(row["content_count"] or 0),
                views_count=int(row["views_count"] or 0),
                likes_count=int(row["likes_count"] or 0),
                trend_score=float(row["trend_score"] or 0),
            )
            for row in rows
        ]
