from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DBSession
from app.core.response import success
from app.core.security import create_access_token, create_refresh_token
from app.modules.admin import schemas
from app.modules.admin.deps import get_current_admin_user
from app.modules.admin.models import AdminUser
from app.modules.admin.service import (
    AdminAuthService,
    AdminRoleService,
    AdminUserService,
    CategoryManagementService,
    CommentManagementService,
    ContentManagementService,
    CourseManagementService,
    OperationLogService,
    StatisticsService,
    TagManagementService,
    UserManagementService,
)
from app.modules.storage.schemas import (
    StorageCompleteMultipartUploadRequest,
    StorageCompleteUploadRequest,
    StorageInitiateMultipartUploadRequest,
    StoragePresignUploadPartRequest,
    StoragePresignUploadRequest,
)
from app.db.session import get_session_factory
from app.modules.storage.service import StorageAppService

router = APIRouter(prefix="/admin")


def model_to_dict(obj: Any) -> dict:
    """将 SQLAlchemy 模型或 Pydantic 模型转换为字典"""
    if obj is None:
        return None
    
    # 如果是 Pydantic 模型
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    
    # 如果是 SQLAlchemy Row 对象
    if hasattr(obj, '_mapping'):
        result = {}
        for key, value in obj._mapping.items():
            # 如果值是 SQLAlchemy 模型对象，递归转换并合并到结果中
            if hasattr(value, '__table__'):
                nested_dict = model_to_dict(value)
                if nested_dict:
                    result.update(nested_dict)
            # 如果值是 datetime 对象
            elif hasattr(value, 'isoformat'):
                result[key] = value.isoformat()
            # 如果值不是 None，直接添加
            elif value is not None:
                result[key] = value
        return result
    
    # 如果是 SQLAlchemy 模型对象
    if hasattr(obj, '__table__'):
        from sqlalchemy import inspect as sa_inspect
        result = {}
        for attr in sa_inspect(type(obj)).column_attrs:
            value = getattr(obj, attr.key)
            if hasattr(value, 'isoformat'):
                result[attr.key] = value.isoformat()
            else:
                result[attr.key] = value
        return result
    
    # 如果是普通对象，尝试转换为字典
    if hasattr(obj, '__dict__'):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    
    return obj


def serialize_items(items: list) -> list:
    """序列化列表中的所有项"""
    result = []
    for item in items:
        if isinstance(item, dict):
            result.append(item)
        else:
            result.append(model_to_dict(item))
    return result


# ============ 管理员认证相关 ============
@router.post("/auth/login")
async def admin_login(
    login_data: schemas.AdminLoginRequest,
    request: Request,
    db: DBSession,
):
    """管理员登录"""
    admin = await AdminAuthService.authenticate_admin(
        db, login_data.username, login_data.password
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 生成令牌（使用extra参数标记为admin类型）
    access_token = create_access_token(str(admin.id))
    refresh_token = create_refresh_token(str(admin.id))

    # 记录登录日志
    await OperationLogService.create_log(
        db,
        admin_user_id=admin.id,
        module="auth",
        action="login",
        description="管理员登录",
        ip_address=request.client.host if request.client else None,
    )

    # 构建响应数据
    admin_user_data = {
        "id": admin.id,
        "username": admin.username,
        "email": admin.email,
        "real_name": admin.real_name,
        "role_id": admin.role_id,
        "role_name": admin.role.name if admin.role else "未知角色",
        "status": admin.status,
        "last_login_at": admin.last_login_at.isoformat() if admin.last_login_at else None,
        "created_at": admin.created_at.isoformat() if admin.created_at else None,
    }

    return success(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "admin_user": admin_user_data,
        }
    )


@router.get("/auth/me")
async def get_current_admin(
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """获取当前管理员信息"""
    admin_data = model_to_dict(current_admin)
    return success(data=admin_data)


# ============ 管理员用户管理 ============
@router.post("/users")
async def create_admin_user(
    user_data: schemas.AdminUserCreate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """创建管理员用户"""
    admin = await AdminUserService.create_admin_user(db, user_data)

    await OperationLogService.create_log(
        db,
        admin_user_id=current_admin.id,
        module="admin_user",
        action="create",
        target_type="admin_user",
        target_id=admin.id,
        description=f"创建管理员用户: {admin.username}",
    )

    return success(data=model_to_dict(admin))


@router.get("/users")
async def get_admin_users(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = None,
):
    """获取管理员用户列表"""
    skip = (page - 1) * page_size
    result = await AdminUserService.get_admin_users(db, skip, page_size, keyword)

    return success(
        data={
            "items": serialize_items(result["items"]),
            "total": result["total"],
            "page": page,
            "page_size": page_size,
        }
    )


@router.put("/users/{user_id}")
async def update_admin_user(
    user_id: int,
    user_data: schemas.AdminUserUpdate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """更新管理员用户"""
    admin = await AdminUserService.update_admin_user(db, user_id, user_data)

    if not admin:
        raise HTTPException(status_code=404, detail="管理员用户不存在")

    await OperationLogService.create_log(
        db,
        admin_user_id=current_admin.id,
        module="admin_user",
        action="update",
        target_type="admin_user",
        target_id=user_id,
        description=f"更新管理员用户: {admin.username}",
    )

    return success(data=model_to_dict(admin))


# ============ 角色管理 ============
@router.post("/roles")
async def create_role(
    role_data: schemas.AdminRoleCreate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """创建角色"""
    role = await AdminRoleService.create_role(db, role_data)
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="role", action="create",
        target_type="role", target_id=role.id, description=f"创建角色: {role.name}",
    )
    return success(data=model_to_dict(role))


@router.get("/roles")
async def get_roles(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """获取角色列表"""
    skip = (page - 1) * page_size
    result = await AdminRoleService.get_roles(db, skip, page_size)
    return success(data={"items": serialize_items(result["items"]), "total": result["total"], "page": page, "page_size": page_size})


@router.put("/roles/{role_id}")
async def update_role(
    role_id: int,
    role_data: schemas.AdminRoleUpdate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """更新角色"""
    role = await AdminRoleService.update_role(db, role_id, role_data)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="role", action="update",
        target_type="role", target_id=role_id, description=f"更新角色: {role.name}",
    )
    return success(data=model_to_dict(role))


# ============ 用户管理 ============
@router.get("/management/users")
async def get_users(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = None,
    status: str | None = None,
):
    """获取用户列表"""
    skip = (page - 1) * page_size
    result = await UserManagementService.get_users(db, skip, page_size, keyword, status)
    
    return success(data={"items": serialize_items(result["items"]), "total": result["total"], "page": page, "page_size": page_size})


@router.get("/management/users/{user_id}")
async def get_user_detail(
    user_id: int,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """获取用户详情"""
    user_data = await UserManagementService.get_user_detail(db, user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="用户不存在")
    return success(data=user_data)


@router.put("/management/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    status_data: schemas.UserStatusUpdate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """更新用户状态"""
    user = await UserManagementService.update_user_status(db, user_id, status_data)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="user", action="update_status",
        target_type="user", target_id=user_id, description=f"更新用户状态: {status_data.status}",
    )
    return success(data={"message": "用户状态更新成功"})


# ============ 内容管理 ============
@router.get("/management/contents")
async def get_contents(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = None,
    audit_status: str | None = None,
    publish_status: str | None = None,
    content_type: str | None = None,
):
    """获取内容列表"""
    skip = (page - 1) * page_size
    result = await ContentManagementService.get_contents(db, skip, page_size, keyword, audit_status, publish_status, content_type)
    
    return success(data={"items": serialize_items(result["items"]), "total": result["total"], "page": page, "page_size": page_size})


@router.put("/management/contents/{content_id}/audit")
async def update_content_audit(
    content_id: int,
    audit_data: schemas.ContentAuditUpdate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """更新内容审核状态"""
    content = await ContentManagementService.update_content_audit(db, content_id, audit_data)
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="content", action="audit",
        target_type="content", target_id=content_id, description=f"审核内容: {audit_data.audit_status}",
    )
    return success(data={"message": "内容审核状态更新成功"})


@router.put("/management/contents/{content_id}/publish")
async def update_content_publish(
    content_id: int,
    publish_data: schemas.ContentPublishUpdate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """更新内容发布状态"""
    content = await ContentManagementService.update_content_publish(db, content_id, publish_data)
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="content", action="publish",
        target_type="content", target_id=content_id, description=f"更新发布状态: {publish_data.publish_status}",
    )
    return success(data={"message": "内容发布状态更新成功"})


@router.delete("/management/contents/{content_id}")
async def delete_content(
    content_id: int,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """删除内容"""
    deleted = await ContentManagementService.delete_content(db, content_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="内容不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="content", action="delete",
        target_type="content", target_id=content_id, description="删除内容",
    )
    return success(data={"message": "内容删除成功"})


# ============ 评论管理 ============
@router.get("/management/comments")
async def get_comments(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = None,
    status: str | None = None,
):
    """获取评论列表"""
    skip = (page - 1) * page_size
    result = await CommentManagementService.get_comments(db, skip, page_size, keyword, status)
    
    return success(data={"items": serialize_items(result["items"]), "total": result["total"], "page": page, "page_size": page_size})


@router.put("/management/comments/{comment_id}/status")
async def update_comment_status(
    comment_id: int,
    status_data: schemas.CommentStatusUpdate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """更新评论状态"""
    comment = await CommentManagementService.update_comment_status(db, comment_id, status_data)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="comment", action="update_status",
        target_type="comment", target_id=comment_id, description=f"更新评论状态: {status_data.status}",
    )
    return success(data={"message": "评论状态更新成功"})


# ============ 分类和标签管理 ============
@router.post("/management/categories")
async def create_category(
    category_data: schemas.CategoryManagementCreate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """创建分类"""
    category = await CategoryManagementService.create_category(db, category_data)
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="category", action="create",
        target_type="category", target_id=category.id, description=f"创建分类: {category.name}",
    )
    return success(data=model_to_dict(category))


@router.get("/management/categories")
async def get_categories(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
):
    """获取分类列表"""
    skip = (page - 1) * page_size
    result = await CategoryManagementService.get_categories(db, skip, page_size)
    return success(data={"items": serialize_items(result["items"]), "total": result["total"], "page": page, "page_size": page_size})


@router.put("/management/categories/{category_id}")
async def update_category(
    category_id: int,
    category_data: schemas.CategoryManagementUpdate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """更新分类"""
    category = await CategoryManagementService.update_category(db, category_id, category_data)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="category", action="update",
        target_type="category", target_id=category_id, description=f"更新分类: {category.name}",
    )
    return success(data=model_to_dict(category))


@router.delete("/management/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """删除分类"""
    deleted = await CategoryManagementService.delete_category(db, category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="分类不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="category", action="delete",
        target_type="category", target_id=category_id, description="删除分类",
    )
    return success(data={"message": "分类删除成功"})


@router.post("/management/tags")
async def create_tag(
    tag_data: schemas.TagManagementCreate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """创建标签"""
    tag = await TagManagementService.create_tag(db, tag_data)
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="tag", action="create",
        target_type="tag", target_id=tag.id, description=f"创建标签: {tag.name}",
    )
    return success(data=model_to_dict(tag))


@router.get("/management/tags")
async def get_tags(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    keyword: str | None = None,
):
    """获取标签列表"""
    skip = (page - 1) * page_size
    result = await TagManagementService.get_tags(db, skip, page_size, keyword)
    return success(data={"items": serialize_items(result["items"]), "total": result["total"], "page": page, "page_size": page_size})


@router.put("/management/tags/{tag_id}")
async def update_tag(
    tag_id: int,
    tag_data: schemas.TagManagementUpdate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """更新标签"""
    tag = await TagManagementService.update_tag(db, tag_id, tag_data)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="tag", action="update",
        target_type="tag", target_id=tag_id, description=f"更新标签: {tag.name}",
    )
    return success(data=model_to_dict(tag))


@router.delete("/management/tags/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """删除标签"""
    deleted = await TagManagementService.delete_tag(db, tag_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="标签不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="tag", action="delete",
        target_type="tag", target_id=tag_id, description="删除标签",
    )
    return success(data={"message": "标签删除成功"})


# ============ 课程管理 ============
@router.get("/management/courses")
async def get_courses(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = None,
    status: str | None = None,
):
    skip = (page - 1) * page_size
    result = await CourseManagementService.get_courses(db, skip, page_size, keyword, status)
    return success(data={"items": serialize_items(result["items"]), "total": result["total"], "page": page, "page_size": page_size})


@router.post("/management/courses")
async def create_course(
    course_data: schemas.CourseCreate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    course = await CourseManagementService.create_course(db, course_data, current_admin.id)
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="course", action="create",
        target_type="course", target_id=course.id, description=f"创建课程: {course.title}",
    )
    return success(data=model_to_dict(course))


@router.put("/management/courses/{course_id}")
async def update_course(
    course_id: int,
    course_data: schemas.CourseUpdate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    course = await CourseManagementService.update_course(db, course_id, course_data)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="course", action="update",
        target_type="course", target_id=course_id, description=f"更新课程: {course.title}",
    )
    return success(data=model_to_dict(course))


@router.delete("/management/courses/{course_id}")
async def delete_course(
    course_id: int,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    deleted = await CourseManagementService.delete_course(db, course_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="课程不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="course", action="delete",
        target_type="course", target_id=course_id, description="删除课程",
    )
    return success(data={"message": "课程删除成功"})


@router.get("/management/courses/{course_id}/lessons")
async def get_course_lessons(
    course_id: int,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    lessons = await CourseManagementService.get_course_lessons(db, course_id)
    return success(data={"items": serialize_items(lessons), "total": len(lessons)})


@router.post("/management/courses/{course_id}/lessons")
async def create_course_lesson(
    course_id: int,
    lesson_data: schemas.CourseLessonCreate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    lesson = await CourseManagementService.create_lesson(db, course_id, lesson_data)
    if not lesson:
        raise HTTPException(status_code=404, detail="课程不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="course_lesson", action="create",
        target_type="course_lesson", target_id=lesson.id, description=f"创建课时: {lesson.title}",
    )
    return success(data=model_to_dict(lesson))


@router.put("/management/courses/{course_id}/lessons/{lesson_id}")
async def update_course_lesson(
    course_id: int,
    lesson_id: int,
    lesson_data: schemas.CourseLessonUpdate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    lesson = await CourseManagementService.update_lesson(db, course_id, lesson_id, lesson_data)
    if not lesson:
        raise HTTPException(status_code=404, detail="课时不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="course_lesson", action="update",
        target_type="course_lesson", target_id=lesson_id, description=f"更新课时: {lesson.title}",
    )
    return success(data=model_to_dict(lesson))


@router.delete("/management/courses/{course_id}/lessons/{lesson_id}")
async def delete_course_lesson(
    course_id: int,
    lesson_id: int,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    deleted = await CourseManagementService.delete_lesson(db, course_id, lesson_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="课时不存在")
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="course_lesson", action="delete",
        target_type="course_lesson", target_id=lesson_id, description="删除课时",
    )
    return success(data={"message": "课时删除成功"})


@router.get("/management/content-items")
async def list_content_items(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    keyword: str | None = None,
):
    skip = (page - 1) * page_size
    result = await CourseManagementService.list_content_items_for_link(db, skip, page_size, keyword)
    return success(data={"items": serialize_items(result["items"]), "total": result["total"], "page": page, "page_size": page_size})


# ============ 管理后台存储上传 ============
@router.post("/management/storage/presign-upload")
async def admin_presign_upload(
    payload: StoragePresignUploadRequest,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    service = StorageAppService()
    async with get_session_factory()() as session:
        data = await service.presign_upload(session, user_id=None, payload=payload)
    return success(data=data.model_dump())


@router.post("/management/storage/initiate-multipart-upload")
async def admin_initiate_multipart_upload(
    payload: StorageInitiateMultipartUploadRequest,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    service = StorageAppService()
    async with get_session_factory()() as session:
        data = await service.initiate_multipart_upload(session, user_id=None, payload=payload)
    return success(data=data.model_dump())


@router.post("/management/storage/presign-upload-part")
async def admin_presign_upload_part(
    payload: StoragePresignUploadPartRequest,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    service = StorageAppService()
    async with get_session_factory()() as session:
        data = await service.presign_upload_part(session, user_id=None, payload=payload)
    return success(data=data.model_dump())


@router.post("/management/storage/complete-upload")
async def admin_complete_upload(
    payload: StorageCompleteUploadRequest,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    service = StorageAppService()
    async with get_session_factory()() as session:
        data = await service.complete_upload(session, user_id=None, payload=payload)
    return success(data=data.model_dump())


@router.post("/management/storage/complete-multipart-upload")
async def admin_complete_multipart_upload(
    payload: StorageCompleteMultipartUploadRequest,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    service = StorageAppService()
    async with get_session_factory()() as session:
        data = await service.complete_multipart_upload(session, user_id=None, payload=payload)
    return success(data=data.model_dump())


@router.post("/management/content-items")
async def admin_create_content_item(
    payload: schemas.AdminContentItemCreate,
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    from app.modules.content.models import ContentItem
    content = ContentItem(
        author_id=1,
        title=payload.title,
        primary_media_asset_id=payload.primary_media_asset_id,
        content_type=payload.content_type,
        category_id=payload.category_id,
        audit_status="approved",
        publish_status="published",
    )
    db.add(content)
    await db.commit()
    await db.refresh(content)
    await OperationLogService.create_log(
        db, admin_user_id=current_admin.id, module="content", action="create",
        target_type="content_item", target_id=content.id, description=f"管理后台创建内容: {content.title}",
    )
    return success(data={"id": content.id, "title": content.title})


# ============ 统计数据 ============
@router.get("/statistics/dashboard")
async def get_dashboard_stats(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """获取仪表盘统计数据"""
    stats = await StatisticsService.get_dashboard_stats(db)
    return success(data=model_to_dict(stats))


@router.get("/statistics/user-growth")
async def get_user_growth_stats(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    days: int = Query(30, ge=1, le=365),
):
    """获取用户增长统计"""
    stats = await StatisticsService.get_user_growth_stats(db, days)
    return success(data=[model_to_dict(s) for s in stats])


@router.get("/statistics/content")
async def get_content_stats(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    days: int = Query(30, ge=1, le=365),
):
    """获取内容统计"""
    stats = await StatisticsService.get_content_stats(db, days)
    return success(data=[model_to_dict(s) for s in stats])


@router.get("/statistics/category")
async def get_category_stats(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
):
    """获取分类统计"""
    stats = await StatisticsService.get_category_stats(db)
    return success(data=[model_to_dict(s) for s in stats])


# ============ 操作日志 ============
@router.get("/logs")
async def get_operation_logs(
    db: DBSession,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    admin_user_id: int | None = None,
    module: str | None = None,
):
    """获取操作日志列表"""
    skip = (page - 1) * page_size
    result = await OperationLogService.get_logs(db, skip, page_size, admin_user_id, module)
    
    return success(data={"items": serialize_items(result["items"]), "total": result["total"], "page": page, "page_size": page_size})

