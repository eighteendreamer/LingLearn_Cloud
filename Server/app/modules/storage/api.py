from fastapi import APIRouter

from app.api.deps import CurrentUser, DBSession
from app.core.response import success
from app.modules.storage.schemas import (
    StorageCompleteUploadRequest,
    StoragePresignUploadRequest,
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
