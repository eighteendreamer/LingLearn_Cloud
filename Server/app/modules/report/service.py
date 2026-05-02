from __future__ import annotations

import re
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, NotFoundError
from app.infra.ai.agent_manager import AgentManager
from app.modules.assessment.repository import AssessmentRepository
from app.modules.report.repository import ReportRepository
from app.modules.report.schemas import (
    MonthlyReportResponse,
    ReportAchievementResponse,
    ReportExportResponse,
)


class ReportService:
    def __init__(
        self,
        *,
        repository: ReportRepository | None = None,
        assessment_repository: AssessmentRepository | None = None,
    ) -> None:
        self.repository = repository or ReportRepository()
        self.assessment_repository = assessment_repository or AssessmentRepository()
        self.agent_manager = AgentManager()

    async def list_reports(self, session: AsyncSession, user_id: int) -> list[MonthlyReportResponse]:
        reports = await self.repository.list_user_reports(session, user_id)
        return [await self._build_response(session, report) for report in reports]

    async def get_report(self, session: AsyncSession, user_id: int, report_month: str) -> MonthlyReportResponse:
        self._validate_report_month(report_month)
        report = await self.repository.get_report(session, user_id, report_month)
        if not report:
            raise NotFoundError(message="Monthly report not found.")
        return await self._build_response(session, report)

    async def generate_report(self, session: AsyncSession, user_id: int, report_month: str) -> MonthlyReportResponse:
        self._validate_report_month(report_month)

        monthly_stats = await self.repository.aggregate_monthly_stats(session, user_id, report_month)
        snapshot = await self.assessment_repository.get_latest_snapshot(session, user_id, assessment_type="monthly")
        latest_snapshot = snapshot or await self.assessment_repository.get_latest_snapshot(session, user_id)

        total_learning_minutes = monthly_stats["total_learning_minutes"]
        completed_courses = monthly_stats["completed_courses"]
        average_score = monthly_stats["average_score"]
        correct_rate = monthly_stats["correct_rate"]
        focus_rate = monthly_stats["focus_rate"]
        practice_sessions = monthly_stats["practice_sessions"]
        active_days = monthly_stats["active_days"]
        category_breakdown = monthly_stats["category_breakdown"]

        if total_learning_minutes == 0 and latest_snapshot:
            total_learning_minutes = latest_snapshot.total_learning_minutes
        if completed_courses == 0 and latest_snapshot:
            completed_courses = latest_snapshot.completed_courses
        if average_score == 0 and latest_snapshot:
            average_score = float(latest_snapshot.average_score or 0)
        if correct_rate is None and latest_snapshot and latest_snapshot.correct_rate is not None:
            correct_rate = float(latest_snapshot.correct_rate)
        if focus_rate is None and latest_snapshot and latest_snapshot.focus_rate is not None:
            focus_rate = float(latest_snapshot.focus_rate)

        learning_data = {
            "report_month": report_month,
            "assessment_snapshot_id": latest_snapshot.id if latest_snapshot else None,
            "total_learning_minutes": total_learning_minutes,
            "completed_courses": completed_courses,
            "average_score": average_score,
            "correct_rate": correct_rate,
            "focus_rate": focus_rate,
            "practice_sessions": practice_sessions,
            "active_days": active_days,
            "category_breakdown": category_breakdown,
        }

        ai_summary = (
            f"{report_month} 学习报告已生成。"
            f"本月累计学习 {total_learning_minutes} 分钟，完成课程 {completed_courses} 门，"
            f"练习平均分 {round(float(average_score or 0), 1)} 分。"
        )
        strengths = self._build_default_strengths(
            total_learning_minutes=total_learning_minutes,
            active_days=active_days,
            average_score=average_score,
        )
        improvements = self._build_default_improvements(
            total_learning_minutes=total_learning_minutes,
            correct_rate=correct_rate,
            completed_courses=completed_courses,
        )
        achievements = [
            {
                "title": "完成月度复盘",
                "description": "系统已根据本月学习数据生成阶段总结与建议。",
                "icon": "report",
                "color_token": "success",
            }
        ]

        try:
            agent_result = await self.agent_manager.run_monthly_report(
                session,
                user_id=user_id,
                month=report_month,
                learning_data=learning_data,
            )
            report_content = agent_result.get("report_content") or {}
            recommendations = agent_result.get("recommendations") or []

            ai_summary = (
                self._extract_text(report_content, "detailed_report")
                or self._extract_text(report_content, "overview")
                or ai_summary
            )

            report_highlights = report_content.get("highlights")
            if isinstance(report_highlights, list):
                strengths = [str(item).strip() for item in report_highlights if str(item).strip()] or strengths

            report_improvements = report_content.get("improvements")
            if isinstance(report_improvements, list):
                improvements = [str(item).strip() for item in report_improvements if str(item).strip()] or improvements
            else:
                recommendation_texts = [
                    str(item.get("title") or item.get("content") or item.get("description") or "").strip()
                    for item in recommendations
                    if isinstance(item, dict)
                ]
                recommendation_texts = [item for item in recommendation_texts if item]
                if recommendation_texts:
                    improvements = recommendation_texts[:4]

            generated_achievements = []
            for item in strengths[:3]:
                generated_achievements.append(
                    {
                        "title": item[:24],
                        "description": item,
                        "icon": "star",
                        "color_token": "primary",
                    }
                )
            if generated_achievements:
                achievements = generated_achievements
        except Exception:
            pass

        report = await self.repository.upsert_report(
            session,
            user_id=user_id,
            report_month=report_month,
            assessment_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            total_learning_minutes=total_learning_minutes,
            completed_courses=completed_courses,
            average_score=average_score,
            site_rank=None,
            strengths=strengths,
            improvements=improvements,
            ai_summary=ai_summary,
            achievements=achievements,
        )
        await session.commit()
        return await self._build_response(session, report)

    async def export_report(self, session: AsyncSession, user_id: int, report_month: str) -> ReportExportResponse:
        self._validate_report_month(report_month)
        report = await self.repository.get_report(session, user_id, report_month)
        if not report:
            raise NotFoundError(message="Monthly report not found.")
        await self.repository.mark_exported(
            session,
            user_id=user_id,
            report_month=report_month,
            exported_pdf_asset_id=report.exported_pdf_asset_id,
        )
        await session.commit()
        return ReportExportResponse(
            report_month=report_month,
            exported_pdf_asset_id=report.exported_pdf_asset_id,
            status="exported",
        )

    async def _build_response(self, session: AsyncSession, report) -> MonthlyReportResponse:
        achievements = await self.repository.list_achievements(session, report.id)
        return MonthlyReportResponse(
            id=report.id,
            user_id=report.user_id,
            report_month=report.report_month,
            assessment_snapshot_id=report.assessment_snapshot_id,
            report_status=report.report_status,
            total_learning_minutes=report.total_learning_minutes,
            completed_courses=report.completed_courses,
            average_score=float(report.average_score),
            site_rank=report.site_rank,
            strengths=report.strengths_json or [],
            improvements=report.improvements_json or [],
            ai_summary=report.ai_summary,
            exported_pdf_asset_id=report.exported_pdf_asset_id,
            generated_at=report.generated_at,
            achievements=[
                ReportAchievementResponse(
                    id=item.id,
                    title=item.title,
                    description=item.description,
                    icon=item.icon,
                    color_token=item.color_token,
                    sort_order=item.sort_order,
                )
                for item in achievements
            ],
        )

    @staticmethod
    def _build_default_strengths(
        *,
        total_learning_minutes: int,
        active_days: int,
        average_score: float,
    ) -> list[str]:
        strengths: list[str] = []
        if total_learning_minutes > 0:
            strengths.append(f"本月累计学习 {total_learning_minutes} 分钟，已经形成稳定投入。")
        if active_days >= 4:
            strengths.append(f"本月活跃学习 {active_days} 天，学习节奏比较稳定。")
        if average_score >= 70:
            strengths.append(f"本月练习平均分 {round(float(average_score), 1)} 分，整体掌握情况良好。")
        if not strengths:
            strengths.append("本月学习数据已开始沉淀，适合继续积累形成趋势。")
        return strengths[:4]

    @staticmethod
    def _build_default_improvements(
        *,
        total_learning_minutes: int,
        correct_rate: float | None,
        completed_courses: int,
    ) -> list[str]:
        improvements: list[str] = []
        if total_learning_minutes < 120:
            improvements.append("建议适当增加每周固定学习时段，先把学习总时长稳定下来。")
        if correct_rate is not None and correct_rate < 70:
            improvements.append("建议增加练习后的错题复盘，优先巩固正确率偏低的知识点。")
        if completed_courses == 0:
            improvements.append("建议优先完成一个当前正在学习的课程节点，形成阶段成果。")
        if not improvements:
            improvements.append("建议继续保持当前节奏，并在每次学习后增加小结或练习巩固。")
        return improvements[:4]

    @staticmethod
    def _extract_text(value: Any, key: str) -> str:
        if isinstance(value, dict):
            inner = value.get(key)
            if isinstance(inner, str):
                return inner.strip()
        return ""

    @staticmethod
    def _validate_report_month(report_month: str) -> None:
        if not re.fullmatch(r"\d{4}-\d{2}", report_month):
            raise BadRequestError(message="report_month must be in YYYY-MM format.")
