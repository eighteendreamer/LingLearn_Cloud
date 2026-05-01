"""
AI学习助手对话智能体 - Tutor Chat Agent
功能：多轮对话交互、流式输出展示、资源收藏管理
"""
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages


class TutorChatState(TypedDict):
    """对话状态"""

    messages: Annotated[list, add_messages]
    user_id: int
    session_id: int
    scene_code: str
    context: dict  # 用户学习上下文


class TutorChatGraph:
    """AI学习助手对话图"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建对话图"""
        workflow = StateGraph(TutorChatState)

        # 添加节点
        workflow.add_node("analyze_intent", self._analyze_intent)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("format_output", self._format_output)

        # 设置入口
        workflow.set_entry_point("analyze_intent")

        # 添加边
        workflow.add_edge("analyze_intent", "generate_response")
        workflow.add_edge("generate_response", "format_output")
        workflow.add_edge("format_output", "__end__")

        return workflow.compile()

    async def _analyze_intent(self, state: TutorChatState) -> TutorChatState:
        """分析用户意图"""
        # 这里可以添加意图识别逻辑
        return state

    async def _generate_response(self, state: TutorChatState) -> TutorChatState:
        """生成AI回复"""
        # 构建系统提示词
        system_prompt = self._build_system_prompt(state["scene_code"], state["context"])

        messages = [SystemMessage(content=system_prompt)] + state["messages"]

        # 调用LLM
        response = await self.llm.ainvoke(messages)

        # 添加AI回复到消息列表
        state["messages"].append(AIMessage(content=response.content))

        return state

    async def _format_output(self, state: TutorChatState) -> TutorChatState:
        """格式化输出"""
        # 可以在这里添加输出格式化逻辑
        return state

    def _build_system_prompt(self, scene_code: str, context: dict) -> str:
        """构建系统提示词"""
        base_prompt = """你是LingLearn的AI学习助手，专注于帮助学生提升学习效果。

你的职责：
1. 回答学生的学习问题
2. 提供个性化学习建议
3. 推荐合适的学习资源
4. 分析学习数据并给出改进建议

请用友好、专业的语气与学生交流。"""

        # 根据场景添加特定提示
        scene_prompts = {
            "learning_guidance": "\n\n当前场景：学习指导\n请重点关注学习方法和学习计划的建议。",
            "practice_help": "\n\n当前场景：练习辅导\n请帮助学生理解题目，引导思考，而不是直接给出答案。",
            "progress_analysis": "\n\n当前场景：进度分析\n请基于学生的学习数据，提供客观的分析和建议。",
        }

        prompt = base_prompt + scene_prompts.get(scene_code, "")

        # 添加用户上下文
        if context:
            prompt += f"\n\n学生信息：\n{self._format_context(context)}"

        return prompt

    def _format_context(self, context: dict) -> str:
        """格式化用户上下文"""
        parts = []
        if "recent_courses" in context:
            parts.append(f"最近学习课程：{', '.join(context['recent_courses'])}")
        if "weak_areas" in context:
            parts.append(f"薄弱知识点：{', '.join(context['weak_areas'])}")
        if "learning_goal" in context:
            parts.append(f"学习目标：{context['learning_goal']}")
        return "\n".join(parts)

    async def run(self, state: TutorChatState) -> TutorChatState:
        """执行对话图"""
        return await self.graph.ainvoke(state)
