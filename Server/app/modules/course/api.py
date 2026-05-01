from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DBSession, OptionalCurrentUser, Pagination
from app.core.response import success
from app.modules.course.service import CourseService

router = APIRouter()


@router.get("")
async def list_courses(
    session: DBSession,
    current_user: OptionalCurrentUser,
    pagination: Pagination,
    category_id: Annotated[int | None, Query(gt=0)] = None,
):
    service = CourseService()
    data = await service.list_courses(
        session,
        viewer_user_id=int(current_user.sub) if current_user else None,
        category_id=category_id,
        pagination=pagination,
    )
    return success(data=data.model_dump(mode="json"))


@router.get("/{course_id}")
async def get_course_detail(
    course_id: int,
    session: DBSession,
    current_user: OptionalCurrentUser,
):
    service = CourseService()
    data = await service.get_course_detail(
        session,
        course_id=course_id,
        viewer_user_id=int(current_user.sub) if current_user else None,
    )
    return success(data=data.model_dump(mode="json"))


@router.post("/{course_id}/enroll")
async def enroll_course(
    course_id: int,
    session: DBSession,
    current_user: CurrentUser,
):
    service = CourseService()
    data = await service.enroll_course(
        session,
        user_id=int(current_user.sub),
        course_id=course_id,
    )
    return success(data=data.model_dump(mode="json"))
