from sqlalchemy import desc, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import utc_now_naive
from app.modules.report.models import MonthlyReport, ReportAchievement


class ReportRepository:
    async def list_user_reports(self, session: AsyncSession, user_id: int) -> list[MonthlyReport]:
        result = await session.execute(
            select(MonthlyReport)
            .where(MonthlyReport.user_id == user_id)
            .order_by(desc(MonthlyReport.report_month), desc(MonthlyReport.id))
        )
        return list(result.scalars().all())

    async def get_report(self, session: AsyncSession, user_id: int, report_month: str) -> MonthlyReport | None:
        return await session.scalar(
            select(MonthlyReport).where(
                MonthlyReport.user_id == user_id,
                MonthlyReport.report_month == report_month,
            )
        )

    async def list_achievements(self, session: AsyncSession, report_id: int) -> list[ReportAchievement]:
        result = await session.execute(
            select(ReportAchievement)
            .where(ReportAchievement.report_id == report_id)
            .order_by(ReportAchievement.sort_order, ReportAchievement.id)
        )
        return list(result.scalars().all())

    async def upsert_report(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        report_month: str,
        assessment_snapshot_id: int | None,
        total_learning_minutes: int,
        completed_courses: int,
        average_score: float,
        site_rank: int | None,
        strengths: list,
        improvements: list,
        ai_summary: str,
        achievements: list[dict],
    ) -> MonthlyReport:
        now = utc_now_naive()
        report = await self.get_report(session, user_id, report_month)
        if report:
            report.assessment_snapshot_id = assessment_snapshot_id
            report.report_status = "generated"
            report.total_learning_minutes = total_learning_minutes
            report.completed_courses = completed_courses
            report.average_score = average_score
            report.site_rank = site_rank
            report.strengths_json = strengths
            report.improvements_json = improvements
            report.ai_summary = ai_summary
            report.generated_at = now
            report.updated_at = now
            await session.flush()
            await session.execute(delete(ReportAchievement).where(ReportAchievement.report_id == report.id))
        else:
            report = MonthlyReport(
                user_id=user_id,
                report_month=report_month,
                assessment_snapshot_id=assessment_snapshot_id,
                report_status="generated",
                total_learning_minutes=total_learning_minutes,
                completed_courses=completed_courses,
                average_score=average_score,
                site_rank=site_rank,
                strengths_json=strengths,
                improvements_json=improvements,
                ai_summary=ai_summary,
                generated_at=now,
                created_at=now,
                updated_at=now,
            )
            session.add(report)
            await session.flush()

        session.add_all(
            [
                ReportAchievement(
                    report_id=report.id,
                    title=item["title"],
                    description=item.get("description"),
                    icon=item.get("icon"),
                    color_token=item.get("color_token"),
                    sort_order=index,
                    created_at=now,
                )
                for index, item in enumerate(achievements, start=1)
            ]
        )
        await session.flush()
        await session.refresh(report)
        return report

    async def mark_exported(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        report_month: str,
        exported_pdf_asset_id: int | None,
    ) -> bool:
        result = await session.execute(
            update(MonthlyReport)
            .where(MonthlyReport.user_id == user_id, MonthlyReport.report_month == report_month)
            .values(
                report_status="exported",
                exported_pdf_asset_id=exported_pdf_asset_id,
                updated_at=utc_now_naive(),
            )
        )
        return bool(result.rowcount)
