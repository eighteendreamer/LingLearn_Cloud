from pathlib import Path

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

    async def object_exists(self, *, object_key: str) -> bool:
        return await self.minio_client.object_exists(object_key=object_key)

    async def download_object_to_path(self, *, object_key: str, target_path: str | Path) -> None:
        await self.minio_client.download_file(object_key=object_key, target_path=target_path)

    async def upload_file(
        self,
        *,
        object_key: str,
        file_path: str | Path,
        content_type: str | None = None,
    ) -> dict:
        return await self.minio_client.upload_file(
            object_key=object_key,
            file_path=file_path,
            content_type=content_type,
        )

    async def read_text_object(self, *, object_key: str, encoding: str = "utf-8") -> str:
        return await self.minio_client.read_text_object(object_key=object_key, encoding=encoding)

    def build_public_url(self, object_key: str) -> str | None:
        return self.minio_client.build_public_url(object_key)
