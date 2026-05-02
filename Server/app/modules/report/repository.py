from sqlalchemy import Integer, desc, delete, func, select, union_all, update
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

    async def aggregate_monthly_stats(
        self,
        session: AsyncSession,
        user_id: int,
        report_month: str,
    ) -> dict:
        """Aggregate real learning data for a given YYYY-MM month from DB tables."""
        from app.modules.content.models import ContentCategory, ContentItem, ContentViewHistory
        from app.modules.course.models import UserCourseEnrollment, UserLessonProgress
        from app.modules.practice.models import PracticeAnswer, PracticeSession

        year_str, month_str = report_month.split("-")
        year, month = int(year_str), int(month_str)

        import calendar
        from datetime import date, datetime, time, timedelta

        period_start = date(year, month, 1)
        period_end = date(year, month, calendar.monthrange(year, month)[1])
        period_start_dt = datetime.combine(period_start, time.min)
        period_end_dt = datetime.combine(period_end + timedelta(days=1), time.min)
        submitted_session_time = func.coalesce(PracticeSession.finished_at, PracticeSession.submitted_at)

        lesson_minutes_result = await session.execute(
            select(func.coalesce(func.sum(UserLessonProgress.watch_seconds), 0))
            .where(UserLessonProgress.user_id == user_id)
            .where(func.date(UserLessonProgress.updated_at) >= period_start)
            .where(func.date(UserLessonProgress.updated_at) <= period_end)
        )
        content_minutes_result = await session.execute(
            select(func.coalesce(func.sum(ContentViewHistory.watch_seconds), 0))
            .where(ContentViewHistory.user_id == user_id)
            .where(ContentViewHistory.view_date >= period_start)
            .where(ContentViewHistory.view_date <= period_end)
        )
        total_learning_seconds = int(lesson_minutes_result.scalar() or 0) + int(content_minutes_result.scalar() or 0)
        total_learning_minutes = int(round(total_learning_seconds / 60)) if total_learning_seconds else 0

        completed_result = await session.execute(
            select(func.count(UserCourseEnrollment.id))
            .where(UserCourseEnrollment.user_id == user_id)
            .where(UserCourseEnrollment.completed_at.isnot(None))
            .where(func.date(UserCourseEnrollment.completed_at) >= period_start)
            .where(func.date(UserCourseEnrollment.completed_at) <= period_end)
        )
        completed_courses = int(completed_result.scalar() or 0)

        session_score_result = await session.execute(
            select(
                func.coalesce(
                    func.avg(
                        PracticeSession.earned_score * 100.0 /
                        func.nullif(PracticeSession.total_questions, 0)
                    ),
                    0
                )
            )
            .where(PracticeSession.user_id == user_id)
            .where(PracticeSession.status.in_(("submitted", "completed")))
            .where(PracticeSession.total_questions > 0)
            .where(submitted_session_time.isnot(None))
            .where(submitted_session_time >= period_start_dt)
            .where(submitted_session_time < period_end_dt)
        )
        average_score = float(session_score_result.scalar() or 0)

        correct_result = await session.execute(
            select(
                func.count(PracticeAnswer.id).label("total"),
                func.coalesce(func.sum(func.cast(PracticeAnswer.is_correct, Integer)), 0).label("correct"),
            )
            .join(PracticeSession, PracticeAnswer.session_id == PracticeSession.id)
            .where(PracticeSession.user_id == user_id)
            .where(PracticeSession.status.in_(("submitted", "completed")))
            .where(submitted_session_time.isnot(None))
            .where(submitted_session_time >= period_start_dt)
            .where(submitted_session_time < period_end_dt)
        )
        correct_row = correct_result.first()
        total_answers = int(correct_row.total or 0) if correct_row else 0
        correct_answers = int(correct_row.correct or 0) if correct_row else 0
        correct_rate = (correct_answers / total_answers * 100) if total_answers > 0 else None

        practice_session_count_result = await session.execute(
            select(func.count(PracticeSession.id))
            .where(PracticeSession.user_id == user_id)
            .where(PracticeSession.status.in_(("submitted", "completed")))
            .where(submitted_session_time.isnot(None))
            .where(submitted_session_time >= period_start_dt)
            .where(submitted_session_time < period_end_dt)
        )
        practice_sessions = int(practice_session_count_result.scalar() or 0)

        activity_days_union = union_all(
            select(ContentViewHistory.view_date.label("activity_date"))
            .where(ContentViewHistory.user_id == user_id)
            .where(ContentViewHistory.view_date >= period_start)
            .where(ContentViewHistory.view_date <= period_end),
            select(func.date(UserLessonProgress.updated_at).label("activity_date"))
            .where(UserLessonProgress.user_id == user_id)
            .where(UserLessonProgress.updated_at >= period_start_dt)
            .where(UserLessonProgress.updated_at < period_end_dt),
            select(func.date(submitted_session_time).label("activity_date"))
            .where(PracticeSession.user_id == user_id)
            .where(PracticeSession.status.in_(("submitted", "completed")))
            .where(submitted_session_time.isnot(None))
            .where(submitted_session_time >= period_start_dt)
            .where(submitted_session_time < period_end_dt),
        ).subquery()
        active_days_result = await session.execute(
            select(func.count(func.distinct(activity_days_union.c.activity_date)))
        )
        active_days = int(active_days_result.scalar() or 0)

        avg_watch_progress_result = await session.execute(
            select(func.avg(ContentViewHistory.watch_progress))
            .where(ContentViewHistory.user_id == user_id)
            .where(ContentViewHistory.view_date >= period_start)
            .where(ContentViewHistory.view_date <= period_end)
        )
        avg_watch_progress = float(avg_watch_progress_result.scalar() or 0)

        completed_views_result = await session.execute(
            select(func.count(ContentViewHistory.id))
            .where(ContentViewHistory.user_id == user_id)
            .where(ContentViewHistory.view_date >= period_start)
            .where(ContentViewHistory.view_date <= period_end)
            .where(ContentViewHistory.completed.is_(True))
        )
        completed_views = int(completed_views_result.scalar() or 0)

        all_views_result = await session.execute(
            select(func.count(ContentViewHistory.id))
            .where(ContentViewHistory.user_id == user_id)
            .where(ContentViewHistory.view_date >= period_start)
            .where(ContentViewHistory.view_date <= period_end)
        )
        all_views = int(all_views_result.scalar() or 0)
        view_completion_rate = (completed_views / all_views * 100) if all_views > 0 else 0.0
        focus_rate = min(
            100.0,
            ((active_days / max(1, period_end.day)) * 100 * 0.35) + (avg_watch_progress * 0.45) + (view_completion_rate * 0.20),
        )

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

        category_breakdown: list[dict] = []
        for row in category_rows:
            watch_seconds = int(row.get("watch_seconds") or 0)
            if watch_seconds <= 0:
                continue
            category_breakdown.append(
                {
                    "name": str(row.get("category_name") or "未分类"),
                    "watch_minutes": round(watch_seconds / 60, 1),
                    "value": round((watch_seconds / total_learning_seconds) * 100, 1) if total_learning_seconds else 0.0,
                }
            )

        return {
            "total_learning_minutes": total_learning_minutes,
            "completed_courses": completed_courses,
            "average_score": round(average_score, 2),
            "correct_rate": round(correct_rate, 2) if correct_rate is not None else None,
            "focus_rate": round(focus_rate, 2),
            "practice_sessions": practice_sessions,
            "active_days": active_days,
            "category_breakdown": category_breakdown,
        }

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
