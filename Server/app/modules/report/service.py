import re

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
        snapshot = await self.assessment_repository.get_latest_snapshot(session, user_id)
        learning_data = {
            "report_month": report_month,
            "assessment_snapshot_id": snapshot.id if snapshot else None,
            "total_learning_minutes": snapshot.total_learning_minutes if snapshot else 0,
            "completed_courses": snapshot.completed_courses if snapshot else 0,
            "average_score": float(snapshot.average_score) if snapshot else 0,
            "correct_rate": float(snapshot.correct_rate) if snapshot and snapshot.correct_rate is not None else None,
            "focus_rate": float(snapshot.focus_rate) if snapshot and snapshot.focus_rate is not None else None,
        }

        ai_summary = "本月学习报告已生成。建议保持稳定节奏，并优先处理薄弱知识点。"
        strengths = ["学习记录已沉淀", "具备持续优化空间"]
        improvements = ["建议增加练习复盘", "建议补充阶段性小测"]
        achievements = [
            {
                "title": "完成月度复盘",
                "description": "系统已根据学习数据生成本月表现总结",
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
            ai_summary = report_content.get("detailed_report") or report_content.get("overview") or ai_summary
            strengths = report_content.get("highlights") or strengths
            improvements = report_content.get("improvements") or [
                item.get("title") or item.get("content")
                for item in recommendations
                if isinstance(item, dict) and (item.get("title") or item.get("content"))
            ] or improvements
            achievements = [
                {
                    "title": str(item),
                    "description": "AI 月报识别出的亮点",
                    "icon": "spark",
                    "color_token": "primary",
                }
                for item in strengths[:3]
            ] or achievements
        except Exception:
            pass

        report = await self.repository.upsert_report(
            session,
            user_id=user_id,
            report_month=report_month,
            assessment_snapshot_id=snapshot.id if snapshot else None,
            total_learning_minutes=learning_data["total_learning_minutes"],
            completed_courses=learning_data["completed_courses"],
            average_score=learning_data["average_score"],
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
    def _validate_report_month(report_month: str) -> None:
        if not re.fullmatch(r"\d{4}-\d{2}", report_month):
            raise BadRequestError(message="report_month must be in YYYY-MM format.")
