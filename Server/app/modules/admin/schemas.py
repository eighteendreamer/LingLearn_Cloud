from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


# ============ 管理员用户相关 ============
class AdminUserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    real_name: str | None = None
    phone: str | None = None


class AdminUserCreate(AdminUserBase):
    password: str = Field(..., min_length=6, max_length=128)
    role_id: int


class AdminUserUpdate(BaseModel):
    email: EmailStr | None = None
    real_name: str | None = None
    phone: str | None = None
    role_id: int | None = None
    status: str | None = None


class AdminUserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=128)


class AdminUserResponse(AdminUserBase):
    id: int
    role_id: int
    role_name: str
    status: str
    last_login_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 管理员角色相关 ============
class AdminRoleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=64)
    description: str | None = None
    permissions: list[str] = Field(default_factory=list)


class AdminRoleCreate(AdminRoleBase):
    pass


class AdminRoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    permissions: list[str] | None = None
    status: str | None = None


class AdminRoleResponse(AdminRoleBase):
    id: int
    status: str
    is_super: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 管理员登录相关 ============
class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    admin_user: AdminUserResponse


# ============ 操作日志相关 ============
class AdminOperationLogResponse(BaseModel):
    id: int
    admin_user_id: int
    admin_username: str
    module: str
    action: str
    target_type: str | None
    target_id: int | None
    description: str | None
    ip_address: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 用户管理相关 ============
class UserManagementResponse(BaseModel):
    id: int
    username: str
    email: str
    phone: str | None
    status: str
    display_name: str
    followers_count: int
    following_count: int
    total_learning_minutes: int
    register_source: str
    email_verified: bool
    phone_verified: bool
    last_login_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class UserStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(active|suspended|banned)$")
    reason: str | None = None


# ============ 内容管理相关 ============
class ContentManagementResponse(BaseModel):
    id: int
    title: str
    author_id: int
    author_name: str
    content_type: str
    category_name: str | None
    audit_status: str
    publish_status: str
    views_count: int
    likes_count: int
    comments_count: int
    favorites_count: int
    shares_count: int
    hot_score: float
    published_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class ContentAuditUpdate(BaseModel):
    audit_status: str = Field(..., pattern="^(pending|approved|rejected)$")
    audit_reason: str | None = None


class ContentPublishUpdate(BaseModel):
    publish_status: str = Field(..., pattern="^(draft|published|archived)$")


# ============ 评论管理相关 ============
class CommentManagementResponse(BaseModel):
    id: int
    content_item_id: int
    content_title: str
    user_id: int
    username: str
    content: str
    like_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CommentStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(normal|hidden|deleted)$")
    reason: str | None = None


# ============ 分类管理相关 ============
class CategoryManagementCreate(BaseModel):
    parent_id: int | None = None
    name: str = Field(..., min_length=1, max_length=64)
    slug: str = Field(..., min_length=1, max_length=64)
    description: str | None = None
    icon: str | None = None
    sort_order: int = 0


class CategoryManagementUpdate(BaseModel):
    parent_id: int | None = None
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    icon: str | None = None
    sort_order: int | None = None
    status: str | None = None


class CategoryManagementResponse(BaseModel):
    id: int
    parent_id: int | None
    name: str
    slug: str
    description: str | None
    icon: str | None
    sort_order: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 标签管理相关 ============
class TagManagementCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    slug: str = Field(..., min_length=1, max_length=64)
    tag_type: str = "topic"


class TagManagementUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    tag_type: str | None = None
    status: str | None = None


class TagManagementResponse(BaseModel):
    id: int
    name: str
    slug: str
    tag_type: str
    status: str
    use_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 统计数据相关 ============
class DashboardStats(BaseModel):
    total_users: int
    active_users: int
    new_users_today: int
    total_contents: int
    pending_audit_contents: int
    new_contents_today: int
    total_comments: int
    pending_comments: int
    total_views_today: int
    total_interactions_today: int


class UserGrowthStats(BaseModel):
    date: str
    new_users: int
    active_users: int


class ContentStats(BaseModel):
    date: str
    new_contents: int
    total_views: int
    total_likes: int
    total_comments: int


class CategoryStats(BaseModel):
    category_id: int
    category_name: str
    content_count: int
    total_views: int
    total_likes: int
