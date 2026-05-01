from pydantic import BaseModel, Field


class SearchContentsQuery(BaseModel):
    keyword: str | None = Field(default=None, max_length=120)
    category_id: int | None = Field(default=None, gt=0)
