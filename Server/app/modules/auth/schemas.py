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


class AuthTokenResponse(BaseModel):
    user_id: int
    access_token: str
    refresh_token: str
    expires_in: int
