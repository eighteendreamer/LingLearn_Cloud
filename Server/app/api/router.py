from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.modules.admin.api import router as admin_router
from app.modules.ai_chat.api import router as ai_chat_router
from app.modules.assessment.api import router as assessment_router
from app.modules.auth.api import router as auth_router
from app.modules.content.api import contents_router, feed_router
from app.modules.course.api import router as course_router
from app.modules.discover.api import router as discover_router
from app.modules.learning.api import router as learning_router
from app.modules.learning_path.api import router as learning_path_router
from app.modules.notification.api import router as notification_router
from app.modules.practice.api import router as practice_router
from app.modules.quiz.api import router as quiz_router
from app.modules.report.api import router as report_router
from app.modules.resource.api import router as resource_router
from app.modules.search.api import router as search_router
from app.modules.storage.api import router as storage_router
from app.modules.user.api import router as user_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(admin_router, tags=["admin"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(discover_router, prefix="/discover", tags=["discover"])
api_router.include_router(feed_router, prefix="/feed", tags=["feed"])
api_router.include_router(contents_router, prefix="/contents", tags=["contents"])
api_router.include_router(storage_router, prefix="/storage", tags=["storage"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(course_router, prefix="/courses", tags=["courses"])
api_router.include_router(resource_router, prefix="/resources", tags=["resources"])
api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(learning_router, prefix="/users/me/learning", tags=["learning"])
api_router.include_router(practice_router, prefix="/practice", tags=["practice"])
api_router.include_router(quiz_router, prefix="/quizzes", tags=["quiz"])
api_router.include_router(assessment_router, tags=["assessment"])
api_router.include_router(learning_path_router, tags=["learning-path"])
api_router.include_router(report_router, tags=["report"])
api_router.include_router(notification_router, tags=["notification"])
api_router.include_router(ai_chat_router, tags=["ai-chat"])
