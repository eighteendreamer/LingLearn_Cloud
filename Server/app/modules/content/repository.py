from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from datetime import date, datetime

from sqlalchemy import Select, and_, exists, func, literal, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.modules.auth.models import User
from app.modules.content.models import (
    ContentCategory,
    ContentComment,
    ContentFavorite,
    ContentItem,
    ContentItemTag,
    ContentLike,
    ContentShare,
    ContentViewHistory,
    Tag,
)
from app.modules.storage.models import MediaAsset
from app.modules.user.models import UserFollowRelation, UserProfile


class ContentRepository:
    async def get_category_by_id(self, session: AsyncSession, category_id: int) -> ContentCategory | None:
        return await session.get(ContentCategory, category_id)

    async def list_active_categories(self, session: AsyncSession) -> list[ContentCategory]:
        stmt = (
            select(ContentCategory)
            .where(ContentCategory.status == "active")
            .order_by(ContentCategory.sort_order.asc(), ContentCategory.id.asc())
        )
        return list((await session.scalars(stmt)).all())

    async def create_category(
        self,
        session: AsyncSession,
        *,
        name: str,
        slug: str,
        description: str | None = None,
        icon: str | None = None,
        sort_order: int = 0,
    ) -> ContentCategory:
        entity = ContentCategory(
            name=name,
            slug=slug,
            description=description,
            icon=icon,
            sort_order=sort_order,
            status="active",
        )
        session.add(entity)
        await session.flush()
        return entity

    async def get_media_assets_by_ids(
        self,
        session: AsyncSession,
        asset_ids: Sequence[int],
    ) -> dict[int, MediaAsset]:
        if not asset_ids:
            return {}
        stmt = select(MediaAsset).where(MediaAsset.id.in_(asset_ids))
        items = (await session.scalars(stmt)).all()
        return {item.id: item for item in items}

    async def get_tags_by_names(self, session: AsyncSession, names: Sequence[str]) -> list[Tag]:
        if not names:
            return []
        stmt = select(Tag).where(Tag.name.in_(names))
        return list((await session.scalars(stmt)).all())

    async def create_tag(
        self,
        session: AsyncSession,
        *,
        name: str,
        slug: str,
        tag_type: str = "topic",
    ) -> Tag:
        tag = Tag(name=name, slug=slug, tag_type=tag_type, status="active")
        session.add(tag)
        await session.flush()
        return tag

    async def increment_tag_use_count(self, session: AsyncSession, tag_ids: Sequence[int]) -> None:
        if not tag_ids:
            return
        stmt = update(Tag).where(Tag.id.in_(tag_ids)).values(use_count=Tag.use_count + 1)
        await session.execute(stmt)

    async def create_content_item(self, session: AsyncSession, **values) -> ContentItem:
        item = ContentItem(**values)
        session.add(item)
        await session.flush()
        return item

    async def replace_content_tags(
        self,
        session: AsyncSession,
        *,
        content_item_id: int,
        tag_ids: Sequence[int],
    ) -> None:
        existing_stmt = select(ContentItemTag).where(ContentItemTag.content_item_id == content_item_id)
        existing = (await session.scalars(existing_stmt)).all()
        for row in existing:
            await session.delete(row)

        for tag_id in tag_ids:
            session.add(ContentItemTag(content_item_id=content_item_id, tag_id=tag_id))
        await session.flush()

    async def get_content_item_by_id(self, session: AsyncSession, content_id: int) -> ContentItem | None:
        return await session.get(ContentItem, content_id)

    async def get_content_item_by_id_for_update(
        self,
        session: AsyncSession,
        content_id: int,
    ) -> ContentItem | None:
        stmt = select(ContentItem).where(ContentItem.id == content_id).with_for_update()
        return await session.scalar(stmt)

    async def update_content_item(self, session: AsyncSession, *, content_id: int, values: dict) -> None:
        if not values:
            return
        stmt = update(ContentItem).where(ContentItem.id == content_id).values(**values)
        await session.execute(stmt)

    async def get_content_tag_names(self, session: AsyncSession, *, content_item_id: int) -> list[str]:
        stmt = (
            select(Tag.name)
            .join(ContentItemTag, ContentItemTag.tag_id == Tag.id)
            .where(ContentItemTag.content_item_id == content_item_id)
            .order_by(Tag.use_count.desc(), Tag.id.asc())
        )
        return list((await session.scalars(stmt)).all())

    async def get_content_detail_row(
        self,
        session: AsyncSession,
        *,
        content_id: int,
        viewer_user_id: int | None,
        include_unpublished_for_author_id: int | None = None,
    ):
        stmt = self._build_content_row_stmt(viewer_user_id=viewer_user_id).where(ContentItem.id == content_id)

        if include_unpublished_for_author_id is None:
            stmt = stmt.where(*self._public_content_conditions())
        else:
            stmt = stmt.where(
                or_(
                    and_(*self._public_content_conditions()),
                    and_(
                        ContentItem.author_id == include_unpublished_for_author_id,
                        ContentItem.deleted_at.is_(None),
                    ),
                )
            )

        return (await session.execute(stmt)).mappings().first()

    async def get_content_like(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        content_item_id: int,
    ) -> ContentLike | None:
        stmt = select(ContentLike).where(
            ContentLike.user_id == user_id,
            ContentLike.content_item_id == content_item_id,
        )
        return await session.scalar(stmt)

    async def create_content_like(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        content_item_id: int,
    ) -> ContentLike:
        entity = ContentLike(user_id=user_id, content_item_id=content_item_id)
        session.add(entity)
        await session.flush()
        return entity

    async def delete_content_like(self, session: AsyncSession, entity: ContentLike) -> None:
        await session.delete(entity)

    async def get_content_favorite(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        content_item_id: int,
    ) -> ContentFavorite | None:
        stmt = select(ContentFavorite).where(
            ContentFavorite.user_id == user_id,
            ContentFavorite.content_item_id == content_item_id,
        )
        return await session.scalar(stmt)

    async def create_content_favorite(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        content_item_id: int,
    ) -> ContentFavorite:
        entity = ContentFavorite(user_id=user_id, content_item_id=content_item_id)
        session.add(entity)
        await session.flush()
        return entity

    async def delete_content_favorite(self, session: AsyncSession, entity: ContentFavorite) -> None:
        await session.delete(entity)

    async def create_content_share(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        content_item_id: int,
        share_channel: str,
    ) -> ContentShare:
        entity = ContentShare(
            user_id=user_id,
            content_item_id=content_item_id,
            share_channel=share_channel,
        )
        session.add(entity)
        await session.flush()
        return entity

    async def get_content_comment_by_id(
        self,
        session: AsyncSession,
        comment_id: int,
    ) -> ContentComment | None:
        return await session.get(ContentComment, comment_id)

    async def create_content_comment(
        self,
        session: AsyncSession,
        *,
        content_item_id: int,
        user_id: int,
        content: str,
        parent_id: int | None,
        root_id: int | None,
        reply_to_user_id: int | None,
    ) -> ContentComment:
        entity = ContentComment(
            content_item_id=content_item_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id,
            root_id=root_id,
            reply_to_user_id=reply_to_user_id,
        )
        session.add(entity)
        await session.flush()
        return entity

    async def get_view_history_for_day(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        content_item_id: int,
        view_date: date,
    ) -> ContentViewHistory | None:
        stmt = select(ContentViewHistory).where(
            ContentViewHistory.user_id == user_id,
            ContentViewHistory.content_item_id == content_item_id,
            ContentViewHistory.view_date == view_date,
        )
        return await session.scalar(stmt)

    async def create_view_history(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        content_item_id: int,
        view_date: date,
        watch_seconds: int,
        watch_progress: float,
        last_position_seconds: int,
        completed: bool,
        liked: bool,
        favorited: bool,
        last_viewed_at: datetime,
    ) -> ContentViewHistory:
        entity = ContentViewHistory(
            user_id=user_id,
            content_item_id=content_item_id,
            view_date=view_date,
            view_count=1,
            watch_seconds=watch_seconds,
            watch_progress=watch_progress,
            last_position_seconds=last_position_seconds,
            completed=completed,
            liked=liked,
            favorited=favorited,
            last_viewed_at=last_viewed_at,
        )
        session.add(entity)
        await session.flush()
        return entity

    async def update_view_history(
        self,
        session: AsyncSession,
        *,
        history_id: int,
        values: dict,
    ) -> None:
        if not values:
            return
        stmt = update(ContentViewHistory).where(ContentViewHistory.id == history_id).values(**values)
        await session.execute(stmt)

    async def increment_content_counters(
        self,
        session: AsyncSession,
        *,
        content_id: int,
        likes_delta: int = 0,
        comments_delta: int = 0,
        favorites_delta: int = 0,
        shares_delta: int = 0,
        hot_score_delta: float | Decimal = Decimal("0"),
    ) -> None:
        values: dict = {}
        if likes_delta:
            values["likes_count"] = func.greatest(ContentItem.likes_count + likes_delta, 0)
        if comments_delta:
            values["comments_count"] = func.greatest(ContentItem.comments_count + comments_delta, 0)
        if favorites_delta:
            values["favorites_count"] = func.greatest(ContentItem.favorites_count + favorites_delta, 0)
        if shares_delta:
            values["shares_count"] = func.greatest(ContentItem.shares_count + shares_delta, 0)
        if hot_score_delta:
            values["hot_score"] = ContentItem.hot_score + Decimal(str(hot_score_delta))
        if not values:
            return
        stmt = (
            update(ContentItem)
            .where(ContentItem.id == content_id)
            .values(**values)
            .execution_options(synchronize_session=False)
        )
        await session.execute(stmt)

    async def increment_views_count(self, session: AsyncSession, *, content_id: int, delta: int = 1) -> None:
        if not delta:
            return
        stmt = (
            update(ContentItem)
            .where(ContentItem.id == content_id)
            .values(views_count=func.greatest(ContentItem.views_count + delta, 0))
            .execution_options(synchronize_session=False)
        )
        await session.execute(stmt)

    async def increment_author_likes_received(
        self,
        session: AsyncSession,
        *,
        author_user_id: int,
        delta: int,
    ) -> None:
        if not delta:
            return
        stmt = (
            update(UserProfile)
            .where(UserProfile.user_id == author_user_id)
            .values(likes_received_count=func.greatest(UserProfile.likes_received_count + delta, 0))
            .execution_options(synchronize_session=False)
        )
        await session.execute(stmt)

    async def list_content_comments_rows(
        self,
        session: AsyncSession,
        *,
        content_item_id: int,
        offset: int,
        limit: int,
    ) -> tuple[list[dict], int]:
        author_profile = aliased(UserProfile)
        author_avatar = aliased(MediaAsset)
        reply_profile = aliased(UserProfile)

        total_stmt = (
            select(func.count())
            .select_from(ContentComment)
            .where(
                ContentComment.content_item_id == content_item_id,
                ContentComment.deleted_at.is_(None),
                ContentComment.status == "normal",
            )
        )
        total = int((await session.scalar(total_stmt)) or 0)

        stmt = (
            select(
                ContentComment.id.label("id"),
                ContentComment.content_item_id.label("content_item_id"),
                ContentComment.user_id.label("user_id"),
                ContentComment.content.label("content"),
                ContentComment.like_count.label("like_count"),
                ContentComment.parent_id.label("parent_id"),
                ContentComment.root_id.label("root_id"),
                ContentComment.reply_to_user_id.label("reply_to_user_id"),
                ContentComment.created_at.label("created_at"),
                author_profile.display_name.label("display_name"),
                author_avatar.object_key.label("avatar_object_key"),
                author_avatar.public_url.label("avatar_public_url"),
                reply_profile.display_name.label("reply_to_display_name"),
            )
            .select_from(ContentComment)
            .join(author_profile, author_profile.user_id == ContentComment.user_id)
            .outerjoin(author_avatar, author_avatar.id == author_profile.avatar_asset_id)
            .outerjoin(reply_profile, reply_profile.user_id == ContentComment.reply_to_user_id)
            .where(
                ContentComment.content_item_id == content_item_id,
                ContentComment.deleted_at.is_(None),
                ContentComment.status == "normal",
            )
            .order_by(ContentComment.created_at.desc(), ContentComment.id.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = list((await session.execute(stmt)).mappings().all())
        return rows, total

    async def list_feed_rows(
        self,
        session: AsyncSession,
        *,
        viewer_user_id: int | None,
        limit: int,
        category_id: int | None,
        recommend_type: str,
        cursor: tuple[datetime, int] | None,
    ) -> list[dict]:
        stmt = self._build_content_row_stmt(viewer_user_id=viewer_user_id).where(
            *self._public_content_conditions()
        )

        if category_id is not None:
            stmt = stmt.where(ContentItem.category_id == category_id)

        normalized_type = recommend_type.strip().lower()
        if normalized_type == "following":
            if viewer_user_id is None:
                stmt = stmt.where(literal(False))
            else:
                stmt = stmt.join(
                    UserFollowRelation,
                    and_(
                        UserFollowRelation.followee_user_id == ContentItem.author_id,
                        UserFollowRelation.follower_user_id == viewer_user_id,
                    ),
                )
            stmt = stmt.order_by(ContentItem.published_at.desc(), ContentItem.id.desc())
        else:
            stmt = stmt.order_by(
                ContentItem.hot_score.desc(),
                ContentItem.published_at.desc(),
                ContentItem.id.desc(),
            )

        if cursor is not None:
            cursor_published_at, cursor_id = cursor
            stmt = stmt.where(
                or_(
                    ContentItem.published_at < cursor_published_at,
                    and_(
                        ContentItem.published_at == cursor_published_at,
                        ContentItem.id < cursor_id,
                    ),
                )
            )

        stmt = stmt.limit(limit)
        return list((await session.execute(stmt)).mappings().all())

    async def list_recommendation_candidate_rows(
        self,
        session: AsyncSession,
        *,
        viewer_user_id: int | None,
        limit: int,
        category_ids: Sequence[int] | None = None,
        tag_ids: Sequence[int] | None = None,
        author_ids: Sequence[int] | None = None,
        exclude_content_ids: Sequence[int] | None = None,
        published_after: datetime | None = None,
        published_before: datetime | None = None,
        order_by: str = "hot",
    ) -> list[dict]:
        stmt = self._build_content_row_stmt(viewer_user_id=viewer_user_id).where(
            *self._public_content_conditions()
        )

        if category_ids:
            stmt = stmt.where(ContentItem.category_id.in_(category_ids))
        if author_ids:
            stmt = stmt.where(ContentItem.author_id.in_(author_ids))
        if exclude_content_ids:
            stmt = stmt.where(ContentItem.id.not_in(list(exclude_content_ids)))
        if published_after is not None:
            stmt = stmt.where(ContentItem.published_at >= published_after)
        if published_before is not None:
            stmt = stmt.where(ContentItem.published_at < published_before)
        if tag_ids:
            stmt = stmt.join(ContentItemTag, ContentItemTag.content_item_id == ContentItem.id).where(
                ContentItemTag.tag_id.in_(tag_ids)
            )

        if order_by == "recent":
            stmt = stmt.order_by(ContentItem.published_at.desc(), ContentItem.id.desc())
        else:
            stmt = stmt.order_by(ContentItem.hot_score.desc(), ContentItem.published_at.desc(), ContentItem.id.desc())

        stmt = stmt.limit(limit)
        rows = list((await session.execute(stmt)).mappings().all())
        deduped: dict[int, dict] = {}
        for row in rows:
            deduped.setdefault(int(row["id"]), row)
        return list(deduped.values())

    async def get_content_rows_by_ids(
        self,
        session: AsyncSession,
        *,
        viewer_user_id: int | None,
        content_ids: Sequence[int],
    ) -> list[dict]:
        if not content_ids:
            return []
        stmt = self._build_content_row_stmt(viewer_user_id=viewer_user_id).where(
            *self._public_content_conditions(),
            ContentItem.id.in_(list(content_ids)),
        )
        rows = list((await session.execute(stmt)).mappings().all())
        row_map = {int(row["id"]): row for row in rows}
        return [row_map[content_id] for content_id in content_ids if content_id in row_map]

    async def get_content_tag_ids(
        self,
        session: AsyncSession,
        *,
        content_item_id: int,
    ) -> list[int]:
        stmt = select(ContentItemTag.tag_id).where(ContentItemTag.content_item_id == content_item_id)
        return [int(value) for value in (await session.scalars(stmt)).all()]

    async def list_author_works_rows(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        offset: int,
        limit: int,
    ) -> tuple[list[dict], int]:
        cover_asset = aliased(MediaAsset)

        total_stmt = (
            select(func.count())
            .select_from(ContentItem)
            .where(
                ContentItem.author_id == user_id,
                *self._public_content_conditions(),
            )
        )
        total = int((await session.scalar(total_stmt)) or 0)

        stmt = (
            select(
                ContentItem.id.label("id"),
                ContentItem.title.label("title"),
                ContentItem.summary.label("summary"),
                ContentItem.published_at.label("published_at"),
                cover_asset.object_key.label("cover_object_key"),
                cover_asset.public_url.label("cover_public_url"),
            )
            .select_from(ContentItem)
            .outerjoin(cover_asset, cover_asset.id == ContentItem.cover_asset_id)
            .where(
                ContentItem.author_id == user_id,
                *self._public_content_conditions(),
            )
            .order_by(ContentItem.published_at.desc(), ContentItem.id.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = list((await session.execute(stmt)).mappings().all())
        return rows, total

    def _build_content_row_stmt(self, *, viewer_user_id: int | None) -> Select:
        cover_asset = aliased(MediaAsset)
        primary_asset = aliased(MediaAsset)
        avatar_asset = aliased(MediaAsset)
        viewer_follow_relation = aliased(UserFollowRelation)

        liked_expr = literal(False)
        favorited_expr = literal(False)
        author_following_expr = literal(False)
        if viewer_user_id is not None:
            liked_expr = exists(
                select(1).where(
                    ContentLike.user_id == viewer_user_id,
                    ContentLike.content_item_id == ContentItem.id,
                )
            )
            favorited_expr = exists(
                select(1).where(
                    ContentFavorite.user_id == viewer_user_id,
                    ContentFavorite.content_item_id == ContentItem.id,
                )
            )
            author_following_expr = viewer_follow_relation.id.is_not(None)

        stmt = (
            select(
                ContentItem.id.label("id"),
                ContentItem.author_id.label("author_id"),
                ContentItem.title.label("title"),
                ContentItem.summary.label("summary"),
                ContentItem.hashtags_json.label("hashtags_json"),
                ContentItem.duration_seconds.label("duration_seconds"),
                ContentItem.bvid.label("bvid"),
                ContentItem.external_video_url.label("external_video_url"),
                ContentItem.has_quiz.label("has_quiz"),
                ContentItem.quiz_count.label("quiz_count"),
                ContentItem.views_count.label("views_count"),
                ContentItem.likes_count.label("likes_count"),
                ContentItem.comments_count.label("comments_count"),
                ContentItem.favorites_count.label("favorites_count"),
                ContentItem.shares_count.label("shares_count"),
                ContentItem.published_at.label("published_at"),
                UserProfile.display_name.label("author_display_name"),
                ContentCategory.id.label("category_id"),
                ContentCategory.name.label("category_name"),
                cover_asset.object_key.label("cover_object_key"),
                cover_asset.public_url.label("cover_public_url"),
                primary_asset.object_key.label("video_object_key"),
                primary_asset.public_url.label("video_public_url"),
                avatar_asset.object_key.label("avatar_object_key"),
                avatar_asset.public_url.label("avatar_public_url"),
                liked_expr.label("liked"),
                favorited_expr.label("favorited"),
                author_following_expr.label("author_is_following"),
            )
            .select_from(ContentItem)
            .join(User, User.id == ContentItem.author_id)
            .join(UserProfile, UserProfile.user_id == User.id)
            .outerjoin(ContentCategory, ContentCategory.id == ContentItem.category_id)
            .outerjoin(cover_asset, cover_asset.id == ContentItem.cover_asset_id)
            .outerjoin(primary_asset, primary_asset.id == ContentItem.primary_media_asset_id)
            .outerjoin(avatar_asset, avatar_asset.id == UserProfile.avatar_asset_id)
        )

        if viewer_user_id is not None:
            stmt = stmt.outerjoin(
                viewer_follow_relation,
                and_(
                    viewer_follow_relation.follower_user_id == viewer_user_id,
                    viewer_follow_relation.followee_user_id == ContentItem.author_id,
                ),
            )

        return stmt

    @staticmethod
    def _public_content_conditions():
        return (
            ContentItem.deleted_at.is_(None),
            ContentItem.visibility == "public",
            ContentItem.audit_status == "approved",
            ContentItem.publish_status == "published",
            ContentItem.published_at.is_not(None),
        )
