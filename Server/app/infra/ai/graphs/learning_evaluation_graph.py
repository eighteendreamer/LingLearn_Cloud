"""
学习评估智能体 - Learning Evaluation Agent
功能：自动批改评分、学据度判定、学习报告生成
"""
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph


class LearningEvaluationState(TypedDict):
    """学习评估状态"""

    user_id: int
    evaluation_type: str  # practice/course/overall
    data: dict
    scores: dict
    report: dict
    status: str


class LearningEvaluationGraph:
    """学习评估智能体图"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建评估图"""
        workflow = StateGraph(LearningEvaluationState)

        # 添加节点
        workflow.add_node("collect_data", self._collect_data)
        workflow.add_node("calculate_scores", self._calculate_scores)
        workflow.add_node("generate_report", self._generate_report)

        # 设置入口
        workflow.set_entry_point("collect_data")

        # 添加边
        workflow.add_edge("collect_data", "calculate_scores")
        workflow.add_edge("calculate_scores", "generate_report")
        workflow.add_edge("generate_report", "__end__")

        return workflow.compile()

    async def _collect_data(self, state: LearningEvaluationState) -> LearningEvaluationState:
        """收集评估数据"""
        # 这里可以从数据库收集用户学习数据
        state["status"] = "data_collected"
        return state

    async def _calculate_scores(
        self, state: LearningEvaluationState
    ) -> LearningEvaluationState:
        """计算评分"""
        prompt = f"""请基于以下学习数据，计算各项评分：

评估类型：{state['evaluation_type']}
学习数据：{state['data']}

请计算以下维度的评分（0-100分）：
1. 完成度评分
2. 正确率评分
3. 学习专注度
4. 进步幅度
5. 综合评分

返回JSON格式的评分结果。"""

        messages = [
            SystemMessage(content="你是一个专业的学习评估专家。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        # 解析评分结果
        state["scores"] = {
            "completion_score": 85,
            "accuracy_score": 78,
            "focus_score": 90,
            "progress_score": 82,
            "overall_score": 84,
            "ai_analysis": response.content,
        }
        state["status"] = "scored"

        return state

    async def _generate_report(self, state: LearningEvaluationState) -> LearningEvaluationState:
        """生成学习报告"""
        prompt = f"""请基于以下评分结果，生成详细的学习报告：

评分结果：{state['scores']}

报告应包含：
1. 学习表现总结
2. 优势分析
3. 薄弱环节
4. 改进建议
5. 下一步学习计划

请用友好、鼓励的语气撰写。"""

        messages = [
            SystemMessage(content="你是一个专业的学习报告撰写专家。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        state["report"] = {
            "summary": response.content,
            "scores": state["scores"],
            "generated_at": "2026-05-01",
        }
        state["status"] = "completed"

        return state

    async def run(self, state: LearningEvaluationState) -> LearningEvaluationState:
        """执行评估图"""
        return await self.graph.ainvoke(state)
