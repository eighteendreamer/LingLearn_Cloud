from __future__ import annotations

from statistics import mean
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_chat.repository import AIChatRepository
from app.modules.assessment.repository import AssessmentRepository
from app.modules.content.repository import ContentRepository
from app.modules.course.repository import CourseRepository
from app.modules.learning_path.repository import LearningPathRepository
from app.modules.practice.repository import PracticeRepository
from app.modules.report.repository import ReportRepository
from app.modules.user.repository import UserRepository


class AgentDatabaseContextBuilder:
    """Build per-agent tool context from real database data."""

    def __init__(self) -> None:
        self.user_repository = UserRepository()
        self.ai_chat_repository = AIChatRepository()
        self.content_repository = ContentRepository()
        self.course_repository = CourseRepository()
        self.practice_repository = PracticeRepository()
        self.assessment_repository = AssessmentRepository()
        self.learning_path_repository = LearningPathRepository()
        self.report_repository = ReportRepository()

    async def build_user_interaction_context(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        session_id: int | None,
        latest_user_text: str,
        recent_transcript: list[dict[str, str]],
    ) -> dict[str, Any]:
        profile = await self._profile_context(session, user_id)
        favorite_rows = await self._favorite_rows(session, user_id, limit=5)
        watch_rows = await self._watch_history_rows(session, user_id, limit=5)
        db_transcript = await self._session_transcript(session, session_id, limit=8)

        return {
            "workflow-router": {
                "latest_user_text": latest_user_text,
                "scene_code": "study_assistant",
                "preferred_route_source": "llm_intent",
            },
            "learning-context-reader": profile,
            "session-memory-reader": {"recent_transcript": db_transcript or recent_transcript[-8:]},
            "favorite-resource-manager": {
                "supports_favorite_action": True,
                "favorite_resources": favorite_rows,
                "recent_watch_history": watch_rows,
            },
            "response-style-planner": {
                "style": "markdown",
                "tone": "friendly_direct",
                "reply_granularity": "actionable",
                "locale": profile.get("locale") or "zh-CN",
            },
        }

    async def build_feature_extraction_context(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        source_type: str,
        source_ref_id: int | None,
        latest_user_text: str,
        recent_transcript: list[dict[str, str]],
    ) -> dict[str, Any]:
        latest_assessment = await self._latest_assessment(session, user_id)
        weekly_snapshots = await self._assessment_rows(session, user_id, "weekly", limit=4)
        practice_summary = await self._practice_summary(session, user_id, limit=8)

        return {
            "dialogue-evidence-reader": {
                "source_type": source_type,
                "source_ref_id": source_ref_id,
                "latest_question": latest_user_text,
                "dialogue_evidence": recent_transcript[-10:],
            },
            "six-dimension-profile-generator": {
                "dimensions": ["knowledge", "logic", "expression", "habit", "motivation", "reflection"],
                "latest_assessment": latest_assessment,
                "weekly_snapshots": weekly_snapshots,
                "practice_summary": practice_summary,
            },
            "assessment-snapshot-reader": {
                "latest_assessment": latest_assessment,
                "weekly_snapshots": weekly_snapshots,
            },
            "image-quality-validator": {
                "supported": True,
                "notes": "Awaiting image payload; current request contains text-first context.",
            },
        }

    async def build_resource_generation_context(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        latest_user_text: str,
    ) -> dict[str, Any]:
        profile = await self._profile_context(session, user_id)
        recent_courses = await self._recent_courses(session, user_id, limit=6)
        practice_summary = await self._practice_summary(session, user_id, limit=8)
        latest_assessment = await self._latest_assessment(session, user_id)
        active_path = await self._active_learning_path(session, user_id)
        skill_profile = await self._latest_skill_profile(session, user_id)
        favorites = await self._favorite_rows(session, user_id, limit=6)
        watch_history = await self._watch_history_rows(session, user_id, limit=6)

        return {
            "learning-goal-analyzer": {
                "goal": latest_user_text or profile.get("learning_goal"),
                "profile_goal": profile.get("learning_goal"),
                "profession": profile.get("profession"),
                "active_learning_path": active_path,
            },
            "learning-context-reader": profile,
            "course-progress-reader": {"recent_courses": recent_courses},
            "practice-history-reader": practice_summary,
            "resource-candidate-reader": {
                "favorites": favorites,
                "watch_history": watch_history,
                "recent_courses": recent_courses[:3],
                "latest_assessment": latest_assessment,
            },
            "learning-path-reader": {
                "active_learning_path": active_path,
                "latest_skill_profile": skill_profile,
            },
        }

    async def build_study_plan_context(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        latest_user_text: str,
        evaluation_type: str,
    ) -> dict[str, Any]:
        latest_assessment = await self._latest_assessment(session, user_id)
        weekly_snapshots = await self._assessment_rows(session, user_id, "weekly", limit=4)
        practice_summary = await self._practice_summary(session, user_id, limit=10)
        active_path = await self._active_learning_path(session, user_id)
        latest_report = await self._latest_report(session, user_id)

        average_score = latest_assessment.get("average_score") or practice_summary.get("average_score") or 0
        correct_rate = latest_assessment.get("correct_rate") or 0
        mastery_level = "advanced" if average_score >= 85 else "intermediate" if average_score >= 68 else "beginner"

        return {
            "assessment-snapshot-reader": {
                "evaluation_type": evaluation_type,
                "latest_assessment": latest_assessment,
                "weekly_snapshots": weekly_snapshots,
            },
            "practice-history-reader": practice_summary,
            "learning-path-reader": active_path,
            "mastery-scorer": {
                "average_score": average_score,
                "correct_rate": correct_rate,
                "mastery_level": mastery_level,
            },
            "study-report-writer": {
                "latest_report_summary": latest_report.get("ai_summary"),
                "latest_message": latest_user_text,
            },
        }

    async def build_tutor_qa_context(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        session_id: int | None,
        latest_user_text: str,
        recent_transcript: list[dict[str, str]],
        user_answer: str | None,
        correct_answer: str | None,
    ) -> dict[str, Any]:
        profile = await self._profile_context(session, user_id)
        practice_summary = await self._practice_summary(session, user_id, limit=6)
        latest_assessment = await self._latest_assessment(session, user_id)
        db_transcript = await self._session_transcript(session, session_id, limit=10)

        return {
            "question-intent-parser": {
                "question": latest_user_text,
                "estimated_level": self._infer_level_from_score(latest_assessment.get("average_score")),
            },
            "session-memory-reader": {"recent_transcript": db_transcript or recent_transcript[-10:]},
            "wrong-question-reader": {
                "latest_question": latest_user_text,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "recent_practice_sessions": practice_summary.get("sessions", []),
            },
            "socratic-hint-builder": {
                "strategy": "first hint, then guided steps, then concise summary",
                "learner_level": self._infer_level_from_score(latest_assessment.get("average_score")),
            },
            "concept-example-builder": {
                "example_style": "short_python_examples",
                "learning_goal": profile.get("learning_goal"),
            },
        }

    async def build_learning_evaluation_context(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        month: str | None,
        latest_user_text: str,
    ) -> dict[str, Any]:
        profile = await self._profile_context(session, user_id)
        latest_assessment = await self._latest_assessment(session, user_id)
        weekly_snapshots = await self._assessment_rows(session, user_id, "weekly", limit=4)
        monthly_snapshots = await self._assessment_rows(session, user_id, "monthly", limit=3)
        active_path = await self._active_learning_path(session, user_id)
        latest_report = await self._latest_report(session, user_id)
        skill_profile = await self._latest_skill_profile(session, user_id)

        return {
            "assessment-trend-reader": {
                "latest_assessment": latest_assessment,
                "weekly_snapshots": weekly_snapshots,
                "monthly_snapshots": monthly_snapshots,
            },
            "monthly-report-reader": {
                "target_month": month,
                "latest_report": latest_report,
            },
            "learning-path-reader": active_path,
            "learner-portrait-writer": {
                "profile": profile,
                "latest_skill_profile": skill_profile,
                "latest_report": latest_report,
            },
            "optimization-suggester": {
                "latest_score": latest_assessment.get("average_score"),
                "streak_days": profile.get("streak_days"),
                "path_progress": active_path.get("progress_percent"),
                "latest_message": latest_user_text,
            },
        }

    async def build_for_skill(
        self,
        session: AsyncSession,
        *,
        skill_code: str,
        user_id: int,
        tool_keys: list[str],
        session_id: int | None = None,
        latest_user_text: str = "",
        recent_transcript: list[dict[str, str]] | None = None,
        source_type: str | None = None,
        source_ref_id: int | None = None,
        evaluation_type: str | None = None,
        month: str | None = None,
        user_answer: str | None = None,
        correct_answer: str | None = None,
    ) -> dict[str, Any]:
        recent_transcript = recent_transcript or []
        if skill_code == "user_interaction":
            context = await self.build_user_interaction_context(
                session,
                user_id=user_id,
                session_id=session_id,
                latest_user_text=latest_user_text,
                recent_transcript=recent_transcript,
            )
        elif skill_code == "feature_extraction":
            context = await self.build_feature_extraction_context(
                session,
                user_id=user_id,
                source_type=source_type or "chat",
                source_ref_id=source_ref_id,
                latest_user_text=latest_user_text,
                recent_transcript=recent_transcript,
            )
        elif skill_code == "resource_generation":
            context = await self.build_resource_generation_context(
                session,
                user_id=user_id,
                latest_user_text=latest_user_text,
            )
        elif skill_code == "study_plan":
            context = await self.build_study_plan_context(
                session,
                user_id=user_id,
                latest_user_text=latest_user_text,
                evaluation_type=evaluation_type or "chat_assessment",
            )
        elif skill_code == "tutor_qa":
            context = await self.build_tutor_qa_context(
                session,
                user_id=user_id,
                session_id=session_id,
                latest_user_text=latest_user_text,
                recent_transcript=recent_transcript,
                user_answer=user_answer,
                correct_answer=correct_answer,
            )
        elif skill_code == "learning_evaluation":
            context = await self.build_learning_evaluation_context(
                session,
                user_id=user_id,
                month=month,
                latest_user_text=latest_user_text,
            )
        else:
            context = {}

        return {tool_key: context.get(tool_key, {}) for tool_key in tool_keys}

    async def _profile_context(self, session: AsyncSession, user_id: int) -> dict[str, Any]:
        bundle = await self._safe_call(
            self.user_repository.get_user_with_profile_and_settings(session, user_id),
            None,
        )
        if not bundle:
            return {}
        _, profile, settings = bundle
        return {
            "display_name": profile.display_name,
            "bio": profile.bio,
            "profession": profile.profession,
            "learning_goal": profile.learning_goal,
            "streak_days": profile.streak_days,
            "total_learning_minutes": profile.total_learning_minutes,
            "locale": profile.locale,
            "timezone": profile.timezone,
            "daily_reminder_enabled": settings.daily_reminder_enabled,
            "weekly_report_enabled": settings.weekly_report_enabled,
        }

    async def _recent_courses(self, session: AsyncSession, user_id: int, *, limit: int) -> list[dict[str, Any]]:
        payload = await self._safe_call(
            self.course_repository.list_user_enrollments(session, user_id, offset=0, limit=limit),
            ([], 0),
        )
        rows, _ = payload
        return [
            {
                "course_id": row["course_id"],
                "title": row["title"],
                "progress_percent": float(row["progress_percent"] or 0),
                "completed_lessons": int(row["completed_lessons"] or 0),
                "last_studied_at": self._dt(row.get("last_studied_at")),
            }
            for row in rows
        ]

    async def _practice_summary(self, session: AsyncSession, user_id: int, *, limit: int) -> dict[str, Any]:
        sessions = await self._safe_call(
            self.practice_repository.list_user_sessions(session, user_id=user_id, limit=limit),
            [],
        )
        completed = [item for item in sessions if item.status == "completed"]
        return {
            "recent_session_count": len(sessions),
            "completed_session_count": len(completed),
            "average_score": round(mean(float(item.earned_score or 0) for item in completed), 2) if completed else 0.0,
            "latest_status": sessions[0].status if sessions else None,
            "sessions": [
                {
                    "session_id": item.id,
                    "bank_id": item.bank_id,
                    "status": item.status,
                    "total_questions": item.total_questions,
                    "answered_questions": item.answered_questions,
                    "correct_answers": item.correct_answers,
                    "score": float(item.earned_score or 0),
                    "started_at": self._dt(item.started_at),
                    "submitted_at": self._dt(item.submitted_at),
                    "finished_at": self._dt(item.finished_at),
                }
                for item in sessions[:limit]
            ],
        }

    async def _latest_assessment(self, session: AsyncSession, user_id: int) -> dict[str, Any]:
        item = await self._safe_call(
            self.assessment_repository.get_latest_snapshot(session, user_id),
            None,
        )
        return self._serialize_assessment(item)

    async def _assessment_rows(
        self,
        session: AsyncSession,
        user_id: int,
        assessment_type: str,
        *,
        limit: int,
    ) -> list[dict[str, Any]]:
        rows = await self._safe_call(
            self.assessment_repository.list_snapshots_by_type(session, user_id, assessment_type, limit=limit),
            [],
        )
        return [self._serialize_assessment(item) for item in rows]

    async def _latest_skill_profile(self, session: AsyncSession, user_id: int) -> dict[str, Any]:
        item = await self._safe_call(
            self.learning_path_repository.get_latest_snapshot(session, user_id),
            None,
        )
        if not item:
            return {}
        return {
            "snapshot_id": item.id,
            "source_type": item.source_type,
            "total_score": float(item.total_score or 0),
            "rank_percent": float(item.rank_percent or 0),
            "generated_at": self._dt(item.generated_at),
        }

    async def _active_learning_path(self, session: AsyncSession, user_id: int) -> dict[str, Any]:
        item = await self._safe_call(
            self.learning_path_repository.get_active_user_path(session, user_id),
            None,
        )
        if not item:
            return {}
        return {
            "user_path_id": item.id,
            "path_id": item.path_id,
            "status": item.status,
            "progress_percent": float(item.progress_percent or 0),
            "current_node_id": item.current_node_id,
            "started_at": self._dt(item.started_at),
            "completed_at": self._dt(item.completed_at),
            "ai_summary": item.ai_summary,
        }

    async def _latest_report(self, session: AsyncSession, user_id: int) -> dict[str, Any]:
        rows = await self._safe_call(self.report_repository.list_user_reports(session, user_id), [])
        item = next(iter(rows), None)
        if not item:
            return {}
        return {
            "report_id": item.id,
            "report_month": item.report_month,
            "average_score": float(item.average_score or 0),
            "completed_courses": item.completed_courses,
            "total_learning_minutes": item.total_learning_minutes,
            "ai_summary": item.ai_summary,
            "generated_at": self._dt(item.generated_at),
        }

    async def _favorite_rows(self, session: AsyncSession, user_id: int, *, limit: int) -> list[dict[str, Any]]:
        payload = await self._safe_call(
            self.content_repository.list_user_favorites(session, user_id=user_id, offset=0, limit=limit),
            ([], 0),
        )
        rows, _ = payload
        return [
            {
                "content_id": row.get("id"),
                "title": row.get("title"),
                "summary": row.get("summary"),
                "category_name": row.get("category_name"),
                "favorited_at": self._dt(row.get("favorited_at")),
            }
            for row in rows
        ]

    async def _watch_history_rows(self, session: AsyncSession, user_id: int, *, limit: int) -> list[dict[str, Any]]:
        payload = await self._safe_call(
            self.content_repository.list_user_watch_history(session, user_id=user_id, offset=0, limit=limit),
            ([], 0),
        )
        rows, _ = payload
        return [
            {
                "content_id": row.get("id"),
                "title": row.get("title"),
                "watch_progress": float(row.get("history_watch_progress") or 0),
                "watch_seconds": int(row.get("history_watch_seconds") or 0),
                "last_viewed_at": self._dt(row.get("history_last_viewed_at")),
            }
            for row in rows
        ]

    async def _session_transcript(
        self,
        session: AsyncSession,
        session_id: int | None,
        *,
        limit: int,
    ) -> list[dict[str, str]]:
        if not session_id:
            return []
        rows = await self._safe_call(
            self.ai_chat_repository.list_session_messages(session, session_id, limit=limit),
            [],
        )
        return [
            {
                "role": item.role,
                "content": item.content,
            }
            for item in rows[-limit:]
        ]

    async def _safe_call(self, awaitable, default):
        try:
            return await awaitable
        except Exception:
            return default

    @staticmethod
    def _serialize_assessment(item) -> dict[str, Any]:
        if not item:
            return {}
        return {
            "assessment_id": item.id,
            "assessment_type": item.assessment_type,
            "period_start": item.period_start.isoformat() if item.period_start else None,
            "period_end": item.period_end.isoformat() if item.period_end else None,
            "total_learning_minutes": item.total_learning_minutes,
            "completed_courses": item.completed_courses,
            "average_score": float(item.average_score or 0),
            "rank_percent": float(item.rank_percent or 0) if item.rank_percent is not None else None,
            "correct_rate": float(item.correct_rate or 0) if item.correct_rate is not None else None,
            "focus_rate": float(item.focus_rate or 0) if item.focus_rate is not None else None,
            "metrics": item.metrics_json or {},
        }

    @staticmethod
    def _infer_level_from_score(score: Any) -> str:
        try:
            numeric = float(score or 0)
        except (TypeError, ValueError):
            numeric = 0.0
        if numeric >= 85:
            return "advanced"
        if numeric >= 68:
            return "intermediate"
        return "beginner"

    @staticmethod
    def _dt(value: Any) -> str | None:
        if value is None:
            return None
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)
