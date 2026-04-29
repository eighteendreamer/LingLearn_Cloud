from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from app.core.logging import get_request_id

T = TypeVar("T")


class ResponseEnvelope(BaseModel, Generic[T]):
    code: int
    message: str
    data: T | None = None
    request_id: str | None = None


def success(data: Any | None = None, message: str = "ok") -> dict[str, Any]:
    return ResponseEnvelope[Any](
        code=0,
        message=message,
        data=data,
        request_id=get_request_id(),
    ).model_dump(mode="json")


def error(code: int, message: str, data: Any | None = None) -> dict[str, Any]:
    return ResponseEnvelope[Any](
        code=code,
        message=message,
        data=data,
        request_id=get_request_id(),
    ).model_dump(mode="json")
