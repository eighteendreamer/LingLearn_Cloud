from pydantic import BaseModel, EmailStr, Field


class AuthRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    display_name: str = Field(min_length=1, max_length=64)


class AuthLoginRequest(BaseModel):
    account: str = Field(min_length=3, max_length=128)
    password: str = Field(min_length=6, max_length=128)
    device_id: str | None = Field(default=None, max_length=64)


class AuthRefreshRequest(BaseModel):
    refresh_token: str


class AuthLogoutRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    account: str = Field(min_length=3, max_length=128)


class PasswordResetConfirmRequest(BaseModel):
    account: str = Field(min_length=3, max_length=128)
    code: str = Field(min_length=4, max_length=12)
    new_password: str = Field(min_length=6, max_length=128)


class PasswordResetRequestResponse(BaseModel):
    message: str
    expires_in_seconds: int
    masked_email: str | None = None
    sent: bool = False


class PasswordResetConfirmResponse(BaseModel):
    message: str


class AuthTokenResponse(BaseModel):
    user_id: int
    access_token: str
    refresh_token: str
    expires_in: int
