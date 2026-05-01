from decimal import Decimal

from app.modules.recommendation.service import RecommendationService


def test_watch_behavior_delta_scores_effective_watch() -> None:
    deltas = RecommendationService._build_behavior_deltas(
        event_type="watch",
        watch_seconds=8,
        watch_progress=60,
        completed=False,
    )

    assert deltas["interest"] == Decimal("5")
    assert deltas["watch"] == Decimal("5")
    assert deltas["negative"] == Decimal("0")


def test_watch_behavior_delta_scores_quick_skip_as_negative() -> None:
    deltas = RecommendationService._build_behavior_deltas(
        event_type="watch",
        watch_seconds=1,
        watch_progress=3,
        completed=False,
    )

    assert deltas["interest"] == Decimal("-1")
    assert deltas["negative"] == Decimal("1")


def test_recommendation_diversifies_adjacent_authors_and_categories() -> None:
    rows = [
        {"id": 1, "author_id": 10, "category_id": 1},
        {"id": 2, "author_id": 10, "category_id": 1},
        {"id": 3, "author_id": 10, "category_id": 1},
        {"id": 4, "author_id": 20, "category_id": 2},
    ]
    items = [{"content_id": row["id"], "recall_source": "hot", "rank_score": 1} for row in rows]

    diversified_rows, diversified_items = RecommendationService._diversify_rows_with_items(
        rows=rows,
        items=items,
    )

    assert [item["content_id"] for item in diversified_items] == [row["id"] for row in diversified_rows]
    assert diversified_rows[1]["author_id"] != diversified_rows[0]["author_id"]
