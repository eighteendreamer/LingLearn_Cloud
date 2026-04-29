from app.infra.storage.minio_client import MinIOClient


class StorageService:
    """Infrastructure-level object storage helper."""

    def __init__(self, minio_client: MinIOClient | None = None) -> None:
        self.minio_client = minio_client or MinIOClient()

    async def presign_upload(self, *, object_key: str, mime_type: str) -> dict:
        return await self.minio_client.create_presigned_upload(
            object_key=object_key,
            content_type=mime_type,
        )

    async def stat_uploaded_object(self, *, object_key: str) -> dict:
        return await self.minio_client.stat_object(object_key=object_key)

    def build_public_url(self, object_key: str) -> str | None:
        return self.minio_client.build_public_url(object_key)
