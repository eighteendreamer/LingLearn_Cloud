from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.modules.ai_chat.api import router as ai_chat_router
from app.modules.auth.api import router as auth_router
from app.modules.content.api import contents_router, feed_router
from app.modules.storage.api import router as storage_router
from app.modules.user.api import router as user_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(ai_chat_router, prefix="/ai-chat", tags=["ai-chat"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(feed_router, prefix="/feed", tags=["feed"])
api_router.include_router(contents_router, prefix="/contents", tags=["contents"])
api_router.include_router(storage_router, prefix="/storage", tags=["storage"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
