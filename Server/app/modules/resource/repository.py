from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.resource.models import Resource, UserResourceAccess


class ResourceRepository:
    async def list_resources(
        self,
        session: AsyncSession,
        *,
        resource_type: str | None = None,
        category_id: int | None = None,
        keyword: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict], int]:
        from app.modules.storage.models import MediaAsset

        query = (
            select(
                Resource.id,
                Resource.title,
                Resource.description,
                Resource.resource_type,
                Resource.file_size,
                Resource.download_count,
                Resource.created_at,
                MediaAsset.object_key.label("file_object_key"),
                MediaAsset.public_url.label("file_public_url"),
            )
            .outerjoin(MediaAsset, Resource.file_asset_id == MediaAsset.id)
            .where(Resource.deleted_at.is_(None))
            .where(Resource.status == "published")
        )

        if resource_type:
            query = query.where(Resource.resource_type == resource_type)

        if category_id is not None:
            query = query.where(Resource.category_id == category_id)

        if keyword:
            search_pattern = f"%{keyword}%"
            query = query.where(
                or_(
                    Resource.title.ilike(search_pattern),
                    Resource.description.ilike(search_pattern),
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query) or 0

        query = query.order_by(Resource.created_at.desc()).offset(offset).limit(limit)
        result = await session.execute(query)
        rows = [dict(row._mapping) for row in result]

        return rows, total

    async def list_user_recent_resources(
        self,
        session: AsyncSession,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict], int]:
        from app.modules.storage.models import MediaAsset

        query = (
            select(
                Resource.id,
                Resource.title,
                Resource.description,
                Resource.resource_type,
                Resource.file_size,
                Resource.download_count,
                Resource.created_at,
                MediaAsset.object_key.label("file_object_key"),
                MediaAsset.public_url.label("file_public_url"),
            )
            .join(UserResourceAccess, Resource.id == UserResourceAccess.resource_id)
            .outerjoin(MediaAsset, Resource.file_asset_id == MediaAsset.id)
            .where(UserResourceAccess.user_id == user_id)
            .where(Resource.deleted_at.is_(None))
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query) or 0

        query = query.order_by(UserResourceAccess.accessed_at.desc()).offset(offset).limit(limit)
        result = await session.execute(query)
        rows = [dict(row._mapping) for row in result]

        return rows, total
