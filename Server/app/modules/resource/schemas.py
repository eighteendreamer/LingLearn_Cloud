from datetime import datetime

from pydantic import BaseModel


class ResourceListItemResponse(BaseModel):
    id: int
    title: str
    description: str | None
    resource_type: str
    file_url: str | None
    file_size: int
    download_count: int
    created_at: datetime
