from datetime import datetime

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User, UserRefreshToken
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
