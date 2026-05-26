from fastapi import APIRouter, Request

from app.api.deps import DBSession
from app.core.response import success
from app.modules.auth.schemas import (
    AuthLoginRequest,
    AuthLogoutRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    AuthRefreshRequest,
    AuthRegisterRequest,
)
from app.modules.auth.service import AuthService

router = APIRouter()


def _request_meta(request: Request) -> tuple[str | None, str | None]:
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return client_ip, user_agent


@router.post("/register")
async def register(request: Request, payload: AuthRegisterRequest, session: DBSession):
    service = AuthService()
    ip_address, user_agent = _request_meta(request)
    data = await service.register(
        session,
        payload,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return success(data=data.model_dump())


@router.post("/login")
async def login(request: Request, payload: AuthLoginRequest, session: DBSession):
    service = AuthService()
    ip_address, user_agent = _request_meta(request)
    data = await service.login(
        session,
        payload,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return success(data=data.model_dump())


@router.post("/refresh")
async def refresh(payload: AuthRefreshRequest, session: DBSession):
    service = AuthService()
    data = await service.refresh(session, payload)
    return success(data=data.model_dump())


@router.post("/logout")
async def logout(payload: AuthLogoutRequest, session: DBSession):
    service = AuthService()
    await service.logout(session, payload)
    return success(message="logged out")


@router.post("/password-reset/request")
async def request_password_reset(
    request: Request,
    payload: PasswordResetRequest,
    session: DBSession,
):
    service = AuthService()
    ip_address, _ = _request_meta(request)
    data = await service.request_password_reset(
        session,
        payload,
        ip_address=ip_address,
    )
    return success(data=data.model_dump())


@router.post("/password-reset/confirm")
async def confirm_password_reset(payload: PasswordResetConfirmRequest, session: DBSession):
    service = AuthService()
    data = await service.confirm_password_reset(session, payload)
    return success(data=data.model_dump())
