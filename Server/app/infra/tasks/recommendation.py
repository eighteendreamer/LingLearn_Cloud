from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session_factory
from app.modules.recommendation.service import RecommendationService


async def update_content_hot_scores(session: AsyncSession | None = None) -> int:
    service = RecommendationService()
    if session is not None:
        return await service.refresh_hot_scores(session)

    session_factory = get_session_factory()
    async with session_factory() as owned_session:
        return await service.refresh_hot_scores(owned_session)


async def decay_interest_profiles(
    session: AsyncSession | None = None,
    *,
    ratio: Decimal = Decimal("0.95"),
) -> None:
    service = RecommendationService()
    if session is not None:
        await service.decay_interest_profiles(session, ratio=ratio)
        return

    session_factory = get_session_factory()
    async with session_factory() as owned_session:
        await service.decay_interest_profiles(owned_session, ratio=ratio)


async def cleanup_old_impressions(
    session: AsyncSession | None = None,
    *,
    retention_days: int = 30,
) -> int:
    service = RecommendationService()
    if session is not None:
        return await service.cleanup_old_impressions(
            session,
            retention_days=retention_days,
        )

    session_factory = get_session_factory()
    async with session_factory() as owned_session:
        return await service.cleanup_old_impressions(
            owned_session,
            retention_days=retention_days,
        )


async def run_recommendation_maintenance(
    *,
    interest_decay_ratio: Decimal = Decimal("0.95"),
    impression_retention_days: int = 30,
) -> dict[str, int]:
    service = RecommendationService()
    session_factory = get_session_factory()
    async with session_factory() as session:
        return await service.run_maintenance(
            session,
            interest_decay_ratio=interest_decay_ratio,
            impression_retention_days=impression_retention_days,
        )
