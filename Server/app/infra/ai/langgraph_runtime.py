from typing import Any

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.infra.ai.llm_client import LLMClient


class BackendChatModel:
    """Small chat-model adapter with the ainvoke API used by our LangGraph nodes."""

    def __init__(self) -> None:
        self.client = LLMClient()

    async def ainvoke(self, messages: list[Any]) -> AIMessage:
        response = await self.client.chat(self._serialize_messages(messages))
        return AIMessage(content=self._extract_content(response))

    def _serialize_messages(self, messages: list[Any]) -> list[dict[str, str]]:
        serialized: list[dict[str, str]] = []
        for message in messages:
            role = getattr(message, "type", None) or getattr(message, "role", None) or "user"
            if role == "human":
                role = "user"
            elif role == "ai":
                role = "assistant"
            elif role not in {"system", "user", "assistant", "tool"}:
                role = "user"
            serialized.append({"role": role, "content": str(getattr(message, "content", message))})
        return serialized

    def _extract_content(self, response: dict) -> str:
        choices = response.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0] or {}
            message = first.get("message") or {}
            content = message.get("content") or first.get("text")
            if content:
                return str(content)

        data = response.get("data")
        if isinstance(data, dict):
            content = data.get("content") or data.get("text") or data.get("output_text")
            if content:
                return str(content)

        content = response.get("content") or response.get("text") or response.get("output_text")
        if content:
            return str(content)

        raise RuntimeError(f"LLM upstream returned no assistant content: {response}")


class LangGraphRuntime:
    """LangGraph runtime manager for creating and executing graphs."""

    def __init__(self) -> None:
        self._llm: BackendChatModel | None = None

    def get_llm(self) -> BackendChatModel:
        if self._llm is None:
            self._llm = BackendChatModel()
        return self._llm

    def create_graph(self, graph_builder: StateGraph) -> CompiledStateGraph:
        return graph_builder.compile()

    async def execute_graph(
        self,
        graph: CompiledStateGraph,
        initial_state: dict[str, Any],
    ) -> dict[str, Any]:
        return await graph.ainvoke(initial_state)
