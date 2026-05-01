from fastapi import APIRouter

from app.api.deps import CurrentUser, DBSession, Pagination
from app.core.response import success
from app.modules.course.service import CourseService

router = APIRouter()


@router.get("/dashboard")
async def get_learning_dashboard(
    session: DBSession,
    current_user: CurrentUser,
):
    service = CourseService()
    data = await service.get_learning_dashboard(session, int(current_user.sub))
    return success(data=data.model_dump(mode="json"))


@router.get("/courses")
async def list_user_learning_courses(
    session: DBSession,
    current_user: CurrentUser,
    pagination: Pagination,
):
    service = CourseService()
    data = await service.list_user_courses(
        session,
        user_id=int(current_user.sub),
        pagination=pagination,
    )
    return success(data=data.model_dump(mode="json"))
