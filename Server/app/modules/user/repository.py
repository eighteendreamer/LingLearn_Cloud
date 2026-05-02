from collections.abc import Sequence
from datetime import date, datetime, timedelta

from sqlalchemy import and_, case, desc, func, literal, select, union_all, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.modules.auth.models import User
from app.modules.content.models import ContentCategory, ContentFavorite, ContentItem, ContentItemTag, ContentLike, Tag
from app.modules.content.models import ContentViewHistory
from app.modules.course.models import UserLessonProgress
from app.modules.practice.models import PracticeSession
from app.modules.storage.models import MediaAsset
from app.modules.user.models import UserFollowRelation, UserProfile, UserSettings


class UserRepository:
    async def get_user_with_profile_and_settings(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> tuple[User, UserProfile, UserSettings] | None:
        stmt = (
            select(User, UserProfile, UserSettings)
            .join(UserProfile, UserProfile.user_id == User.id)
            .join(UserSettings, UserSettings.user_id == User.id)
            .where(User.id == user_id, User.deleted_at.is_(None))
        )
        row = (await session.execute(stmt)).first()
        return tuple(row) if row else None

    async def get_public_user_with_profile(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> tuple[User, UserProfile] | None:
        stmt = (
            select(User, UserProfile)
            .join(UserProfile, UserProfile.user_id == User.id)
            .where(User.id == user_id, User.deleted_at.is_(None))
        )
        row = (await session.execute(stmt)).first()
        return tuple(row) if row else None

    async def update_user_fields(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        values: dict,
    ) -> None:
        if not values:
            return
        stmt = update(User).where(User.id == user_id).values(**values)
        await session.execute(stmt)

    async def update_profile_fields(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        values: dict,
    ) -> None:
        if not values:
            return
        stmt = update(UserProfile).where(UserProfile.user_id == user_id).values(**values)
        await session.execute(stmt)

    async def update_settings_fields(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        values: dict,
    ) -> None:
        if not values:
            return
        stmt = update(UserSettings).where(UserSettings.user_id == user_id).values(**values)
        await session.execute(stmt)

    async def get_media_asset_by_id(
        self,
        session: AsyncSession,
        *,
        asset_id: int,
    ) -> MediaAsset | None:
        return await session.scalar(select(MediaAsset).where(MediaAsset.id == asset_id))

    async def aggregate_user_learning_stats(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        today: date | None = None,
    ) -> dict[str, int]:
        lesson_seconds_result = await session.execute(
            select(func.coalesce(func.sum(UserLessonProgress.watch_seconds), 0))
            .where(UserLessonProgress.user_id == user_id)
        )
        content_seconds_result = await session.execute(
            select(func.coalesce(func.sum(ContentViewHistory.watch_seconds), 0))
            .where(ContentViewHistory.user_id == user_id)
        )

        total_learning_seconds = int(lesson_seconds_result.scalar() or 0) + int(content_seconds_result.scalar() or 0)
        total_learning_minutes = int(round(total_learning_seconds / 60)) if total_learning_seconds else 0

        activity_dates: set[date] = set()
        activity_statements = [
            select(ContentViewHistory.view_date).where(ContentViewHistory.user_id == user_id),
            select(func.date(UserLessonProgress.updated_at)).where(UserLessonProgress.user_id == user_id),
            select(func.date(func.coalesce(PracticeSession.finished_at, PracticeSession.submitted_at)))
            .where(PracticeSession.user_id == user_id)
            .where(PracticeSession.status.in_(("submitted", "completed")))
            .where(func.coalesce(PracticeSession.finished_at, PracticeSession.submitted_at).is_not(None)),
        ]
        for stmt in activity_statements:
            values = (await session.execute(stmt)).scalars().all()
            for value in values:
                normalized = self._normalize_activity_date(value)
                if normalized is not None:
                    activity_dates.add(normalized)

        return {
            "total_learning_minutes": total_learning_minutes,
            "streak_days": self._calculate_streak_days(activity_dates, today=today or date.today()),
        }

    async def get_follow_relation(
        self,
        session: AsyncSession,
        *,
        follower_user_id: int,
        followee_user_id: int,
    ) -> UserFollowRelation | None:
        stmt = select(UserFollowRelation).where(
            UserFollowRelation.follower_user_id == follower_user_id,
            UserFollowRelation.followee_user_id == followee_user_id,
        )
        return await session.scalar(stmt)

    async def create_follow_relation(
        self,
        session: AsyncSession,
        *,
        follower_user_id: int,
        followee_user_id: int,
        created_at,
    ) -> UserFollowRelation:
        relation = UserFollowRelation(
            follower_user_id=follower_user_id,
            followee_user_id=followee_user_id,
            created_at=created_at,
        )
        session.add(relation)
        await session.flush()
        return relation

    async def delete_follow_relation(
        self,
        session: AsyncSession,
        *,
        relation_id: int,
    ) -> None:
        relation = await session.get(UserFollowRelation, relation_id)
        if relation is not None:
            await session.delete(relation)

    async def increment_follow_counts(
        self,
        session: AsyncSession,
        *,
        follower_user_id: int,
        followee_user_id: int,
        delta: int,
    ) -> None:
        await session.execute(
            update(UserProfile)
            .where(UserProfile.user_id == follower_user_id)
            .values(following_count=UserProfile.following_count + delta)
        )
        await session.execute(
            update(UserProfile)
            .where(UserProfile.user_id == followee_user_id)
            .values(followers_count=UserProfile.followers_count + delta)
        )

    async def is_following(
        self,
        session: AsyncSession,
        *,
        follower_user_id: int,
        followee_user_id: int,
    ) -> bool:
        stmt = select(func.count()).select_from(UserFollowRelation).where(
            UserFollowRelation.follower_user_id == follower_user_id,
            UserFollowRelation.followee_user_id == followee_user_id,
        )
        return bool(await session.scalar(stmt))

    async def get_learning_preference_insight(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        top_limit: int = 6,
        recent_limit: int = 8,
    ) -> dict:
        interactions = self._interaction_union(user_id).subquery("user_preference_actions")

        likes_case = case((interactions.c.action_type == "like", 1), else_=0)
        favorites_case = case((interactions.c.action_type == "favorite", 1), else_=0)

        counts_stmt = select(
            func.coalesce(func.sum(likes_case), 0).label("likes_count"),
            func.coalesce(func.sum(favorites_case), 0).label("favorites_count"),
            func.count().label("total_count"),
        ).select_from(interactions)
        counts_row = (await session.execute(counts_stmt)).mappings().one()

        category_name_expr = func.coalesce(ContentCategory.name, literal("未分类"))
        category_key_expr = func.coalesce(ContentCategory.slug, literal("uncategorized"))
        category_stmt = (
            select(
                category_key_expr.label("key"),
                category_name_expr.label("name"),
                func.coalesce(func.sum(interactions.c.weight), 0).label("score"),
                func.coalesce(func.sum(likes_case), 0).label("likes_count"),
                func.coalesce(func.sum(favorites_case), 0).label("favorites_count"),
                func.count(func.distinct(interactions.c.content_item_id)).label("content_count"),
            )
            .select_from(interactions)
            .join(ContentItem, ContentItem.id == interactions.c.content_item_id)
            .outerjoin(ContentCategory, ContentCategory.id == ContentItem.category_id)
            .group_by(category_key_expr, category_name_expr)
            .order_by(desc("score"), desc("favorites_count"), desc("likes_count"), category_name_expr.asc())
            .limit(top_limit)
        )
        category_rows = list((await session.execute(category_stmt)).mappings().all())

        tag_stmt = (
            select(
                Tag.slug.label("key"),
                Tag.name.label("name"),
                func.coalesce(func.sum(interactions.c.weight), 0).label("score"),
                func.coalesce(func.sum(likes_case), 0).label("likes_count"),
                func.coalesce(func.sum(favorites_case), 0).label("favorites_count"),
                func.count(func.distinct(interactions.c.content_item_id)).label("content_count"),
            )
            .select_from(interactions)
            .join(ContentItemTag, ContentItemTag.content_item_id == interactions.c.content_item_id)
            .join(Tag, Tag.id == ContentItemTag.tag_id)
            .group_by(Tag.slug, Tag.name)
            .order_by(desc("score"), desc("favorites_count"), desc("likes_count"), Tag.name.asc())
            .limit(top_limit)
        )
        tag_rows = list((await session.execute(tag_stmt)).mappings().all())

        author_stmt = (
            select(
                ContentItem.author_id.label("user_id"),
                UserProfile.display_name.label("display_name"),
                func.coalesce(func.sum(interactions.c.weight), 0).label("score"),
                func.coalesce(func.sum(likes_case), 0).label("likes_count"),
                func.coalesce(func.sum(favorites_case), 0).label("favorites_count"),
                func.count(func.distinct(interactions.c.content_item_id)).label("content_count"),
            )
            .select_from(interactions)
            .join(ContentItem, ContentItem.id == interactions.c.content_item_id)
            .join(UserProfile, UserProfile.user_id == ContentItem.author_id)
            .group_by(ContentItem.author_id, UserProfile.display_name)
            .order_by(desc("score"), desc("favorites_count"), desc("likes_count"), UserProfile.display_name.asc())
            .limit(top_limit)
        )
        author_rows = list((await session.execute(author_stmt)).mappings().all())

        cover_asset = aliased(MediaAsset)
        recent_stmt = (
            select(
                interactions.c.content_item_id.label("content_id"),
                ContentItem.title.label("title"),
                cover_asset.object_key.label("cover_object_key"),
                cover_asset.public_url.label("cover_public_url"),
                ContentCategory.name.label("category_name"),
                UserProfile.display_name.label("author_name"),
                interactions.c.action_type.label("action_type"),
                interactions.c.acted_at.label("acted_at"),
            )
            .select_from(interactions)
            .join(ContentItem, ContentItem.id == interactions.c.content_item_id)
            .join(UserProfile, UserProfile.user_id == ContentItem.author_id)
            .outerjoin(ContentCategory, ContentCategory.id == ContentItem.category_id)
            .outerjoin(cover_asset, cover_asset.id == ContentItem.cover_asset_id)
            .order_by(interactions.c.acted_at.desc(), interactions.c.content_item_id.desc())
            .limit(recent_limit)
        )
        recent_rows = list((await session.execute(recent_stmt)).mappings().all())

        return {
            "counts": counts_row,
            "categories": category_rows,
            "tags": tag_rows,
            "authors": author_rows,
            "recent_actions": recent_rows,
        }

    async def list_learning_preference_content_rows(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        limit: int = 80,
    ) -> list[dict]:
        interactions = self._interaction_union(user_id).subquery("user_preference_actions")
        cover_asset = aliased(MediaAsset)
        category_name_expr = func.coalesce(ContentCategory.name, literal("未分类"))
        category_key_expr = func.coalesce(ContentCategory.slug, literal("uncategorized"))

        stmt = (
            select(
                ContentItem.id.label("content_id"),
                ContentItem.title.label("title"),
                cover_asset.object_key.label("cover_object_key"),
                cover_asset.public_url.label("cover_public_url"),
                category_key_expr.label("category_key"),
                category_name_expr.label("category_name"),
                UserProfile.display_name.label("author_name"),
                interactions.c.action_type.label("action_type"),
                interactions.c.acted_at.label("acted_at"),
            )
            .select_from(interactions)
            .join(ContentItem, ContentItem.id == interactions.c.content_item_id)
            .join(UserProfile, UserProfile.user_id == ContentItem.author_id)
            .outerjoin(ContentCategory, ContentCategory.id == ContentItem.category_id)
            .outerjoin(cover_asset, cover_asset.id == ContentItem.cover_asset_id)
            .order_by(interactions.c.acted_at.desc(), ContentItem.id.desc())
            .limit(limit)
        )
        return list((await session.execute(stmt)).mappings().all())

    @staticmethod
    def _interaction_union(user_id: int):
        like_stmt = (
            select(
                ContentLike.content_item_id.label("content_item_id"),
                literal("like").label("action_type"),
                literal(1.0).label("weight"),
                ContentLike.created_at.label("acted_at"),
            )
            .select_from(ContentLike)
            .join(ContentItem, ContentItem.id == ContentLike.content_item_id)
            .where(ContentLike.user_id == user_id, *UserRepository._public_content_conditions())
        )
        favorite_stmt = (
            select(
                ContentFavorite.content_item_id.label("content_item_id"),
                literal("favorite").label("action_type"),
                literal(2.0).label("weight"),
                ContentFavorite.created_at.label("acted_at"),
            )
            .select_from(ContentFavorite)
            .join(ContentItem, ContentItem.id == ContentFavorite.content_item_id)
            .where(ContentFavorite.user_id == user_id, *UserRepository._public_content_conditions())
        )
        return union_all(like_stmt, favorite_stmt)

    @staticmethod
    def _public_content_conditions():
        return (
            ContentItem.deleted_at.is_(None),
            ContentItem.visibility == "public",
            ContentItem.audit_status == "approved",
            ContentItem.publish_status == "published",
            ContentItem.published_at.is_not(None),
        )

    @staticmethod
    def _normalize_activity_date(value) -> date | None:
        if value is None:
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                return None
        return None

    @staticmethod
    def _calculate_streak_days(activity_dates: set[date], *, today: date) -> int:
        if not activity_dates:
            return 0

        latest_activity = max(activity_dates)
        if latest_activity < today - timedelta(days=1):
            return 0

        streak_days = 0
        cursor = latest_activity
        while cursor in activity_dates:
            streak_days += 1
            cursor -= timedelta(days=1)
        return streak_days
