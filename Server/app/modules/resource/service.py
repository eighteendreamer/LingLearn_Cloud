from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginationParams, build_page_response
from app.infra.storage.service import StorageService
from app.modules.resource.repository import ResourceRepository
from app.modules.resource.schemas import ResourceListItemResponse


class ResourceService:
    def __init__(
        self,
        *,
        repository: ResourceRepository | None = None,
        storage_service: StorageService | None = None,
    ) -> None:
        self.repository = repository or ResourceRepository()
        self.storage_service = storage_service or StorageService()

    async def list_resources(
        self,
        session: AsyncSession,
        *,
        resource_type: str | None,
        category_id: int | None,
        keyword: str | None,
        pagination: PaginationParams,
    ):
        rows, total = await self.repository.list_resources(
            session,
            resource_type=resource_type,
            category_id=category_id,
            keyword=keyword,
            offset=pagination.offset,
            limit=pagination.page_size,
        )

        items = []
        for row in rows:
            file_url = await self.storage_service.build_access_url(
                object_key=row["file_object_key"],
                public_url=row["file_public_url"],
            )
            items.append(
                ResourceListItemResponse(
                    id=row["id"],
                    title=row["title"],
                    description=row["description"],
                    resource_type=row["resource_type"],
                    file_url=file_url,
                    file_size=row["file_size"],
                    download_count=row["download_count"],
                    created_at=row["created_at"],
                )
            )

        return build_page_response(items, total, pagination)

    async def list_recent_resources(
        self,
        session: AsyncSession,
        user_id: int,
        pagination: PaginationParams,
    ):
        rows, total = await self.repository.list_user_recent_resources(
            session,
            user_id=user_id,
            offset=pagination.offset,
            limit=pagination.page_size,
        )

        items = []
        for row in rows:
            file_url = await self.storage_service.build_access_url(
                object_key=row["file_object_key"],
                public_url=row["file_public_url"],
            )
            items.append(
                ResourceListItemResponse(
                    id=row["id"],
                    title=row["title"],
                    description=row["description"],
                    resource_type=row["resource_type"],
                    file_url=file_url,
                    file_size=row["file_size"],
                    download_count=row["download_count"],
                    created_at=row["created_at"],
                )
            )

        return build_page_response(items, total, pagination)
