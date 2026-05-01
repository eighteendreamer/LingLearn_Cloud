from fastapi import APIRouter

from app.api.deps import CurrentUser, DBSession
from app.core.response import success
from app.modules.assessment.schemas import AssessmentGenerateRequest
from app.modules.assessment.service import AssessmentService

router = APIRouter()


@router.get("/users/me/assessments/latest")
async def get_latest_assessment(
    current_user: CurrentUser,
    session: DBSession,
):
    """Get the latest assessment snapshot for current user"""
    service = AssessmentService()
    result = await service.get_latest_assessment(session, int(current_user.sub))
    return success(data=result)


@router.get("/users/me/assessments/trend")
async def get_assessment_trend(
    current_user: CurrentUser,
    session: DBSession,
    assessment_type: str = "weekly",
):
    """Get assessment trend data for charts"""
    service = AssessmentService()
    result = await service.get_assessment_trend(session, int(current_user.sub), assessment_type)
    return success(data=result)


@router.post("/users/me/assessments/generate")
async def generate_assessment(
    payload: AssessmentGenerateRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    """Generate a new assessment snapshot"""
    service = AssessmentService()
    result = await service.generate_assessment(session, int(current_user.sub), payload)
    return success(data=result, message="Assessment generated successfully.")
