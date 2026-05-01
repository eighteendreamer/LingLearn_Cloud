from fastapi import APIRouter

from app.api.deps import CurrentUser, DBSession, OptionalCurrentUser, Pagination
from app.core.response import success
from app.modules.user.schemas import UserProfileUpdateRequest, UserSettingsUpdateRequest
from app.modules.user.service import UserService

router = APIRouter()


@router.get("/me")
async def get_me(session: DBSession, current_user: CurrentUser):
    service = UserService()
    data = await service.get_me(session, int(current_user.sub))
    return success(data=data.model_dump(mode="json"))


@router.put("/me/profile")
async def update_profile(
    payload: UserProfileUpdateRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = UserService()
    data = await service.update_profile(session, int(current_user.sub), payload)
    return success(data=data.model_dump(mode="json"))


@router.put("/me/settings")
async def update_settings(
    payload: UserSettingsUpdateRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = UserService()
    data = await service.update_settings(session, int(current_user.sub), payload)
    return success(data=data.model_dump(mode="json"))


@router.get("/me/favorites")
async def list_my_favorites(session: DBSession, current_user: CurrentUser, pagination: Pagination):
    service = UserService()
    data = await service.list_my_favorites(session, int(current_user.sub), pagination)
    return success(data=data.model_dump(mode="json"))


@router.get("/me/watch-history")
async def list_my_watch_history(session: DBSession, current_user: CurrentUser, pagination: Pagination):
    service = UserService()
    data = await service.list_my_watch_history(session, int(current_user.sub), pagination)
    return success(data=data.model_dump(mode="json"))


@router.get("/{user_id}")
async def get_public_user(user_id: int, session: DBSession, current_user: OptionalCurrentUser):
    service = UserService()
    data = await service.get_public_user(
        session,
        user_id,
        viewer_user_id=int(current_user.sub) if current_user else None,
    )
    return success(data=data.model_dump(mode="json"))


@router.post("/{user_id}/follow")
async def follow_user(user_id: int, session: DBSession, current_user: CurrentUser):
    service = UserService()
    data = await service.follow_user(session, int(current_user.sub), user_id)
    return success(data=data.model_dump(mode="json"))


@router.delete("/{user_id}/follow")
async def unfollow_user(user_id: int, session: DBSession, current_user: CurrentUser):
    service = UserService()
    data = await service.unfollow_user(session, int(current_user.sub), user_id)
    return success(data=data.model_dump(mode="json"))


@router.get("/{user_id}/works")
async def get_user_works(user_id: int, session: DBSession, pagination: Pagination):
    service = UserService()
    data = await service.list_user_works(session, user_id, pagination)
    return success(data=data.model_dump(mode="json"))
