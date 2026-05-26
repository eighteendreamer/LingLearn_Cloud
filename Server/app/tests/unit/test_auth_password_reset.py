import asyncio
from dataclasses import dataclass
from datetime import timedelta

import pytest

from app.common.utils import utc_now_naive
from app.core.exceptions import BadRequestError
from app.modules.auth.service import AuthService
from app.modules.auth.schemas import PasswordResetConfirmRequest, PasswordResetRequest


class _AsyncTransaction:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _SessionStub:
    def begin(self):
        return _AsyncTransaction()


@dataclass
class _UserStub:
    id: int
    email: str


@dataclass
class _ResetRecordStub:
    id: int
    user_id: int
    email: str
    code_hash: str
    expired_at: object
    created_at: object
    used_at: object | None = None
    failed_attempts: int = 0


class _MailerStub:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def send_password_reset_code(self, **kwargs):
        self.sent.append(kwargs)


class _RepositoryStub:
    def __init__(self, user=None, record=None) -> None:
        self.user = user
        self.record = record
        self.created_code = None
        self.updated_password_hash = None
        self.used_code_id = None
        self.revoked_user_id = None
        self.failed_attempts_incremented = 0

    async def get_active_user_by_account(self, session, account):
        return self.user

    async def get_latest_active_password_reset_code(self, session, *, user_id, now):
        return self.record

    async def count_password_reset_codes_for_user_since(self, session, *, user_id, since):
        return 0

    async def count_password_reset_codes_for_ip_since(self, session, *, request_ip, since):
        return 0

    async def create_password_reset_code(self, session, **kwargs):
        self.created_code = kwargs
        return _ResetRecordStub(
            id=1,
            user_id=kwargs["user_id"],
            email=kwargs["email"],
            code_hash=kwargs["code_hash"],
            expired_at=kwargs["expired_at"],
            created_at=utc_now_naive(),
        )

    async def update_user_password(self, session, *, user_id, password_hash):
        self.updated_password_hash = password_hash

    async def mark_password_reset_code_used(self, session, *, code_id, at):
        self.used_code_id = code_id

    async def revoke_refresh_tokens_for_user(self, session, *, user_id, at):
        self.revoked_user_id = user_id

    async def increment_password_reset_failed_attempts(self, session, *, code_id):
        self.failed_attempts_incremented += 1


def test_password_reset_request_creates_code_and_sends_email() -> None:
    async def run_case() -> None:
        user = _UserStub(id=7, email="learner@example.com")
        repository = _RepositoryStub(user=user)
        mailer = _MailerStub()
        service = AuthService(repository=repository, mailer=mailer)

        response = await service.request_password_reset(
            _SessionStub(),
            PasswordResetRequest(account="learner"),
            ip_address="127.0.0.1",
        )

        assert response.expires_in_seconds > 0
        assert response.sent is True
        assert response.masked_email == "le***r@example.com"
        assert repository.created_code is not None
        assert repository.created_code["user_id"] == user.id
        assert len(mailer.sent) == 1
        assert mailer.sent[0]["to_email"] == user.email
        assert mailer.sent[0]["code"].isdigit()
        assert len(mailer.sent[0]["code"]) == 6

    asyncio.run(run_case())


def test_password_reset_request_does_not_advance_for_unknown_account() -> None:
    async def run_case() -> None:
        repository = _RepositoryStub(user=None)
        mailer = _MailerStub()
        service = AuthService(repository=repository, mailer=mailer)

        response = await service.request_password_reset(
            _SessionStub(),
            PasswordResetRequest(account="missing-user"),
            ip_address="127.0.0.1",
        )

        assert response.sent is False
        assert response.masked_email is None
        assert repository.created_code is None
        assert mailer.sent == []

    asyncio.run(run_case())


def test_password_reset_confirm_updates_password_and_revokes_tokens() -> None:
    async def run_case() -> None:
        user = _UserStub(id=8, email="learner@example.com")
        code = "123456"
        record = _ResetRecordStub(
            id=3,
            user_id=user.id,
            email=user.email,
            code_hash=AuthService._hash_reset_code(user_id=user.id, email=user.email, code=code),
            expired_at=utc_now_naive() + timedelta(minutes=10),
            created_at=utc_now_naive(),
        )
        repository = _RepositoryStub(user=user, record=record)
        service = AuthService(repository=repository, mailer=_MailerStub())

        response = await service.confirm_password_reset(
            _SessionStub(),
            PasswordResetConfirmRequest(
                account="learner",
                code=code,
                new_password="new-password",
            ),
        )

        assert "密码已重置" in response.message
        assert repository.updated_password_hash is not None
        assert repository.used_code_id == record.id
        assert repository.revoked_user_id == user.id

    asyncio.run(run_case())


def test_password_reset_confirm_increments_failed_attempts_for_wrong_code() -> None:
    async def run_case() -> None:
        user = _UserStub(id=9, email="learner@example.com")
        record = _ResetRecordStub(
            id=4,
            user_id=user.id,
            email=user.email,
            code_hash=AuthService._hash_reset_code(user_id=user.id, email=user.email, code="123456"),
            expired_at=utc_now_naive() + timedelta(minutes=10),
            created_at=utc_now_naive(),
        )
        repository = _RepositoryStub(user=user, record=record)
        service = AuthService(repository=repository, mailer=_MailerStub())

        with pytest.raises(BadRequestError):
            await service.confirm_password_reset(
                _SessionStub(),
                PasswordResetConfirmRequest(
                    account="learner",
                    code="000000",
                    new_password="new-password",
                ),
            )

        assert repository.failed_attempts_incremented == 1
        assert repository.updated_password_hash is None

    asyncio.run(run_case())
