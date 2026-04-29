from __future__ import annotations

import asyncio
from datetime import timedelta

from app.core.config import get_settings
from app.core.exceptions import InfrastructureError

try:
    from minio import Minio
    from minio.error import S3Error
except ImportError:  # pragma: no cover - handled dynamically at runtime
    Minio = None
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
