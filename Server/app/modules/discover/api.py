from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import DBSession
from app.core.response import success
from app.modules.discover.service import DiscoverService

router = APIRouter()


@router.get("/categories")
async def list_categories(session: DBSession):
    service = DiscoverService()
    data = await service.list_categories(session)
    return success(data=[item.model_dump(mode="json") for item in data])


@router.get("/hot-topics")
async def list_hot_topics(session: DBSession):
    service = DiscoverService()
    data = await service.list_hot_topics(session)
    return success(data=[item.model_dump(mode="json") for item in data])


@router.get("/hot-tags")
async def list_hot_tags(session: DBSession):
    service = DiscoverService()
    data = await service.list_hot_tags(session)
    return success(data=[item.model_dump(mode="json") for item in data])
