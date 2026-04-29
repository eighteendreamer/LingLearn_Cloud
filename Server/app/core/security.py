import base64
import hashlib
import hmac
import json
import secrets
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


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _encode_token(payload: dict[str, Any]) -> str:
    settings = get_settings()
    if settings.jwt_algorithm != "HS256":
        raise RuntimeError("Only HS256 is supported by the built-in token encoder.")

    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    header_segment = _b64url_encode(
        json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    payload_segment = _b64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    signature_segment = _b64url_encode(signature)
    return f"{header_segment}.{payload_segment}.{signature_segment}"


def _decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    if settings.jwt_algorithm != "HS256":
        raise RuntimeError("Only HS256 is supported by the built-in token decoder.")

    try:
        header_segment, payload_segment, signature_segment = token.split(".")
    except ValueError as exc:
        raise AuthenticationError(message="Invalid token.") from exc

    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    expected_signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    actual_signature = _b64url_decode(signature_segment)
    if not hmac.compare_digest(expected_signature, actual_signature):
        raise AuthenticationError(message="Invalid token.")

    try:
        payload = json.loads(_b64url_decode(payload_segment))
    except (json.JSONDecodeError, ValueError) as exc:
        raise AuthenticationError(message="Invalid token.") from exc

    exp = payload.get("exp")
    if exp is None or int(exp) < int(utc_now().timestamp()):
        raise AuthenticationError(message="Token expired.")

    return payload


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


def hash_password(password: str) -> str:
    iterations = 390000
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_str, salt, digest = password_hash.split("$", maxsplit=3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    computed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations_str),
    ).hex()
    return hmac.compare_digest(computed, digest)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(auth_scheme),
) -> TokenPayload:
    if credentials is None:
        raise AuthenticationError()

    payload = decode_token(credentials.credentials)
    if payload.token_type != TokenType.ACCESS:
        raise AuthenticationError(message="Invalid access token.")

    return payload
