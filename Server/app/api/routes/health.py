from fastapi import APIRouter

from app.api.deps import DBSession
from app.common.utils import utc_now_iso
from app.core.config import get_settings
from app.core.exceptions import InfrastructureError
from app.core.response import success
from app.db.session import check_database_connection

router = APIRouter()
settings = get_settings()


@router.get("", summary="Liveness check")
async def liveness():
    return success(
        data={
            "status": "up",
            "service": settings.app_name,
            "environment": settings.app_env.value,
            "timestamp": utc_now_iso(),
        }
    )


@router.get("/ready", summary="Readiness check")
async def readiness(session: DBSession):
    database_ok = await check_database_connection(session)
    if not database_ok:
        raise InfrastructureError(
            message="Database connection is unavailable.",
            data={"status": "degraded", "database": "down"},
        )

    return success(
        data={
            "status": "ready",
            "service": settings.app_name,
            "database": "up",
            "timestamp": utc_now_iso(),
        }
    )
