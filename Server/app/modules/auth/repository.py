from datetime import datetime

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import PasswordResetCode, User, UserRefreshToken
from app.modules.user.models import UserProfile, UserSettings


class AuthRepository:
    async def get_user_by_id(self, session: AsyncSession, user_id: int) -> User | None:
        return await session.get(User, user_id)

    async def get_user_by_account(self, session: AsyncSession, account: str) -> User | None:
        stmt = select(User).where(
            User.deleted_at.is_(None),
            or_(User.username == account, User.email == account),
        )
        return await session.scalar(stmt)

    async def get_active_user_by_account(self, session: AsyncSession, account: str) -> User | None:
        stmt = select(User).where(
            User.deleted_at.is_(None),
            User.status == "active",
            or_(User.username == account, User.email == account),
        )
        return await session.scalar(stmt)

    async def username_exists(self, session: AsyncSession, username: str) -> bool:
        stmt = select(func.count()).select_from(User).where(
            User.username == username,
            User.deleted_at.is_(None),
        )
        return bool(await session.scalar(stmt))

    async def email_exists(
        self,
        session: AsyncSession,
        email: str,
        *,
        exclude_user_id: int | None = None,
    ) -> bool:
        stmt = select(func.count()).select_from(User).where(
            User.email == email,
            User.deleted_at.is_(None),
        )
        if exclude_user_id is not None:
            stmt = stmt.where(User.id != exclude_user_id)
        return bool(await session.scalar(stmt))

    async def phone_exists(
        self,
        session: AsyncSession,
        phone: str,
        *,
        exclude_user_id: int | None = None,
    ) -> bool:
        stmt = select(func.count()).select_from(User).where(
            User.phone == phone,
            User.deleted_at.is_(None),
        )
        if exclude_user_id is not None:
            stmt = stmt.where(User.id != exclude_user_id)
        return bool(await session.scalar(stmt))

    async def create_user(
        self,
        session: AsyncSession,
        *,
        username: str,
        email: str,
        password_hash: str,
    ) -> User:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            status="active",
            register_source="password",
            email_verified=False,
            phone_verified=False,
        )
        session.add(user)
        await session.flush()
        return user

    async def create_default_profile(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        display_name: str,
    ) -> UserProfile:
        profile = UserProfile(user_id=user_id, display_name=display_name)
        session.add(profile)
        await session.flush()
        return profile

    async def create_default_settings(self, session: AsyncSession, *, user_id: int) -> UserSettings:
        settings = UserSettings(user_id=user_id)
        session.add(settings)
        await session.flush()
        return settings

    async def update_last_login(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        ip_address: str | None,
        at: datetime,
    ) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=at, last_login_ip=ip_address)
        )
        await session.execute(stmt)

    async def create_refresh_token(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        refresh_token_hash: str,
        expired_at: datetime,
        device_id: str | None,
        ip_address: str | None,
        user_agent: str | None,
        created_at: datetime,
    ) -> UserRefreshToken:
        record = UserRefreshToken(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            expired_at=expired_at,
            device_id=device_id,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=created_at,
            last_used_at=created_at,
        )
        session.add(record)
        await session.flush()
        return record

    async def get_refresh_token_by_hash(
        self,
        session: AsyncSession,
        refresh_token_hash: str,
    ) -> UserRefreshToken | None:
        stmt = select(UserRefreshToken).where(UserRefreshToken.refresh_token_hash == refresh_token_hash)
        return await session.scalar(stmt)

    async def mark_refresh_token_used(
        self,
        session: AsyncSession,
        *,
        token_id: int,
        at: datetime,
    ) -> None:
        stmt = update(UserRefreshToken).where(UserRefreshToken.id == token_id).values(last_used_at=at)
        await session.execute(stmt)

    async def revoke_refresh_token_by_hash(
        self,
        session: AsyncSession,
        *,
        refresh_token_hash: str,
        at: datetime,
    ) -> None:
        stmt = (
            update(UserRefreshToken)
            .where(
                UserRefreshToken.refresh_token_hash == refresh_token_hash,
                UserRefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=at)
        )
        await session.execute(stmt)

    async def revoke_refresh_tokens_for_user(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        at: datetime,
    ) -> None:
        stmt = (
            update(UserRefreshToken)
            .where(
                UserRefreshToken.user_id == user_id,
                UserRefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=at)
        )
        await session.execute(stmt)

    async def update_user_password(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        password_hash: str,
    ) -> None:
        stmt = update(User).where(User.id == user_id).values(password_hash=password_hash)
        await session.execute(stmt)

    async def create_password_reset_code(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        email: str,
        code_hash: str,
        request_ip: str | None,
        expired_at: datetime,
    ) -> PasswordResetCode:
        record = PasswordResetCode(
            user_id=user_id,
            email=email,
            code_hash=code_hash,
            request_ip=request_ip,
            expired_at=expired_at,
        )
        session.add(record)
        await session.flush()
        return record

    async def get_latest_active_password_reset_code(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        now: datetime,
    ) -> PasswordResetCode | None:
        stmt = (
            select(PasswordResetCode)
            .where(
                PasswordResetCode.user_id == user_id,
                PasswordResetCode.used_at.is_(None),
                PasswordResetCode.expired_at >= now,
            )
            .order_by(PasswordResetCode.created_at.desc(), PasswordResetCode.id.desc())
            .limit(1)
        )
        return await session.scalar(stmt)

    async def count_password_reset_codes_for_user_since(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        since: datetime,
    ) -> int:
        stmt = select(func.count()).select_from(PasswordResetCode).where(
            PasswordResetCode.user_id == user_id,
            PasswordResetCode.created_at >= since,
        )
        return int(await session.scalar(stmt) or 0)

    async def count_password_reset_codes_for_ip_since(
        self,
        session: AsyncSession,
        *,
        request_ip: str,
        since: datetime,
    ) -> int:
        stmt = select(func.count()).select_from(PasswordResetCode).where(
            PasswordResetCode.request_ip == request_ip,
            PasswordResetCode.created_at >= since,
        )
        return int(await session.scalar(stmt) or 0)

    async def mark_password_reset_code_used(
        self,
        session: AsyncSession,
        *,
        code_id: int,
        at: datetime,
    ) -> None:
        stmt = update(PasswordResetCode).where(PasswordResetCode.id == code_id).values(used_at=at)
        await session.execute(stmt)

    async def increment_password_reset_failed_attempts(
        self,
        session: AsyncSession,
        *,
        code_id: int,
    ) -> None:
        stmt = (
            update(PasswordResetCode)
            .where(PasswordResetCode.id == code_id)
            .values(failed_attempts=PasswordResetCode.failed_attempts + 1)
        )
        await session.execute(stmt)
