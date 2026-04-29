import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.response import error

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(
        self,
        *,
        code: int,
        message: str,
        status_code: int,
        data: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.data = data


class BadRequestError(AppError):
    def __init__(self, message: str = "Bad request.", data: Any | None = None) -> None:
        super().__init__(code=40001, message=message, status_code=400, data=data)


class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication required.", data: Any | None = None) -> None:
        super().__init__(code=40101, message=message, status_code=401, data=data)


class AuthorizationError(AppError):
    def __init__(self, message: str = "Permission denied.", data: Any | None = None) -> None:
        super().__init__(code=40301, message=message, status_code=403, data=data)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found.", data: Any | None = None) -> None:
        super().__init__(code=40401, message=message, status_code=404, data=data)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource conflict.", data: Any | None = None) -> None:
        super().__init__(code=40901, message=message, status_code=409, data=data)


class RateLimitError(AppError):
    def __init__(self, message: str = "Too many requests.", data: Any | None = None) -> None:
        super().__init__(code=42901, message=message, status_code=429, data=data)


class InfrastructureError(AppError):
    def __init__(self, message: str = "Service unavailable.", data: Any | None = None) -> None:
        super().__init__(code=50001, message=message, status_code=503, data=data)


def _map_http_status_to_code(status_code: int) -> int:
    code_mapping = {
        400: 40001,
        401: 40101,
        403: 40301,
        404: 40401,
        409: 40901,
        429: 42901,
    }
    return code_mapping.get(status_code, 50001)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=error(code=exc.code, message=exc.message, data=exc.data),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=error(
                code=40001,
                message="Request validation failed.",
                data={"errors": exc.errors()},
            ),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error(
                code=_map_http_status_to_code(exc.status_code),
                message=str(exc.detail),
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception):
        logger.exception("Unhandled application error.")
        return JSONResponse(
            status_code=500,
            content=error(code=50001, message="Internal server error."),
        )
