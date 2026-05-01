from fastapi import APIRouter

from app.api.deps import CurrentUser, DBSession
from app.core.response import success
from app.modules.report.service import ReportService

router = APIRouter()


@router.get("/users/me/reports")
async def list_reports(
    current_user: CurrentUser,
    session: DBSession,
):
    service = ReportService()
    result = await service.list_reports(session, int(current_user.sub))
    return success(data=result)


@router.get("/users/me/reports/{report_month}")
async def get_report(
    report_month: str,
    current_user: CurrentUser,
    session: DBSession,
):
    service = ReportService()
    result = await service.get_report(session, int(current_user.sub), report_month)
    return success(data=result)


@router.post("/users/me/reports/{report_month}/generate")
async def generate_report(
    report_month: str,
    current_user: CurrentUser,
    session: DBSession,
):
    service = ReportService()
    result = await service.generate_report(session, int(current_user.sub), report_month)
    return success(data=result, message="Monthly report generated successfully.")


@router.post("/users/me/reports/{report_month}/export")
async def export_report(
    report_month: str,
    current_user: CurrentUser,
    session: DBSession,
):
    service = ReportService()
    result = await service.export_report(session, int(current_user.sub), report_month)
    return success(data=result, message="Monthly report exported successfully.")
