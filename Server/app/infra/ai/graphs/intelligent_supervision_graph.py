"""
智能督学智能体 - Intelligent Supervision Agent
功能：多轮对话疑难、思维链引导辅导、错题讲题分析
"""
from typing import TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph


class SupervisionState(TypedDict):
    """督学状态"""

    user_id: int
    question_id: int
    question_content: str
    user_answer: str
    correct_answer: str
    conversation_history: list
    analysis: dict
    guidance: str
    status: str


class IntelligentSupervisionGraph:
    """智能督学智能体图"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建督学图"""
        workflow = StateGraph(SupervisionState)

        # 添加节点
        workflow.add_node("analyze_error", self._analyze_error)
        workflow.add_node("generate_guidance", self._generate_guidance)
        workflow.add_node("provide_hints", self._provide_hints)

        # 设置入口
        workflow.set_entry_point("analyze_error")

        # 添加边
        workflow.add_edge("analyze_error", "generate_guidance")
        workflow.add_edge("generate_guidance", "provide_hints")
        workflow.add_edge("provide_hints", "__end__")

        return workflow.compile()

    async def _analyze_error(self, state: SupervisionState) -> SupervisionState:
        """分析错误"""
        prompt = f"""请分析学生的答题情况：

题目：{state['question_content']}
学生答案：{state['user_answer']}
正确答案：{state['correct_answer']}

请分析：
1. 错误类型（概念理解/计算错误/粗心大意等）
2. 知识点掌握情况
3. 思维过程中的问题
4. 需要加强的方面

返回JSON格式的分析结果。"""

        messages = [
            SystemMessage(content="你是一个专业的学习督导专家，擅长分析学生的学习问题。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        state["analysis"] = {
            "error_type": "概念理解不足",
            "knowledge_gap": "需要加强基础概念",
            "thinking_issue": "逻辑推理不够严密",
            "detailed_analysis": response.content,
        }
        state["status"] = "analyzed"

        return state

    async def _generate_guidance(self, state: SupervisionState) -> SupervisionState:
        """生成引导"""
        prompt = f"""基于以下错误分析，生成思维链式的引导：

错误分析：{state['analysis']}

请设计3-5个引导性问题，帮助学生：
1. 回顾相关知识点
2. 理解题目要求
3. 发现自己的错误
4. 找到正确的解题思路

不要直接给出答案，而是通过问题引导学生思考。"""

        messages = [
            SystemMessage(content="你是一个善于启发式教学的导师。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        state["guidance"] = response.content
        state["status"] = "guidance_generated"

        return state

    async def _provide_hints(self, state: SupervisionState) -> SupervisionState:
        """提供提示"""
        prompt = f"""基于引导问题，提供渐进式的提示：

引导内容：{state['guidance']}

请提供3个层次的提示：
1. 轻度提示：指向相关知识点
2. 中度提示：提示解题方向
3. 重度提示：详细解题步骤

让学生可以根据需要逐步获取帮助。"""

        messages = [
            SystemMessage(content="你是一个耐心的辅导老师。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        state["analysis"]["hints"] = response.content
        state["status"] = "completed"

        return state

    async def run(self, state: SupervisionState) -> SupervisionState:
        """执行督学图"""
        return await self.graph.ainvoke(state)
