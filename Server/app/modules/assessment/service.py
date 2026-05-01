from datetime import date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import utc_now_naive
from app.core.exceptions import NotFoundError
from app.modules.assessment.repository import AssessmentRepository
from app.modules.assessment.schemas import (
    AssessmentGenerateRequest,
    AssessmentSnapshotResponse,
    AssessmentTrendDataPoint,
    AssessmentTrendResponse,
)
from app.modules.course.repository import CourseRepository
from app.modules.practice.repository import PracticeRepository
from app.modules.user.repository import UserRepository


class AssessmentService:
    def __init__(
        self,
        *,
        repository: AssessmentRepository | None = None,
        user_repository: UserRepository | None = None,
        course_repository: CourseRepository | None = None,
        practice_repository: PracticeRepository | None = None,
    ) -> None:
        self.repository = repository or AssessmentRepository()
        self.user_repository = user_repository or UserRepository()
        self.course_repository = course_repository or CourseRepository()
        self.practice_repository = practice_repository or PracticeRepository()

    async def get_latest_assessment(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> AssessmentSnapshotResponse | None:
        snapshot = await self.repository.get_latest_snapshot(session, user_id)
        
        if not snapshot:
            return None
        
        return AssessmentSnapshotResponse(
            id=snapshot.id,
            user_id=snapshot.user_id,
            assessment_type=snapshot.assessment_type,
            period_start=snapshot.period_start,
            period_end=snapshot.period_end,
            total_learning_minutes=snapshot.total_learning_minutes,
            completed_courses=snapshot.completed_courses,
            average_score=snapshot.average_score,
            rank_percent=snapshot.rank_percent,
            correct_rate=snapshot.correct_rate,
            focus_rate=snapshot.focus_rate,
            metrics_json=snapshot.metrics_json,
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
        )

    async def get_assessment_trend(
        self,
        session: AsyncSession,
        user_id: int,
        assessment_type: str = "weekly",
    ) -> AssessmentTrendResponse:
        limit = 12 if assessment_type == "monthly" else 8
        snapshots = await self.repository.list_snapshots_by_type(
            session,
            user_id=user_id,
            assessment_type=assessment_type,
            limit=limit,
        )
        
        data_points = [
            AssessmentTrendDataPoint(
                date=snapshot.period_end.strftime("%Y-%m-%d"),
                learning_minutes=snapshot.total_learning_minutes,
                average_score=snapshot.average_score,
                correct_rate=snapshot.correct_rate,
            )
            for snapshot in reversed(snapshots)
        ]
        
        return AssessmentTrendResponse(
            assessment_type=assessment_type,
            data_points=data_points,
        )

    async def generate_assessment(
        self,
        session: AsyncSession,
        user_id: int,
        payload: AssessmentGenerateRequest,
    ) -> AssessmentSnapshotResponse:
        """
        Generate assessment snapshot by aggregating user learning data.
        In production, this would call AI workflow for insights generation.
        """
        bundle = await self.user_repository.get_user_with_profile_and_settings(session, user_id)
        if not bundle:
            raise NotFoundError(message="User not found.")
        
        _, profile, _ = bundle
        
        # Calculate period date range
        today = date.today()
        if payload.assessment_type == "daily":
            period_start = today
            period_end = today
        elif payload.assessment_type == "weekly":
            period_end = today
            period_start = today - timedelta(days=6)
        else:  # monthly
            period_end = today
            period_start = today - timedelta(days=29)
        
        # Aggregate learning data (simplified version)
        # In production, query actual learning activities within period
        total_learning_minutes = profile.total_learning_minutes
        
        # Get completed courses count
        enrollments, _ = await self.course_repository.list_user_enrollments(
            session,
            user_id=user_id,
            offset=0,
            limit=100,
        )
        completed_courses = sum(1 for row in enrollments if row["progress_percent"] >= 100)
        
        # Get practice statistics
        practice_sessions = await self.practice_repository.list_user_sessions(
            session,
            user_id=user_id,
            status="completed",
            limit=100,
        )
        
        # Calculate average score and correct rate
        if practice_sessions:
            total_score = sum(s.earned_score for s in practice_sessions)
            max_score = sum(s.total_score for s in practice_sessions)
            average_score = (total_score / max_score * 100) if max_score > 0 else 0.0
            
            # Calculate correct rate
            correct_answers = sum(
                1 for s in practice_sessions 
                if s.total_score > 0 and (s.earned_score / s.total_score) >= 0.6
            )
            correct_rate = (correct_answers / len(practice_sessions) * 100) if practice_sessions else 0.0
        else:
            average_score = 0.0
            correct_rate = 0.0
        
        # Mock additional metrics
        rank_percent = 75.5  # Mock: user is in top 25%
        focus_rate = 85.0  # Mock: 85% focus rate
        
        # Build metrics JSON
        metrics_json = {
            "total_sessions": len(practice_sessions),
            "completed_courses": completed_courses,
            "streak_days": profile.streak_days,
            "learning_hours": round(total_learning_minutes / 60, 1),
        }
        
        try:
            snapshot = await self.repository.create_snapshot(
                session,
                user_id=user_id,
                assessment_type=payload.assessment_type,
                period_start=period_start,
                period_end=period_end,
                total_learning_minutes=total_learning_minutes,
                completed_courses=completed_courses,
                average_score=round(average_score, 2),
                rank_percent=round(rank_percent, 2),
                correct_rate=round(correct_rate, 2),
                focus_rate=round(focus_rate, 2),
                metrics_json=metrics_json,
                created_at=utc_now_naive(),
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        
        return AssessmentSnapshotResponse(
            id=snapshot.id,
            user_id=snapshot.user_id,
            assessment_type=snapshot.assessment_type,
            period_start=snapshot.period_start,
            period_end=snapshot.period_end,
            total_learning_minutes=snapshot.total_learning_minutes,
            completed_courses=snapshot.completed_courses,
            average_score=snapshot.average_score,
            rank_percent=snapshot.rank_percent,
            correct_rate=snapshot.correct_rate,
            focus_rate=snapshot.focus_rate,
            metrics_json=snapshot.metrics_json,
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
        )
