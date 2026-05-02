from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.deps import DBSession
from app.core.config import get_settings
from app.core.exceptions import AuthenticationError
from app.core.security import decode_token
from app.modules.admin.models import AdminUser
from app.modules.admin.service import AdminAuthService

settings = get_settings()
security = HTTPBearer()


async def get_current_admin_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: DBSession,
) -> AdminUser:
    """获取当前管理员用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = decode_token(token)
        admin_id = payload.sub
        
        # 检查是否是管理员token（通过extra字段或其他方式）
        # 这里简单检查sub是否为数字ID
        if not admin_id:
            raise credentials_exception

    except (AuthenticationError, Exception):
        raise credentials_exception

    admin = await AdminAuthService.get_admin_by_id(db, int(admin_id))

    if admin is None or admin.status != "active":
        raise credentials_exception

    return admin
