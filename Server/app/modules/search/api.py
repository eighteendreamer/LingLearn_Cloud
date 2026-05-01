from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import DBSession, OptionalCurrentUser, Pagination
from app.core.response import success
from app.modules.search.service import SearchService

router = APIRouter()


@router.get("/contents")
async def search_contents(
    session: DBSession,
    current_user: OptionalCurrentUser,
    pagination: Pagination,
    keyword: Annotated[str | None, Query(max_length=120)] = None,
    category_id: Annotated[int | None, Query(gt=0)] = None,
):
    service = SearchService()
    data = await service.search_contents(
        session,
        viewer_user_id=int(current_user.sub) if current_user else None,
        keyword=keyword,
        category_id=category_id,
        pagination=pagination,
    )
    return success(data=data.model_dump(mode="json"))
