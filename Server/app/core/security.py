from datetime import timedelta
from typing import Any, Sequence

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.common.utils import utc_now
from app.core.config import get_settings
from app.core.enums import RoleCode, TokenType
from app.core.exceptions import AuthenticationError

auth_scheme = HTTPBearer(auto_error=False)


class TokenPayload(BaseModel):
    sub: str
    token_type: TokenType
    roles: list[RoleCode] = Field(default_factory=list)


def _load_jwt_module():
    try:
        import jwt
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyJWT is required for token operations.") from exc
    return jwt


def _encode_token(payload: dict[str, Any]) -> str:
    jwt = _load_jwt_module()
    settings = get_settings()
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def _decode_token(token: str) -> dict[str, Any]:
    jwt = _load_jwt_module()
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError(message="Token expired.") from exc
    except jwt.PyJWTError as exc:
        raise AuthenticationError(message="Invalid token.") from exc


def create_token(
    *,
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
    roles: Sequence[RoleCode] | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    now = utc_now()
    payload: dict[str, Any] = {
        "sub": subject,
        "token_type": token_type.value,
        "roles": [role.value for role in (roles or [RoleCode.USER])],
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    if extra:
        payload.update(extra)
    return _encode_token(payload)


def create_access_token(subject: str, roles: Sequence[RoleCode] | None = None) -> str:
    settings = get_settings()
    return create_token(
        subject=subject,
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        roles=roles,
    )


def create_refresh_token(subject: str, roles: Sequence[RoleCode] | None = None) -> str:
    settings = get_settings()
    return create_token(
        subject=subject,
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        roles=roles,
    )


def decode_token(token: str) -> TokenPayload:
    payload = _decode_token(token)
    return TokenPayload(
        sub=str(payload["sub"]),
        token_type=TokenType(payload["token_type"]),
        roles=[RoleCode(role) for role in payload.get("roles", [RoleCode.USER.value])],
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(auth_scheme),
) -> TokenPayload:
    if credentials is None:
        raise AuthenticationError()

    payload = decode_token(credentials.credentials)
    if payload.token_type != TokenType.ACCESS:
        raise AuthenticationError(message="Invalid access token.")

    return payload
