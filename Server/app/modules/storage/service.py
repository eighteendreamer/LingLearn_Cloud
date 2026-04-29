from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import ceil
from pathlib import Path
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import utc_now_naive
from app.core.exceptions import BadRequestError, NotFoundError
from app.infra.storage.service import StorageService as InfraStorageService
from app.modules.storage.repository import StorageRepository
from app.modules.storage.schemas import (
    StorageCompleteMultipartUploadRequest,
    StorageCompleteUploadRequest,
    StorageCompleteUploadResponse,
    StorageInitiateMultipartUploadRequest,
    StorageInitiateMultipartUploadResponse,
    StoragePresignUploadPartRequest,
    StoragePresignUploadPartResponse,
    StoragePresignUploadRequest,
    StoragePresignUploadResponse,
)

MULTIPART_MIN_PART_SIZE = 5 * 1024 * 1024
MULTIPART_DEFAULT_PART_SIZE = 10 * 1024 * 1024
MULTIPART_MAX_PARTS = 10_000


@dataclass(frozen=True)
class UploadRule:
    asset_type: str
    object_prefix: str
    max_size: int
    mime_prefixes: tuple[str, ...]
    allowed_extensions: tuple[str, ...]


UPLOAD_RULES: dict[str, UploadRule] = {
    "user_avatar": UploadRule(
        asset_type="avatar",
        object_prefix="avatars",
        max_size=5 * 1024 * 1024,
        mime_prefixes=("image/",),
        allowed_extensions=(".jpg", ".jpeg", ".png", ".webp"),
    ),
    "content_cover": UploadRule(
        asset_type="cover",
        object_prefix="content/covers",
        max_size=10 * 1024 * 1024,
        mime_prefixes=("image/",),
        allowed_extensions=(".jpg", ".jpeg", ".png", ".webp"),
    ),
    "content_video": UploadRule(
        asset_type="video",
        object_prefix="content/videos",
        max_size=500 * 1024 * 1024,
        mime_prefixes=("video/",),
        allowed_extensions=(".mp4", ".mov", ".m4v", ".webm"),
    ),
    "resource_file": UploadRule(
        asset_type="document",
        object_prefix="resources/files",
        max_size=100 * 1024 * 1024,
        mime_prefixes=("application/", "text/"),
        allowed_extensions=(".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt", ".zip"),
    ),
    "report_pdf": UploadRule(
        asset_type="report",
        object_prefix="reports/pdf",
        max_size=20 * 1024 * 1024,
        mime_prefixes=("application/pdf",),
        allowed_extensions=(".pdf",),
    ),
}


class StorageAppService:
    def __init__(
        self,
        repository: StorageRepository | None = None,
        infra_service: InfraStorageService | None = None,
    ) -> None:
        self.repository = repository or StorageRepository()
        self.infra_service = infra_service or InfraStorageService()

    async def presign_upload(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        payload: StoragePresignUploadRequest,
    ) -> StoragePresignUploadResponse:
        rule = self._get_rule(payload.biz_type)
        extension = Path(payload.file_name).suffix.lower()
        self._validate_upload_payload(payload, rule, extension)

        object_key = self._build_object_key(rule.object_prefix, extension)
        upload_data = await self.infra_service.presign_upload(
            object_key=object_key,
            mime_type=payload.mime_type,
        )

        async with session.begin():
            asset = await self.repository.create_media_asset(
                session,
                bucket_name=upload_data["bucket_name"],
                object_key=object_key,
                original_name=payload.file_name,
                mime_type=payload.mime_type,
                extension=extension or None,
                asset_type=rule.asset_type,
                file_size=payload.file_size,
                uploaded_by=user_id,
                status="pending",
            )

        return StoragePresignUploadResponse(
            asset_id=asset.id,
            bucket_name=upload_data["bucket_name"],
            object_key=object_key,
            upload_url=upload_data["upload_url"],
            headers=upload_data["headers"],
        )

    async def complete_upload(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        payload: StorageCompleteUploadRequest,
    ) -> StorageCompleteUploadResponse:
        async with session.begin():
            asset = await self.repository.get_media_asset_by_id(session, asset_id=payload.asset_id)
            if asset is None:
                raise NotFoundError(message="Uploaded asset not found.")
            if asset.uploaded_by not in {None, user_id}:
                raise NotFoundError(message="Uploaded asset not found.")

            object_info = await self.infra_service.stat_uploaded_object(object_key=asset.object_key)
            asset.file_size = object_info["size"]
            asset.status = "active"
            asset.public_url = self.infra_service.build_public_url(asset.object_key)

        return StorageCompleteUploadResponse(
            asset_id=asset.id,
            bucket_name=asset.bucket_name,
            object_key=asset.object_key,
            status=asset.status,
            file_size=asset.file_size,
            mime_type=asset.mime_type,
            public_url=asset.public_url,
        )

    async def initiate_multipart_upload(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        payload: StorageInitiateMultipartUploadRequest,
    ) -> StorageInitiateMultipartUploadResponse:
        rule = self._get_rule(payload.biz_type)
        extension = Path(payload.file_name).suffix.lower()
        self._validate_upload_payload(payload, rule, extension)

        if payload.biz_type.strip().lower() != "content_video":
            raise BadRequestError(message="Multipart upload is currently enabled for videos only.")

        object_key = self._build_object_key(rule.object_prefix, extension)
        upload_data = await self.infra_service.initiate_multipart_upload(
            object_key=object_key,
            mime_type=payload.mime_type,
        )
        part_size = self._resolve_part_size(payload.file_size)
        part_count = ceil(payload.file_size / part_size)

        async with session.begin():
            asset = await self.repository.create_media_asset(
                session,
                bucket_name=upload_data["bucket_name"],
                object_key=object_key,
                original_name=payload.file_name,
                mime_type=payload.mime_type,
                extension=extension or None,
                asset_type=rule.asset_type,
                file_size=payload.file_size,
                uploaded_by=user_id,
                status="pending",
            )

        return StorageInitiateMultipartUploadResponse(
            asset_id=asset.id,
            bucket_name=upload_data["bucket_name"],
            object_key=object_key,
            upload_id=upload_data["upload_id"],
            part_size=part_size,
            part_count=part_count,
        )

    async def presign_upload_part(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        payload: StoragePresignUploadPartRequest,
    ) -> StoragePresignUploadPartResponse:
        asset = await self.repository.get_media_asset_by_id(session, asset_id=payload.asset_id)
        if asset is None or asset.uploaded_by not in {None, user_id}:
            raise NotFoundError(message="Uploaded asset not found.")
        if asset.status != "pending":
            raise BadRequestError(message="Upload has already been completed.")

        part_data = await self.infra_service.presign_upload_part(
            object_key=asset.object_key,
            upload_id=payload.upload_id,
            part_number=payload.part_number,
        )

        return StoragePresignUploadPartResponse(
            asset_id=asset.id,
            upload_id=payload.upload_id,
            part_number=payload.part_number,
            upload_url=part_data["upload_url"],
            headers=part_data["headers"],
        )

    async def complete_multipart_upload(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        payload: StorageCompleteMultipartUploadRequest,
    ) -> StorageCompleteUploadResponse:
        normalized_parts = self._normalize_multipart_parts(payload.parts)

        async with session.begin():
            asset = await self.repository.get_media_asset_by_id(session, asset_id=payload.asset_id)
            if asset is None:
                raise NotFoundError(message="Uploaded asset not found.")
            if asset.uploaded_by not in {None, user_id}:
                raise NotFoundError(message="Uploaded asset not found.")
            if asset.status != "pending":
                raise BadRequestError(message="Upload has already been completed.")

            await self.infra_service.complete_multipart_upload(
                object_key=asset.object_key,
                upload_id=payload.upload_id,
                parts=normalized_parts,
            )
            object_info = await self.infra_service.stat_uploaded_object(object_key=asset.object_key)
            asset.file_size = object_info["size"]
            asset.status = "active"
            asset.public_url = self.infra_service.build_public_url(asset.object_key)

        return StorageCompleteUploadResponse(
            asset_id=asset.id,
            bucket_name=asset.bucket_name,
            object_key=asset.object_key,
            status=asset.status,
            file_size=asset.file_size,
            mime_type=asset.mime_type,
            public_url=asset.public_url,
        )

    @staticmethod
    def _get_rule(biz_type: str) -> UploadRule:
        normalized = biz_type.strip().lower()
        rule = UPLOAD_RULES.get(normalized)
        if rule is None:
            raise BadRequestError(message=f"Unsupported biz_type: {biz_type}.")
        return rule

    @staticmethod
    def _validate_upload_payload(
        payload: StoragePresignUploadRequest,
        rule: UploadRule,
        extension: str,
    ) -> None:
        if payload.file_size > rule.max_size:
            raise BadRequestError(
                message=f"File size exceeds limit for {payload.biz_type}.",
                data={"max_size": rule.max_size},
            )

        mime_type = payload.mime_type.strip().lower()
        if not any(
            mime_type == prefix or mime_type.startswith(prefix) for prefix in rule.mime_prefixes
        ):
            raise BadRequestError(message=f"Unsupported mime_type: {payload.mime_type}.")

        if not extension:
            raise BadRequestError(message="File extension is required.")
        if extension not in rule.allowed_extensions:
            raise BadRequestError(message=f"Unsupported file extension: {extension}.")

    @staticmethod
    def _build_object_key(prefix: str, extension: str) -> str:
        now: datetime = utc_now_naive()
        file_name = f"{uuid4().hex}{extension}"
        return f"{prefix}/{now.year:04d}/{now.month:02d}/{now.day:02d}/{file_name}"

    @staticmethod
    def _resolve_part_size(file_size: int) -> int:
        calculated = max(
            MULTIPART_DEFAULT_PART_SIZE,
            ceil(file_size / MULTIPART_MAX_PARTS),
            MULTIPART_MIN_PART_SIZE,
        )
        return calculated

    @staticmethod
    def _normalize_multipart_parts(parts: list) -> list[dict[str, str | int]]:
        normalized: list[dict[str, str | int]] = []
        seen_part_numbers: set[int] = set()

        for item in sorted(parts, key=lambda current: current.part_number):
            if item.part_number in seen_part_numbers:
                raise BadRequestError(message="Duplicate multipart part numbers are not allowed.")
            seen_part_numbers.add(item.part_number)
            normalized.append(
                {
                    "part_number": item.part_number,
                    "etag": item.etag.strip().strip('"'),
                }
            )

        return normalized
