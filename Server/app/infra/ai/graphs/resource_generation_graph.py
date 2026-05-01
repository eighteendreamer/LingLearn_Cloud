"""
资源生成智能体 - Resource Generation Agent
功能：学习目标分析、六维表内容生成、画像质量校验、动态智能体化
"""
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph


class ResourceGenerationState(TypedDict):
    """资源生成状态"""

    user_id: int
    learning_goal: str
    analysis_result: dict
    generated_content: dict
    quality_score: float
    status: str


class ResourceGenerationGraph:
    """资源生成智能体图"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建资源生成图"""
        workflow = StateGraph(ResourceGenerationState)

        # 添加节点
        workflow.add_node("analyze_goal", self._analyze_goal)
        workflow.add_node("generate_content", self._generate_content)
        workflow.add_node("validate_quality", self._validate_quality)
        workflow.add_node("optimize_content", self._optimize_content)

        # 设置入口
        workflow.set_entry_point("analyze_goal")

        # 添加边
        workflow.add_edge("analyze_goal", "generate_content")
        workflow.add_edge("generate_content", "validate_quality")

        # 条件边：质量不达标则优化
        workflow.add_conditional_edges(
            "validate_quality",
            self._should_optimize,
            {
                "optimize": "optimize_content",
                "finish": "__end__",
            },
        )
        workflow.add_edge("optimize_content", "validate_quality")

        return workflow.compile()

    async def _analyze_goal(self, state: ResourceGenerationState) -> ResourceGenerationState:
        """分析学习目标"""
        prompt = f"""请分析以下学习目标，提取关键信息：

学习目标：{state['learning_goal']}

请从以下六个维度分析：
1. 活动内容分析
2. 六维表内容生成
3. 学习目标分解
4. 路径智能规划
5. 动态智能体化
6. 资源收藏管理

返回JSON格式的分析结果。"""

        messages = [
            SystemMessage(content="你是一个专业的学习目标分析专家。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        # 解析分析结果
        state["analysis_result"] = {"raw_analysis": response.content}
        state["status"] = "analyzed"

        return state

    async def _generate_content(self, state: ResourceGenerationState) -> ResourceGenerationState:
        """生成六维表内容"""
        prompt = f"""基于以下分析结果，生成详细的学习资源内容：

分析结果：{state['analysis_result']}

请生成包含以下内容的学习资源：
1. 学习路径规划
2. 推荐课程列表
3. 练习题目建议
4. 学习时间安排
5. 评估标准
6. 资源链接

返回结构化的JSON格式。"""

        messages = [
            SystemMessage(content="你是一个专业的学习资源生成专家。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        state["generated_content"] = {"content": response.content}
        state["status"] = "generated"

        return state

    async def _validate_quality(self, state: ResourceGenerationState) -> ResourceGenerationState:
        """校验内容质量"""
        # 简单的质量评分逻辑
        content = state["generated_content"].get("content", "")

        # 基于内容长度和结构完整性评分
        score = min(len(content) / 1000, 1.0)  # 简化评分

        state["quality_score"] = score
        state["status"] = "validated"

        return state

    def _should_optimize(self, state: ResourceGenerationState) -> str:
        """判断是否需要优化"""
        if state["quality_score"] < 0.7:
            return "optimize"
        return "finish"

    async def _optimize_content(self, state: ResourceGenerationState) -> ResourceGenerationState:
        """优化内容"""
        prompt = f"""请优化以下学习资源内容，使其更加完善：

当前内容：{state['generated_content']}
质量评分：{state['quality_score']}

请改进内容的：
1. 完整性
2. 可操作性
3. 个性化程度
4. 结构清晰度"""

        messages = [
            SystemMessage(content="你是一个内容优化专家。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        state["generated_content"]["content"] = response.content
        state["status"] = "optimized"

        return state

    async def run(self, state: ResourceGenerationState) -> ResourceGenerationState:
        """执行资源生成图"""
        return await self.graph.ainvoke(state)
