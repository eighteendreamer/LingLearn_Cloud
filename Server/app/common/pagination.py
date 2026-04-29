from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

from app.common.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=DEFAULT_PAGE, ge=1)
    page_size: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PageResponse(BaseModel, Generic[T]):
    list: list[T]
    page: int
    page_size: int
    total: int
    has_more: bool


def get_pagination_params(
    page: int = Query(DEFAULT_PAGE, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


def build_page_response(items: list[T], total: int, params: PaginationParams) -> PageResponse[T]:
    return PageResponse(
        list=items,
        page=params.page,
        page_size=params.page_size,
        total=total,
        has_more=params.offset + len(items) < total,
    )
