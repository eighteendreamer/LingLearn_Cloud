from collections.abc import Sequence

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User
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

    async def list_user_works(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        offset: int,
        limit: int,
    ) -> tuple[Sequence[dict], int]:
        # Content module is not wired yet, so keep the contract stable with an empty list.
        _ = session, user_id, offset, limit
        return [], 0
