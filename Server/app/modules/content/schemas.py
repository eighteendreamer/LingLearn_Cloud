from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ContentAuthorResponse(BaseModel):
    user_id: int
    display_name: str
    avatar_url: str | None = None
    is_following: bool = False


class ContentCategoryResponse(BaseModel):
    id: int
    name: str


class ContentInteractionResponse(BaseModel):
    views_count: int
    likes_count: int
    comments_count: int
    favorites_count: int
    shares_count: int
    liked: bool = False
    favorited: bool = False


class ContentInteractionMutationResponse(BaseModel):
    content_id: int
    interaction: ContentInteractionResponse


class ContentCommentResponse(BaseModel):
    id: int
    content_item_id: int
    user_id: int
    display_name: str
    avatar_url: str | None = None
    content: str
    like_count: int
    parent_id: int | None = None
    root_id: int | None = None
    reply_to_user_id: int | None = None
    reply_to_display_name: str | None = None
    created_at: datetime


class ContentCommentListResponse(BaseModel):
    list: list[ContentCommentResponse]
    page: int
    page_size: int
    total: int
    has_more: bool


class ContentVideoResponse(BaseModel):
    id: int
    title: str
    summary: str | None = None
    hashtags: list[str] = Field(default_factory=list)
    author: ContentAuthorResponse
    category: ContentCategoryResponse | None = None
    cover_url: str | None = None
    video_url: str | None = None
    duration_seconds: int | None = None
    bvid: str | None = None
    interaction: ContentInteractionResponse
    has_quiz: bool = False
    quiz_count: int = 0
    published_at: datetime | None = None


class FeedVideosResponse(BaseModel):
    list: list[ContentVideoResponse]
    next_cursor: str | None = None
    has_more: bool


class ContentFavoriteItemResponse(BaseModel):
    content: ContentVideoResponse
    favorited_at: datetime


class ContentWatchHistoryItemResponse(BaseModel):
    content: ContentVideoResponse
    watch_seconds: int
    watch_progress: float
    last_position_seconds: int
    completed: bool
    last_viewed_at: datetime


class ContentCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    summary: str | None = Field(default=None, max_length=500)
    category_id: int | None = Field(default=None, gt=0)
    cover_asset_id: int | None = Field(default=None, gt=0)
    primary_media_asset_id: int | None = Field(default=None, gt=0)
    content_type: str = Field(default="short_video", min_length=1, max_length=32)
    hashtags: list[str] = Field(default_factory=list, max_length=20)
    duration_seconds: int | None = Field(default=None, ge=0)
    allow_comment: bool = True
    allow_duet: bool = False


class ContentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    summary: str | None = Field(default=None, max_length=500)
    category_id: int | None = Field(default=None, ge=1)
    cover_asset_id: int | None = Field(default=None, ge=1)
    primary_media_asset_id: int | None = Field(default=None, ge=1)
    hashtags: list[str] | None = Field(default=None, max_length=20)
    duration_seconds: int | None = Field(default=None, ge=0)
    allow_comment: bool | None = None
    allow_duet: bool | None = None


class FeedQueryParams(BaseModel):
    cursor: str | None = None
    limit: int = Field(default=10, ge=1, le=20)
    category_id: int | None = Field(default=None, gt=0)
    recommend_type: str = Field(default="for_you", min_length=1, max_length=32)


class ContentShareRequest(BaseModel):
    share_channel: str = Field(default="internal", min_length=1, max_length=32)


class ContentCommentCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1000)
    parent_id: int | None = Field(default=None, gt=0)


class ContentWatchProgressRequest(BaseModel):
    watch_seconds: int = Field(default=0, ge=0)
    watch_progress: float = Field(default=0, ge=0, le=100)
    last_position_seconds: int = Field(default=0, ge=0)
    completed: bool = False


class ContentInteractionBatchLikeItemRequest(BaseModel):
    client_id: str = Field(min_length=1, max_length=64)
    action: Literal["set_like"]
    content_id: int = Field(gt=0)
    liked: bool


class ContentInteractionBatchFavoriteItemRequest(BaseModel):
    client_id: str = Field(min_length=1, max_length=64)
    action: Literal["set_favorite"]
    content_id: int = Field(gt=0)
    favorited: bool


class ContentInteractionBatchCommentItemRequest(BaseModel):
    client_id: str = Field(min_length=1, max_length=64)
    action: Literal["create_comment"]
    content_id: int = Field(gt=0)
    content: str = Field(min_length=1, max_length=1000)
    parent_id: int | None = Field(default=None, gt=0)


ContentInteractionBatchItemRequest = (
    ContentInteractionBatchLikeItemRequest
    | ContentInteractionBatchFavoriteItemRequest
    | ContentInteractionBatchCommentItemRequest
)


class ContentInteractionBatchSyncRequest(BaseModel):
    items: list[ContentInteractionBatchItemRequest] = Field(default_factory=list, max_length=100)


class ContentInteractionBatchItemResponse(BaseModel):
    client_id: str
    action: str
    content_id: int
    interaction: ContentInteractionResponse
    comment: ContentCommentResponse | None = None


class ContentInteractionBatchSyncResponse(BaseModel):
    items: list[ContentInteractionBatchItemResponse] = Field(default_factory=list)
