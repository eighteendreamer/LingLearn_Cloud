from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DBSession, Pagination
from app.core.response import success
from app.modules.resource.service import ResourceService

router = APIRouter()


@router.get("")
async def list_resources(
    session: DBSession,
    pagination: Pagination,
    resource_type: Annotated[str | None, Query()] = None,
    category_id: Annotated[int | None, Query(gt=0)] = None,
    keyword: Annotated[str | None, Query()] = None,
):
    service = ResourceService()
    data = await service.list_resources(
        session,
        resource_type=resource_type,
        category_id=category_id,
        keyword=keyword,
        pagination=pagination,
    )
    return success(data=data.model_dump(mode="json"))


@router.get("/recent")
async def list_recent_resources(
    session: DBSession,
    current_user: CurrentUser,
    pagination: Pagination,
):
    service = ResourceService()
    data = await service.list_recent_resources(
        session,
        user_id=int(current_user.sub),
        pagination=pagination,
    )
    return success(data=data.model_dump(mode="json"))
