from __future__ import annotations

import asyncio
from datetime import timedelta
from pathlib import Path
from threading import Lock
from time import time

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

    _verified_buckets: set[tuple[str, str]] = set()
    _verified_buckets_lock = Lock()
    _presigned_download_cache: dict[tuple[str, str, str], tuple[float, str]] = {}
    _presigned_download_cache_lock = Lock()
    _presigned_cache_refresh_window_seconds = 60
    _object_exists_cache: dict[tuple[str, str, str], tuple[float, bool]] = {}
    _object_exists_cache_lock = Lock()
    _object_exists_cache_ttl_seconds = 300

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
        self._bucket_cache_key = (self.settings.minio_endpoint, self.bucket_name)

    async def ensure_bucket_exists(self) -> None:
        if self._bucket_cache_key in self._verified_buckets:
            return
        await asyncio.to_thread(self._ensure_bucket_exists)

    async def create_presigned_upload(self, *, object_key: str, content_type: str) -> dict:
        await self.ensure_bucket_exists()
        return await asyncio.to_thread(self._create_presigned_upload, object_key, content_type)

    async def create_presigned_download(self, *, object_key: str) -> str:
        cache_key = (self.settings.minio_endpoint, self.bucket_name, object_key)
        cached_url = self._get_cached_presigned_download(cache_key)
        if cached_url is not None:
            return cached_url

        await self.ensure_bucket_exists()
        url = await asyncio.to_thread(self._create_presigned_download, object_key)
        self._set_cached_presigned_download(cache_key, url)
        return url

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

    async def object_exists(self, *, object_key: str) -> bool:
        cache_key = (self.settings.minio_endpoint, self.bucket_name, object_key)
        cached = self._get_cached_object_exists(cache_key)
        if cached is not None:
            return cached

        await self.ensure_bucket_exists()
        exists = await asyncio.to_thread(self._object_exists, object_key)
        self._set_cached_object_exists(cache_key, exists)
        return exists

    async def download_file(self, *, object_key: str, target_path: str | Path) -> None:
        await self.ensure_bucket_exists()
        await asyncio.to_thread(self._download_file, object_key, str(target_path))

    async def upload_file(
        self,
        *,
        object_key: str,
        file_path: str | Path,
        content_type: str | None = None,
    ) -> dict:
        await self.ensure_bucket_exists()
        result = await asyncio.to_thread(
            self._upload_file,
            object_key,
            str(file_path),
            content_type,
        )
        cache_key = (self.settings.minio_endpoint, self.bucket_name, object_key)
        self._set_cached_object_exists(cache_key, True)
        return result

    async def read_text_object(self, *, object_key: str, encoding: str = "utf-8") -> str:
        await self.ensure_bucket_exists()
        return await asyncio.to_thread(self._read_text_object, object_key, encoding)

    def build_public_url(self, object_key: str) -> str | None:
        base = self.settings.minio_public_base_url.strip().rstrip("/")
        if not base:
            return None
        return f"{base}/{object_key.lstrip('/')}"

    def _ensure_bucket_exists(self) -> None:
        with self._verified_buckets_lock:
            if self._bucket_cache_key in self._verified_buckets:
                return
        try:
            if self.client.bucket_exists(self.bucket_name):
                with self._verified_buckets_lock:
                    self._verified_buckets.add(self._bucket_cache_key)
                return
            if not self.settings.minio_auto_create_bucket:
                raise InfrastructureError(message=f"Bucket '{self.bucket_name}' does not exist.")
            self.client.make_bucket(self.bucket_name)
            with self._verified_buckets_lock:
                self._verified_buckets.add(self._bucket_cache_key)
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

    def _object_exists(self, object_key: str) -> bool:
        try:
            self.client.stat_object(self.bucket_name, object_key)
            return True
        except S3Error as exc:
            if getattr(exc, "code", "") in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
                return False
            raise InfrastructureError(message=f"Check MinIO object failed: {exc}.") from exc

    def _download_file(self, object_key: str, target_path: str) -> None:
        try:
            self.client.fget_object(self.bucket_name, object_key, target_path)
        except S3Error as exc:
            raise InfrastructureError(message=f"Download MinIO object failed: {exc}.") from exc

    def _upload_file(self, object_key: str, file_path: str, content_type: str | None) -> dict:
        try:
            result = self.client.fput_object(
                self.bucket_name,
                object_key,
                file_path,
                content_type=content_type,
            )
        except S3Error as exc:
            raise InfrastructureError(message=f"Upload file to MinIO failed: {exc}.") from exc

        return {
            "bucket_name": self.bucket_name,
            "object_key": object_key,
            "etag": getattr(result, "etag", None),
            "version_id": getattr(result, "version_id", None),
        }

    def _read_text_object(self, object_key: str, encoding: str) -> str:
        response = None
        try:
            response = self.client.get_object(self.bucket_name, object_key)
            return response.read().decode(encoding)
        except S3Error as exc:
            raise InfrastructureError(message=f"Read MinIO object failed: {exc}.") from exc
        finally:
            if response is not None:
                response.close()
                response.release_conn()

    def _get_cached_presigned_download(self, cache_key: tuple[str, str, str]) -> str | None:
        with self._presigned_download_cache_lock:
            cached = self._presigned_download_cache.get(cache_key)
            if cached is None:
                return None
            expires_at, url = cached
            if expires_at <= time():
                self._presigned_download_cache.pop(cache_key, None)
                return None
            return url

    def _set_cached_presigned_download(self, cache_key: tuple[str, str, str], url: str) -> None:
        ttl_seconds = max(
            1,
            int(self.settings.minio_presign_expire_seconds)
            - self._presigned_cache_refresh_window_seconds,
        )
        with self._presigned_download_cache_lock:
            self._presigned_download_cache[cache_key] = (time() + ttl_seconds, url)

    def _get_cached_object_exists(self, cache_key: tuple[str, str, str]) -> bool | None:
        with self._object_exists_cache_lock:
            cached = self._object_exists_cache.get(cache_key)
            if cached is None:
                return None
            expires_at, exists = cached
            if expires_at <= time():
                self._object_exists_cache.pop(cache_key, None)
                return None
            return exists

    def _set_cached_object_exists(self, cache_key: tuple[str, str, str], exists: bool) -> None:
        with self._object_exists_cache_lock:
            self._object_exists_cache[cache_key] = (
                time() + self._object_exists_cache_ttl_seconds,
                exists,
            )
