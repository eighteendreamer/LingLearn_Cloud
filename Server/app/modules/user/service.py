from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginationParams, build_page_response
from app.common.utils import utc_now_naive
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.modules.auth.repository import AuthRepository
from app.modules.user.repository import UserRepository
from app.modules.user.schemas import (
    CurrentUserResponse,
    PublicUserResponse,
    UserFollowActionResponse,
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserSettingsResponse,
    UserSettingsUpdateRequest,
    UserStatsResponse,
    UserWorkListItemResponse,
)


class UserService:
    def __init__(
        self,
        *,
        repository: UserRepository | None = None,
        auth_repository: AuthRepository | None = None,
    ) -> None:
        self.repository = repository or UserRepository()
        self.auth_repository = auth_repository or AuthRepository()

    async def get_me(self, session: AsyncSession, user_id: int) -> CurrentUserResponse:
        bundle = await self.repository.get_user_with_profile_and_settings(session, user_id)
        if bundle is None:
            raise NotFoundError(message="User not found.")
        user, profile, settings = bundle
        return CurrentUserResponse(
            profile=self._build_profile_response(user, profile),
            settings=UserSettingsResponse.model_validate(settings, from_attributes=True),
        )

    async def update_profile(
        self,
        session: AsyncSession,
        user_id: int,
        req: UserProfileUpdateRequest,
    ) -> CurrentUserResponse:
        user_updates: dict = {}
        profile_updates: dict = {}

        if req.email is not None:
            if await self.auth_repository.email_exists(session, req.email, exclude_user_id=user_id):
                raise ConflictError(message="Email already exists.")
            user_updates["email"] = str(req.email)

        if req.phone is not None:
            if req.phone and await self.auth_repository.phone_exists(
                session,
                req.phone,
                exclude_user_id=user_id,
            ):
                raise ConflictError(message="Phone already exists.")
            user_updates["phone"] = req.phone or None

        for field_name in [
            "display_name",
            "bio",
            "location",
            "profession",
            "birthday",
            "learning_goal",
        ]:
            value = getattr(req, field_name)
            if value is not None:
                profile_updates[field_name] = value

        async with session.begin():
            await self.repository.update_user_fields(session, user_id=user_id, values=user_updates)
            await self.repository.update_profile_fields(session, user_id=user_id, values=profile_updates)

        return await self.get_me(session, user_id)

    async def update_settings(
        self,
        session: AsyncSession,
        user_id: int,
        req: UserSettingsUpdateRequest,
    ) -> CurrentUserResponse:
        settings_updates = req.model_dump(exclude_none=True)
        async with session.begin():
            await self.repository.update_settings_fields(
                session,
                user_id=user_id,
                values=settings_updates,
            )
        return await self.get_me(session, user_id)

    async def get_public_user(
        self,
        session: AsyncSession,
        user_id: int,
        *,
        viewer_user_id: int | None = None,
    ) -> PublicUserResponse:
        bundle = await self.repository.get_public_user_with_profile(session, user_id)
        if bundle is None:
            raise NotFoundError(message="User not found.")
        user, profile = bundle
        is_following = False
        if viewer_user_id is not None and viewer_user_id != user_id:
            is_following = await self.repository.is_following(
                session,
                follower_user_id=viewer_user_id,
                followee_user_id=user_id,
            )
        return PublicUserResponse(
            user_id=user.id,
            username=user.username,
            display_name=profile.display_name,
            avatar_asset_id=profile.avatar_asset_id,
            bio=profile.bio,
            location=profile.location,
            profession=profile.profession,
            learning_goal=profile.learning_goal,
            stats=self._build_stats(profile),
            is_following=is_following,
        )

    async def follow_user(
        self,
        session: AsyncSession,
        follower_user_id: int,
        followee_user_id: int,
    ) -> UserFollowActionResponse:
        if follower_user_id == followee_user_id:
            raise BadRequestError(message="You cannot follow yourself.")
        target = await self.repository.get_public_user_with_profile(session, followee_user_id)
        if target is None:
            raise NotFoundError(message="Target user not found.")

        relation = await self.repository.get_follow_relation(
            session,
            follower_user_id=follower_user_id,
            followee_user_id=followee_user_id,
        )
        if relation is None:
            async with session.begin():
                await self.repository.create_follow_relation(
                    session,
                    follower_user_id=follower_user_id,
                    followee_user_id=followee_user_id,
                    created_at=utc_now_naive(),
                )
                await self.repository.increment_follow_counts(
                    session,
                    follower_user_id=follower_user_id,
                    followee_user_id=followee_user_id,
                    delta=1,
                )

        return UserFollowActionResponse(target_user_id=followee_user_id, is_following=True)

    async def unfollow_user(
        self,
        session: AsyncSession,
        follower_user_id: int,
        followee_user_id: int,
    ) -> UserFollowActionResponse:
        relation = await self.repository.get_follow_relation(
            session,
            follower_user_id=follower_user_id,
            followee_user_id=followee_user_id,
        )
        if relation is not None:
            async with session.begin():
                await self.repository.delete_follow_relation(session, relation_id=relation.id)
                await self.repository.increment_follow_counts(
                    session,
                    follower_user_id=follower_user_id,
                    followee_user_id=followee_user_id,
                    delta=-1,
                )

        return UserFollowActionResponse(target_user_id=followee_user_id, is_following=False)

    async def list_user_works(
        self,
        session: AsyncSession,
        user_id: int,
        pagination: PaginationParams,
    ):
        bundle = await self.repository.get_public_user_with_profile(session, user_id)
        if bundle is None:
            raise NotFoundError(message="User not found.")
        items, total = await self.repository.list_user_works(
            session,
            user_id=user_id,
            offset=pagination.offset,
            limit=pagination.page_size,
        )
        work_items = [UserWorkListItemResponse.model_validate(item) for item in items]
        return build_page_response(work_items, total, pagination)

    @staticmethod
    def _build_stats(profile) -> UserStatsResponse:
        return UserStatsResponse(
            total_learning_minutes=profile.total_learning_minutes,
            streak_days=profile.streak_days,
            followers_count=profile.followers_count,
            following_count=profile.following_count,
            likes_received_count=profile.likes_received_count,
        )

    def _build_profile_response(self, user, profile) -> UserProfileResponse:
        return UserProfileResponse(
            user_id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            display_name=profile.display_name,
            avatar_asset_id=profile.avatar_asset_id,
            bio=profile.bio,
            gender=profile.gender,
            birthday=profile.birthday,
            location=profile.location,
            profession=profile.profession,
            learning_goal=profile.learning_goal,
            timezone=profile.timezone,
            locale=profile.locale,
            stats=self._build_stats(profile),
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
