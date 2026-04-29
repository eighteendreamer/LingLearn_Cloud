from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginationParams, get_pagination_params
from app.core.security import TokenPayload, get_current_user, get_current_user_optional
from app.db.session import get_db_session

DBSession = Annotated[AsyncSession, Depends(get_db_session)]
Pagination = Annotated[PaginationParams, Depends(get_pagination_params)]
CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]
OptionalCurrentUser = Annotated[TokenPayload | None, Depends(get_current_user_optional)]
