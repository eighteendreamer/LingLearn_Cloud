from fastapi import APIRouter

from app.api.deps import CurrentUser, DBSession
from app.core.response import success
from app.modules.learning_path.schemas import (
    LearningPathActivateRequest,
    LearningPathGenerateRequest,
    LearningPathNodeUpdateRequest,
    SkillProfileGenerateRequest,
)
from app.modules.learning_path.service import LearningPathService

router = APIRouter()


@router.get("/users/me/skill-profile/latest")
async def get_latest_skill_profile(
    current_user: CurrentUser,
    session: DBSession,
):
    service = LearningPathService()
    result = await service.get_latest_skill_profile(session, int(current_user.sub))
    return success(data=result)


@router.post("/users/me/skill-profile/generate")
async def generate_skill_profile(
    payload: SkillProfileGenerateRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    service = LearningPathService()
    result = await service.generate_skill_profile(session, int(current_user.sub), payload)
    return success(data=result, message="Skill profile generated successfully.")


@router.get("/users/me/skill-profile/history")
async def list_skill_profile_history(
    current_user: CurrentUser,
    session: DBSession,
):
    service = LearningPathService()
    result = await service.list_skill_profile_history(session, int(current_user.sub))
    return success(data=result)


@router.get("/users/me/learning-paths/active")
async def get_active_learning_path(
    current_user: CurrentUser,
    session: DBSession,
):
    service = LearningPathService()
    result = await service.get_active_learning_path(session, int(current_user.sub))
    return success(data=result)


@router.get("/users/me/learning-paths/history")
async def list_learning_path_history(
    current_user: CurrentUser,
    session: DBSession,
):
    service = LearningPathService()
    result = await service.list_learning_path_history(session, int(current_user.sub))
    return success(data=result)


@router.post("/users/me/learning-paths/generate")
async def generate_learning_path(
    payload: LearningPathGenerateRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    service = LearningPathService()
    result = await service.generate_learning_path(session, int(current_user.sub), payload)
    return success(data=result, message="Learning path generated successfully.")


@router.post("/users/me/learning-paths/plan")
async def generate_learning_path_plan(
    payload: LearningPathGenerateRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    service = LearningPathService()
    result = await service.generate_learning_path_plan(session, int(current_user.sub), payload)
    return success(data=result, message="Learning path options generated successfully.")


@router.post("/users/me/learning-paths/activate")
async def activate_learning_path(
    payload: LearningPathActivateRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    service = LearningPathService()
    result = await service.activate_learning_path(session, int(current_user.sub), payload)
    return success(data=result, message="Learning path activated successfully.")


@router.get("/users/me/learning-paths/{user_path_id}")
async def get_learning_path(
    user_path_id: int,
    current_user: CurrentUser,
    session: DBSession,
):
    service = LearningPathService()
    result = await service.get_learning_path(session, int(current_user.sub), user_path_id)
    return success(data=result)


@router.patch("/users/me/learning-paths/{user_path_id}/nodes/{node_id}")
async def update_learning_path_node(
    user_path_id: int,
    node_id: int,
    payload: LearningPathNodeUpdateRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    service = LearningPathService()
    result = await service.update_learning_path_node(
        session,
        int(current_user.sub),
        user_path_id,
        node_id,
        payload,
    )
    return success(data=result)


@router.post("/users/me/learning-paths/{user_path_id}/nodes/{node_id}/generate-practice")
async def generate_learning_path_node_practice(
    user_path_id: int,
    node_id: int,
    current_user: CurrentUser,
    session: DBSession,
):
    service = LearningPathService()
    result = await service.generate_node_practice(
        session,
        int(current_user.sub),
        user_path_id,
        node_id,
    )
    return success(data=result, message="Stage practice generated successfully.")
