from __future__ import annotations

import asyncio
from datetime import timedelta

from app.core.config import get_settings
from app.core.exceptions import InfrastructureError

try:
    from minio import Minio
    from minio.datatypes import Part
    from minio.error import S3Error
except ImportError:  # pragma: no cover - handled dynamically at runtime
    Minio = None
    Part = None
    S3Error = Exception


class MinIOClient:
    """Async wrapper around the MinIO SDK."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.bucket_name = self.settings.minio_bucket_name

        if Minio is None:
            raise InfrastructureError(
                message="MinIO SDK is not installed. Please install the 'minio' package.",
            )

        self.client = Minio(
            self.settings.minio_endpoint,
            access_key=self.settings.minio_access_key,
            secret_key=self.settings.minio_secret_key,
            secure=self.settings.minio_secure,
        )

    async def ensure_bucket_exists(self) -> None:
        await asyncio.to_thread(self._ensure_bucket_exists)

    async def create_presigned_upload(self, *, object_key: str, content_type: str) -> dict:
        await self.ensure_bucket_exists()
        return await asyncio.to_thread(self._create_presigned_upload, object_key, content_type)

    async def create_presigned_download(self, *, object_key: str) -> str:
        await self.ensure_bucket_exists()
        return await asyncio.to_thread(self._create_presigned_download, object_key)

    async def create_multipart_upload(self, *, object_key: str, content_type: str) -> dict:
        await self.ensure_bucket_exists()
        return await asyncio.to_thread(self._create_multipart_upload, object_key, content_type)

    async def create_presigned_part_upload(self, *, object_key: str, upload_id: str, part_number: int) -> dict:
        await self.ensure_bucket_exists()
        return await asyncio.to_thread(
            self._create_presigned_part_upload,
            object_key,
            upload_id,
            part_number,
        )

    async def complete_multipart_upload(
        self,
        *,
        object_key: str,
        upload_id: str,
        parts: list[dict[str, str | int]],
    ) -> dict:
        await self.ensure_bucket_exists()
        return await asyncio.to_thread(
            self._complete_multipart_upload,
            object_key,
            upload_id,
            parts,
        )

    async def abort_multipart_upload(self, *, object_key: str, upload_id: str) -> None:
        await self.ensure_bucket_exists()
        await asyncio.to_thread(self._abort_multipart_upload, object_key, upload_id)

    async def stat_object(self, *, object_key: str) -> dict:
        await self.ensure_bucket_exists()
        return await asyncio.to_thread(self._stat_object, object_key)

    def build_public_url(self, object_key: str) -> str | None:
        base = self.settings.minio_public_base_url.strip().rstrip("/")
        if not base:
            return None
        return f"{base}/{object_key.lstrip('/')}"

    def _ensure_bucket_exists(self) -> None:
        try:
            if self.client.bucket_exists(self.bucket_name):
                return
            if not self.settings.minio_auto_create_bucket:
                raise InfrastructureError(message=f"Bucket '{self.bucket_name}' does not exist.")
            self.client.make_bucket(self.bucket_name)
        except S3Error as exc:
            raise InfrastructureError(message=f"MinIO bucket check failed: {exc}.") from exc

    def _create_presigned_upload(self, object_key: str, content_type: str) -> dict:
        try:
            url = self.client.presigned_put_object(
                self.bucket_name,
                object_key,
                expires=timedelta(seconds=self.settings.minio_presign_expire_seconds),
            )
        except S3Error as exc:
            raise InfrastructureError(message=f"Create MinIO upload URL failed: {exc}.") from exc

        return {
            "bucket_name": self.bucket_name,
            "object_key": object_key,
            "upload_url": url,
            "headers": {
                "Content-Type": content_type,
            },
        }

    def _create_presigned_download(self, object_key: str) -> str:
        try:
            return self.client.presigned_get_object(
                self.bucket_name,
                object_key,
                expires=timedelta(seconds=self.settings.minio_presign_expire_seconds),
            )
        except S3Error as exc:
            raise InfrastructureError(message=f"Create MinIO download URL failed: {exc}.") from exc

    def _create_multipart_upload(self, object_key: str, content_type: str) -> dict:
        try:
            upload_id = self.client._create_multipart_upload(
                self.bucket_name,
                object_key,
                headers={"Content-Type": content_type},
            )
        except S3Error as exc:
            raise InfrastructureError(message=f"Create MinIO multipart upload failed: {exc}.") from exc

        return {
            "bucket_name": self.bucket_name,
            "object_key": object_key,
            "upload_id": upload_id,
        }

    def _create_presigned_part_upload(self, object_key: str, upload_id: str, part_number: int) -> dict:
        try:
            url = self.client.get_presigned_url(
                "PUT",
                self.bucket_name,
                object_key,
                expires=timedelta(seconds=self.settings.minio_presign_expire_seconds),
                extra_query_params={
                    "partNumber": str(part_number),
                    "uploadId": upload_id,
                },
            )
        except S3Error as exc:
            raise InfrastructureError(
                message=f"Create MinIO multipart upload part URL failed: {exc}.",
            ) from exc

        return {
            "bucket_name": self.bucket_name,
            "object_key": object_key,
            "upload_id": upload_id,
            "part_number": part_number,
            "upload_url": url,
            "headers": {},
        }

    def _complete_multipart_upload(
        self,
        object_key: str,
        upload_id: str,
        parts: list[dict[str, str | int]],
    ) -> dict:
        try:
            result = self.client._complete_multipart_upload(
                self.bucket_name,
                object_key,
                upload_id,
                [
                    Part(
                        int(item["part_number"]),
                        str(item["etag"]),
                    )
                    for item in parts
                ],
            )
        except S3Error as exc:
            raise InfrastructureError(
                message=f"Complete MinIO multipart upload failed: {exc}.",
            ) from exc

        return {
            "bucket_name": self.bucket_name,
            "object_key": object_key,
            "etag": getattr(result, "etag", None),
            "version_id": getattr(result, "version_id", None),
        }

    def _abort_multipart_upload(self, object_key: str, upload_id: str) -> None:
        try:
            self.client._abort_multipart_upload(self.bucket_name, object_key, upload_id)
        except S3Error as exc:
            raise InfrastructureError(message=f"Abort MinIO multipart upload failed: {exc}.") from exc

    def _stat_object(self, object_key: str) -> dict:
        try:
            stat = self.client.stat_object(self.bucket_name, object_key)
        except S3Error as exc:
            raise InfrastructureError(message=f"Stat MinIO object failed: {exc}.") from exc

        return {
            "bucket_name": self.bucket_name,
            "object_key": object_key,
            "size": stat.size,
            "etag": stat.etag,
            "content_type": getattr(stat, "content_type", None),
        }
