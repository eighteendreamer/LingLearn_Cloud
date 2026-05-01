from datetime import date, datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assessment.models import AssessmentSnapshot


class AssessmentRepository:
    async def get_latest_snapshot(
        self,
        session: AsyncSession,
        user_id: int,
        assessment_type: str | None = None,
    ) -> AssessmentSnapshot | None:
        stmt = select(AssessmentSnapshot).where(AssessmentSnapshot.user_id == user_id)
        
        if assessment_type:
            stmt = stmt.where(AssessmentSnapshot.assessment_type == assessment_type)
        
        stmt = stmt.order_by(desc(AssessmentSnapshot.period_end)).limit(1)
        
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_snapshots_by_type(
        self,
        session: AsyncSession,
        user_id: int,
        assessment_type: str,
        limit: int = 10,
    ) -> list[AssessmentSnapshot]:
        stmt = (
            select(AssessmentSnapshot)
            .where(
                AssessmentSnapshot.user_id == user_id,
                AssessmentSnapshot.assessment_type == assessment_type,
            )
            .order_by(desc(AssessmentSnapshot.period_end))
            .limit(limit)
        )
        
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def create_snapshot(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        assessment_type: str,
        period_start: date,
        period_end: date,
        total_learning_minutes: int,
        completed_courses: int,
        average_score: float,
        rank_percent: float | None = None,
        correct_rate: float | None = None,
        focus_rate: float | None = None,
        metrics_json: dict | None = None,
        created_at: datetime,
    ) -> AssessmentSnapshot:
        snapshot = AssessmentSnapshot(
            user_id=user_id,
            assessment_type=assessment_type,
            period_start=period_start,
            period_end=period_end,
            total_learning_minutes=total_learning_minutes,
            completed_courses=completed_courses,
            average_score=average_score,
            rank_percent=rank_percent,
            correct_rate=correct_rate,
            focus_rate=focus_rate,
            metrics_json=metrics_json,
            created_at=created_at,
            updated_at=created_at,
        )
        session.add(snapshot)
        await session.flush()
        await session.refresh(snapshot)
        return snapshot

    async def get_snapshot_by_id(
        self,
        session: AsyncSession,
        snapshot_id: int,
    ) -> AssessmentSnapshot | None:
        stmt = select(AssessmentSnapshot).where(AssessmentSnapshot.id == snapshot_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
