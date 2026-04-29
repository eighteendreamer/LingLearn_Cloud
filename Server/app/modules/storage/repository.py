from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.storage.models import MediaAsset


class StorageRepository:
    async def create_media_asset(
        self,
        session: AsyncSession,
        *,
        bucket_name: str,
        object_key: str,
        original_name: str,
        mime_type: str,
        extension: str | None,
        asset_type: str,
        file_size: int,
        uploaded_by: int | None,
        status: str,
    ) -> MediaAsset:
        asset = MediaAsset(
            bucket_name=bucket_name,
            object_key=object_key,
            original_name=original_name,
            mime_type=mime_type,
            extension=extension,
            asset_type=asset_type,
            storage_provider="minio",
            file_size=file_size,
            uploaded_by=uploaded_by,
            status=status,
        )
        session.add(asset)
        await session.flush()
        return asset

    async def get_media_asset_by_id(
        self,
        session: AsyncSession,
        *,
        asset_id: int,
    ) -> MediaAsset | None:
        stmt = select(MediaAsset).where(MediaAsset.id == asset_id)
        return await session.scalar(stmt)
