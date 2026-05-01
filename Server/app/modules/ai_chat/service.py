from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator

from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import utc_now_naive
from app.core.exceptions import AuthorizationError, NotFoundError
from app.infra.ai.agent_manager import AgentManager
from app.infra.ai.agent_skills import AGENT_CATALOG_MARKDOWN
from app.modules.ai_chat.repository import AIChatRepository
from app.modules.ai_chat.schemas import (
    AIChatMessageResponse,
    AIChatMessageSendRequest,
    AIChatSessionCreateRequest,
    AIChatSessionResponse,
)

logger = logging.getLogger(__name__)


class AIChatService:
    def __init__(self, *, repository: AIChatRepository | None = None) -> None:
        self.repository = repository or AIChatRepository()
        self.agent_manager = AgentManager()

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
        return [self._to_message_response(item) for item in messages]

    async def send_message(
        self,
        session: AsyncSession,
        user_id: int,
        session_id: int,
        payload: AIChatMessageSendRequest,
    ) -> AIChatMessageResponse:
        chat_session = await self._ensure_session_owner(session, user_id, session_id)
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

            try:
                ai_response_content = await self._generate_agent_response(
                    session,
                    user_id=user_id,
                    session_id=session_id,
                    scene_code=chat_session.scene_code or "study_assistant",
                    page_context=payload.page_context,
                )
            except Exception:
                logger.exception("AI chat response generation failed: session_id=%s user_id=%s", session_id, user_id)
                ai_response_content = self._build_local_fallback_response(payload.content)

            ai_message = await self.repository.create_message(
                session,
                session_id=session_id,
                role="assistant",
                message_type="text",
                content=ai_response_content,
                token_count=len(ai_response_content.split()),
                latency_ms=100,
                created_at=utc_now_naive(),
            )
            await self.repository.update_session_timestamp(session, session_id, utc_now_naive())
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        return self._to_message_response(ai_message)

    async def stream_message_events(
        self,
        session: AsyncSession,
        user_id: int,
        session_id: int,
        payload: AIChatMessageSendRequest,
    ) -> AsyncIterator[dict]:
        chat_session = await self._ensure_session_owner(session, user_id, session_id)
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

        yield {"type": "start"}
        yield {"type": "delta", "content": "正在分析你的需求...\n\n"}

        task = asyncio.create_task(
            self._generate_agent_response(
                session,
                user_id=user_id,
                session_id=session_id,
                scene_code=chat_session.scene_code or "study_assistant",
                page_context=payload.page_context,
            )
        )

        yielded_route_hint = False
        while not task.done():
            await asyncio.sleep(0.25)
            if not yielded_route_hint:
                yielded_route_hint = True
                yield {"type": "delta", "content": "正在调用对应智能体处理，请稍等...\n\n"}

        try:
            content = await task
        except Exception:
            logger.exception("AI chat stream generation failed: session_id=%s user_id=%s", session_id, user_id)
            content = self._build_local_fallback_response(payload.content)

        for chunk in self._chunk_text(content):
            yield {"type": "delta", "content": chunk}
            await asyncio.sleep(0.02)

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

    async def _ensure_session_owner(
        self,
        session: AsyncSession,
        user_id: int,
        session_id: int,
    ):
        chat_session = await self.repository.get_session_by_id(session, session_id)
        if not chat_session:
            raise NotFoundError(message="Chat session not found.")
        if chat_session.user_id != user_id:
            raise AuthorizationError(message="Not your chat session.")
        return chat_session

    async def _generate_agent_response(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        session_id: int,
        scene_code: str,
        page_context: dict[str, object] | None = None,
    ) -> str:
        messages = await self.repository.list_session_messages(session, session_id)
        latest_user_text = next((item.content for item in reversed(messages) if item.role == "user"), "")
        normalized_page_context = page_context if isinstance(page_context, dict) else {}
        message_history = [
            HumanMessage(content=item.content) if item.role == "user" else AIMessage(content=item.content)
            for item in messages[-10:]
        ]

        try:
            result = await asyncio.wait_for(
                self.agent_manager.run_tutor_chat(
                    db_session=session,
                    user_id=user_id,
                    session_id=session_id,
                    scene_code=scene_code,
                    messages=message_history,
                    context={"page_context": normalized_page_context},
                ),
                timeout=35,
            )
        except Exception:
            logger.exception("AgentManager.run_tutor_chat failed: session_id=%s user_id=%s", session_id, user_id)
            specialized = await self._generate_specialized_fallback_response(
                session,
                user_id=user_id,
                latest_user_text=latest_user_text,
                message_history=message_history,
                page_context=normalized_page_context,
            )
            return self._append_page_context_markdown(
                specialized or self._build_local_fallback_response(latest_user_text),
                normalized_page_context,
            )

        if result.get("messages"):
            content = str(result["messages"][-1].content or "").strip()
            if content:
                return self._append_page_context_markdown(content, normalized_page_context)

        specialized = await self._generate_specialized_fallback_response(
            session,
            user_id=user_id,
            latest_user_text=latest_user_text,
            message_history=message_history,
            page_context=normalized_page_context,
        )
        if specialized:
            return self._append_page_context_markdown(specialized, normalized_page_context)

        return self._append_page_context_markdown(
            self._build_local_fallback_response(latest_user_text),
            normalized_page_context,
        )

    async def _generate_specialized_fallback_response(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        latest_user_text: str,
        message_history: list,
        page_context: dict[str, object] | None = None,
    ) -> str | None:
        route = self._infer_specialized_route(latest_user_text, page_context)
        try:
            if route == "resource_generation":
                result = await self.agent_manager.run_resource_generation_agent(
                    session,
                    user_id=user_id,
                    learning_goal=self._augment_learning_goal_with_page_context(latest_user_text, page_context),
                    current_level="beginner",
                    tool_context=self._build_page_tool_context(page_context),
                )
                return self._combine_markdown_sections(
                    self._extract_text(result.get("goal_analysis")),
                    self._extract_text(result.get("path_plan")),
                    self._extract_text(result.get("generated_content")),
                    self._extract_text(result.get("adjustments")),
                )

            if route == "study_plan":
                result = await self.agent_manager.run_study_plan_agent(
                    session,
                    user_id=user_id,
                    evaluation_type="chat_assessment",
                    data={"latest_message": latest_user_text},
                )
                return self._combine_markdown_sections(
                    self._extract_text(result.get("grading")),
                    self._extract_text(result.get("mastery")),
                    self._extract_text(result.get("report")),
                )

            if route == "learning_evaluation":
                result = await self.agent_manager.run_learning_evaluation_agent(
                    session,
                    user_id=user_id,
                    month=None,
                    learning_data={"latest_message": latest_user_text},
                )
                return self._combine_markdown_sections(
                    self._extract_text(result.get("diagnosis")),
                    self._extract_text(result.get("learner_portrait")),
                    self._extract_text(result.get("optimization")),
                    self._extract_text(result.get("report_content")),
                )

            result = await self.agent_manager.run_tutor_qa_agent(
                session,
                user_id=user_id,
                question_content=latest_user_text,
                conversation_history=message_history,
                tool_context=self._build_page_tool_context(page_context),
            )
            return self._combine_markdown_sections(
                self._extract_text(result.get("guidance")),
                self._extract_text(result.get("answer")),
            )
        except Exception:
            logger.exception("Specialized fallback failed: user_id=%s route=%s", user_id, route)
            return None

    @staticmethod
    def _chunk_text(content: str, chunk_size: int = 18) -> list[str]:
        normalized = (content or "").strip() or "抱歉，我暂时没能生成有效回复，请稍后再试。"
        return [normalized[index:index + chunk_size] for index in range(0, len(normalized), chunk_size)]

    @staticmethod
    def _infer_specialized_route(text: str, page_context: dict[str, object] | None = None) -> str:
        normalized = (text or "").lower()
        if AIChatService._page_context_prefers_resource_generation(normalized, page_context):
            return "resource_generation"
        if any(keyword in normalized for keyword in ("????", "????", "??", "??", "??", "??", "??", "quiz", "practice")):
            return "resource_generation"
        if any(keyword in normalized for keyword in ("??", "??", "??", "???", "??")):
            return "study_plan"
        if any(keyword in normalized for keyword in ("??", "??", "??", "??", "??")):
            return "learning_evaluation"
        return "tutor_qa"

    @staticmethod
    def _page_context_prefers_resource_generation(text: str, page_context: dict[str, object] | None = None) -> bool:
        if not isinstance(page_context, dict) or not page_context:
            return False
        current_video = page_context.get("current_video")
        if not isinstance(current_video, dict) or not current_video.get("title"):
            return False
        page_keywords = ("????", "????", "????", "????", "???", "???", "????", "????", "?????", "?????")
        action_keywords = ("??", "??", "quiz", "practice", "????", "????", "??", "??", "????", "??", "??", "??")
        return any(keyword in text for keyword in page_keywords) and any(keyword in text for keyword in action_keywords)

    @staticmethod
    def _build_page_tool_context(page_context: dict[str, object] | None = None) -> dict[str, object]:
        if not isinstance(page_context, dict) or not page_context:
            return {}
        actions = page_context.get("available_actions")
        return {
            "page-context-reader": {
                "route": page_context.get("route"),
                "page_type": page_context.get("page_type"),
                "page_title": page_context.get("page_title"),
                "summary": page_context.get("summary"),
                "current_video": page_context.get("current_video") if isinstance(page_context.get("current_video"), dict) else None,
                "available_actions": actions if isinstance(actions, list) else [],
                "metadata": page_context.get("metadata") if isinstance(page_context.get("metadata"), dict) else {},
            }
        }

    @staticmethod
    def _augment_learning_goal_with_page_context(text: str, page_context: dict[str, object] | None = None) -> str:
        goal = (text or "").strip()
        if not isinstance(page_context, dict) or not page_context:
            return goal
        current_video = page_context.get("current_video")
        if not isinstance(current_video, dict) or not current_video.get("title"):
            return goal
        title = str(current_video.get("title") or "").strip()
        category = str(current_video.get("category_name") or "").strip()
        summary = str(current_video.get("summary") or "").strip()
        details = [f"Current video: {title}"]
        if category:
            details.append(f"Category: {category}")
        if summary:
            details.append(f"Summary: {summary}")
        details.append("Please generate same-topic practice, question-bank suggestions, study-path guidance, and actionable next links from the current page.")
        return f"{goal}\n\n" + "\n".join(details)

    @staticmethod
    def _extract_text(value) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            for key in ("raw", "summary", "content", "overview", "detailed_report"):
                inner = value.get(key)
                if isinstance(inner, str) and inner.strip():
                    return inner.strip()
        return ""

    @staticmethod
    def _combine_markdown_sections(*parts: str) -> str:
        chunks = [part.strip() for part in parts if isinstance(part, str) and part.strip()]
        return "\n\n".join(chunks) if chunks else ""

    @staticmethod
    def _append_page_context_markdown(content: str, page_context: dict[str, object]) -> str:
        if not isinstance(page_context, dict) or not page_context:
            return content
        if "## 当前页面" in (content or ""):
            return content

        blocks: list[str] = [content.strip()]
        page_title = str(page_context.get("page_title") or "").strip()
        summary = str(page_context.get("summary") or "").strip()
        if page_title:
            page_lines = [f"## 当前页面\n你当前所在页面：**{page_title}**"]
            if summary:
                page_lines.append(summary)
            blocks.append("\n".join(page_lines))

        current_video = page_context.get("current_video")
        if isinstance(current_video, dict) and current_video.get("title"):
            video_lines = [
                "## 当前页面内容",
                f"- 当前视频：**{current_video.get('title')}**",
            ]
            if current_video.get("summary"):
                video_lines.append(f"- 摘要：{current_video.get('summary')}")
            if current_video.get("category_name"):
                video_lines.append(f"- 分类：{current_video.get('category_name')}")
            blocks.append("\n".join(video_lines))

        actions = page_context.get("available_actions")
        if isinstance(actions, list) and actions:
            action_lines = ["## 你现在还可以继续"]
            for action in actions[:4]:
                if not isinstance(action, dict):
                    continue
                label = str(action.get("label") or "").strip()
                href = str(action.get("href") or "").strip()
                description = str(action.get("description") or "").strip()
                if not label:
                    continue
                action_lines.append(f"- [{label}]({href})" if href else f"- {label}")
                if description:
                    action_lines.append(f"  {description}")
            if len(action_lines) > 1:
                blocks.append("\n".join(action_lines))

        return "\n\n".join(block for block in blocks if block.strip())

    @staticmethod
    def _is_agent_catalog_question(text: str) -> bool:
        normalized = (text or "").strip().lower()
        keywords = [
            "你能做什么",
            "你可以做什么",
            "有哪些智能体",
            "有什么智能体",
            "智能体",
            "agent",
            "skills",
        ]
        return any(keyword in normalized for keyword in keywords)

    @classmethod
    def _build_local_fallback_response(cls, latest_user_text: str) -> str:
        if cls._is_agent_catalog_question(latest_user_text):
            return (
                f"{AGENT_CATALOG_MARKDOWN}\n\n"
                "你可以继续直接告诉我你的目标，比如：\n"
                "- 帮我规划一周 Python 学习路径\n"
                "- 根据我最近的练习情况分析薄弱点\n"
                "- 帮我讲解一道题为什么做错\n"
                "- 给我推荐下一步该看的课程和练习"
            )

        latest_user_text = (latest_user_text or "").strip()
        if latest_user_text:
            return (
                f"我已经收到你的问题：**{latest_user_text}**。\n\n"
                "当前模型服务暂时不稳定，但会话已经保留。你可以继续换一种更具体的问法发我，比如：\n"
                "- 把问题拆成一步一步讲\n"
                "- 直接给我这道题的思路\n"
                "- 根据我当前学习数据给出下周计划\n"
                "- 分析我最近练习的薄弱点"
            )

        return (
            "当前模型服务暂时不稳定，不过聊天入口仍然可用。你可以继续直接告诉我：\n"
            "- 你想学什么\n"
            "- 你卡在哪道题\n"
            "- 想要学习路径、资源推荐、答疑还是学习评估"
        )

    @staticmethod
    def _to_message_response(item) -> AIChatMessageResponse:
        return AIChatMessageResponse(
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
