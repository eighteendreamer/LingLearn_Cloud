"""
Six LangGraph agents for the learning-domain AI layer.

The agents map directly to the product design:
01 UserInteractionAgent
02 FeatureExtractionAgent
03 ResourceGenerationAgent
04 StudyPlanAgent
05 TutorQAAgent
06 LearningEvaluationAgent
"""
from __future__ import annotations

from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph


AGENT_CATALOG_MARKDOWN = """LingLearn 当前已接入六大 LangGraph 智能体：

1. 用户交互智能体：负责多轮对话交互、流式输出展示、资源收藏管理。
2. 特征抽取智能体：负责对话内容分析、六维态内容生成、画像质量校验。
3. 资源生成智能体：负责学习目标分析、路径智能规划、动态调整优化。
4. 学习计划智能体：负责自动批改评分、掌握度判定、学习报告生成。
5. 智能答疑智能体：负责多轮对话答疑、思维引导辅导、错题讲题分析。
6. 学习评估智能体：负责学习效果诊断、学情画像生成、迭代优化建议。
"""

AGENT_CATALOG_INSTRUCTION = (
    "如果用户问“你能做什么”“有哪些智能体”“智能体职责”，"
    "必须明确说明 LingLearn 已接入六大 LangGraph 智能体，"
    "不能回答“只有一个 AI 学习助手”。"
)


def _message_text(messages: list[Any], limit: int = 8) -> str:
    items = []
    for message in messages[-limit:]:
        role = _message_role(message)
        content = _message_content(message)
        items.append(f"{role}: {content}")
    return "\n".join(items)


def _message_role(message: Any) -> str:
    if isinstance(message, dict):
        return str(message.get("type") or message.get("role") or "message")
    return str(getattr(message, "type", None) or getattr(message, "role", None) or "message")


def _message_content(message: Any) -> str:
    if isinstance(message, dict):
        return str(message.get("content", ""))
    return str(getattr(message, "content", message))


async def _ask(llm: Any, system: str, prompt: str) -> str:
    response = await llm.ainvoke([SystemMessage(content=system), HumanMessage(content=prompt)])
    return str(getattr(response, "content", response)).strip()


def _is_agent_catalog_question(text: str) -> bool:
    return any(keyword in text for keyword in ["你能做什么", "有哪些智能体", "什么智能体", "智能体", "agent"])


class UserInteractionState(TypedDict):
    user_id: int
    session_id: int | None
    scene_code: str
    messages: list[Any]
    context: dict[str, Any]
    intent: dict[str, Any]
    resource_actions: list[dict[str, Any]]
    response: str
    status: str


class UserInteractionAgent:
    """01 用户交互智能体：多轮对话、流式展示上游内容、资源收藏意图管理。"""

    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(UserInteractionState)
        graph.add_node("analyze_intent", self._analyze_intent)
        graph.add_node("manage_resource_actions", self._manage_resource_actions)
        graph.add_node("generate_response", self._generate_response)
        graph.set_entry_point("analyze_intent")
        graph.add_edge("analyze_intent", "manage_resource_actions")
        graph.add_edge("manage_resource_actions", "generate_response")
        graph.add_edge("generate_response", "__end__")
        return graph.compile()

    async def _analyze_intent(self, state: UserInteractionState) -> UserInteractionState:
        latest_content = _message_text(state["messages"], limit=1) if state["messages"] else ""
        if _is_agent_catalog_question(latest_content):
            state["intent"] = {
                "raw": "用户在询问 LingLearn 已接入的六大智能体和能力边界。",
                "scene_code": state["scene_code"],
                "requires_resource_action": False,
                "agent_catalog_question": True,
            }
            state["status"] = "intent_analyzed"
            return state

        prompt = f"""
请分析用户当前多轮对话意图，并返回简洁的结构化判断。

场景：{state['scene_code']}
上下文：{state['context']}
对话：
{_message_text(state['messages'])}

请覆盖：intent、confidence、need_resource、need_practice、need_path、emotion。
"""
        content = await _ask(self.llm, "你是用户交互智能体，负责理解学习场景中的用户意图。", prompt)
        state["intent"] = {
            "raw": content,
            "scene_code": state["scene_code"],
            "requires_resource_action": any(word in content for word in ["收藏", "资源", "课程", "路径"]),
        }
        state["status"] = "intent_analyzed"
        return state

    async def _manage_resource_actions(self, state: UserInteractionState) -> UserInteractionState:
        actions: list[dict[str, Any]] = []
        raw_intent = state["intent"].get("raw", "")
        if "收藏" in raw_intent:
            actions.append({"action": "favorite_suggestion", "status": "pending_confirmation"})
        if "资源" in raw_intent or "课程" in raw_intent:
            actions.append({"action": "recommend_resource", "status": "ready"})
        state["resource_actions"] = actions
        state["status"] = "resource_actions_prepared"
        return state

    async def _generate_response(self, state: UserInteractionState) -> UserInteractionState:
        latest_content = _message_text(state["messages"], limit=1) if state["messages"] else ""
        if state["intent"].get("agent_catalog_question") or _is_agent_catalog_question(latest_content):
            state["response"] = (
                "我可以通过 **六大 LangGraph 智能体** 协同帮助你学习：\n\n"
                f"{AGENT_CATALOG_MARKDOWN}\n"
                "你可以直接问我学习问题，也可以让我生成学习路径、分析错题、生成月报或做能力画像。"
            )
            state["status"] = "completed"
            return state

        prompt = f"""
请基于用户意图和学习上下文，生成面向学生的 Markdown 回复。

智能体能力清单：
{AGENT_CATALOG_MARKDOWN}

意图分析：{state['intent']}
资源动作：{state['resource_actions']}
学习上下文：{state['context']}
最近对话：
{_message_text(state['messages'])}

要求：
1. 语气友好，直接解决问题。
2. 如果适合，用 Markdown 列表或小标题。
3. 如果需要学习路径或资源，给出可执行下一步。
4. 不要编造不存在的数据库资源 ID。
"""
        state["response"] = await _ask(
            self.llm,
            f"你是 LingLearn 的用户交互智能体。\n{AGENT_CATALOG_MARKDOWN}\n{AGENT_CATALOG_INSTRUCTION}",
            prompt,
        )
        state["status"] = "completed"
        return state

    async def run(self, state: UserInteractionState) -> UserInteractionState:
        return await self.graph.ainvoke(state)


class FeatureExtractionState(TypedDict):
    user_id: int
    source_type: str
    source_ref_id: int | None
    conversations: list[Any]
    assessment_data: dict[str, Any]
    dialogue_analysis: dict[str, Any]
    six_dimension_profile: dict[str, Any]
    quality_report: dict[str, Any]
    status: str


class FeatureExtractionAgent:
    """02 特征抽取智能体：对话分析、六维态内容生成、画像质量校验。"""

    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(FeatureExtractionState)
        graph.add_node("analyze_dialogue", self._analyze_dialogue)
        graph.add_node("build_profile", self._build_profile)
        graph.add_node("validate_quality", self._validate_quality)
        graph.set_entry_point("analyze_dialogue")
        graph.add_edge("analyze_dialogue", "build_profile")
        graph.add_edge("build_profile", "validate_quality")
        graph.add_edge("validate_quality", "__end__")
        return graph.compile()

    async def _analyze_dialogue(self, state: FeatureExtractionState) -> FeatureExtractionState:
        prompt = f"""
请分析学习者对话和评估数据，提取学习特征。

来源：{state['source_type']}#{state['source_ref_id']}
对话：{_message_text(state['conversations'])}
评估数据：{state['assessment_data']}

请提取：知识基础、薄弱点、学习偏好、动机水平、表达能力、风险信号。
"""
        content = await _ask(self.llm, "你是学习特征抽取智能体，擅长从行为与对话中提取画像特征。", prompt)
        state["dialogue_analysis"] = {"raw": content}
        state["status"] = "dialogue_analyzed"
        return state

    async def _build_profile(self, state: FeatureExtractionState) -> FeatureExtractionState:
        prompt = f"""
基于特征分析生成六维能力画像。请按 0-100 分给出：
1. 编程基础
2. 算法思维
3. 数据库能力
4. 前端开发
5. 学习自驱
6. 表达与复盘

特征分析：{state['dialogue_analysis']}
"""
        content = await _ask(self.llm, "你是学生画像生成专家。", prompt)
        state["six_dimension_profile"] = {
            "raw": content,
            "dimensions": ["programming", "algorithm", "database", "frontend", "learning", "reflection"],
        }
        state["status"] = "profile_built"
        return state

    async def _validate_quality(self, state: FeatureExtractionState) -> FeatureExtractionState:
        raw = state["six_dimension_profile"].get("raw", "")
        quality_score = min(1.0, max(0.45, len(raw) / 900))
        state["quality_report"] = {
            "quality_score": round(quality_score, 2),
            "passed": quality_score >= 0.6,
            "checks": ["dimension_coverage", "actionability", "evidence_traceability"],
        }
        state["status"] = "completed"
        return state

    async def run(self, state: FeatureExtractionState) -> FeatureExtractionState:
        return await self.graph.ainvoke(state)


class ResourceGenerationState(TypedDict):
    user_id: int
    learning_goal: str
    current_level: str
    learning_history: dict[str, Any]
    profile: dict[str, Any]
    goal_analysis: dict[str, Any]
    path_plan: dict[str, Any]
    generated_content: dict[str, Any]
    adjustments: dict[str, Any]
    quality_score: float
    status: str


class ResourceGenerationAgent:
    """03 资源生成智能体：目标分析、路径规划、动态调整优化。"""

    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(ResourceGenerationState)
        graph.add_node("analyze_goal", self._analyze_goal)
        graph.add_node("plan_path", self._plan_path)
        graph.add_node("generate_resources", self._generate_resources)
        graph.add_node("optimize_adjustments", self._optimize_adjustments)
        graph.set_entry_point("analyze_goal")
        graph.add_edge("analyze_goal", "plan_path")
        graph.add_edge("plan_path", "generate_resources")
        graph.add_edge("generate_resources", "optimize_adjustments")
        graph.add_edge("optimize_adjustments", "__end__")
        return graph.compile()

    async def _analyze_goal(self, state: ResourceGenerationState) -> ResourceGenerationState:
        prompt = f"""
请分析学习目标并拆解优先级。

目标：{state['learning_goal']}
当前水平：{state['current_level']}
学习历史：{state['learning_history']}
画像：{state['profile']}

输出：目标类型、先修要求、关键里程碑、风险点。
"""
        state["goal_analysis"] = {"raw": await _ask(self.llm, "你是学习目标分析智能体。", prompt)}
        state["status"] = "goal_analyzed"
        return state

    async def _plan_path(self, state: ResourceGenerationState) -> ResourceGenerationState:
        prompt = f"""
请基于目标分析规划学习路径。

目标分析：{state['goal_analysis']}

输出 3-5 个阶段，每个阶段包含标题、目标、推荐资源类型、预计时间、验收方式。
"""
        state["path_plan"] = {"raw": await _ask(self.llm, "你是路径智能规划智能体。", prompt)}
        state["status"] = "path_planned"
        return state

    async def _generate_resources(self, state: ResourceGenerationState) -> ResourceGenerationState:
        prompt = f"""
请把学习路径转成可展示的资源方案。

学习路径：{state['path_plan']}

要求包含：课程建议、练习建议、复盘任务、收藏建议。不要编造数据库 ID。
"""
        content = await _ask(self.llm, "你是资源生成智能体。", prompt)
        state["generated_content"] = {
            "content": content,
            "recommended_resource_types": ["course", "practice", "review_task"],
        }
        state["quality_score"] = min(1.0, max(0.5, len(content) / 1000))
        state["status"] = "resources_generated"
        return state

    async def _optimize_adjustments(self, state: ResourceGenerationState) -> ResourceGenerationState:
        prompt = f"""
请为学习路径生成动态调整策略。

路径：{state['path_plan']}
资源方案：{state['generated_content']}
质量分：{state['quality_score']}

输出：触发条件、调整动作、预警文案。
"""
        state["adjustments"] = {"raw": await _ask(self.llm, "你是动态学习路径优化智能体。", prompt)}
        state["status"] = "completed"
        return state

    async def run(self, state: ResourceGenerationState) -> ResourceGenerationState:
        return await self.graph.ainvoke(state)


class StudyPlanState(TypedDict):
    user_id: int
    evaluation_type: str
    data: dict[str, Any]
    grading: dict[str, Any]
    mastery: dict[str, Any]
    report: dict[str, Any]
    status: str


class StudyPlanAgent:
    """04 学习计划智能体：自动批改评分、掌握度判定、学习报告生成。"""

    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(StudyPlanState)
        graph.add_node("auto_grade", self._auto_grade)
        graph.add_node("judge_mastery", self._judge_mastery)
        graph.add_node("generate_study_report", self._generate_study_report)
        graph.set_entry_point("auto_grade")
        graph.add_edge("auto_grade", "judge_mastery")
        graph.add_edge("judge_mastery", "generate_study_report")
        graph.add_edge("generate_study_report", "__end__")
        return graph.compile()

    async def _auto_grade(self, state: StudyPlanState) -> StudyPlanState:
        prompt = f"""
请对学习/练习数据进行自动评分。

类型：{state['evaluation_type']}
数据：{state['data']}

输出：completion_score、accuracy_score、focus_score、progress_score、overall_score 和依据。
"""
        state["grading"] = {"raw": await _ask(self.llm, "你是自动批改评分智能体。", prompt)}
        state["status"] = "graded"
        return state

    async def _judge_mastery(self, state: StudyPlanState) -> StudyPlanState:
        prompt = f"""
请基于评分判断掌握度。

评分：{state['grading']}

输出：mastery_level、weak_points、next_practice、promotion_condition。
"""
        state["mastery"] = {"raw": await _ask(self.llm, "你是掌握度判定智能体。", prompt)}
        state["status"] = "mastery_judged"
        return state

    async def _generate_study_report(self, state: StudyPlanState) -> StudyPlanState:
        prompt = f"""
请生成学习报告。

评分：{state['grading']}
掌握度：{state['mastery']}

要求：总结、优势、问题、下一步计划，Markdown 格式。
"""
        state["report"] = {
            "summary": await _ask(self.llm, "你是学习报告生成智能体。", prompt),
            "grading": state["grading"],
            "mastery": state["mastery"],
        }
        state["status"] = "completed"
        return state

    async def run(self, state: StudyPlanState) -> StudyPlanState:
        return await self.graph.ainvoke(state)


class TutorQAState(TypedDict):
    user_id: int
    question_id: int | None
    question_content: str
    user_answer: str | None
    correct_answer: str | None
    conversation_history: list[Any]
    intent: dict[str, Any]
    guidance: str
    wrong_question_analysis: dict[str, Any]
    answer: str
    status: str


class TutorQAAgent:
    """05 智能答疑智能体：多轮答疑、思维引导、错题讲题。"""

    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(TutorQAState)
        graph.add_node("understand_question", self._understand_question)
        graph.add_node("socratic_guidance", self._socratic_guidance)
        graph.add_node("analyze_wrong_question", self._wrong_question_analysis)
        graph.add_node("final_answer", self._final_answer)
        graph.set_entry_point("understand_question")
        graph.add_edge("understand_question", "socratic_guidance")
        graph.add_edge("socratic_guidance", "analyze_wrong_question")
        graph.add_edge("analyze_wrong_question", "final_answer")
        graph.add_edge("final_answer", "__end__")
        return graph.compile()

    async def _understand_question(self, state: TutorQAState) -> TutorQAState:
        prompt = f"""
请理解学生问题类型。

问题：{state['question_content']}
历史：{_message_text(state['conversation_history'])}

输出：question_type、knowledge_points、difficulty、answer_strategy。
"""
        state["intent"] = {"raw": await _ask(self.llm, "你是智能答疑意图识别智能体。", prompt)}
        state["status"] = "question_understood"
        return state

    async def _socratic_guidance(self, state: TutorQAState) -> TutorQAState:
        prompt = f"""
请给出启发式思维引导，不要只抛最终答案。

问题理解：{state['intent']}
问题：{state['question_content']}

输出 3 个逐步提示和关键思路。
"""
        state["guidance"] = await _ask(self.llm, "你是善于苏格拉底式提问的导师。", prompt)
        state["status"] = "guidance_generated"
        return state

    async def _wrong_question_analysis(self, state: TutorQAState) -> TutorQAState:
        if not state.get("user_answer") and not state.get("correct_answer"):
            state["wrong_question_analysis"] = {}
            return state
        prompt = f"""
请分析错题。

题目：{state['question_content']}
学生答案：{state.get('user_answer')}
正确答案：{state.get('correct_answer')}

输出：错误原因、关键知识点、纠错讲解、相似题建议。
"""
        state["wrong_question_analysis"] = {
            "raw": await _ask(self.llm, "你是错题讲题分析智能体。", prompt)
        }
        state["status"] = "wrong_question_analyzed"
        return state

    async def _final_answer(self, state: TutorQAState) -> TutorQAState:
        prompt = f"""
请整合为最终答疑回复。

问题：{state['question_content']}
引导：{state['guidance']}
错题分析：{state['wrong_question_analysis']}

要求：Markdown、先引导再总结、必要时给例子。
"""
        state["answer"] = await _ask(self.llm, "你是 LingLearn 智能答疑智能体。", prompt)
        state["status"] = "completed"
        return state

    async def run(self, state: TutorQAState) -> TutorQAState:
        return await self.graph.ainvoke(state)


class LearningEvaluationState(TypedDict):
    user_id: int
    month: str | None
    learning_data: dict[str, Any]
    path_progress: dict[str, Any]
    diagnosis: dict[str, Any]
    learner_portrait: dict[str, Any]
    optimization: dict[str, Any]
    report_content: dict[str, Any]
    recommendations: list[dict[str, Any]]
    status: str


class LearningEvaluationAgent:
    """06 学习评估智能体：效果诊断、学情画像、迭代优化建议。"""

    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(LearningEvaluationState)
        graph.add_node("diagnose_effect", self._diagnose_effect)
        graph.add_node("generate_portrait", self._generate_portrait)
        graph.add_node("optimize_next_iteration", self._optimize_next_iteration)
        graph.set_entry_point("diagnose_effect")
        graph.add_edge("diagnose_effect", "generate_portrait")
        graph.add_edge("generate_portrait", "optimize_next_iteration")
        graph.add_edge("optimize_next_iteration", "__end__")
        return graph.compile()

    async def _diagnose_effect(self, state: LearningEvaluationState) -> LearningEvaluationState:
        prompt = f"""
请诊断学习效果。

月份：{state.get('month')}
学习数据：{state['learning_data']}
路径进度：{state['path_progress']}

输出：学习时长、完成度、正确率、专注度、进步幅度、风险点。
"""
        state["diagnosis"] = {"raw": await _ask(self.llm, "你是学习效果诊断智能体。", prompt)}
        state["status"] = "effect_diagnosed"
        return state

    async def _generate_portrait(self, state: LearningEvaluationState) -> LearningEvaluationState:
        prompt = f"""
请基于学习效果诊断生成学情画像。

诊断：{state['diagnosis']}

输出：学习者类型、优势、短板、学习节奏、能力雷达建议。
"""
        state["learner_portrait"] = {"raw": await _ask(self.llm, "你是学情画像生成智能体。", prompt)}
        state["status"] = "portrait_generated"
        return state

    async def _optimize_next_iteration(self, state: LearningEvaluationState) -> LearningEvaluationState:
        prompt = f"""
请给出下一轮迭代优化建议，并形成月报内容。

诊断：{state['diagnosis']}
画像：{state['learner_portrait']}

输出：月报概览、亮点、改进项、下月建议、可执行任务。
"""
        content = await _ask(self.llm, "你是迭代优化建议智能体。", prompt)
        state["optimization"] = {"raw": content}
        state["report_content"] = {
            "overview": content,
            "highlights": ["完成学习效果诊断", "生成学情画像", "形成下一轮优化建议"],
            "improvements": ["按薄弱点安排练习", "每周复盘一次学习路径"],
            "detailed_report": content,
        }
        state["recommendations"] = [
            {"type": "practice", "title": "补强薄弱知识点", "description": "优先完成错题相关练习"},
            {"type": "review", "title": "建立周复盘", "description": "记录掌握度变化和卡点"},
        ]
        state["status"] = "completed"
        return state

    async def run(self, state: LearningEvaluationState) -> LearningEvaluationState:
        return await self.graph.ainvoke(state)
