from collections.abc import AsyncIterator

from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import utc_now_naive
from app.core.exceptions import AuthorizationError, NotFoundError
from app.infra.ai.agent_manager import AgentManager
from app.infra.ai.graphs.six_agents import AGENT_CATALOG_INSTRUCTION, AGENT_CATALOG_MARKDOWN
from app.infra.ai.llm_client import LLMClient
from app.modules.ai_chat.repository import AIChatRepository
from app.modules.ai_chat.schemas import (
    AIChatMessageResponse,
    AIChatMessageSendRequest,
    AIChatSessionCreateRequest,
    AIChatSessionResponse,
)


class AIChatService:
    def __init__(self, *, repository: AIChatRepository | None = None) -> None:
        self.repository = repository or AIChatRepository()
        self.agent_manager = AgentManager()
        self.llm_client = LLMClient()

    async def list_user_sessions(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[AIChatSessionResponse]:
        sessions = await self.repository.list_user_sessions(session, user_id)
        return [
            AIChatSessionResponse(
                id=item.id,
                session_name=item.session_name,
                scene_code=item.scene_code,
                model_name=item.model_name,
                status=item.status,
                summary=item.summary,
                last_message_at=item.last_message_at,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in sessions
        ]

    async def create_session(
        self,
        session: AsyncSession,
        user_id: int,
        payload: AIChatSessionCreateRequest,
    ) -> AIChatSessionResponse:
        try:
            chat_session = await self.repository.create_session(
                session,
                user_id=user_id,
                session_name=payload.session_name,
                scene_code=payload.scene_code,
                model_name=payload.model_name,
                created_at=utc_now_naive(),
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        return AIChatSessionResponse(
            id=chat_session.id,
            session_name=chat_session.session_name,
            scene_code=chat_session.scene_code,
            model_name=chat_session.model_name,
            status=chat_session.status,
            summary=chat_session.summary,
            last_message_at=chat_session.last_message_at,
            created_at=chat_session.created_at,
            updated_at=chat_session.updated_at,
        )

    async def list_session_messages(
        self,
        session: AsyncSession,
        user_id: int,
        session_id: int,
    ) -> list[AIChatMessageResponse]:
        chat_session = await self.repository.get_session_by_id(session, session_id)
        if not chat_session:
            raise NotFoundError(message="Chat session not found.")
        if chat_session.user_id != user_id:
            raise AuthorizationError(message="Not your chat session.")

        messages = await self.repository.list_session_messages(session, session_id)
        return [
            AIChatMessageResponse(
                id=item.id,
                session_id=item.session_id,
                role=item.role,
                message_type=item.message_type,
                content=item.content,
                token_count=item.token_count,
                latency_ms=item.latency_ms,
                error_code=item.error_code,
                trace_id=item.trace_id,
                created_at=item.created_at,
            )
            for item in messages
        ]

    async def send_message(
        self,
        session: AsyncSession,
        user_id: int,
        session_id: int,
        payload: AIChatMessageSendRequest,
    ) -> AIChatMessageResponse:
        chat_session = await self.repository.get_session_by_id(session, session_id)
        if not chat_session:
            raise NotFoundError(message="Chat session not found.")
        if chat_session.user_id != user_id:
            raise AuthorizationError(message="Not your chat session.")

        now = utc_now_naive()

        try:
            await self.repository.create_message(
                session,
                session_id=session_id,
                role="user",
                message_type="text",
                content=payload.content,
                token_count=len(payload.content.split()),
                created_at=now,
            )

            messages = await self.repository.list_session_messages(session, session_id)
            message_history = [
                HumanMessage(content=item.content)
                if item.role == "user"
                else AIMessage(content=item.content)
                for item in messages[-10:]
            ]
            user_context = {
                "recent_courses": ["Python基础", "数据结构"],
                "weak_areas": ["算法复杂度", "递归"],
                "learning_goal": "掌握Python编程",
            }

            try:
                result = await self.agent_manager.run_tutor_chat(
                    db_session=session,
                    user_id=user_id,
                    session_id=session_id,
                    scene_code=chat_session.scene_code or "learning_guidance",
                    messages=message_history,
                    context=user_context,
                )
                ai_response_content = (
                    result["messages"][-1].content
                    if result.get("messages")
                    else "抱歉，我暂时没有生成有效回复，请稍后再试。"
                )
            except Exception:
                ai_response_content = "抱歉，当前无法获取回答，请稍后再试。"

            ai_message = await self.repository.create_message(
                session,
                session_id=session_id,
                role="assistant",
                message_type="text",
                content=ai_response_content,
                token_count=len(ai_response_content.split()),
                latency_ms=100,
                created_at=now,
            )
            await self.repository.update_session_timestamp(session, session_id, now)
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        return AIChatMessageResponse(
            id=ai_message.id,
            session_id=ai_message.session_id,
            role=ai_message.role,
            message_type=ai_message.message_type,
            content=ai_message.content,
            token_count=ai_message.token_count,
            latency_ms=ai_message.latency_ms,
            error_code=ai_message.error_code,
            trace_id=ai_message.trace_id,
            created_at=ai_message.created_at,
        )

    async def stream_message_events(
        self,
        session: AsyncSession,
        user_id: int,
        session_id: int,
        payload: AIChatMessageSendRequest,
    ) -> AsyncIterator[dict]:
        chat_session = await self.repository.get_session_by_id(session, session_id)
        if not chat_session:
            raise NotFoundError(message="Chat session not found.")
        if chat_session.user_id != user_id:
            raise AuthorizationError(message="Not your chat session.")

        now = utc_now_naive()
        await self.repository.create_message(
            session,
            session_id=session_id,
            role="user",
            message_type="text",
            content=payload.content,
            token_count=len(payload.content.split()),
            created_at=now,
        )

        messages = await self.repository.list_session_messages(session, session_id)
        upstream_messages = self._build_upstream_messages(
            chat_session.scene_code or "learning_guidance",
            [
                {"role": item.role, "content": item.content}
                for item in messages[-10:]
            ],
        )
        yield {"type": "start"}

        chunks: list[str] = []
        try:
            async for chunk in self.llm_client.stream_chat(upstream_messages):
                chunks.append(chunk)
                yield {"type": "delta", "content": chunk}
        except Exception:
            fallback = "抱歉，当前无法获取回答，请稍后再试。"
            chunks = [fallback]
            yield {"type": "delta", "content": fallback}

        content = "".join(chunks).strip() or "抱歉，我暂时没有生成有效回复，请稍后再试。"
        ai_message = await self.repository.create_message(
            session,
            session_id=session_id,
            role="assistant",
            message_type="text",
            content=content,
            token_count=len(content.split()),
            latency_ms=100,
            created_at=utc_now_naive(),
        )
        await self.repository.update_session_timestamp(session, session_id, utc_now_naive())
        await session.commit()
        yield {
            "type": "done",
            "message": {
                "id": ai_message.id,
                "session_id": ai_message.session_id,
                "role": ai_message.role,
                "message_type": ai_message.message_type,
                "content": ai_message.content,
                "token_count": ai_message.token_count,
                "latency_ms": ai_message.latency_ms,
                "error_code": ai_message.error_code,
                "trace_id": ai_message.trace_id,
                "created_at": ai_message.created_at.isoformat(),
            },
        }

    def _build_upstream_messages(self, scene_code: str, history: list[dict[str, str]]) -> list[dict[str, str]]:
        system_prompt = (
            "你是 LingLearn 的 AI 学习助手，专注于帮助学生提升学习效果。"
            "请用清晰、友好、专业的中文回答。"
            "如果适合，请使用 Markdown 的标题、列表、代码块或表格来组织内容。"
            f"\n\n{AGENT_CATALOG_MARKDOWN}\n{AGENT_CATALOG_INSTRUCTION}"
        )
        if scene_code == "practice_help":
            system_prompt += "当前场景是练习辅导，请引导思考，不要直接替学生完成所有答案。"
        elif scene_code == "progress_analysis":
            system_prompt += "当前场景是进度分析，请给出客观分析和可执行建议。"

        normalized_history = []
        for item in history:
            role = item.get("role") or "user"
            if role not in {"system", "user", "assistant"}:
                role = "user"
            normalized_history.append({"role": role, "content": item.get("content", "")})
        return [{"role": "system", "content": system_prompt}, *normalized_history]
