"""
学习路径智能体 - Learning Path Agent
功能：学习效果诊断、学情画像生成、迭代优化建议
"""
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph


class LearningPathState(TypedDict):
    """学习路径状态"""

    user_id: int
    current_level: str
    learning_history: dict
    diagnosis: dict
    profile: dict
    path: dict
    optimization: dict
    status: str


class LearningPathGraph:
    """学习路径智能体图"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建学习路径图"""
        workflow = StateGraph(LearningPathState)

        # 添加节点
        workflow.add_node("diagnose_level", self._diagnose_level)
        workflow.add_node("generate_profile", self._generate_profile)
        workflow.add_node("plan_path", self._plan_path)
        workflow.add_node("optimize_path", self._optimize_path)

        # 设置入口
        workflow.set_entry_point("diagnose_level")

        # 添加边
        workflow.add_edge("diagnose_level", "generate_profile")
        workflow.add_edge("generate_profile", "plan_path")
        workflow.add_edge("plan_path", "optimize_path")
        workflow.add_edge("optimize_path", "__end__")

        return workflow.compile()

    async def _diagnose_level(self, state: LearningPathState) -> LearningPathState:
        """诊断学习水平"""
        prompt = f"""请基于以下学习历史，诊断学生的学习水平：

当前等级：{state['current_level']}
学习历史：{state['learning_history']}

请诊断：
1. 知识掌握程度
2. 学习能力评估
3. 学习风格偏好
4. 薄弱知识点
5. 优势领域

返回JSON格式的诊断结果。"""

        messages = [
            SystemMessage(content="你是一个专业的学习诊断专家。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        state["diagnosis"] = {
            "knowledge_level": "中级",
            "learning_ability": "良好",
            "learning_style": "视觉型学习者",
            "weak_points": ["高级语法", "写作技巧"],
            "strengths": ["词汇记忆", "听力理解"],
            "detailed_diagnosis": response.content,
        }
        state["status"] = "diagnosed"

        return state

    async def _generate_profile(self, state: LearningPathState) -> LearningPathState:
        """生成学情画像"""
        prompt = f"""基于诊断结果，生成详细的学情画像：

诊断结果：{state['diagnosis']}

请生成包含以下内容的学情画像：
1. 学习者特征描述
2. 知识图谱
3. 能力雷达图数据
4. 学习偏好分析
5. 个性化标签

返回结构化的JSON格式。"""

        messages = [
            SystemMessage(content="你是一个学情画像生成专家。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        state["profile"] = {
            "learner_type": "视觉型学习者",
            "knowledge_map": {"基础": 85, "中级": 70, "高级": 45},
            "ability_radar": {
                "听": 80,
                "说": 65,
                "读": 75,
                "写": 60,
                "词汇": 85,
                "语法": 70,
            },
            "tags": ["勤奋", "善于记忆", "需要加强写作"],
            "detailed_profile": response.content,
        }
        state["status"] = "profiled"

        return state

    async def _plan_path(self, state: LearningPathState) -> LearningPathState:
        """规划学习路径"""
        prompt = f"""基于学情画像，规划个性化学习路径：

学情画像：{state['profile']}

请规划：
1. 短期目标（1个月）
2. 中期目标（3个月）
3. 长期目标（6个月）
4. 每个阶段的学习内容
5. 推荐课程和资源
6. 学习时间安排
7. 里程碑设置

返回详细的学习路径规划。"""

        messages = [
            SystemMessage(content="你是一个学习路径规划专家。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        state["path"] = {
            "short_term": "巩固中级语法，提升写作能力",
            "mid_term": "掌握高级语法，能写流畅文章",
            "long_term": "达到高级水平，自如运用语言",
            "milestones": [
                {"week": 4, "goal": "完成中级语法课程"},
                {"week": 8, "goal": "写作水平提升到70分"},
                {"week": 12, "goal": "通过中级水平测试"},
            ],
            "detailed_plan": response.content,
        }
        state["status"] = "planned"

        return state

    async def _optimize_path(self, state: LearningPathState) -> LearningPathState:
        """优化路径"""
        prompt = f"""请对学习路径进行优化建议：

当前路径：{state['path']}
学情画像：{state['profile']}

请提供：
1. 路径可行性分析
2. 潜在风险点
3. 优化建议
4. 替代方案
5. 动态调整策略

帮助学生更好地完成学习目标。"""

        messages = [
            SystemMessage(content="你是一个学习路径优化专家。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        state["optimization"] = {
            "feasibility": "高",
            "risks": ["写作提升需要更多时间", "可能需要额外辅导"],
            "suggestions": ["增加写作练习频率", "参加写作工作坊"],
            "detailed_optimization": response.content,
        }
        state["status"] = "completed"

        return state

    async def run(self, state: LearningPathState) -> LearningPathState:
        """执行学习路径图"""
        return await self.graph.ainvoke(state)
