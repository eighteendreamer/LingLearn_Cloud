from __future__ import annotations

from datetime import date
from statistics import mean
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assessment.repository import AssessmentRepository
from app.modules.course.repository import CourseRepository
from app.modules.learning_path.repository import LearningPathRepository
from app.modules.practice.repository import PracticeRepository
from app.modules.report.repository import ReportRepository
from app.modules.user.repository import UserRepository


class UserLearningContextBuilder:
    """Build a compact learning snapshot for agent orchestration."""

    def __init__(self) -> None:
        self.user_repository = UserRepository()
        self.course_repository = CourseRepository()
        self.practice_repository = PracticeRepository()
        self.assessment_repository = AssessmentRepository()
        self.learning_path_repository = LearningPathRepository()
        self.report_repository = ReportRepository()

    async def build(self, session: AsyncSession, user_id: int) -> dict[str, Any]:
        bundle = await self._safe_call(
            session,
            self.user_repository.get_user_with_profile_and_settings(session, user_id),
            None,
        )
        enrollments_payload = await self._safe_call(
            session,
            self.course_repository.list_user_enrollments(session, user_id, offset=0, limit=5),
            ([], 0),
        )
        enrollments, _ = enrollments_payload
        practice_sessions = await self._safe_call(
            session,
            self.practice_repository.list_user_sessions(session, user_id=user_id, limit=5),
            [],
        )
        latest_assessment = await self._safe_call(
            session,
            self.assessment_repository.get_latest_snapshot(session, user_id),
            None,
        )
        latest_skill_snapshot = await self._safe_call(
            session,
            self.learning_path_repository.get_latest_snapshot(session, user_id),
            None,
        )
        active_path = await self._safe_call(
            session,
            self.learning_path_repository.get_active_user_path(session, user_id),
            None,
        )
        reports = await self._safe_call(
            session,
            self.report_repository.list_user_reports(session, user_id),
            [],
        )
        latest_report = next(iter(reports), None)

        profile_context: dict[str, Any] = {}
        if bundle:
            _, profile, settings = bundle
            profile_context = {
                "display_name": profile.display_name,
                "bio": profile.bio,
                "profession": profile.profession,
                "learning_goal": profile.learning_goal,
                "total_learning_minutes": profile.total_learning_minutes,
                "streak_days": profile.streak_days,
                "locale": profile.locale,
                "timezone": profile.timezone,
                "daily_reminder_enabled": settings.daily_reminder_enabled,
                "weekly_report_enabled": settings.weekly_report_enabled,
            }

        recent_courses = [
            {
                "course_id": row["course_id"],
                "title": row["title"],
                "progress_percent": float(row["progress_percent"] or 0),
                "completed_lessons": int(row["completed_lessons"] or 0),
            }
            for row in enrollments[:5]
        ]

        completed_sessions = [item for item in practice_sessions if item.status == "completed"]
        practice_context = {
            "recent_session_count": len(practice_sessions),
            "completed_session_count": len(completed_sessions),
            "average_score": round(
                mean(float(item.earned_score or 0) for item in completed_sessions),
                2,
            ) if completed_sessions else 0.0,
            "latest_status": practice_sessions[0].status if practice_sessions else None,
        }

        assessment_context = None
        if latest_assessment:
            assessment_context = {
                "assessment_type": latest_assessment.assessment_type,
                "period_end": latest_assessment.period_end.isoformat(),
                "average_score": float(latest_assessment.average_score or 0),
                "correct_rate": float(latest_assessment.correct_rate or 0),
                "focus_rate": float(latest_assessment.focus_rate or 0),
                "total_learning_minutes": latest_assessment.total_learning_minutes,
                "completed_courses": latest_assessment.completed_courses,
            }

        skill_context = None
        if latest_skill_snapshot:
            skill_context = {
                "snapshot_id": latest_skill_snapshot.id,
                "total_score": float(latest_skill_snapshot.total_score or 0),
                "rank_percent": float(latest_skill_snapshot.rank_percent or 0),
                "generated_at": latest_skill_snapshot.generated_at.isoformat(),
            }

        active_path_context = None
        if active_path:
            active_path_context = {
                "user_path_id": active_path.id,
                "progress_percent": float(active_path.progress_percent or 0),
                "status": active_path.status,
                "current_node_id": active_path.current_node_id,
                "ai_summary": active_path.ai_summary,
            }

        latest_report_context = None
        if latest_report:
            latest_report_context = {
                "report_month": latest_report.report_month,
                "average_score": float(latest_report.average_score or 0),
                "completed_courses": latest_report.completed_courses,
                "total_learning_minutes": latest_report.total_learning_minutes,
                "ai_summary": latest_report.ai_summary,
            }

        return {
            "user_id": user_id,
            "generated_on": date.today().isoformat(),
            "profile": profile_context,
            "recent_courses": recent_courses,
            "practice_summary": practice_context,
            "latest_assessment": assessment_context,
            "latest_skill_profile": skill_context,
            "active_learning_path": active_path_context,
            "latest_report": latest_report_context,
        }

    async def _safe_call(self, session: AsyncSession, awaitable, default):
        try:
            return await awaitable
        except Exception:
            return default
