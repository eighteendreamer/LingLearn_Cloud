from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.enums import AppEnv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(...)
    app_env: AppEnv = Field(...)
    debug: bool = Field(...)

    api_v1_prefix: str = Field(...)
    host: str = Field(...)
    port: int = Field(...)

    log_level: str = Field(...)
    cors_origins: str = Field(...)

    database_url: str = Field(...)
    db_echo: bool = Field(...)
    db_pool_recycle: int = Field(...)
    redis_enabled: bool = Field(default=False)
    redis_url: str = Field(default="")
    redis_prefix: str = Field(default="linglearn")
    redis_default_ttl_seconds: int = Field(default=300)

    minio_endpoint: str = Field(...)
    minio_access_key: str = Field(...)
    minio_secret_key: str = Field(...)
    minio_bucket_name: str = Field(...)
    minio_secure: bool = Field(...)
    minio_public_base_url: str = Field(...)
    minio_presign_expire_seconds: int = Field(...)
    minio_auto_create_bucket: bool = Field(...)

    jwt_secret_key: str = Field(...)
    jwt_algorithm: str = Field(...)
    access_token_expire_minutes: int = Field(...)
    refresh_token_expire_days: int = Field(...)

    llm_api_key: str = Field(...)
    llm_model: str = Field(...)
    llm_base_url: str = Field(...)
    llm_timeout_seconds: int = Field(...)

    video_audio_api_key: str = Field(default="")
    video_audio_model: str = Field(default="qwen3-omni-30b-a3b-captioner")
    video_audio_base_url: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1")
    video_audio_timeout_seconds: int = Field(default=120)

    video_vision_api_key: str = Field(default="")
    video_vision_model: str = Field(default="Qwen/Qwen3.5-122B-A10B")
    video_vision_base_url: str = Field(default="https://api-inference.modelscope.cn/v1")
    video_vision_timeout_seconds: int = Field(default=120)

    video_extract_max_frames: int = Field(default=6)
    video_extract_interval_seconds: int = Field(default=20)
    video_extract_audio_format: str = Field(default="mp3")

    docs_url: str = Field(...)
    redoc_url: str = Field(...)
    openapi_url: str = Field(...)

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
