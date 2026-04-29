from app.core.config import get_settings
from app.core.exceptions import BadRequestError, InfrastructureError
from app.infra.ai.llm_client import LLMClient
from app.modules.ai_chat.schemas import AIChatCompletionRequest, AIChatCompletionResponse

SYSTEM_PROMPT = (
    "你是一个专业的编程学习 AI 助手，名字叫“智能学习助手”。"
    "你的职责是解答编程相关问题，讲解技术概念，提供学习路径建议。"
    "请始终用中文回答，表达简洁、准确、实用。"
)


class AIChatService:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    async def complete(self, payload: AIChatCompletionRequest) -> AIChatCompletionResponse:
        normalized_messages = []
        for message in payload.messages:
            role = message.role.strip().lower()
            if role not in {"user", "assistant"}:
                raise BadRequestError(message=f"Unsupported chat role: {message.role}.")
            normalized_messages.append({"role": role, "content": message.content.strip()})

        upstream = await self.llm_client.chat(
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *normalized_messages],
        )
        reply = upstream.get("choices", [{}])[0].get("message", {}).get("content")
        if not reply:
            raise InfrastructureError(message="LLM upstream returned an empty reply.")

        settings = get_settings()
        return AIChatCompletionResponse(reply=reply, model=settings.llm_model)
