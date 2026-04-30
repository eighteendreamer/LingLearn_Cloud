from __future__ import annotations

from pydantic import BaseModel


class DiscoverCategoryResponse(BaseModel):
    id: int
    name: str


class DiscoverHotTopicResponse(BaseModel):
    id: int
    name: str
    content_count: int
    views_count: int
    likes_count: int
    trend_score: float


class DiscoverHotTagResponse(BaseModel):
    id: int
    name: str
    content_count: int
    views_count: int
    likes_count: int
    trend_score: float
