from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta
from decimal import Decimal
from math import exp

from sqlalchemy import and_, delete, func, literal, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.content.models import ContentItem, ContentItemTag, ContentViewHistory
from app.modules.recommendation.models import (
    ContentRecommendationImpression,
    UserAuthorInterestProfile,
    UserCategoryInterestProfile,
    UserTagInterestProfile,
)


class RecommendationRepository:
    async def get_user_category_profile(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        category_id: int,
    ) -> UserCategoryInterestProfile | None:
        stmt = select(UserCategoryInterestProfile).where(
            UserCategoryInterestProfile.user_id == user_id,
            UserCategoryInterestProfile.category_id == category_id,
        )
        return await session.scalar(stmt)

    async def create_user_category_profile(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        category_id: int,
    ) -> UserCategoryInterestProfile:
        entity = UserCategoryInterestProfile(user_id=user_id, category_id=category_id)
        session.add(entity)
        await session.flush()
        return entity

    async def get_user_tag_profiles(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        tag_ids: Sequence[int],
    ) -> list[UserTagInterestProfile]:
        if not tag_ids:
            return []
        stmt = select(UserTagInterestProfile).where(
            UserTagInterestProfile.user_id == user_id,
            UserTagInterestProfile.tag_id.in_(tag_ids),
        )
        return list((await session.scalars(stmt)).all())

    async def create_user_tag_profile(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        tag_id: int,
    ) -> UserTagInterestProfile:
        entity = UserTagInterestProfile(user_id=user_id, tag_id=tag_id)
        session.add(entity)
        await session.flush()
        return entity

    async def get_user_author_profile(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        author_id: int,
    ) -> UserAuthorInterestProfile | None:
        stmt = select(UserAuthorInterestProfile).where(
            UserAuthorInterestProfile.user_id == user_id,
            UserAuthorInterestProfile.author_id == author_id,
        )
        return await session.scalar(stmt)

    async def create_user_author_profile(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        author_id: int,
    ) -> UserAuthorInterestProfile:
        entity = UserAuthorInterestProfile(user_id=user_id, author_id=author_id)
        session.add(entity)
        await session.flush()
        return entity

    async def get_content_taxonomy(
        self,
        session: AsyncSession,
        *,
        content_id: int,
    ) -> dict | None:
        stmt = (
            select(
                ContentItem.id.label("content_id"),
                ContentItem.author_id.label("author_id"),
                ContentItem.category_id.label("category_id"),
                ContentItem.hot_score.label("hot_score"),
                ContentItem.published_at.label("published_at"),
                ContentItemTag.tag_id.label("tag_id"),
            )
            .select_from(ContentItem)
            .outerjoin(ContentItemTag, ContentItemTag.content_item_id == ContentItem.id)
            .where(ContentItem.id == content_id)
        )
        rows = list((await session.execute(stmt)).mappings().all())
        if not rows:
            return None
        first = rows[0]
        return {
            "content_id": first["content_id"],
            "author_id": first["author_id"],
            "category_id": first["category_id"],
            "hot_score": first["hot_score"],
            "published_at": first["published_at"],
            "tag_ids": [int(row["tag_id"]) for row in rows if row["tag_id"] is not None],
        }

    async def apply_category_interest_delta(
        self,
        session: AsyncSession,
        *,
        profile_id: int,
        interest_delta: Decimal,
        watch_delta: Decimal = Decimal("0"),
        like_delta: Decimal = Decimal("0"),
        favorite_delta: Decimal = Decimal("0"),
        comment_delta: Decimal = Decimal("0"),
        share_delta: Decimal = Decimal("0"),
        complete_delta: Decimal = Decimal("0"),
        negative_delta: Decimal = Decimal("0"),
        happened_at: datetime,
    ) -> None:
        stmt = (
            update(UserCategoryInterestProfile)
            .where(UserCategoryInterestProfile.id == profile_id)
            .values(
                interest_score=UserCategoryInterestProfile.interest_score + interest_delta,
                watch_score=UserCategoryInterestProfile.watch_score + watch_delta,
                like_score=UserCategoryInterestProfile.like_score + like_delta,
                favorite_score=UserCategoryInterestProfile.favorite_score + favorite_delta,
                comment_score=UserCategoryInterestProfile.comment_score + comment_delta,
                share_score=UserCategoryInterestProfile.share_score + share_delta,
                complete_score=UserCategoryInterestProfile.complete_score + complete_delta,
                negative_score=UserCategoryInterestProfile.negative_score + negative_delta,
                last_interaction_at=happened_at,
            )
            .execution_options(synchronize_session=False)
        )
        await session.execute(stmt)

    async def apply_tag_interest_delta(
        self,
        session: AsyncSession,
        *,
        profile_id: int,
        interest_delta: Decimal,
        watch_delta: Decimal = Decimal("0"),
        like_delta: Decimal = Decimal("0"),
        favorite_delta: Decimal = Decimal("0"),
        comment_delta: Decimal = Decimal("0"),
        share_delta: Decimal = Decimal("0"),
        complete_delta: Decimal = Decimal("0"),
        negative_delta: Decimal = Decimal("0"),
        happened_at: datetime,
    ) -> None:
        stmt = (
            update(UserTagInterestProfile)
            .where(UserTagInterestProfile.id == profile_id)
            .values(
                interest_score=UserTagInterestProfile.interest_score + interest_delta,
                watch_score=UserTagInterestProfile.watch_score + watch_delta,
                like_score=UserTagInterestProfile.like_score + like_delta,
                favorite_score=UserTagInterestProfile.favorite_score + favorite_delta,
                comment_score=UserTagInterestProfile.comment_score + comment_delta,
                share_score=UserTagInterestProfile.share_score + share_delta,
                complete_score=UserTagInterestProfile.complete_score + complete_delta,
                negative_score=UserTagInterestProfile.negative_score + negative_delta,
                last_interaction_at=happened_at,
            )
            .execution_options(synchronize_session=False)
        )
        await session.execute(stmt)

    async def apply_author_interest_delta(
        self,
        session: AsyncSession,
        *,
        profile_id: int,
        interest_delta: Decimal,
        watch_delta: Decimal = Decimal("0"),
        like_delta: Decimal = Decimal("0"),
        favorite_delta: Decimal = Decimal("0"),
        comment_delta: Decimal = Decimal("0"),
        share_delta: Decimal = Decimal("0"),
        complete_delta: Decimal = Decimal("0"),
        negative_delta: Decimal = Decimal("0"),
        happened_at: datetime,
    ) -> None:
        stmt = (
            update(UserAuthorInterestProfile)
            .where(UserAuthorInterestProfile.id == profile_id)
            .values(
                interest_score=UserAuthorInterestProfile.interest_score + interest_delta,
                watch_score=UserAuthorInterestProfile.watch_score + watch_delta,
                like_score=UserAuthorInterestProfile.like_score + like_delta,
                favorite_score=UserAuthorInterestProfile.favorite_score + favorite_delta,
                comment_score=UserAuthorInterestProfile.comment_score + comment_delta,
                share_score=UserAuthorInterestProfile.share_score + share_delta,
                complete_score=UserAuthorInterestProfile.complete_score + complete_delta,
                negative_score=UserAuthorInterestProfile.negative_score + negative_delta,
                last_interaction_at=happened_at,
            )
            .execution_options(synchronize_session=False)
        )
        await session.execute(stmt)

    async def get_top_category_scores(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        limit: int,
    ) -> list[dict]:
        stmt = (
            select(
                UserCategoryInterestProfile.category_id.label("category_id"),
                UserCategoryInterestProfile.interest_score.label("interest_score"),
            )
            .where(UserCategoryInterestProfile.user_id == user_id)
            .order_by(UserCategoryInterestProfile.interest_score.desc(), UserCategoryInterestProfile.updated_at.desc())
            .limit(limit)
        )
        return list((await session.execute(stmt)).mappings().all())

    async def get_top_tag_scores(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        limit: int,
    ) -> list[dict]:
        stmt = (
            select(
                UserTagInterestProfile.tag_id.label("tag_id"),
                UserTagInterestProfile.interest_score.label("interest_score"),
            )
            .where(UserTagInterestProfile.user_id == user_id)
            .order_by(UserTagInterestProfile.interest_score.desc(), UserTagInterestProfile.updated_at.desc())
            .limit(limit)
        )
        return list((await session.execute(stmt)).mappings().all())

    async def get_top_author_scores(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        limit: int,
    ) -> list[dict]:
        stmt = (
            select(
                UserAuthorInterestProfile.author_id.label("author_id"),
                UserAuthorInterestProfile.interest_score.label("interest_score"),
            )
            .where(UserAuthorInterestProfile.user_id == user_id)
            .order_by(UserAuthorInterestProfile.interest_score.desc(), UserAuthorInterestProfile.updated_at.desc())
            .limit(limit)
        )
        return list((await session.execute(stmt)).mappings().all())

    async def has_interest_profile(self, session: AsyncSession, *, user_id: int) -> bool:
        stmt = (
            select(func.count())
            .select_from(UserCategoryInterestProfile)
            .where(UserCategoryInterestProfile.user_id == user_id)
        )
        return bool(await session.scalar(stmt))

    async def list_recently_viewed_content_ids(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        days: int = 3,
        limit: int = 200,
    ) -> list[int]:
        since = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(ContentViewHistory.content_item_id)
            .where(
                ContentViewHistory.user_id == user_id,
                ContentViewHistory.last_viewed_at >= since,
            )
            .order_by(ContentViewHistory.last_viewed_at.desc())
            .limit(limit)
        )
        return [int(value) for value in (await session.scalars(stmt)).all()]

    async def create_impressions(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        session_id: str,
        scene_code: str,
        recommend_type: str,
        items: Sequence[dict],
    ) -> None:
        if not items:
            return
        for index, item in enumerate(items, start=1):
            session.add(
                ContentRecommendationImpression(
                    user_id=user_id,
                    content_item_id=int(item["content_id"]),
                    scene_code=scene_code,
                    recommend_type=recommend_type,
                    recall_source=str(item["recall_source"]),
                    session_id=session_id,
                    position_no=index,
                    rank_score=Decimal(str(item["rank_score"])),
                )
            )
        await session.flush()

    async def update_latest_impression_feedback(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        content_id: int,
        liked: bool | None = None,
        favorited: bool | None = None,
        commented: bool | None = None,
        shared: bool | None = None,
        watch_seconds: int | None = None,
        watch_progress: Decimal | None = None,
        completed: bool | None = None,
        clicked_at: datetime | None = None,
    ) -> None:
        latest_id_stmt = (
            select(ContentRecommendationImpression.id)
            .where(
                ContentRecommendationImpression.user_id == user_id,
                ContentRecommendationImpression.content_item_id == content_id,
            )
            .order_by(ContentRecommendationImpression.shown_at.desc(), ContentRecommendationImpression.id.desc())
            .limit(1)
        )
        latest_id = await session.scalar(latest_id_stmt)
        if latest_id is None:
            return

        values: dict = {}
        if liked is not None:
            values["liked"] = liked
        if favorited is not None:
            values["favorited"] = favorited
        if commented is not None:
            values["commented"] = commented
        if shared is not None:
            values["shared"] = shared
        if watch_seconds is not None:
            values["watch_seconds"] = func.greatest(ContentRecommendationImpression.watch_seconds, watch_seconds)
        if watch_progress is not None:
            values["watch_progress"] = func.greatest(ContentRecommendationImpression.watch_progress, watch_progress)
        if completed is not None:
            values["completed"] = completed
        if clicked_at is not None:
            values["clicked_at"] = clicked_at
        if not values:
            return

        stmt = (
            update(ContentRecommendationImpression)
            .where(ContentRecommendationImpression.id == latest_id)
            .values(**values)
            .execution_options(synchronize_session=False)
        )
        await session.execute(stmt)

    async def apply_interest_decay(self, session: AsyncSession, *, ratio: Decimal) -> None:
        for model in (UserCategoryInterestProfile, UserTagInterestProfile, UserAuthorInterestProfile):
            stmt = (
                update(model)
                .values(
                    interest_score=model.interest_score * ratio,
                    watch_score=model.watch_score * ratio,
                    like_score=model.like_score * ratio,
                    favorite_score=model.favorite_score * ratio,
                    comment_score=model.comment_score * ratio,
                    share_score=model.share_score * ratio,
                    complete_score=model.complete_score * ratio,
                    negative_score=model.negative_score * ratio,
                )
                .execution_options(synchronize_session=False)
            )
            await session.execute(stmt)

    async def recalculate_content_hot_scores(
        self,
        session: AsyncSession,
        *,
        now: datetime | None = None,
    ) -> int:
        current_time = now or datetime.utcnow().replace(tzinfo=None)
        stmt = select(
            ContentItem.id,
            ContentItem.views_count,
            ContentItem.likes_count,
            ContentItem.favorites_count,
            ContentItem.comments_count,
            ContentItem.shares_count,
            ContentItem.published_at,
        ).where(
            ContentItem.deleted_at.is_(None),
            ContentItem.visibility == "public",
            ContentItem.audit_status == "approved",
            ContentItem.publish_status == "published",
            ContentItem.published_at.is_not(None),
        )
        rows = list((await session.execute(stmt)).mappings().all())

        for row in rows:
            published_at = row["published_at"]
            age_days = 0
            if published_at is not None:
                age_days = max((current_time - published_at).total_seconds() / 86400, 0)
            recency_bonus = exp(-age_days / 7) * 20
            hot_score = (
                float(row["views_count"] or 0) * 0.05
                + float(row["likes_count"] or 0) * 1.0
                + float(row["favorites_count"] or 0) * 1.5
                + float(row["comments_count"] or 0) * 1.8
                + float(row["shares_count"] or 0) * 1.2
                + recency_bonus
            )
            await session.execute(
                update(ContentItem)
                .where(ContentItem.id == row["id"])
                .values(hot_score=Decimal(str(round(hot_score, 4))))
                .execution_options(synchronize_session=False)
            )

        return len(rows)

    async def delete_old_impressions(
        self,
        session: AsyncSession,
        *,
        before: datetime,
    ) -> int:
        result = await session.execute(
            delete(ContentRecommendationImpression).where(
                ContentRecommendationImpression.shown_at < before
            )
        )
        return int(result.rowcount or 0)
