import logging
import time
import uuid
from contextvars import ContextVar, Token

from starlette.middleware.base import BaseHTTPMiddleware

from app.common.constants import REQUEST_ID_HEADER

request_id_context: ContextVar[str] = ContextVar("request_id", default="-")


def set_request_id(request_id: str) -> Token:
    return request_id_context.set(request_id)


def reset_request_id(token: Token) -> None:
    request_id_context.reset(token)


def get_request_id() -> str:
    return request_id_context.get()


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


def configure_logging(log_level: str = "INFO") -> None:
    root_logger = logging.getLogger()

    if getattr(configure_logging, "_configured", False):
        root_logger.setLevel(log_level.upper())
        return

    handler = logging.StreamHandler()
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(request_id)s | %(name)s | %(message)s"
        )
    )

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())
    configure_logging._configured = True


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        request.state.request_id = request_id
        token = set_request_id(request_id)
        logger = logging.getLogger("app.request")
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.exception(
                "Unhandled request error: %s %s (%.2f ms)",
                request.method,
                request.url.path,
                latency_ms,
            )
            raise
        else:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            response.headers[REQUEST_ID_HEADER] = request_id
            logger.info(
                "%s %s -> %s (%.2f ms)",
                request.method,
                request.url.path,
                response.status_code,
                latency_ms,
            )
            return response
        finally:
            reset_request_id(token)
