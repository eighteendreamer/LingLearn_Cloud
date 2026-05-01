"""
学习月报智能体 - Monthly Report Agent
功能：学习效果诊断、学情画像生成、迭代优化建议
"""
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph


class MonthlyReportState(TypedDict):
    """月报状态"""

    user_id: int
    month: str
    learning_data: dict
    analysis: dict
    report_content: dict
    recommendations: list
    status: str


class MonthlyReportGraph:
    """学习月报智能体图"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建月报图"""
        workflow = StateGraph(MonthlyReportState)

        # 添加节点
        workflow.add_node("aggregate_data", self._aggregate_data)
        workflow.add_node("analyze_performance", self._analyze_performance)
        workflow.add_node("generate_report", self._generate_report)
        workflow.add_node("create_recommendations", self._create_recommendations)

        # 设置入口
        workflow.set_entry_point("aggregate_data")

        # 添加边
        workflow.add_edge("aggregate_data", "analyze_performance")
        workflow.add_edge("analyze_performance", "generate_report")
        workflow.add_edge("generate_report", "create_recommendations")
        workflow.add_edge("create_recommendations", "__end__")

        return workflow.compile()

    async def _aggregate_data(self, state: MonthlyReportState) -> MonthlyReportState:
        """聚合学习数据"""
        # 这里可以从数据库聚合一个月的学习数据
        state["status"] = "data_aggregated"
        return state

    async def _analyze_performance(self, state: MonthlyReportState) -> MonthlyReportState:
        """分析学习表现"""
        prompt = f"""请分析以下一个月的学习数据：

月份：{state['month']}
学习数据：{state['learning_data']}

请从以下维度分析：
1. 学习时长统计
2. 完成课程数量
3. 练习正确率趋势
4. 知识点掌握情况
5. 学习专注度
6. 进步幅度
7. 与上月对比

返回详细的分析结果。"""

        messages = [
            SystemMessage(content="你是一个专业的学习数据分析专家。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        state["analysis"] = {
            "total_hours": 45,
            "courses_completed": 8,
            "average_accuracy": 82,
            "focus_rate": 88,
            "progress_rate": 15,
            "detailed_analysis": response.content,
        }
        state["status"] = "analyzed"

        return state

    async def _generate_report(self, state: MonthlyReportState) -> MonthlyReportState:
        """生成月报内容"""
        prompt = f"""基于分析结果，生成一份详细的学习月报：

分析结果：{state['analysis']}

月报应包含：
1. 学习概览（总结性描述）
2. 数据可视化建议（图表类型和数据）
3. 亮点成就
4. 需要改进的地方
5. 知识点掌握热力图
6. 学习轨迹时间线
7. 排名和对比（如果有）

请用鼓励和专业的语气撰写。"""

        messages = [
            SystemMessage(content="你是一个专业的学习报告撰写专家。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        state["report_content"] = {
            "overview": "本月学习表现优秀，完成了8门课程，学习时长达45小时。",
            "highlights": ["连续学习21天", "练习正确率提升10%", "完成3个重要里程碑"],
            "improvements": ["写作练习需要加强", "高级语法掌握不够扎实"],
            "charts": {
                "learning_hours": [2, 3, 2.5, 3, 2, 1.5, 3],  # 每周学习时长
                "accuracy_trend": [75, 78, 80, 82, 85, 83, 82],  # 正确率趋势
            },
            "detailed_report": response.content,
        }
        state["status"] = "report_generated"

        return state

    async def _create_recommendations(self, state: MonthlyReportState) -> MonthlyReportState:
        """创建改进建议"""
        prompt = f"""基于月报分析，提供下个月的学习建议：

月报内容：{state['report_content']}
分析结果：{state['analysis']}

请提供：
1. 3-5条具体的改进建议
2. 推荐的学习重点
3. 建议的学习时间分配
4. 推荐课程和资源
5. 挑战目标设定

让建议具有可操作性和激励性。"""

        messages = [
            SystemMessage(content="你是一个学习规划顾问。"),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)

        state["recommendations"] = [
            {
                "type": "focus_area",
                "title": "加强写作练习",
                "description": "每天完成一篇短文写作",
            },
            {
                "type": "time_management",
                "title": "保持学习节奏",
                "description": "继续保持每天2小时的学习时间",
            },
            {
                "type": "challenge",
                "title": "挑战高级课程",
                "description": "尝试开始高级语法课程",
            },
            {"type": "ai_suggestion", "content": response.content},
        ]
        state["status"] = "completed"

        return state

    async def run(self, state: MonthlyReportState) -> MonthlyReportState:
        """执行月报图"""
        return await self.graph.ainvoke(state)
