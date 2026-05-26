import hashlib
import hmac
import logging
import secrets
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import utc_now_naive
from app.core.config import get_settings
from app.core.enums import RoleCode
from app.core.exceptions import AuthenticationError, BadRequestError, ConflictError, RateLimitError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.infra.email.service import EmailService, email_service
from app.modules.auth.models import UserRefreshToken
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    AuthLoginRequest,
    AuthLogoutRequest,
    AuthRefreshRequest,
    AuthRegisterRequest,
    AuthTokenResponse,
    PasswordResetConfirmRequest,
    PasswordResetConfirmResponse,
    PasswordResetRequest,
    PasswordResetRequestResponse,
)

logger = logging.getLogger(__name__)

PASSWORD_RESET_GENERIC_MESSAGE = "如果账号已绑定邮箱，验证码将发送到对应邮箱。"


class AuthService:
    def __init__(
        self,
        repository: AuthRepository | None = None,
        mailer: EmailService | None = None,
    ) -> None:
        self.repository = repository or AuthRepository()
        self.mailer = mailer or email_service

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
        async with session.begin():
            user = await self.repository.get_user_by_account(session, req.account)
            if user is None or not verify_password(req.password, user.password_hash):
                raise AuthenticationError(message="Invalid account or password.")
            if user.status != "active":
                raise AuthenticationError(message="Current account is not active.")

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
        now = utc_now_naive()
        async with session.begin():
            record = await self.repository.get_refresh_token_by_hash(session, token_hash)
            self._validate_refresh_record(record)
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

    async def request_password_reset(
        self,
        session: AsyncSession,
        req: PasswordResetRequest,
        *,
        ip_address: str | None,
    ) -> PasswordResetRequestResponse:
        settings = get_settings()
        ttl_seconds = settings.password_reset_code_ttl_minutes * 60
        account = req.account.strip()
        now = utc_now_naive()

        async with session.begin():
            user = await self.repository.get_active_user_by_account(session, account)
            if user is None or not user.email:
                return PasswordResetRequestResponse(
                    message=PASSWORD_RESET_GENERIC_MESSAGE,
                    expires_in_seconds=ttl_seconds,
                )

            try:
                await self._validate_password_reset_limits(
                    session,
                    user_id=user.id,
                    request_ip=ip_address,
                    now=now,
                )
            except RateLimitError:
                logger.info("Password reset request was rate limited for user_id=%s.", user.id)
                return PasswordResetRequestResponse(
                    message="验证码发送过于频繁，请稍后再试。",
                    expires_in_seconds=ttl_seconds,
                    masked_email=self._mask_email(user.email),
                )

            code = self._generate_reset_code()
            await self.repository.create_password_reset_code(
                session,
                user_id=user.id,
                email=user.email,
                code_hash=self._hash_reset_code(user_id=user.id, email=user.email, code=code),
                request_ip=ip_address,
                expired_at=now + timedelta(minutes=settings.password_reset_code_ttl_minutes),
            )

            try:
                await self.mailer.send_password_reset_code(
                    to_email=user.email,
                    code=code,
                    ttl_minutes=settings.password_reset_code_ttl_minutes,
                )
            except Exception:
                logger.exception("Failed to send password reset code.")
                raise

        return PasswordResetRequestResponse(
            message=f"验证码已发送至绑定邮箱 {self._mask_email(user.email)}。",
            expires_in_seconds=ttl_seconds,
            masked_email=self._mask_email(user.email),
            sent=True,
        )

    async def confirm_password_reset(
        self,
        session: AsyncSession,
        req: PasswordResetConfirmRequest,
    ) -> PasswordResetConfirmResponse:
        account = req.account.strip()
        code = req.code.strip()
        now = utc_now_naive()

        async with session.begin():
            user = await self.repository.get_active_user_by_account(session, account)
            if user is None or not user.email:
                raise BadRequestError(message="验证码无效或已过期。")

            record = await self.repository.get_latest_active_password_reset_code(
                session,
                user_id=user.id,
                now=now,
            )
            if record is None:
                raise BadRequestError(message="验证码无效或已过期。")
            if record.failed_attempts >= 5:
                raise BadRequestError(message="验证码错误次数过多，请重新获取。")

            expected_hash = self._hash_reset_code(user_id=user.id, email=record.email, code=code)
            if not hmac.compare_digest(expected_hash, record.code_hash):
                await self.repository.increment_password_reset_failed_attempts(
                    session,
                    code_id=record.id,
                )
                raise BadRequestError(message="验证码无效或已过期。")

            await self.repository.update_user_password(
                session,
                user_id=user.id,
                password_hash=hash_password(req.new_password),
            )
            await self.repository.mark_password_reset_code_used(
                session,
                code_id=record.id,
                at=now,
            )
            await self.repository.revoke_refresh_tokens_for_user(
                session,
                user_id=user.id,
                at=now,
            )

        return PasswordResetConfirmResponse(message="密码已重置，请使用新密码登录。")

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

    async def _validate_password_reset_limits(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        request_ip: str | None,
        now,
    ) -> None:
        settings = get_settings()
        recent_record = await self.repository.get_latest_active_password_reset_code(
            session,
            user_id=user_id,
            now=now,
        )
        if recent_record is not None:
            elapsed_seconds = (now - recent_record.created_at).total_seconds()
            if elapsed_seconds < settings.password_reset_resend_interval_seconds:
                raise RateLimitError(message="验证码发送过于频繁，请稍后再试。")

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        account_count = await self.repository.count_password_reset_codes_for_user_since(
            session,
            user_id=user_id,
            since=today_start,
        )
        if account_count >= settings.password_reset_daily_account_limit:
            raise RateLimitError(message="今日验证码发送次数已达上限。")

        if request_ip:
            ip_count = await self.repository.count_password_reset_codes_for_ip_since(
                session,
                request_ip=request_ip,
                since=today_start,
            )
            if ip_count >= settings.password_reset_daily_ip_limit:
                raise RateLimitError(message="当前网络请求过于频繁，请稍后再试。")

    @staticmethod
    def _generate_reset_code() -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def _hash_reset_code(*, user_id: int, email: str, code: str) -> str:
        settings = get_settings()
        raw = f"{user_id}:{email.lower()}:{code}:{settings.jwt_secret_key}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _mask_email(email: str) -> str:
        local_part, _, domain = email.partition("@")
        if not domain:
            return email
        if len(local_part) <= 2:
            masked_local = f"{local_part[:1]}*"
        else:
            masked_local = f"{local_part[:2]}***{local_part[-1:]}"
        return f"{masked_local}@{domain}"
