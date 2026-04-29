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

    async def build_access_url(self, *, object_key: str | None, public_url: str | None) -> str | None:
        if public_url:
            return public_url
        if not object_key:
            return None
        return await self.minio_client.create_presigned_download(object_key=object_key)

    async def initiate_multipart_upload(self, *, object_key: str, mime_type: str) -> dict:
        return await self.minio_client.create_multipart_upload(
            object_key=object_key,
            content_type=mime_type,
        )

    async def presign_upload_part(self, *, object_key: str, upload_id: str, part_number: int) -> dict:
        return await self.minio_client.create_presigned_part_upload(
            object_key=object_key,
            upload_id=upload_id,
            part_number=part_number,
        )

    async def complete_multipart_upload(
        self,
        *,
        object_key: str,
        upload_id: str,
        parts: list[dict[str, str | int]],
    ) -> dict:
        return await self.minio_client.complete_multipart_upload(
            object_key=object_key,
            upload_id=upload_id,
            parts=parts,
        )

    async def abort_multipart_upload(self, *, object_key: str, upload_id: str) -> None:
        await self.minio_client.abort_multipart_upload(
            object_key=object_key,
            upload_id=upload_id,
        )

    async def stat_uploaded_object(self, *, object_key: str) -> dict:
        return await self.minio_client.stat_object(object_key=object_key)

    def build_public_url(self, object_key: str) -> str | None:
        return self.minio_client.build_public_url(object_key)
