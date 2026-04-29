from fastapi import APIRouter

from app.core.response import success
from app.modules.ai_chat.schemas import AIChatCompletionRequest
from app.modules.ai_chat.service import AIChatService

router = APIRouter()


@router.post("/completions")
async def complete(payload: AIChatCompletionRequest):
    service = AIChatService()
    data = await service.complete(payload)
    return success(data=data.model_dump())
