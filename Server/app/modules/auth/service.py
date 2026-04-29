from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import utc_now_naive
from app.core.config import get_settings
from app.core.enums import RoleCode
from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.modules.auth.models import UserRefreshToken
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    AuthLoginRequest,
    AuthLogoutRequest,
    AuthRefreshRequest,
    AuthRegisterRequest,
    AuthTokenResponse,
)


class AuthService:
    def __init__(self, repository: AuthRepository | None = None) -> None:
        self.repository = repository or AuthRepository()

    async def register(
        self,
        session: AsyncSession,
        req: AuthRegisterRequest,
        *,
        ip_address: str | None,
        user_agent: str | None,
    ) -> AuthTokenResponse:
        async with session.begin():
            if await self.repository.username_exists(session, req.username):
                raise ConflictError(message="Username already exists.")
            if await self.repository.email_exists(session, req.email):
                raise ConflictError(message="Email already exists.")

            user = await self.repository.create_user(
                session,
                username=req.username,
                email=req.email,
                password_hash=hash_password(req.password),
            )
            await self.repository.create_default_profile(
                session,
                user_id=user.id,
                display_name=req.display_name,
            )
            await self.repository.create_default_settings(session, user_id=user.id)

            return await self._issue_tokens(
                session,
                user_id=user.id,
                device_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
            )

    async def login(
        self,
        session: AsyncSession,
        req: AuthLoginRequest,
        *,
        ip_address: str | None,
        user_agent: str | None,
    ) -> AuthTokenResponse:
        user = await self.repository.get_user_by_account(session, req.account)
        if user is None or not verify_password(req.password, user.password_hash):
            raise AuthenticationError(message="Invalid account or password.")
        if user.status != "active":
            raise AuthenticationError(message="Current account is not active.")

        async with session.begin():
            await self.repository.update_last_login(
                session,
                user_id=user.id,
                ip_address=ip_address,
                at=utc_now_naive(),
            )
            return await self._issue_tokens(
                session,
                user_id=user.id,
                device_id=req.device_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )

    async def refresh(
        self,
        session: AsyncSession,
        req: AuthRefreshRequest,
    ) -> AuthTokenResponse:
        payload = decode_token(req.refresh_token)
        if payload.token_type.value != "refresh":
            raise AuthenticationError(message="Invalid refresh token.")

        token_hash = hash_refresh_token(req.refresh_token)
        record = await self.repository.get_refresh_token_by_hash(session, token_hash)
        self._validate_refresh_record(record)

        now = utc_now_naive()
        async with session.begin():
            await self.repository.mark_refresh_token_used(session, token_id=record.id, at=now)

        access_token = create_access_token(subject=payload.sub, roles=payload.roles)
        settings = get_settings()
        return AuthTokenResponse(
            user_id=int(payload.sub),
            access_token=access_token,
            refresh_token=req.refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def logout(
        self,
        session: AsyncSession,
        req: AuthLogoutRequest,
    ) -> None:
        token_hash = hash_refresh_token(req.refresh_token)
        async with session.begin():
            await self.repository.revoke_refresh_token_by_hash(
                session,
                refresh_token_hash=token_hash,
                at=utc_now_naive(),
            )

    async def _issue_tokens(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        device_id: str | None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> AuthTokenResponse:
        roles = [RoleCode.USER]
        access_token = create_access_token(subject=str(user_id), roles=roles)
        refresh_token = create_refresh_token(subject=str(user_id), roles=roles)
        settings = get_settings()
        now = utc_now_naive()
        await self.repository.create_refresh_token(
            session,
            user_id=user_id,
            refresh_token_hash=hash_refresh_token(refresh_token),
            expired_at=now + timedelta(days=settings.refresh_token_expire_days),
            device_id=device_id,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=now,
        )
        return AuthTokenResponse(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    @staticmethod
    def _validate_refresh_record(record: UserRefreshToken | None) -> None:
        if record is None:
            raise AuthenticationError(message="Refresh token not found.")
        if record.revoked_at is not None:
            raise AuthenticationError(message="Refresh token has been revoked.")
        if record.expired_at < utc_now_naive():
            raise AuthenticationError(message="Refresh token expired.")
