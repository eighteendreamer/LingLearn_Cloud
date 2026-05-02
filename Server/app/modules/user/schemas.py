from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class UserStatsResponse(BaseModel):
    total_learning_minutes: int
    streak_days: int
    followers_count: int
    following_count: int
    likes_received_count: int


class UserProfileResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    phone: str | None
    display_name: str
    avatar_asset_id: int | None
    bio: str | None
    gender: str | None
    birthday: date | None
    location: str | None
    profession: str | None
    learning_goal: str | None
    timezone: str
    locale: str
    stats: UserStatsResponse
    created_at: datetime
    updated_at: datetime


class UserSettingsResponse(BaseModel):
    theme: str
    language: str
    daily_reminder_enabled: bool
    progress_notice_enabled: bool
    badge_notice_enabled: bool
    weekly_report_enabled: bool
    two_factor_enabled: bool
    profile_public: bool
    learning_data_public: bool


class CurrentUserResponse(BaseModel):
    profile: UserProfileResponse
    settings: UserSettingsResponse


class UserProfileUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=64)
    bio: str | None = Field(default=None, max_length=500)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    location: str | None = Field(default=None, max_length=128)
    profession: str | None = Field(default=None, max_length=64)
    birthday: date | None = None
    learning_goal: str | None = Field(default=None, max_length=500)


class UserSettingsUpdateRequest(BaseModel):
    theme: str | None = Field(default=None, max_length=20)
    language: str | None = Field(default=None, max_length=16)
    daily_reminder_enabled: bool | None = None
    progress_notice_enabled: bool | None = None
    badge_notice_enabled: bool | None = None
    weekly_report_enabled: bool | None = None
    two_factor_enabled: bool | None = None
    profile_public: bool | None = None
    learning_data_public: bool | None = None


class PublicUserResponse(BaseModel):
    user_id: int
    username: str
    display_name: str
    avatar_asset_id: int | None
    bio: str | None
    location: str | None
    profession: str | None
    learning_goal: str | None
    stats: UserStatsResponse
    is_following: bool = False


class UserFollowActionResponse(BaseModel):
    target_user_id: int
    is_following: bool


class UserWorkListItemResponse(BaseModel):
    id: int
    title: str
    summary: str | None
    cover_url: str | None = None
    published_at: datetime | None = None


class UserPreferenceFacetResponse(BaseModel):
    key: str
    name: str
    score: float
    likes_count: int
    favorites_count: int
    content_count: int


class UserPreferenceAuthorFacetResponse(BaseModel):
    user_id: int
    display_name: str
    score: float
    likes_count: int
    favorites_count: int
    content_count: int


class UserPreferenceRecentActionResponse(BaseModel):
    content_id: int
    title: str
    cover_url: str | None = None
    category_name: str | None = None
    author_name: str
    action_type: str
    acted_at: datetime


class UserPreferenceContentItemResponse(BaseModel):
    content_id: int
    title: str
    cover_url: str | None = None
    category_key: str
    category_name: str
    author_name: str
    liked: bool
    favorited: bool
    latest_acted_at: datetime


class UserPreferenceCategoryGroupResponse(BaseModel):
    key: str
    name: str
    item_count: int
    items: list[UserPreferenceContentItemResponse]


class UserLearningPreferenceInsightResponse(BaseModel):
    summary: str
    total_likes: int
    total_favorites: int
    total_interactions: int
    top_categories: list[UserPreferenceFacetResponse]
    top_tags: list[UserPreferenceFacetResponse]
    top_authors: list[UserPreferenceAuthorFacetResponse]
    recent_actions: list[UserPreferenceRecentActionResponse]
    grouped_works: list[UserPreferenceCategoryGroupResponse]
