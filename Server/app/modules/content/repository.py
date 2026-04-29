from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import Select, and_, exists, func, literal, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.modules.auth.models import User
from app.modules.content.models import (
    ContentCategory,
    ContentFavorite,
    ContentItem,
    ContentItemTag,
    ContentLike,
    Tag,
)
from app.modules.storage.models import MediaAsset
from app.modules.user.models import UserFollowRelation, UserProfile


class ContentRepository:
    async def get_category_by_id(self, session: AsyncSession, category_id: int) -> ContentCategory | None:
        return await session.get(ContentCategory, category_id)

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

        liked_expr = literal(False)
        favorited_expr = literal(False)
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

        return (
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
            )
            .select_from(ContentItem)
            .join(User, User.id == ContentItem.author_id)
            .join(UserProfile, UserProfile.user_id == User.id)
            .outerjoin(ContentCategory, ContentCategory.id == ContentItem.category_id)
            .outerjoin(cover_asset, cover_asset.id == ContentItem.cover_asset_id)
            .outerjoin(primary_asset, primary_asset.id == ContentItem.primary_media_asset_id)
            .outerjoin(avatar_asset, avatar_asset.id == UserProfile.avatar_asset_id)
        )

    @staticmethod
    def _public_content_conditions():
        return (
            ContentItem.deleted_at.is_(None),
            ContentItem.visibility == "public",
            ContentItem.audit_status == "approved",
            ContentItem.publish_status == "published",
            ContentItem.published_at.is_not(None),
        )
