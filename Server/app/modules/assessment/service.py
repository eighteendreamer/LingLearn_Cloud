from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import utc_now_naive
from app.core.exceptions import NotFoundError
from app.infra.ai.agent_manager import AgentManager
from app.modules.assessment.models import AssessmentSnapshot
from app.modules.assessment.repository import AssessmentRepository
from app.modules.assessment.schemas import (
    AssessmentGenerateRequest,
    AssessmentSnapshotResponse,
    AssessmentTrendDataPoint,
    AssessmentTrendResponse,
)
from app.modules.content.models import ContentCategory, ContentItem, ContentViewHistory
from app.modules.course.models import UserCourseEnrollment
from app.modules.learning_path.repository import LearningPathRepository
from app.modules.practice.models import PracticeSession
from app.modules.user.repository import UserRepository


class AssessmentService:
    def __init__(
        self,
        *,
        repository: AssessmentRepository | None = None,
        user_repository: UserRepository | None = None,
        learning_path_repository: LearningPathRepository | None = None,
        agent_manager: AgentManager | None = None,
    ) -> None:
        self.repository = repository or AssessmentRepository()
        self.user_repository = user_repository or UserRepository()
        self.learning_path_repository = learning_path_repository or LearningPathRepository()
        self.agent_manager = agent_manager or AgentManager()

    async def get_latest_assessment(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> AssessmentSnapshotResponse | None:
        snapshot = await self.repository.get_latest_snapshot(session, user_id)
        return self._to_response(snapshot) if snapshot else None

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
        bundle = await self.user_repository.get_user_with_profile_and_settings(session, user_id)
        if not bundle:
            raise NotFoundError(message="User not found.")

        _, profile, _ = bundle
        period_start, period_end = self._resolve_period(payload.assessment_type)

        existing_snapshot = await self.repository.get_snapshot_for_period(
            session,
            user_id=user_id,
            assessment_type=payload.assessment_type,
            period_start=period_start,
            period_end=period_end,
        )
        if existing_snapshot and not payload.force_regenerate:
            return self._to_response(existing_snapshot)

        watch_metrics = await self._collect_watch_metrics(session, user_id, period_start, period_end)
        practice_metrics = await self._collect_practice_metrics(session, user_id, period_start, period_end)
        course_metrics = await self._collect_course_metrics(session, user_id, period_start, period_end)

        latest_skill_snapshot = await self.learning_path_repository.get_latest_snapshot(session, user_id)
        active_path = await self.learning_path_repository.get_active_user_path(session, user_id)

        total_learning_minutes = watch_metrics["total_learning_minutes"]
        completed_courses = course_metrics["completed_courses_period"]
        average_score = practice_metrics["average_score"]
        correct_rate = practice_metrics["correct_rate"]
        rank_percent = (
            round(float(latest_skill_snapshot.rank_percent or 0), 2)
            if latest_skill_snapshot and latest_skill_snapshot.rank_percent is not None
            else None
        )
        focus_rate = watch_metrics["focus_rate"]

        learning_data = {
            "latest_message": f"请基于用户在 {period_start.isoformat()} 到 {period_end.isoformat()} 的学习数据生成评估报告。",
            "assessment_type": payload.assessment_type,
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
                "days": (period_end - period_start).days + 1,
            },
            "profile": {
                "display_name": profile.display_name,
                "profession": profile.profession,
                "learning_goal": profile.learning_goal,
                "streak_days": profile.streak_days,
                "total_learning_minutes": profile.total_learning_minutes,
            },
            "watch_metrics": watch_metrics,
            "practice_metrics": practice_metrics,
            "course_metrics": course_metrics,
            "skill_snapshot": {
                "total_score": float(latest_skill_snapshot.total_score or 0) if latest_skill_snapshot else 0.0,
                "rank_percent": rank_percent,
            },
        }

        ai_report = await self._generate_ai_report(
            session=session,
            user_id=user_id,
            assessment_type=payload.assessment_type,
            period_start=period_start,
            period_end=period_end,
            learning_data=learning_data,
            path_progress={
                "progress_percent": float(active_path.progress_percent or 0) if active_path else 0.0,
                "status": active_path.status if active_path else None,
                "current_node_id": active_path.current_node_id if active_path else None,
            },
        )

        metrics_json = {
            "period": learning_data["period"],
            "profile": learning_data["profile"],
            "watch_metrics": watch_metrics,
            "practice_metrics": practice_metrics,
            "course_metrics": course_metrics,
            "skill_snapshot": learning_data["skill_snapshot"],
            "report": ai_report,
        }

        now = utc_now_naive()
        snapshot_values = {
            "total_learning_minutes": total_learning_minutes,
            "completed_courses": completed_courses,
            "average_score": round(average_score, 2),
            "rank_percent": rank_percent,
            "correct_rate": round(correct_rate, 2),
            "focus_rate": round(focus_rate, 2),
            "metrics_json": metrics_json,
            "updated_at": now,
        }

        try:
            if existing_snapshot:
                for key, value in snapshot_values.items():
                    setattr(existing_snapshot, key, value)
                snapshot = existing_snapshot
            else:
                snapshot = await self.repository.create_snapshot(
                    session,
                    user_id=user_id,
                    assessment_type=payload.assessment_type,
                    period_start=period_start,
                    period_end=period_end,
                    total_learning_minutes=total_learning_minutes,
                    completed_courses=completed_courses,
                    average_score=round(average_score, 2),
                    rank_percent=rank_percent,
                    correct_rate=round(correct_rate, 2),
                    focus_rate=round(focus_rate, 2),
                    metrics_json=metrics_json,
                    created_at=now,
                )
            await session.commit()
            await session.refresh(snapshot)
        except Exception:
            await session.rollback()
            raise

        return self._to_response(snapshot)

    async def _collect_watch_metrics(
        self,
        session: AsyncSession,
        user_id: int,
        period_start: date,
        period_end: date,
    ) -> dict[str, Any]:
        histories = list(
            (
                await session.execute(
                    select(ContentViewHistory).where(
                        ContentViewHistory.user_id == user_id,
                        ContentViewHistory.view_date >= period_start,
                        ContentViewHistory.view_date <= period_end,
                    )
                )
            )
            .scalars()
            .all()
        )

        total_watch_seconds = sum(int(item.watch_seconds or 0) for item in histories)
        total_learning_minutes = int(round(total_watch_seconds / 60)) if total_watch_seconds else 0
        active_days = len({item.view_date for item in histories if item.view_date})
        avg_watch_progress = (
            sum(float(item.watch_progress or 0) for item in histories) / len(histories)
            if histories
            else 0.0
        )
        completed_views = sum(1 for item in histories if item.completed)
        period_days = max(1, (period_end - period_start).days + 1)
        active_day_ratio = active_days / period_days * 100
        completion_ratio = completed_views / len(histories) * 100 if histories else 0.0
        focus_rate = min(100.0, active_day_ratio * 0.35 + avg_watch_progress * 0.45 + completion_ratio * 0.20)

        category_rows = (
            await session.execute(
                select(
                    ContentCategory.name.label("category_name"),
                    func.sum(ContentViewHistory.watch_seconds).label("watch_seconds"),
                )
                .select_from(ContentViewHistory)
                .join(ContentItem, ContentItem.id == ContentViewHistory.content_item_id)
                .outerjoin(ContentCategory, ContentCategory.id == ContentItem.category_id)
                .where(
                    ContentViewHistory.user_id == user_id,
                    ContentViewHistory.view_date >= period_start,
                    ContentViewHistory.view_date <= period_end,
                )
                .group_by(ContentCategory.name)
                .order_by(func.sum(ContentViewHistory.watch_seconds).desc())
                .limit(5)
            )
        ).mappings().all()

        category_breakdown: list[dict[str, Any]] = []
        for row in category_rows:
            watch_seconds = int(row.get("watch_seconds") or 0)
            if watch_seconds <= 0:
                continue
            category_breakdown.append(
                {
                    "name": str(row.get("category_name") or "未分类"),
                    "watch_minutes": round(watch_seconds / 60, 1),
                    "value": round((watch_seconds / total_watch_seconds) * 100, 1) if total_watch_seconds else 0.0,
                }
            )

        return {
            "total_learning_minutes": total_learning_minutes,
            "total_watch_seconds": total_watch_seconds,
            "active_days": active_days,
            "period_days": period_days,
            "avg_watch_progress": round(avg_watch_progress, 2),
            "completed_views": completed_views,
            "focus_rate": round(focus_rate, 2),
            "category_breakdown": category_breakdown,
        }

    async def _collect_practice_metrics(
        self,
        session: AsyncSession,
        user_id: int,
        period_start: date,
        period_end: date,
    ) -> dict[str, Any]:
        start_dt = datetime.combine(period_start, time.min)
        end_dt = datetime.combine(period_end + timedelta(days=1), time.min)
        sessions = list(
            (
                await session.execute(
                    select(PracticeSession)
                    .where(
                        PracticeSession.user_id == user_id,
                        PracticeSession.started_at >= start_dt,
                        PracticeSession.started_at < end_dt,
                    )
                    .order_by(PracticeSession.started_at.desc(), PracticeSession.id.desc())
                )
            )
            .scalars()
            .all()
        )

        completed_sessions = [item for item in sessions if item.status == "completed"]
        total_questions = sum(int(item.total_questions or 0) for item in completed_sessions)
        answered_questions = sum(int(item.answered_questions or 0) for item in completed_sessions)
        correct_answers = sum(int(item.correct_answers or 0) for item in completed_sessions)
        earned_score = sum(float(item.earned_score or 0) for item in completed_sessions)

        average_score = (earned_score / total_questions * 100) if total_questions > 0 else 0.0
        correct_rate = (correct_answers / answered_questions * 100) if answered_questions > 0 else 0.0

        return {
            "session_count": len(sessions),
            "completed_session_count": len(completed_sessions),
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "correct_answers": correct_answers,
            "earned_score": round(earned_score, 2),
            "average_score": round(average_score, 2),
            "correct_rate": round(correct_rate, 2),
        }

    async def _collect_course_metrics(
        self,
        session: AsyncSession,
        user_id: int,
        period_start: date,
        period_end: date,
    ) -> dict[str, Any]:
        start_dt = datetime.combine(period_start, time.min)
        end_dt = datetime.combine(period_end + timedelta(days=1), time.min)
        enrollments = list(
            (
                await session.execute(
                    select(UserCourseEnrollment).where(UserCourseEnrollment.user_id == user_id)
                )
            )
            .scalars()
            .all()
        )

        completed_courses_total = sum(1 for item in enrollments if float(item.progress_percent or 0) >= 100)
        completed_courses_period = sum(
            1
            for item in enrollments
            if item.completed_at is not None and start_dt <= item.completed_at < end_dt
        )
        active_courses_period = sum(
            1
            for item in enrollments
            if item.updated_at is not None and start_dt <= item.updated_at < end_dt
        )

        return {
            "enrolled_course_count": len(enrollments),
            "completed_courses_total": completed_courses_total,
            "completed_courses_period": completed_courses_period,
            "active_courses_period": active_courses_period,
        }

    async def _generate_ai_report(
        self,
        *,
        session: AsyncSession,
        user_id: int,
        assessment_type: str,
        period_start: date,
        period_end: date,
        learning_data: dict[str, Any],
        path_progress: dict[str, Any],
    ) -> dict[str, Any]:
        fallback = self._build_fallback_report(
            assessment_type=assessment_type,
            period_start=period_start,
            period_end=period_end,
            learning_data=learning_data,
            path_progress=path_progress,
        )
        try:
            result = await self.agent_manager.run_learning_evaluation_agent(
                session,
                user_id=user_id,
                month=period_end.strftime("%Y-%m") if assessment_type == "monthly" else None,
                learning_data=learning_data,
                path_progress=path_progress,
            )
        except Exception:
            return fallback

        diagnosis = self._extract_agent_text(result.get("diagnosis"))
        learner_portrait = self._extract_agent_text(result.get("learner_portrait"))
        optimization = self._extract_agent_text(result.get("optimization"))
        overview = self._extract_agent_text(result.get("report_content"))
        recommendations = self._normalize_recommendations(result.get("recommendations"))

        report = {
            "overview": overview or fallback["overview"],
            "diagnosis": diagnosis or fallback["diagnosis"],
            "learner_portrait": learner_portrait or fallback["learner_portrait"],
            "optimization": optimization or fallback["optimization"],
            "recommendations": recommendations or fallback["recommendations"],
        }

        if not any([diagnosis, learner_portrait, optimization, overview]):
            return fallback
        return report

    def _build_fallback_report(
        self,
        *,
        assessment_type: str,
        period_start: date,
        period_end: date,
        learning_data: dict[str, Any],
        path_progress: dict[str, Any],
    ) -> dict[str, Any]:
        watch_metrics = learning_data["watch_metrics"]
        practice_metrics = learning_data["practice_metrics"]
        course_metrics = learning_data["course_metrics"]
        profile = learning_data["profile"]
        period_label = self._assessment_type_label(assessment_type)

        overview = (
            f"本次{period_label}评估覆盖 {period_start.isoformat()} 至 {period_end.isoformat()}。"
            f"你累计有效学习约 {watch_metrics['total_learning_minutes']} 分钟，"
            f"完成练习 {practice_metrics['completed_session_count']} 次，"
            f"本周期完成课程 {course_metrics['completed_courses_period']} 门。"
        )
        diagnosis = (
            f"当前学习节奏以视频学习为主，活跃学习天数为 {watch_metrics['active_days']} 天，"
            f"平均观看进度 {watch_metrics['avg_watch_progress']:.1f}% 。"
            f"练习平均得分 {practice_metrics['average_score']:.1f} 分，"
            f"答题正确率 {practice_metrics['correct_rate']:.1f}% 。"
        )
        learner_portrait = (
            f"你当前更像一位“持续推进型”学习者。"
            f"连续学习 {profile.get('streak_days') or 0} 天，"
            f"学习目标聚焦在 {profile.get('learning_goal') or '当前阶段能力提升'}，"
            f"当前学习路径进度约 {float(path_progress.get('progress_percent') or 0):.1f}% 。"
        )
        optimization = (
            "接下来建议把“看视频”和“做练习”继续绑定起来："
            "每完成一个主题视频，立即补一组同主题练习；"
            "若本周期课程完成数较低，优先把现有路径中的当前节点学完，再扩展新主题。"
        )
        recommendations = [
            {
                "type": "practice",
                "title": "视频后立即练习",
                "description": "每看完一个主题视频，立刻完成一组 3-5 题的同主题练习，强化记忆闭环。",
            },
            {
                "type": "review",
                "title": "每周固定复盘一次",
                "description": "挑出本周期错题和观看进度低于 60% 的内容，集中做一次回看和复盘。",
            },
            {
                "type": "path",
                "title": "优先推进当前学习路径",
                "description": "先完成当前学习路径节点，再决定是否增加新的课程或视频主题，避免分散注意力。",
            },
        ]
        return {
            "overview": overview,
            "diagnosis": diagnosis,
            "learner_portrait": learner_portrait,
            "optimization": optimization,
            "recommendations": recommendations,
        }

    @staticmethod
    def _normalize_recommendations(value: Any) -> list[dict[str, str]]:
        if not isinstance(value, list):
            return []
        normalized: list[dict[str, str]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or f"建议 {index}").strip()
            description = str(item.get("description") or item.get("content") or "").strip()
            recommendation_type = str(item.get("type") or "optimization").strip()
            if not description:
                continue
            normalized.append(
                {
                    "type": recommendation_type,
                    "title": title,
                    "description": description,
                }
            )
        return normalized

    @staticmethod
    def _extract_agent_text(value: Any) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            for key in ("raw", "content", "summary", "overview", "detailed_report"):
                inner = value.get(key)
                if isinstance(inner, str) and inner.strip():
                    return inner.strip()
        return ""

    @staticmethod
    def _resolve_period(assessment_type: str) -> tuple[date, date]:
        today = date.today()
        if assessment_type == "daily":
            return today, today
        if assessment_type == "monthly":
            return today - timedelta(days=29), today
        return today - timedelta(days=6), today

    @staticmethod
    def _assessment_type_label(assessment_type: str) -> str:
        return {
            "daily": "日度",
            "weekly": "周度",
            "monthly": "月度",
        }.get(assessment_type, "阶段")

    @staticmethod
    def _to_response(snapshot: AssessmentSnapshot) -> AssessmentSnapshotResponse:
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
