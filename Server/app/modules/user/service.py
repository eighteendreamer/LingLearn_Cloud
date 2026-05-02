from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginationParams, build_page_response
from app.common.utils import utc_now_naive
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.modules.auth.repository import AuthRepository
from app.modules.content.service import ContentService
from app.modules.user.repository import UserRepository
from app.modules.user.schemas import (
    CurrentUserResponse,
    PublicUserResponse,
    UserLearningPreferenceInsightResponse,
    UserPreferenceAuthorFacetResponse,
    UserPreferenceCategoryGroupResponse,
    UserPreferenceContentItemResponse,
    UserPreferenceFacetResponse,
    UserPreferenceRecentActionResponse,
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
        content_service: ContentService | None = None,
    ) -> None:
        self.repository = repository or UserRepository()
        self.auth_repository = auth_repository or AuthRepository()
        self.content_service = content_service or ContentService()

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
            if req.email is not None:
                if await self.auth_repository.email_exists(
                    session,
                    req.email,
                    exclude_user_id=user_id,
                ):
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

            await self.repository.update_user_fields(session, user_id=user_id, values=user_updates)
            await self.repository.update_profile_fields(
                session,
                user_id=user_id,
                values=profile_updates,
            )

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
        async with session.begin():
            target = await self.repository.get_public_user_with_profile(session, followee_user_id)
            if target is None:
                raise NotFoundError(message="Target user not found.")

            relation = await self.repository.get_follow_relation(
                session,
                follower_user_id=follower_user_id,
                followee_user_id=followee_user_id,
            )
            if relation is None:
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
        async with session.begin():
            relation = await self.repository.get_follow_relation(
                session,
                follower_user_id=follower_user_id,
                followee_user_id=followee_user_id,
            )
            if relation is not None:
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
        return await self.content_service.list_author_works(
            session,
            user_id=user_id,
            pagination=pagination,
        )

    async def list_my_favorites(
        self,
        session: AsyncSession,
        user_id: int,
        pagination: PaginationParams,
    ):
        return await self.content_service.list_user_favorites(
            session,
            user_id=user_id,
            pagination=pagination,
        )

    async def list_my_watch_history(
        self,
        session: AsyncSession,
        user_id: int,
        pagination: PaginationParams,
    ):
        return await self.content_service.list_user_watch_history(
            session,
            user_id=user_id,
            pagination=pagination,
        )

    async def get_learning_preference_insight(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> UserLearningPreferenceInsightResponse:
        data = await self.repository.get_learning_preference_insight(session, user_id=user_id)
        content_rows = await self.repository.list_learning_preference_content_rows(session, user_id=user_id)
        counts = data["counts"]
        categories = [
            UserPreferenceFacetResponse(
                key=str(row["key"]),
                name=str(row["name"]),
                score=float(row["score"] or 0),
                likes_count=int(row["likes_count"] or 0),
                favorites_count=int(row["favorites_count"] or 0),
                content_count=int(row["content_count"] or 0),
            )
            for row in data["categories"]
        ]
        tags = [
            UserPreferenceFacetResponse(
                key=str(row["key"]),
                name=str(row["name"]),
                score=float(row["score"] or 0),
                likes_count=int(row["likes_count"] or 0),
                favorites_count=int(row["favorites_count"] or 0),
                content_count=int(row["content_count"] or 0),
            )
            for row in data["tags"]
        ]
        authors = [
            UserPreferenceAuthorFacetResponse(
                user_id=int(row["user_id"]),
                display_name=str(row["display_name"]),
                score=float(row["score"] or 0),
                likes_count=int(row["likes_count"] or 0),
                favorites_count=int(row["favorites_count"] or 0),
                content_count=int(row["content_count"] or 0),
            )
            for row in data["authors"]
        ]
        recent_actions = []
        for row in data["recent_actions"]:
            cover_url = await self.content_service.storage_service.build_access_url(
                object_key=row["cover_object_key"],
                public_url=row["cover_public_url"],
            )
            recent_actions.append(
                UserPreferenceRecentActionResponse(
                    content_id=int(row["content_id"]),
                    title=str(row["title"]),
                    cover_url=cover_url,
                    category_name=row["category_name"],
                    author_name=str(row["author_name"]),
                    action_type=str(row["action_type"]),
                    acted_at=row["acted_at"],
                )
            )

        mapped_content_rows = []
        for row in content_rows:
            row_dict = dict(row)
            row_dict["cover_url"] = await self.content_service.storage_service.build_access_url(
                object_key=row["cover_object_key"],
                public_url=row["cover_public_url"],
            )
            mapped_content_rows.append(row_dict)

        grouped_works = self._build_grouped_preference_works(mapped_content_rows)
        total_likes = int(counts["likes_count"] or 0)
        total_favorites = int(counts["favorites_count"] or 0)
        total_interactions = int(counts["total_count"] or 0)
        return UserLearningPreferenceInsightResponse(
            summary=self._build_preference_summary(
                total_interactions=total_interactions,
                top_category=categories[0].name if categories else None,
                top_tag=tags[0].name if tags else None,
                top_author=authors[0].display_name if authors else None,
            ),
            total_likes=total_likes,
            total_favorites=total_favorites,
            total_interactions=total_interactions,
            top_categories=categories,
            top_tags=tags,
            top_authors=authors,
            recent_actions=recent_actions,
            grouped_works=grouped_works,
        )

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

    @staticmethod
    def _build_preference_summary(
        *,
        total_interactions: int,
        top_category: str | None,
        top_tag: str | None,
        top_author: str | None,
    ) -> str:
        if total_interactions <= 0:
            return "你还没有形成足够的点赞或收藏记录，继续互动后这里会逐步生成你的学习兴趣画像。"

        parts: list[str] = [f"最近已记录 {total_interactions} 次点赞/收藏行为。"]
        if top_category:
            parts.append(f"从分类上看，你更偏向“{top_category}”相关内容。")
        if top_tag:
            parts.append(f"从主题标签上看，“{top_tag}”是当前最明显的兴趣点。")
        if top_author:
            parts.append(f"在作者偏好上，你近期更关注 {top_author} 的内容。")
        return "".join(parts)

    @staticmethod
    def _build_grouped_preference_works(rows: list[dict]) -> list[UserPreferenceCategoryGroupResponse]:
        grouped = {
            "liked": {
                "key": "liked",
                "name": "点赞",
                "items": {},
            },
            "favorited": {
                "key": "favorited",
                "name": "收藏",
                "items": {},
            },
        }

        for row in rows:
            item = {
                "content_id": int(row["content_id"]),
                "title": str(row["title"]),
                "cover_url": row["cover_url"],
                "category_key": str(row["category_key"]),
                "category_name": str(row["category_name"]),
                "author_name": str(row["author_name"]),
                "liked": row["action_type"] == "like",
                "favorited": row["action_type"] == "favorite",
                "latest_acted_at": row["acted_at"],
            }

            target_key = "liked" if row["action_type"] == "like" else "favorited"
            existing = grouped[target_key]["items"].get(item["content_id"])
            if existing is None:
                grouped[target_key]["items"][item["content_id"]] = item
            elif row["acted_at"] > existing["latest_acted_at"]:
                existing["latest_acted_at"] = row["acted_at"]

        result: list[UserPreferenceCategoryGroupResponse] = []
        for group_key in ["liked", "favorited"]:
            group = grouped[group_key]
            items = sorted(
                group["items"].values(),
                key=lambda item: item["latest_acted_at"],
                reverse=True,
            )
            result.append(
                UserPreferenceCategoryGroupResponse(
                    key=group["key"],
                    name=group["name"],
                    item_count=len(items),
                    items=[UserPreferenceContentItemResponse(**item) for item in items],
                )
            )
        return result
