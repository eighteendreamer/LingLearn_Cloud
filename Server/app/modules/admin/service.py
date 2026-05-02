import json
from datetime import datetime, timedelta

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password, verify_password
from app.modules.admin.models import AdminOperationLog, AdminRole, AdminUser
from app.modules.admin.schemas import (
    AdminRoleCreate,
    AdminRoleUpdate,
    AdminUserCreate,
    AdminUserUpdate,
    CategoryManagementCreate,
    CategoryManagementUpdate,
    CategoryStats,
    CommentStatusUpdate,
    ContentAuditUpdate,
    ContentPublishUpdate,
    ContentStats,
    DashboardStats,
    TagManagementCreate,
    TagManagementUpdate,
    UserGrowthStats,
    UserStatusUpdate,
)
from app.modules.auth.models import User
from app.modules.content.models import (
    ContentCategory,
    ContentComment,
    ContentItem,
    ContentLike,
    ContentViewHistory,
    Tag,
)
from app.modules.user.models import UserProfile


class AdminAuthService:
    """管理员认证服务"""

    @staticmethod
    async def authenticate_admin(
        db: AsyncSession, username: str, password: str
    ) -> AdminUser | None:
        """验证管理员登录"""
        stmt = (
            select(AdminUser)
            .where(AdminUser.username == username, AdminUser.status == "active")
            .options(selectinload(AdminUser.role))
        )
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()

        if admin and verify_password(password, admin.password_hash):
            # 更新最后登录时间
            admin.last_login_at = datetime.now()
            await db.commit()
            return admin
        return None

    @staticmethod
    async def get_admin_by_id(db: AsyncSession, admin_id: int) -> AdminUser | None:
        """根据ID获取管理员"""
        stmt = select(AdminUser).where(AdminUser.id == admin_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


class AdminUserService:
    """管理员用户管理服务"""

    @staticmethod
    async def create_admin_user(
        db: AsyncSession, admin_data: AdminUserCreate
    ) -> AdminUser:
        """创建管理员用户"""
        admin = AdminUser(
            username=admin_data.username,
            email=admin_data.email,
            password_hash=hash_password(admin_data.password),
            real_name=admin_data.real_name,
            phone=admin_data.phone,
            role_id=admin_data.role_id,
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        return admin

    @staticmethod
    async def get_admin_users(
        db: AsyncSession, skip: int = 0, limit: int = 20, keyword: str | None = None
    ):
        """获取管理员用户列表"""
        stmt = select(AdminUser).order_by(desc(AdminUser.created_at))

        if keyword:
            stmt = stmt.where(
                or_(
                    AdminUser.username.contains(keyword),
                    AdminUser.email.contains(keyword),
                    AdminUser.real_name.contains(keyword),
                )
            )

        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = await db.scalar(total_stmt)

        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        items = result.scalars().all()

        return {"total": total, "items": items}

    @staticmethod
    async def update_admin_user(
        db: AsyncSession, admin_id: int, admin_data: AdminUserUpdate
    ) -> AdminUser | None:
        """更新管理员用户"""
        stmt = select(AdminUser).where(AdminUser.id == admin_id)
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()

        if not admin:
            return None

        if admin_data.email is not None:
            admin.email = admin_data.email
        if admin_data.real_name is not None:
            admin.real_name = admin_data.real_name
        if admin_data.phone is not None:
            admin.phone = admin_data.phone
        if admin_data.role_id is not None:
            admin.role_id = admin_data.role_id
        if admin_data.status is not None:
            admin.status = admin_data.status

        await db.commit()
        await db.refresh(admin)
        return admin


class AdminRoleService:
    """管理员角色管理服务"""

    @staticmethod
    async def create_role(db: AsyncSession, role_data: AdminRoleCreate) -> AdminRole:
        """创建角色"""
        role = AdminRole(
            name=role_data.name,
            description=role_data.description,
            permissions=json.dumps(role_data.permissions),
        )
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    @staticmethod
    async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 50):
        """获取角色列表"""
        stmt = select(AdminRole).order_by(AdminRole.id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        items = result.scalars().all()

        total_stmt = select(func.count()).select_from(AdminRole)
        total = await db.scalar(total_stmt)

        return {"total": total, "items": items}

    @staticmethod
    async def update_role(
        db: AsyncSession, role_id: int, role_data: AdminRoleUpdate
    ) -> AdminRole | None:
        """更新角色"""
        stmt = select(AdminRole).where(AdminRole.id == role_id)
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()

        if not role:
            return None

        if role_data.name is not None:
            role.name = role_data.name
        if role_data.description is not None:
            role.description = role_data.description
        if role_data.permissions is not None:
            role.permissions = json.dumps(role_data.permissions)
        if role_data.status is not None:
            role.status = role_data.status

        await db.commit()
        await db.refresh(role)
        return role


class UserManagementService:
    """用户管理服务"""

    @staticmethod
    async def get_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        keyword: str | None = None,
        status: str | None = None,
    ):
        """获取用户列表"""
        stmt = (
            select(User, UserProfile)
            .outerjoin(UserProfile, User.id == UserProfile.user_id)
            .where(User.deleted_at.is_(None))
            .order_by(desc(User.created_at))
        )

        if keyword:
            stmt = stmt.where(
                or_(
                    User.username.contains(keyword),
                    User.email.contains(keyword),
                    UserProfile.display_name.contains(keyword),
                )
            )

        if status:
            stmt = stmt.where(User.status == status)

        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = await db.scalar(total_stmt)

        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        items = result.all()

        return {"total": total, "items": items}

    @staticmethod
    async def update_user_status(
        db: AsyncSession, user_id: int, status_data: UserStatusUpdate
    ) -> User | None:
        """更新用户状态"""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        user.status = status_data.status
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_user_detail(db: AsyncSession, user_id: int):
        """获取用户详情"""
        stmt = (
            select(User, UserProfile)
            .outerjoin(UserProfile, User.id == UserProfile.user_id)
            .where(User.id == user_id)
        )
        result = await db.execute(stmt)
        return result.first()


class ContentManagementService:
    """内容管理服务"""

    @staticmethod
    async def get_contents(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        keyword: str | None = None,
        audit_status: str | None = None,
        publish_status: str | None = None,
        content_type: str | None = None,
    ):
        """获取内容列表"""
        stmt = (
            select(ContentItem, UserProfile.display_name, ContentCategory.name)
            .outerjoin(UserProfile, ContentItem.author_id == UserProfile.user_id)
            .outerjoin(ContentCategory, ContentItem.category_id == ContentCategory.id)
            .where(ContentItem.deleted_at.is_(None))
            .order_by(desc(ContentItem.created_at))
        )

        if keyword:
            stmt = stmt.where(ContentItem.title.contains(keyword))

        if audit_status:
            stmt = stmt.where(ContentItem.audit_status == audit_status)

        if publish_status:
            stmt = stmt.where(ContentItem.publish_status == publish_status)

        if content_type:
            stmt = stmt.where(ContentItem.content_type == content_type)

        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = await db.scalar(total_stmt)

        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        items = result.all()

        return {"total": total, "items": items}

    @staticmethod
    async def update_content_audit(
        db: AsyncSession, content_id: int, audit_data: ContentAuditUpdate
    ) -> ContentItem | None:
        """更新内容审核状态"""
        stmt = select(ContentItem).where(ContentItem.id == content_id)
        result = await db.execute(stmt)
        content = result.scalar_one_or_none()

        if not content:
            return None

        content.audit_status = audit_data.audit_status
        await db.commit()
        await db.refresh(content)
        return content

    @staticmethod
    async def update_content_publish(
        db: AsyncSession, content_id: int, publish_data: ContentPublishUpdate
    ) -> ContentItem | None:
        """更新内容发布状态"""
        stmt = select(ContentItem).where(ContentItem.id == content_id)
        result = await db.execute(stmt)
        content = result.scalar_one_or_none()

        if not content:
            return None

        content.publish_status = publish_data.publish_status
        if publish_data.publish_status == "published" and not content.published_at:
            content.published_at = datetime.now()

        await db.commit()
        await db.refresh(content)
        return content

    @staticmethod
    async def delete_content(db: AsyncSession, content_id: int) -> bool:
        """删除内容（软删除）"""
        stmt = select(ContentItem).where(ContentItem.id == content_id)
        result = await db.execute(stmt)
        content = result.scalar_one_or_none()

        if not content:
            return False

        content.deleted_at = datetime.now()
        await db.commit()
        return True


class CommentManagementService:
    """评论管理服务"""

    @staticmethod
    async def get_comments(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        keyword: str | None = None,
        status: str | None = None,
    ):
        """获取评论列表"""
        stmt = (
            select(ContentComment, User.username, ContentItem.title)
            .join(User, ContentComment.user_id == User.id)
            .join(ContentItem, ContentComment.content_item_id == ContentItem.id)
            .where(ContentComment.deleted_at.is_(None))
            .order_by(desc(ContentComment.created_at))
        )

        if keyword:
            stmt = stmt.where(ContentComment.content.contains(keyword))

        if status:
            stmt = stmt.where(ContentComment.status == status)

        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = await db.scalar(total_stmt)

        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        items = result.all()

        return {"total": total, "items": items}

    @staticmethod
    async def update_comment_status(
        db: AsyncSession, comment_id: int, status_data: CommentStatusUpdate
    ) -> ContentComment | None:
        """更新评论状态"""
        stmt = select(ContentComment).where(ContentComment.id == comment_id)
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()

        if not comment:
            return None

        comment.status = status_data.status
        if status_data.status == "deleted":
            comment.deleted_at = datetime.now()

        await db.commit()
        await db.refresh(comment)
        return comment


class CategoryManagementService:
    """分类管理服务"""

    @staticmethod
    async def create_category(
        db: AsyncSession, category_data: CategoryManagementCreate
    ) -> ContentCategory:
        """创建分类"""
        category = ContentCategory(
            parent_id=category_data.parent_id,
            name=category_data.name,
            slug=category_data.slug,
            description=category_data.description,
            icon=category_data.icon,
            sort_order=category_data.sort_order,
        )
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
        """获取分类列表"""
        stmt = (
            select(ContentCategory)
            .order_by(ContentCategory.sort_order, ContentCategory.id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        items = result.scalars().all()

        total_stmt = select(func.count()).select_from(ContentCategory)
        total = await db.scalar(total_stmt)

        return {"total": total, "items": items}

    @staticmethod
    async def update_category(
        db: AsyncSession, category_id: int, category_data: CategoryManagementUpdate
    ) -> ContentCategory | None:
        """更新分类"""
        stmt = select(ContentCategory).where(ContentCategory.id == category_id)
        result = await db.execute(stmt)
        category = result.scalar_one_or_none()

        if not category:
            return None

        if category_data.parent_id is not None:
            category.parent_id = category_data.parent_id
        if category_data.name is not None:
            category.name = category_data.name
        if category_data.slug is not None:
            category.slug = category_data.slug
        if category_data.description is not None:
            category.description = category_data.description
        if category_data.icon is not None:
            category.icon = category_data.icon
        if category_data.sort_order is not None:
            category.sort_order = category_data.sort_order
        if category_data.status is not None:
            category.status = category_data.status

        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int) -> bool:
        """删除分类"""
        stmt = select(ContentCategory).where(ContentCategory.id == category_id)
        result = await db.execute(stmt)
        category = result.scalar_one_or_none()

        if not category:
            return False

        await db.delete(category)
        await db.commit()
        return True


class TagManagementService:
    """标签管理服务"""

    @staticmethod
    async def create_tag(db: AsyncSession, tag_data: TagManagementCreate) -> Tag:
        """创建标签"""
        tag = Tag(
            name=tag_data.name,
            slug=tag_data.slug,
            tag_type=tag_data.tag_type,
        )
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        return tag

    @staticmethod
    async def get_tags(
        db: AsyncSession, skip: int = 0, limit: int = 50, keyword: str | None = None
    ):
        """获取标签列表"""
        stmt = select(Tag).order_by(desc(Tag.use_count))

        if keyword:
            stmt = stmt.where(Tag.name.contains(keyword))

        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = await db.scalar(total_stmt)

        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        items = result.scalars().all()

        return {"total": total, "items": items}

    @staticmethod
    async def update_tag(
        db: AsyncSession, tag_id: int, tag_data: TagManagementUpdate
    ) -> Tag | None:
        """更新标签"""
        stmt = select(Tag).where(Tag.id == tag_id)
        result = await db.execute(stmt)
        tag = result.scalar_one_or_none()

        if not tag:
            return None

        if tag_data.name is not None:
            tag.name = tag_data.name
        if tag_data.slug is not None:
            tag.slug = tag_data.slug
        if tag_data.tag_type is not None:
            tag.tag_type = tag_data.tag_type
        if tag_data.status is not None:
            tag.status = tag_data.status

        await db.commit()
        await db.refresh(tag)
        return tag

    @staticmethod
    async def delete_tag(db: AsyncSession, tag_id: int) -> bool:
        """删除标签"""
        stmt = select(Tag).where(Tag.id == tag_id)
        result = await db.execute(stmt)
        tag = result.scalar_one_or_none()

        if not tag:
            return False

        await db.delete(tag)
        await db.commit()
        return True


class StatisticsService:
    """统计数据服务"""

    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
        """获取仪表盘统计数据"""
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())

        # 用户统计
        total_users = await db.scalar(select(func.count()).select_from(User))
        active_users = await db.scalar(
            select(func.count()).select_from(User).where(User.status == "active")
        )
        new_users_today = await db.scalar(
            select(func.count()).select_from(User).where(User.created_at >= today_start)
        )

        # 内容统计
        total_contents = await db.scalar(select(func.count()).select_from(ContentItem))
        pending_audit_contents = await db.scalar(
            select(func.count())
            .select_from(ContentItem)
            .where(ContentItem.audit_status == "pending")
        )
        new_contents_today = await db.scalar(
            select(func.count())
            .select_from(ContentItem)
            .where(ContentItem.created_at >= today_start)
        )

        # 评论统计
        total_comments = await db.scalar(select(func.count()).select_from(ContentComment))
        pending_comments = await db.scalar(
            select(func.count())
            .select_from(ContentComment)
            .where(ContentComment.status == "pending")
        )

        # 今日浏览量
        total_views_today = await db.scalar(
            select(func.sum(ContentViewHistory.view_count))
            .select_from(ContentViewHistory)
            .where(ContentViewHistory.view_date == today)
        ) or 0

        # 今日互动量（点赞+评论+收藏）
        likes_today = await db.scalar(
            select(func.count())
            .select_from(ContentLike)
            .where(ContentLike.created_at >= today_start)
        ) or 0
        comments_today = await db.scalar(
            select(func.count())
            .select_from(ContentComment)
            .where(ContentComment.created_at >= today_start)
        ) or 0

        return DashboardStats(
            total_users=total_users or 0,
            active_users=active_users or 0,
            new_users_today=new_users_today or 0,
            total_contents=total_contents or 0,
            pending_audit_contents=pending_audit_contents or 0,
            new_contents_today=new_contents_today or 0,
            total_comments=total_comments or 0,
            pending_comments=pending_comments or 0,
            total_views_today=total_views_today,
            total_interactions_today=likes_today + comments_today,
        )

    @staticmethod
    async def get_user_growth_stats(
        db: AsyncSession, days: int = 30
    ) -> list[UserGrowthStats]:
        """获取用户增长统计"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # 新增用户统计
        stmt = (
            select(
                func.date(User.created_at).label("date"),
                func.count(User.id).label("new_users"),
            )
            .where(func.date(User.created_at) >= start_date)
            .group_by(func.date(User.created_at))
            .order_by(func.date(User.created_at))
        )
        result = await db.execute(stmt)
        data = result.all()

        return [
            UserGrowthStats(
                date=str(row.date), new_users=row.new_users, active_users=row.new_users
            )
            for row in data
        ]

    @staticmethod
    async def get_content_stats(db: AsyncSession, days: int = 30) -> list[ContentStats]:
        """获取内容统计"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        stmt = (
            select(
                func.date(ContentItem.created_at).label("date"),
                func.count(ContentItem.id).label("new_contents"),
                func.sum(ContentItem.views_count).label("total_views"),
                func.sum(ContentItem.likes_count).label("total_likes"),
                func.sum(ContentItem.comments_count).label("total_comments"),
            )
            .where(func.date(ContentItem.created_at) >= start_date)
            .group_by(func.date(ContentItem.created_at))
            .order_by(func.date(ContentItem.created_at))
        )
        result = await db.execute(stmt)
        data = result.all()

        return [
            ContentStats(
                date=str(row.date),
                new_contents=row.new_contents,
                total_views=row.total_views or 0,
                total_likes=row.total_likes or 0,
                total_comments=row.total_comments or 0,
            )
            for row in data
        ]

    @staticmethod
    async def get_category_stats(db: AsyncSession) -> list[CategoryStats]:
        """获取分类统计"""
        stmt = (
            select(
                ContentCategory.id,
                ContentCategory.name,
                func.count(ContentItem.id).label("content_count"),
                func.sum(ContentItem.views_count).label("total_views"),
                func.sum(ContentItem.likes_count).label("total_likes"),
            )
            .outerjoin(ContentItem, ContentCategory.id == ContentItem.category_id)
            .group_by(ContentCategory.id, ContentCategory.name)
            .order_by(desc(func.count(ContentItem.id)))
        )
        result = await db.execute(stmt)
        data = result.all()

        return [
            CategoryStats(
                category_id=row.id,
                category_name=row.name,
                content_count=row.content_count,
                total_views=row.total_views or 0,
                total_likes=row.total_likes or 0,
            )
            for row in data
        ]


class OperationLogService:
    """操作日志服务"""

    @staticmethod
    async def create_log(
        db: AsyncSession,
        admin_user_id: int,
        module: str,
        action: str,
        target_type: str | None = None,
        target_id: int | None = None,
        description: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        request_data: dict | None = None,
    ):
        """创建操作日志"""
        log = AdminOperationLog(
            admin_user_id=admin_user_id,
            module=module,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            request_data=json.dumps(request_data) if request_data else None,
            created_at=datetime.now(),
        )
        db.add(log)
        await db.commit()

    @staticmethod
    async def get_logs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        admin_user_id: int | None = None,
        module: str | None = None,
    ):
        """获取操作日志列表"""
        stmt = (
            select(AdminOperationLog, AdminUser.username)
            .join(AdminUser, AdminOperationLog.admin_user_id == AdminUser.id)
            .order_by(desc(AdminOperationLog.created_at))
        )

        if admin_user_id:
            stmt = stmt.where(AdminOperationLog.admin_user_id == admin_user_id)

        if module:
            stmt = stmt.where(AdminOperationLog.module == module)

        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = await db.scalar(total_stmt)

        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        items = result.all()

        return {"total": total, "items": items}
