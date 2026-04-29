from fastapi import APIRouter

from app.api.deps import CurrentUser, DBSession
from app.core.response import success
from app.modules.storage.schemas import (
    StorageCompleteMultipartUploadRequest,
    StorageCompleteUploadRequest,
    StorageInitiateMultipartUploadRequest,
    StoragePresignUploadRequest,
    StoragePresignUploadPartRequest,
)
from app.modules.storage.service import StorageAppService

router = APIRouter()


@router.post("/presign-upload")
async def presign_upload(
    payload: StoragePresignUploadRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = StorageAppService()
    data = await service.presign_upload(
        session,
        user_id=int(current_user.sub),
        payload=payload,
    )
    return success(data=data.model_dump())


@router.post("/initiate-multipart-upload")
async def initiate_multipart_upload(
    payload: StorageInitiateMultipartUploadRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = StorageAppService()
    data = await service.initiate_multipart_upload(
        session,
        user_id=int(current_user.sub),
        payload=payload,
    )
    return success(data=data.model_dump())


@router.post("/presign-upload-part")
async def presign_upload_part(
    payload: StoragePresignUploadPartRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = StorageAppService()
    data = await service.presign_upload_part(
        session,
        user_id=int(current_user.sub),
        payload=payload,
    )
    return success(data=data.model_dump())


@router.post("/complete-upload")
async def complete_upload(
    payload: StorageCompleteUploadRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = StorageAppService()
    data = await service.complete_upload(
        session,
        user_id=int(current_user.sub),
        payload=payload,
    )
    return success(data=data.model_dump())


@router.post("/complete-multipart-upload")
async def complete_multipart_upload(
    payload: StorageCompleteMultipartUploadRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = StorageAppService()
    data = await service.complete_multipart_upload(
        session,
        user_id=int(current_user.sub),
        payload=payload,
    )
    return success(data=data.model_dump())
