from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from math import exp
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.content.repository import ContentRepository
from app.modules.recommendation.repository import RecommendationRepository


@dataclass
class RecommendationCandidate:
    content_id: int
    row: dict
    recall_source: str
    rank_score: float


class RecommendationService:
    NEW_CONTENT_BOOST_HOURS = 48

    def __init__(
        self,
        *,
        repository: RecommendationRepository | None = None,
        content_repository: ContentRepository | None = None,
    ) -> None:
        self.repository = repository or RecommendationRepository()
        self.content_repository = content_repository or ContentRepository()

    async def list_for_you_rows(
        self,
        session: AsyncSession,
        *,
        viewer_user_id: int | None,
        limit: int,
        category_id: int | None,
        cursor: tuple[datetime, int] | None,
    ) -> tuple[list[dict], str | None]:
        published_before = cursor[0] if cursor is not None else None
        if viewer_user_id is None:
            rows = await self._build_cold_start_rows(
                session,
                viewer_user_id=None,
                limit=limit,
                category_id=category_id,
                published_before=published_before,
            )
            fresh_rows = await self._build_fresh_explore_rows(
                session,
                viewer_user_id=None,
                limit=self._fresh_insert_target(limit),
                category_id=category_id,
                published_before=published_before,
                exclude_content_ids=[int(row["id"]) for row in rows],
            )
            rows, _ = self._merge_with_fresh_boost(
                rows=rows,
                candidate_items=[
                    {"content_id": row["id"], "recall_source": "cold_start", "rank_score": 0}
                    for row in rows
                ],
                fresh_rows=fresh_rows,
                limit=limit,
            )
            return rows, None

        has_profile = await self.repository.has_interest_profile(session, user_id=viewer_user_id)
        if not has_profile:
            rows = await self._build_cold_start_rows(
                session,
                viewer_user_id=viewer_user_id,
                limit=limit,
                category_id=category_id,
                published_before=published_before,
            )
            rows, items = self._merge_with_fresh_boost(
                rows=rows,
                candidate_items=[
                    {"content_id": row["id"], "recall_source": "cold_start", "rank_score": 0}
                    for row in rows
                ],
                fresh_rows=await self._build_fresh_explore_rows(
                    session,
                    viewer_user_id=viewer_user_id,
                    limit=self._fresh_insert_target(limit),
                    category_id=category_id,
                    published_before=published_before,
                    exclude_content_ids=[int(row["id"]) for row in rows],
                ),
                limit=limit,
            )
            session_id = await self._log_impressions(
                session,
                user_id=viewer_user_id,
                items=items,
            )
            return rows, session_id

        rows, candidate_items = await self._build_personalized_rows(
            session,
            viewer_user_id=viewer_user_id,
            limit=limit,
            category_id=category_id,
            published_before=published_before,
        )
        if not rows:
            rows = await self._build_cold_start_rows(
                session,
                viewer_user_id=viewer_user_id,
                limit=limit,
                category_id=category_id,
                published_before=published_before,
            )
            rows, items = self._merge_with_fresh_boost(
                rows=rows,
                candidate_items=[
                    {
                        "content_id": row["id"],
                        "recall_source": "fallback_cold_start",
                        "rank_score": 0,
                    }
                    for row in rows
                ],
                fresh_rows=await self._build_fresh_explore_rows(
                    session,
                    viewer_user_id=viewer_user_id,
                    limit=self._fresh_insert_target(limit),
                    category_id=category_id,
                    published_before=published_before,
                    exclude_content_ids=[int(row["id"]) for row in rows],
                ),
                limit=limit,
            )
            session_id = await self._log_impressions(
                session,
                user_id=viewer_user_id,
                items=items,
            )
            return rows, session_id

        if len(rows) < limit:
            supplement_rows = await self._build_cold_start_rows(
                session,
                viewer_user_id=viewer_user_id,
                limit=limit - len(rows),
                category_id=category_id,
                published_before=published_before,
                exclude_content_ids=[int(row["id"]) for row in rows],
            )
            if supplement_rows:
                rows.extend(supplement_rows)
                candidate_items.extend(
                    {
                        "content_id": row["id"],
                        "recall_source": "fallback_fill",
                        "rank_score": 0,
                    }
                    for row in supplement_rows
                )

        rows, candidate_items = self._merge_with_fresh_boost(
            rows=rows,
            candidate_items=candidate_items,
            fresh_rows=await self._build_fresh_explore_rows(
                session,
                viewer_user_id=viewer_user_id,
                limit=self._fresh_insert_target(limit),
                category_id=category_id,
                published_before=published_before,
                exclude_content_ids=[int(row["id"]) for row in rows],
            ),
            limit=limit,
        )
        session_id = await self._log_impressions(session, user_id=viewer_user_id, items=candidate_items)
        return rows, session_id

    async def record_behavior(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        content_id: int,
        event_type: str,
        watch_seconds: int = 0,
        watch_progress: float = 0,
        completed: bool = False,
    ) -> None:
        taxonomy = await self.repository.get_content_taxonomy(session, content_id=content_id)
        if taxonomy is None:
            return

        happened_at = datetime.utcnow().replace(tzinfo=None)
        deltas = self._build_behavior_deltas(
            event_type=event_type,
            watch_seconds=watch_seconds,
            watch_progress=watch_progress,
            completed=completed,
        )
        if deltas["interest"] == Decimal("0") and deltas["negative"] == Decimal("0"):
            return

        category_id = taxonomy["category_id"]
        if category_id is not None:
            profile = await self.repository.get_user_category_profile(
                session,
                user_id=user_id,
                category_id=int(category_id),
            )
            if profile is None:
                profile = await self.repository.create_user_category_profile(
                    session,
                    user_id=user_id,
                    category_id=int(category_id),
                )
            await self.repository.apply_category_interest_delta(
                session,
                profile_id=profile.id,
                interest_delta=deltas["interest"],
                watch_delta=deltas["watch"],
                like_delta=deltas["like"],
                favorite_delta=deltas["favorite"],
                comment_delta=deltas["comment"],
                share_delta=deltas["share"],
                complete_delta=deltas["complete"],
                negative_delta=deltas["negative"],
                happened_at=happened_at,
            )

        tag_ids = [int(tag_id) for tag_id in taxonomy["tag_ids"]]
        if tag_ids:
            existing_profiles = await self.repository.get_user_tag_profiles(
                session,
                user_id=user_id,
                tag_ids=tag_ids,
            )
            profiles_by_tag = {profile.tag_id: profile for profile in existing_profiles}
            divisor = Decimal(str(len(tag_ids)))
            for tag_id in tag_ids:
                profile = profiles_by_tag.get(tag_id)
                if profile is None:
                    profile = await self.repository.create_user_tag_profile(
                        session,
                        user_id=user_id,
                        tag_id=tag_id,
                    )
                await self.repository.apply_tag_interest_delta(
                    session,
                    profile_id=profile.id,
                    interest_delta=deltas["interest"] / divisor,
                    watch_delta=deltas["watch"] / divisor,
                    like_delta=deltas["like"] / divisor,
                    favorite_delta=deltas["favorite"] / divisor,
                    comment_delta=deltas["comment"] / divisor,
                    share_delta=deltas["share"] / divisor,
                    complete_delta=deltas["complete"] / divisor,
                    negative_delta=deltas["negative"] / divisor,
                    happened_at=happened_at,
                )

        author_profile = await self.repository.get_user_author_profile(
            session,
            user_id=user_id,
            author_id=int(taxonomy["author_id"]),
        )
        if author_profile is None:
            author_profile = await self.repository.create_user_author_profile(
                session,
                user_id=user_id,
                author_id=int(taxonomy["author_id"]),
            )
        await self.repository.apply_author_interest_delta(
            session,
            profile_id=author_profile.id,
            interest_delta=deltas["interest"],
            watch_delta=deltas["watch"],
            like_delta=deltas["like"],
            favorite_delta=deltas["favorite"],
            comment_delta=deltas["comment"],
            share_delta=deltas["share"],
            complete_delta=deltas["complete"],
            negative_delta=deltas["negative"],
            happened_at=happened_at,
        )

    async def update_impression_feedback(
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
        watch_progress: float | None = None,
        completed: bool | None = None,
        clicked_at: datetime | None = None,
    ) -> None:
        await self.repository.update_latest_impression_feedback(
            session,
            user_id=user_id,
            content_id=content_id,
            liked=liked,
            favorited=favorited,
            commented=commented,
            shared=shared,
            watch_seconds=watch_seconds,
            watch_progress=Decimal(str(watch_progress)) if watch_progress is not None else None,
            completed=completed,
            clicked_at=clicked_at,
        )

    async def _build_cold_start_rows(
        self,
        session: AsyncSession,
        *,
        viewer_user_id: int | None,
        limit: int,
        category_id: int | None,
        exclude_content_ids: list[int] | None = None,
        published_before: datetime | None,
    ) -> list[dict]:
        hot_count = max(1, round(limit * 0.5))
        recent_count = max(1, round(limit * 0.3))
        explore_count = max(1, limit - hot_count - recent_count)

        selected_ids: list[int] = list(exclude_content_ids or [])
        rows: list[dict] = []
        for fetched in (
            await self.content_repository.list_recommendation_candidate_rows(
                session,
                viewer_user_id=viewer_user_id,
                limit=hot_count,
                category_ids=[category_id] if category_id is not None else None,
                exclude_content_ids=selected_ids,
                published_before=published_before,
                order_by="hot",
            ),
            await self.content_repository.list_recommendation_candidate_rows(
                session,
                viewer_user_id=viewer_user_id,
                limit=recent_count,
                category_ids=[category_id] if category_id is not None else None,
                exclude_content_ids=selected_ids,
                published_before=published_before,
                order_by="recent",
            ),
            await self.content_repository.list_recommendation_candidate_rows(
                session,
                viewer_user_id=viewer_user_id,
                limit=explore_count,
                exclude_content_ids=selected_ids,
                published_before=published_before,
                order_by="recent",
            ),
        ):
            for row in fetched:
                if row["id"] in selected_ids:
                    continue
                selected_ids.append(int(row["id"]))
                rows.append(row)
                if len(rows) >= limit:
                    return rows[:limit]
        return rows[:limit]

    async def _build_fresh_explore_rows(
        self,
        session: AsyncSession,
        *,
        viewer_user_id: int | None,
        limit: int,
        category_id: int | None,
        exclude_content_ids: list[int] | None,
        published_before: datetime | None,
    ) -> list[dict]:
        if limit <= 0:
            return []
        return await self.content_repository.list_recommendation_candidate_rows(
            session,
            viewer_user_id=viewer_user_id,
            limit=limit,
            category_ids=[category_id] if category_id is not None else None,
            exclude_content_ids=exclude_content_ids,
            published_after=datetime.utcnow().replace(tzinfo=None) - timedelta(hours=self.NEW_CONTENT_BOOST_HOURS),
            published_before=published_before,
            order_by="recent",
        )

    async def _build_personalized_rows(
        self,
        session: AsyncSession,
        *,
        viewer_user_id: int,
        limit: int,
        category_id: int | None,
        published_before: datetime | None,
    ) -> tuple[list[dict], list[dict]]:
        top_categories = await self.repository.get_top_category_scores(session, user_id=viewer_user_id, limit=3)
        top_tags = await self.repository.get_top_tag_scores(session, user_id=viewer_user_id, limit=5)
        top_authors = await self.repository.get_top_author_scores(session, user_id=viewer_user_id, limit=3)
        recently_viewed_ids = await self.repository.list_recently_viewed_content_ids(
            session,
            user_id=viewer_user_id,
        )
        exclude_ids = set(recently_viewed_ids)

        source_rows: list[tuple[str, list[dict]]] = [
            (
                "hot",
                await self.content_repository.list_recommendation_candidate_rows(
                    session,
                    viewer_user_id=viewer_user_id,
                    limit=max(limit * 2, 20),
                    category_ids=[category_id] if category_id is not None else None,
                    exclude_content_ids=list(exclude_ids),
                    published_before=published_before,
                    order_by="hot",
                ),
            ),
            (
                "category",
                await self.content_repository.list_recommendation_candidate_rows(
                    session,
                    viewer_user_id=viewer_user_id,
                    limit=max(limit, 12),
                    category_ids=[int(item["category_id"]) for item in top_categories] if top_categories else None,
                    exclude_content_ids=list(exclude_ids),
                    published_before=published_before,
                    order_by="recent",
                ),
            ),
            (
                "tag",
                await self.content_repository.list_recommendation_candidate_rows(
                    session,
                    viewer_user_id=viewer_user_id,
                    limit=max(limit, 12),
                    tag_ids=[int(item["tag_id"]) for item in top_tags] if top_tags else None,
                    exclude_content_ids=list(exclude_ids),
                    published_before=published_before,
                    order_by="recent",
                ),
            ),
            (
                "author",
                await self.content_repository.list_recommendation_candidate_rows(
                    session,
                    viewer_user_id=viewer_user_id,
                    limit=max(limit, 10),
                    author_ids=[int(item["author_id"]) for item in top_authors] if top_authors else None,
                    exclude_content_ids=list(exclude_ids),
                    published_before=published_before,
                    order_by="recent",
                ),
            ),
            (
                "explore",
                await self.content_repository.list_recommendation_candidate_rows(
                    session,
                    viewer_user_id=viewer_user_id,
                    limit=max(limit // 2, 6),
                    exclude_content_ids=list(exclude_ids),
                    published_before=published_before,
                    order_by="recent",
                ),
            ),
        ]

        category_score_map = {int(item["category_id"]): float(item["interest_score"]) for item in top_categories}
        tag_score_map = {int(item["tag_id"]): float(item["interest_score"]) for item in top_tags}
        author_score_map = {int(item["author_id"]): float(item["interest_score"]) for item in top_authors}

        max_category_score = max(category_score_map.values(), default=1.0)
        max_tag_score = max(tag_score_map.values(), default=1.0)
        max_author_score = max(author_score_map.values(), default=1.0)

        candidate_map: dict[int, RecommendationCandidate] = {}
        for recall_source, rows in source_rows:
            for row in rows:
                content_id = int(row["id"])
                if content_id in candidate_map:
                    continue
                tag_ids = await self.content_repository.get_content_tag_ids(
                    session,
                    content_item_id=content_id,
                )
                category_match_score = 0.0
                if row["category_id"] in category_score_map:
                    category_match_score = (category_score_map[int(row["category_id"])] / max_category_score) * 100
                tag_match_score = 0.0
                if tag_ids and tag_score_map:
                    matched = [tag_score_map[tag_id] for tag_id in tag_ids if tag_id in tag_score_map]
                    if matched:
                        tag_match_score = (sum(matched) / len(matched) / max_tag_score) * 100
                author_match_score = 0.0
                if int(row["author_id"]) in author_score_map:
                    author_match_score = (author_score_map[int(row["author_id"])] / max_author_score) * 100

                hot_score_norm = min(float(row["likes_count"]) * 1.0 + float(row["favorites_count"]) * 1.5 + float(row["comments_count"]) * 1.8 + float(row["shares_count"]) * 1.2 + float(row["views_count"]) * 0.05, 100.0)
                recency_score = self._calculate_recency_score(row["published_at"])
                behavior_similarity_score = min((category_match_score * 0.5) + (tag_match_score * 0.5), 100.0)
                explore_score = 100.0 if recall_source == "explore" else 0.0

                rank_score = (
                    category_match_score * 0.30
                    + tag_match_score * 0.25
                    + author_match_score * 0.10
                    + behavior_similarity_score * 0.10
                    + hot_score_norm * 0.15
                    + recency_score * 0.05
                    + explore_score * 0.05
                )

                candidate_map[content_id] = RecommendationCandidate(
                    content_id=content_id,
                    row=row,
                    recall_source=recall_source,
                    rank_score=rank_score,
                )

        ranked = sorted(
            candidate_map.values(),
            key=lambda item: (item.rank_score, item.row["published_at"], item.content_id),
            reverse=True,
        )[:limit]

        return (
            [item.row for item in ranked],
            [
                {
                    "content_id": item.content_id,
                    "recall_source": item.recall_source,
                    "rank_score": item.rank_score,
                }
                for item in ranked
            ],
        )

    async def _log_impressions(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        items: list[dict],
    ) -> str:
        session_id = uuid4().hex
        await self.repository.create_impressions(
            session,
            user_id=user_id,
            session_id=session_id,
            scene_code="for_you",
            recommend_type="for_you",
            items=items,
        )
        await session.commit()
        return session_id

    @staticmethod
    def _build_behavior_deltas(
        *,
        event_type: str,
        watch_seconds: int,
        watch_progress: float,
        completed: bool,
    ) -> dict[str, Decimal]:
        zeros = {
            "interest": Decimal("0"),
            "watch": Decimal("0"),
            "like": Decimal("0"),
            "favorite": Decimal("0"),
            "comment": Decimal("0"),
            "share": Decimal("0"),
            "complete": Decimal("0"),
            "negative": Decimal("0"),
        }
        normalized = event_type.strip().lower()
        if normalized == "watch":
            if watch_seconds >= 5 or watch_progress >= 15:
                zeros["interest"] += Decimal("2")
                zeros["watch"] += Decimal("2")
            elif watch_seconds > 0 or watch_progress > 0:
                zeros["interest"] -= Decimal("1")
                zeros["negative"] += Decimal("1")
            if watch_progress >= 50:
                zeros["interest"] += Decimal("3")
                zeros["watch"] += Decimal("3")
            if completed or watch_progress >= 95:
                zeros["interest"] += Decimal("5")
                zeros["complete"] += Decimal("5")
            return zeros
        if normalized == "like":
            zeros["interest"] = Decimal("6")
            zeros["like"] = Decimal("6")
        elif normalized == "unlike":
            zeros["interest"] = Decimal("-3")
            zeros["negative"] = Decimal("1")
        elif normalized == "favorite":
            zeros["interest"] = Decimal("10")
            zeros["favorite"] = Decimal("10")
        elif normalized == "unfavorite":
            zeros["interest"] = Decimal("-5")
            zeros["negative"] = Decimal("1")
        elif normalized == "comment":
            zeros["interest"] = Decimal("12")
            zeros["comment"] = Decimal("12")
        elif normalized == "share":
            zeros["interest"] = Decimal("8")
            zeros["share"] = Decimal("8")
        return zeros

    @staticmethod
    def _calculate_recency_score(published_at: datetime | None) -> float:
        if published_at is None:
            return 0.0
        days = max((datetime.utcnow().replace(tzinfo=None) - published_at).days, 0)
        return min(exp(-days / 7) * 100, 100.0)

    @staticmethod
    def _fresh_insert_target(limit: int) -> int:
        if limit <= 0:
            return 0
        return min(2, max(1, limit // 6))

    @staticmethod
    def _merge_with_fresh_boost(
        *,
        rows: list[dict],
        candidate_items: list[dict],
        fresh_rows: list[dict],
        limit: int,
    ) -> tuple[list[dict], list[dict]]:
        if not fresh_rows:
            return rows[:limit], candidate_items[:limit]

        row_map = {int(row["id"]): row for row in rows}
        item_map = {int(item["content_id"]): item for item in candidate_items}
        ordered_ids = [int(row["id"]) for row in rows]

        insert_positions = [2, 6]
        next_insert_index = 0
        for fresh_row in fresh_rows:
            fresh_id = int(fresh_row["id"])
            if fresh_id in row_map:
                continue
            position = insert_positions[next_insert_index] if next_insert_index < len(insert_positions) else len(ordered_ids)
            position = min(position, len(ordered_ids))
            ordered_ids.insert(position, fresh_id)
            row_map[fresh_id] = fresh_row
            item_map[fresh_id] = {
                "content_id": fresh_id,
                "recall_source": "fresh_boost",
                "rank_score": 0,
            }
            next_insert_index += 1
            if next_insert_index >= len(fresh_rows):
                break

        ordered_ids = ordered_ids[:limit]
        return [row_map[content_id] for content_id in ordered_ids], [item_map[content_id] for content_id in ordered_ids]
