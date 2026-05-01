from fastapi import APIRouter, Request

from app.api.deps import CurrentUser, DBSession
from app.core.response import success
from app.modules.quiz.schemas import QuizSubmitRequest
from app.modules.quiz.service import QuizService

router = APIRouter()


@router.post("/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: int,
    payload: QuizSubmitRequest,
    request: Request,
    session: DBSession,
    current_user: CurrentUser,
):
    service = QuizService()
    client_ip = request.client.host if request.client else None
    data = await service.submit_quiz(
        session,
        quiz_id=quiz_id,
        user_id=int(current_user.sub),
        payload=payload,
        client_ip=client_ip,
    )
    return success(data=data.model_dump(mode="json"))
