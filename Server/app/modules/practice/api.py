from fastapi import APIRouter

from app.api.deps import CurrentUser, DBSession, Pagination
from app.core.response import success
from app.modules.practice.schemas import (
    PracticeAnswerSubmitRequest,
    PracticeSessionCreateRequest,
)
from app.modules.practice.service import PracticeService

router = APIRouter()


@router.get("/banks")
async def list_question_banks(
    session: DBSession,
    pagination: Pagination,
):
    service = PracticeService()
    data = await service.list_question_banks(session, pagination)
    return success(data=data.model_dump(mode="json"))


@router.get("/banks/{bank_id}/questions")
async def list_bank_questions(
    bank_id: int,
    session: DBSession,
):
    service = PracticeService()
    data = await service.list_bank_questions(session, bank_id)
    return success(data=[item.model_dump(mode="json") for item in data])


@router.post("/sessions")
async def create_practice_session(
    payload: PracticeSessionCreateRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = PracticeService()
    data = await service.create_practice_session(
        session,
        user_id=int(current_user.sub),
        payload=payload,
    )
    return success(data=data.model_dump(mode="json"))


@router.post("/sessions/{session_id}/answers")
async def submit_answer(
    session_id: int,
    payload: PracticeAnswerSubmitRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    service = PracticeService()
    data = await service.submit_answer(
        session,
        user_id=int(current_user.sub),
        session_id=session_id,
        payload=payload,
    )
    return success(data=data.model_dump(mode="json"))


@router.post("/sessions/{session_id}/submit")
async def submit_session(
    session_id: int,
    session: DBSession,
    current_user: CurrentUser,
):
    service = PracticeService()
    data = await service.submit_session(
        session,
        user_id=int(current_user.sub),
        session_id=session_id,
    )
    return success(data=data.model_dump(mode="json"))


@router.get("/sessions/{session_id}/result")
async def get_session_result(
    session_id: int,
    session: DBSession,
    current_user: CurrentUser,
):
    service = PracticeService()
    data = await service.get_session_result(
        session,
        user_id=int(current_user.sub),
        session_id=session_id,
    )
    return success(data=data.model_dump(mode="json"))
