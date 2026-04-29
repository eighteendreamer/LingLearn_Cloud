from pydantic import BaseModel, Field


class StoragePresignUploadRequest(BaseModel):
    biz_type: str = Field(min_length=1, max_length=32)
    file_name: str = Field(min_length=1, max_length=255)
    file_size: int = Field(ge=1, le=2 * 1024 * 1024 * 1024)
    mime_type: str = Field(min_length=1, max_length=128)


class StoragePresignUploadResponse(BaseModel):
    asset_id: int
    bucket_name: str
    object_key: str
    upload_url: str
    headers: dict[str, str]


class StorageCompleteUploadRequest(BaseModel):
    asset_id: int = Field(gt=0)


class StorageCompleteUploadResponse(BaseModel):
    asset_id: int
    bucket_name: str
    object_key: str
    status: str
    file_size: int
    mime_type: str
    public_url: str | None
