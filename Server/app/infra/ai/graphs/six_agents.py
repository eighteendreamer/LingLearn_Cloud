"""
Six LangGraph agents for the LingLearn AI layer.
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph

from app.infra.ai.agent_skills import (
    AGENT_CATALOG_MARKDOWN,
    CHAT_ASSISTANT_SKILL_CODES,
    FEATURE_EXTRACTION_SKILL,
    LEARNING_EVALUATION_SKILL,
    RESOURCE_GENERATION_SKILL,
    STUDY_PLAN_SKILL,
    TUTOR_QA_SKILL,
    USER_INTERACTION_SKILL,
    VIDEO_CONTENT_SKILL,
    build_chat_router_skill_catalog,
)
from app.infra.ai.agent_tools import default_tool_keys_for_skill


def _message_role(message: Any) -> str:
    if isinstance(message, dict):
        return str(message.get("type") or message.get("role") or "message")
    return str(getattr(message, "type", None) or getattr(message, "role", None) or "message")


def _message_content(message: Any) -> str:
    if isinstance(message, dict):
        return str(message.get("content", ""))
    return str(getattr(message, "content", message))


def _message_text(messages: list[Any], limit: int = 8) -> str:
    return "\n".join(
        f"{_message_role(message)}: {_message_content(message)}"
        for message in messages[-limit:]
    )


async def _ask(llm: Any, system: str, prompt: str) -> str:
    response = await asyncio.wait_for(
        llm.ainvoke([SystemMessage(content=system), HumanMessage(content=prompt)]),
        timeout=30,
    )
    return str(getattr(response, "content", response)).strip()


def _extract_json_object(raw: str) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _is_agent_catalog_question(text: str) -> bool:
    normalized = (text or "").strip().lower()
    keywords = ["你能做什么", "你可以做什么", "有哪些智能体", "有什么智能体", "智能体", "agent", "skills"]
    return any(keyword in normalized for keyword in keywords)


def _sanitize_skill_codes(values: list[Any]) -> list[str]:
    result: list[str] = []
    for value in values:
        code = str(value)
        if code in CHAT_ASSISTANT_SKILL_CODES and code not in result:
            result.append(code)
    return result[:2]


def _sanitize_tool_plan(raw_plan: Any, skill_codes: list[str]) -> dict[str, list[str]]:
    raw_plan = raw_plan if isinstance(raw_plan, dict) else {}
    output: dict[str, list[str]] = {}
    for skill_code in skill_codes:
        defaults = default_tool_keys_for_skill(skill_code)
        requested = raw_plan.get(skill_code)
        if not isinstance(requested, list):
            output[skill_code] = defaults
            continue
        filtered = [key for key in requested if key in defaults]
        output[skill_code] = filtered or defaults
    return output


def _fallback_skill_codes(text: str) -> list[str]:
    normalized = (text or "").lower()
    if any(keyword in normalized for keyword in ("视频", "当前视频", "画面", "语音", "讲解", "frame", "transcript", "summary", "总结", "笔记", "报告")):
        return [VIDEO_CONTENT_SKILL.code]
    if any(
        keyword in normalized
        for keyword in (
            "学习路线",
            "学习计划",
            "推荐",
            "路径",
            "roadmap",
            "资源",
            "规划",
            "课程",
            "目标",
            "quiz",
            "practice",
        )
    ):
        return [RESOURCE_GENERATION_SKILL.code]
    if any(keyword in normalized for keyword in ("评测", "批改", "成绩", "掌握度", "打分")):
        return [STUDY_PLAN_SKILL.code]
    if any(keyword in normalized for keyword in ("评估", "诊断", "画像", "月报", "学情")):
        return [LEARNING_EVALUATION_SKILL.code]
    return [TUTOR_QA_SKILL.code]


def _page_context_prefers_resource_generation(
    text: str,
    page_context: dict[str, Any] | None,
) -> bool:
    if not isinstance(page_context, dict) or not page_context:
        return False

    current_video = page_context.get("current_video")
    if not isinstance(current_video, dict) or not current_video.get("title"):
        return False

    normalized = (text or "").lower()
    page_keywords = (
        "这个视频",
        "当前内容",
        "这门课程",
        "这个课程",
        "这节课",
        "这堂课",
        "当前学习",
        "当前页面",
        "这个页面的",
        "当前页面的",
    )
    action_keywords = (
        "出题",
        "练习",
        "quiz",
        "practice",
        "做个练习",
        "做个测验",
        "规划",
        "路径",
        "生成路径",
        "推荐",
        "建议",
        "资源",
    )
    return any(keyword in normalized for keyword in page_keywords) and any(keyword in normalized for keyword in action_keywords)


def _page_context_prefers_video_content(
    text: str,
    page_context: dict[str, Any] | None,
) -> bool:
    if not isinstance(page_context, dict) or not page_context:
        return False

    current_video = page_context.get("current_video")
    if not isinstance(current_video, dict) or not current_video.get("video_url"):
        return False

    normalized = (text or "").lower()
    return any(
        keyword in normalized
        for keyword in (
            "视频",
            "当前视频",
            "画面",
            "语音",
            "讲解",
            "总结",
            "报告",
            "笔记",
            "题库",
            "练习",
            "quiz",
            "summary",
            "report",
        )
    )


def _choose_primary_text(result: dict[str, Any]) -> str:
    for key in ("answer", "guidance", "generated_output"):
        value = result.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    report = result.get("report")
    if isinstance(report, dict):
        summary = report.get("summary")
        if isinstance(summary, str) and summary.strip():
            return summary.strip()
    report_content = result.get("report_content")
    if isinstance(report_content, dict):
        overview = report_content.get("overview")
        if isinstance(overview, str) and overview.strip():
            return overview.strip()
    for key in ("generated_content", "goal_analysis", "path_plan", "adjustments", "diagnosis", "learner_portrait"):
        value = result.get(key)
        if isinstance(value, dict):
            raw = value.get("raw")
            if isinstance(raw, str) and raw.strip():
                return raw.strip()
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _unwrap_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ("raw", "content", "summary", "overview", "detailed_report"):
            inner = value.get(key)
            if isinstance(inner, str) and inner.strip():
                return inner.strip()
    return ""


def _merge_embedded_json(result: dict[str, Any], expected_keys: tuple[str, ...]) -> dict[str, Any]:
    merged = dict(result)
    for value in result.values():
        text = _unwrap_text(value)
        parsed = _extract_json_object(text)
        if not parsed or not any(key in parsed for key in expected_keys):
            continue
        for key in expected_keys:
            current_text = _unwrap_text(merged.get(key))
            if (
                key not in merged
                or not current_text
                or current_text == text
                or current_text.lstrip().startswith("{")
            ):
                merged[key] = parsed.get(key)
    return merged


def _append_section(parts: list[str], title: str, body: str) -> None:
    text = (body or "").strip()
    if text:
        parts.append(f"## {title}\n{text}")


def _format_resource_generation_result(result: dict[str, Any]) -> str:
    merged = _merge_embedded_json(
        result,
        ("goal_analysis", "path_plan", "generated_content", "adjustments"),
    )
    parts: list[str] = []
    _append_section(parts, "目标分析", _unwrap_text(merged.get("goal_analysis")))
    _append_section(parts, "学习路径", _unwrap_text(merged.get("path_plan")))
    _append_section(parts, "推荐资源", _unwrap_text(merged.get("generated_content")))
    _append_section(parts, "动态调整建议", _unwrap_text(merged.get("adjustments")))
    return "\n\n".join(parts).strip()


def _format_study_plan_result(result: dict[str, Any]) -> str:
    merged = _merge_embedded_json(result, ("grading", "mastery", "report"))
    parts: list[str] = []
    _append_section(parts, "自动评分", _unwrap_text(merged.get("grading")))
    _append_section(parts, "掌握度判断", _unwrap_text(merged.get("mastery")))
    _append_section(parts, "学习报告", _unwrap_text(merged.get("report")))
    return "\n\n".join(parts).strip()


def _format_tutor_qa_result(result: dict[str, Any]) -> str:
    merged = _merge_embedded_json(result, ("guidance", "wrong_question_analysis", "answer"))
    parts: list[str] = []
    _append_section(parts, "思路引导", _unwrap_text(merged.get("guidance")))
    _append_section(parts, "错题分析", _unwrap_text(merged.get("wrong_question_analysis")))
    answer = _unwrap_text(merged.get("answer"))
    if answer:
        parts.append(answer)
    return "\n\n".join(parts).strip()


def _format_learning_evaluation_result(result: dict[str, Any]) -> str:
    merged = _merge_embedded_json(
        result,
        ("diagnosis", "learner_portrait", "optimization", "report_content"),
    )
    parts: list[str] = []
    _append_section(parts, "学习效果诊断", _unwrap_text(merged.get("diagnosis")))
    _append_section(parts, "学情画像", _unwrap_text(merged.get("learner_portrait")))
    _append_section(parts, "优化建议", _unwrap_text(merged.get("optimization")))
    _append_section(parts, "阶段总结", _unwrap_text(merged.get("report_content")))
    return "\n\n".join(parts).strip()


def _format_video_content_result(result: dict[str, Any]) -> str:
    parts: list[str] = []
    transcript = _unwrap_text(result.get("transcript"))
    visual_analysis = _unwrap_text(result.get("visual_analysis"))
    generated_output = _unwrap_text(result.get("generated_output"))
    if generated_output:
        parts.append(generated_output)
    if visual_analysis:
        parts.append(f"## 视频画面理解\n{visual_analysis}")
    if transcript:
        parts.append(f"## 讲解语音内容\n{transcript}")
    return "\n\n".join(parts).strip()


def _render_skill_result(skill_code: str, result: dict[str, Any]) -> str:
    if skill_code == VIDEO_CONTENT_SKILL.code:
        return _format_video_content_result(result)
    if skill_code == RESOURCE_GENERATION_SKILL.code:
        return _format_resource_generation_result(result)
    if skill_code == STUDY_PLAN_SKILL.code:
        return _format_study_plan_result(result)
    if skill_code == TUTOR_QA_SKILL.code:
        return _format_tutor_qa_result(result)
    if skill_code == LEARNING_EVALUATION_SKILL.code:
        return _format_learning_evaluation_result(result)
    return _choose_primary_text(result)


def _page_context(state: "UserInteractionState") -> dict[str, Any]:
    context = state.get("context") or {}
    if not isinstance(context, dict):
        return {}
    page_context = context.get("page_context")
    return page_context if isinstance(page_context, dict) else {}


def _render_page_awareness(state: "UserInteractionState") -> str:
    page_context = _page_context(state)
    if not page_context:
        return ""

    parts: list[str] = []
    page_title = str(page_context.get("page_title") or "Current Page").strip()
    summary = str(page_context.get("summary") or "").strip()
    if page_title:
        header = f"## Current Page\nYou are currently on **{page_title}**."
        if summary:
            header += f"\n{summary}"
        parts.append(header)

    current_video = page_context.get("current_video")
    if isinstance(current_video, dict) and current_video.get("title"):
        video_lines = [
            "## Current Content",
            f"- Current video: **{current_video.get('title')}**",
        ]
        if current_video.get("category_name"):
            video_lines.append(f"- Category: {current_video.get('category_name')}")
        if current_video.get("author_name"):
            video_lines.append(f"- Author: {current_video.get('author_name')}")
        if current_video.get("summary"):
            video_lines.append(f"- Summary: {current_video.get('summary')}")
        hashtags = current_video.get("hashtags")
        if isinstance(hashtags, list) and hashtags:
            video_lines.append(f"- Keywords: {', '.join(str(item) for item in hashtags[:6])}")
        parts.append("\n".join(video_lines))

    actions = page_context.get("available_actions")
    if isinstance(actions, list) and actions:
        action_lines = ["## You Can Continue With"]
        for action in actions[:5]:
            if not isinstance(action, dict):
                continue
            label = str(action.get("label") or "Next action").strip()
            href = str(action.get("href") or "").strip()
            description = str(action.get("description") or "").strip()
            if href:
                action_lines.append(f"- [{label}]({href})")
            else:
                action_lines.append(f"- {label}")
            if description:
                action_lines.append(f"  {description}")
        parts.append("\n".join(action_lines))

    return "\n\n".join(parts).strip()


def _build_resource_generation_fallback(state: "ResourceGenerationState") -> dict[str, str]:
    goal = (state.get("learning_goal") or "Build a study plan").strip()
    level = (state.get("current_level") or "beginner").strip().lower()
    is_python = "python" in goal.lower()

    goal_analysis = (
        f"## Goal Analysis\nYour current goal is **{goal}**.\n\n"
        f"Based on your current level (`{level}`), you should first build solid fundamentals, then move into functions, data structures, and small projects."
    )

    if is_python:
        path_plan = """## Learning Path
### Stage 1: Basics (Week 1-2)
- Install Python and VS Code or PyCharm Community
- Learn variables, input/output, strings, numbers, booleans
- Learn `if / elif / else` and `for / while`
- Write one small exercise every day

### Stage 2: Functions and Data Structures (Week 3-4)
- Learn list, dict, tuple, set
- Learn function definition, parameters, return values
- Practice string handling and list traversal

### Stage 3: Files and Modules (Week 5-6)
- Learn file read/write and exceptions
- Learn module split and imports
- Build one simple CLI mini project

### Stage 4: Project Practice (Week 7-10)
- Build one complete project such as todo app, expense tracker, weather query, or data-cleaning script
- Start using Git to track your work
- Review weekly and summarize mistakes"""
        resources = """## Recommended Resources
- Liao Xuefeng Python tutorial
- Python official tutorial
- LeetCode easy problems
- Beginner video courses on Bilibili

## Practice Suggestions
- Start with IO, conditionals, and loops
- Then move to list, dict, and function exercises
- After every concept, finish 2-3 small drills"""
    else:
        path_plan = """## Learning Path
### Stage 1: Core Basics
- Environment setup
- Variables, data types, and input/output
- Conditions and loops

### Stage 2: Structured Programming
- Functions
- Common data structures
- File handling and exceptions

### Stage 3: Project Practice
- Finish one small project end-to-end
- Review and iterate every week"""
        resources = """## Recommended Resources
- Official documentation
- One complete beginner course
- One practice platform
- One project-based tutorial"""

    adjustments = """## Dynamic Adjustments
1. If the first two weeks feel difficult, extend the basics stage by one extra week.
2. If you can study two hours daily, enter project practice earlier.
3. If your goal is job readiness, start building project output early.
4. If you get stuck on one concept for more than 2-3 days, switch to a nearby topic and come back later."""

    page_tool = state.get("tool_context", {}).get("page-context-reader")
    if isinstance(page_tool, dict):
        current_video = page_tool.get("current_video")
        actions = page_tool.get("available_actions") if isinstance(page_tool.get("available_actions"), list) else []
        if isinstance(current_video, dict) and current_video.get("title"):
            video_title = str(current_video.get("title") or "").strip()
            video_summary = str(current_video.get("summary") or "").strip()
            action_lines: list[str] = []
            for action in actions[:4]:
                if not isinstance(action, dict):
                    continue
                label = str(action.get("label") or "").strip()
                href = str(action.get("href") or "").strip()
                if not label:
                    continue
                action_lines.append(f"- [{label}]({href})" if href else f"- {label}")

            path_plan += (
                f"\n\n### Extend From Current Video\n"
                f"- Current video: **{video_title}**\n"
                + (f"- Summary: {video_summary}\n" if video_summary else "")
                + "- Extract 3-5 key points from this video, then create practice around those key points."
            )
            if action_lines:
                resources += "\n\n## Continue From This Page\n" + "\n".join(action_lines)

    return {
        "goal_analysis": goal_analysis,
        "path_plan": path_plan,
        "generated_content": resources,
        "adjustments": adjustments,
    }

def _build_tutor_qa_fallback(state: "TutorQAState") -> dict[str, str]:
    question = (state.get("question_content") or "当前问题").strip()
    normalized = question.lower()

    if "for" in normalized and "while" in normalized:
        return {
            "intent": "基础语法对比答疑",
            "guidance": "先看循环次数是不是已知；已知通常优先用 for，不确定结束条件通常考虑 while。",
            "wrong_question_analysis": "这类题最容易混淆的是：什么时候该按“遍历集合”写，什么时候该按“条件控制”写。",
            "answer": (
                "## 核心区别\n"
                "- `for`：更适合**已知遍历对象或已知循环次数**的情况。\n"
                "- `while`：更适合**循环次数未知，只知道结束条件**的情况。\n\n"
                "## 直观理解\n"
                "- `for` 像是“把一个列表里的元素一个个取出来看”。\n"
                "- `while` 像是“只要条件还成立，就继续做”。\n\n"
                "## 例子\n"
                "```python\n"
                "for i in range(5):\n"
                "    print(i)\n"
                "```\n"
                "这段代码会固定执行 5 次。\n\n"
                "```python\n"
                "n = 5\n"
                "while n > 0:\n"
                "    print(n)\n"
                "    n -= 1\n"
                "```\n"
                "这段代码会一直执行到 `n` 不大于 0 为止。\n\n"
                "## 你做题时的判断方法\n"
                "1. 先问自己：是不是在遍历列表、字符串、`range`？如果是，优先考虑 `for`。\n"
                "2. 再问自己：是不是要根据某个条件不断重复？如果是，优先考虑 `while`。\n"
                "3. 最后检查 `while` 里是否会更新条件变量，否则容易死循环。\n"
            ),
        }

    if "报错" in question or "traceback" in normalized or "error" in normalized or "异常" in question:
        return {
            "intent": "报错定位答疑",
            "guidance": "先看最后一行报错类型，再回到报错行上方几行代码找原因。",
            "wrong_question_analysis": "很多人会直接盯着整段 Traceback，看得越多越乱。真正最关键的是最后一行错误类型和出错文件行号。",
            "answer": (
                "## 先这样排查\n"
                "1. 看报错最后一行，确认错误类型，比如 `TypeError`、`NameError`、`IndexError`。\n"
                "2. 找到报错对应的文件和行号。\n"
                "3. 回到那一行上面 3-5 行，看变量值、数据类型、索引范围是否合理。\n\n"
                "## 常见定位思路\n"
                "- `NameError`：变量名没定义，或拼错了。\n"
                "- `TypeError`：数据类型不对，比如把字符串当数字算。\n"
                "- `IndexError`：列表下标越界。\n"
                "- `KeyError`：字典里没有这个键。\n\n"
                "把报错原文和相关代码贴给我，我可以直接帮你定位到具体哪一行、为什么错、怎么改。"
            ),
        }

    if "函数" in question or "def " in normalized or "return" in normalized:
        return {
            "intent": "函数概念答疑",
            "guidance": "先分清楚函数的三个部分：输入参数、处理逻辑、返回结果。",
            "wrong_question_analysis": "初学者最容易混淆的是：什么时候该 `print`，什么时候该 `return`。",
            "answer": (
                "## 函数可以怎么理解\n"
                "函数就是把一段可重复使用的代码封装起来。\n\n"
                "```python\n"
                "def add(a, b):\n"
                "    return a + b\n"
                "```\n\n"
                "这里：\n"
                "- `a, b` 是输入参数\n"
                "- `a + b` 是处理逻辑\n"
                "- `return` 是把结果交回去\n\n"
                "## `print` 和 `return` 的区别\n"
                "- `print`：只是把结果显示出来\n"
                "- `return`：把结果真正返回给调用者，后续还能继续使用\n\n"
                "如果你愿意，我可以继续拿你的一段函数代码，逐行给你讲。"
            ),
        }

    return {
        "intent": "学习答疑",
        "guidance": "先确认题目考什么，再拆成输入、处理过程、输出三个部分去理解。",
        "wrong_question_analysis": "如果你愿意贴代码或报错，我可以继续定位你具体卡住的步骤。",
        "answer": (
            f"你现在的问题是：**{question}**。\n\n"
            "我建议你先把题目拆成三步：\n"
            "1. 输入是什么\n"
            "2. 需要处理什么逻辑\n"
            "3. 最终输出什么结果\n\n"
            "如果你把题目原文、代码或报错发出来，我可以继续按“思路 -> 代码 -> 易错点”给你讲。"
        ),
    }


def _build_study_plan_fallback(state: "StudyPlanState") -> dict[str, str]:
    evaluation_type = state.get("evaluation_type") or "学习评测"
    return {
        "grading": "当前缺少可量化评分输入，暂时无法给出精确分数。",
        "mastery": "从现有上下文看，建议先巩固基础知识点，再进入更复杂练习。",
        "report": (
            f"### {evaluation_type}报告\n"
            "- 当前阶段更适合先夯实基础\n"
            "- 建议通过 3-5 道同类型练习验证是否真正掌握\n"
            "- 下一步优先补足薄弱点，再进入进阶内容"
        ),
    }


def _build_learning_evaluation_fallback(state: "LearningEvaluationState") -> dict[str, str]:
    return {
        "diagnosis": "当前学习数据不足或上游模型响应不稳定，暂时无法做精细化诊断。",
        "learner_portrait": "现阶段更像是处于基础构建期，需要通过稳定练习逐步形成能力画像。",
        "optimization": "建议固定学习节奏、增加练习反馈、每周做一次复盘。",
        "report_content": (
            "### 学习评估总结\n"
            "- 当前数据不足，建议先连续积累 1-2 周学习记录\n"
            "- 后续可结合练习成绩、课程进度、错题情况做更准确评估"
        ),
    }


class UserInteractionState(TypedDict):
    user_id: int
    session_id: int | None
    scene_code: str
    messages: list[Any]
    context: dict[str, Any]
    account_snapshot: dict[str, Any]
    intent: dict[str, Any]
    routing_plan: dict[str, Any]
    selected_skills: list[str]
    tool_plan: dict[str, list[str]]
    resource_actions: list[dict[str, Any]]
    delegated_results: dict[str, Any]
    delegate_runner: Any
    response: str
    status: str


class UserInteractionAgent:
    """01 用户交互智能体。"""

    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(UserInteractionState)
        graph.add_node("analyze_intent", self._analyze_intent)
        graph.add_node("route_skills", self._route_skills)
        graph.add_node("manage_resource_actions", self._manage_resource_actions)
        graph.add_node("invoke_delegates", self._invoke_delegates)
        graph.add_node("generate_response", self._generate_response)
        graph.set_entry_point("analyze_intent")
        graph.add_edge("analyze_intent", "route_skills")
        graph.add_edge("route_skills", "manage_resource_actions")
        graph.add_edge("manage_resource_actions", "invoke_delegates")
        graph.add_edge("invoke_delegates", "generate_response")
        graph.add_edge("generate_response", "__end__")
        return graph.compile()

    @staticmethod
    def _latest_user_text(state: UserInteractionState) -> str:
        for message in reversed(state["messages"]):
            if _message_role(message) in {"human", "user"}:
                return _message_content(message)
        return ""

    async def _analyze_intent(self, state: UserInteractionState) -> UserInteractionState:
        latest_user_text = self._latest_user_text(state)
        if _is_agent_catalog_question(latest_user_text):
            state["intent"] = {
                "intent": "介绍当前智能体能力",
                "goal": "说明 AI 助手能做什么",
                "agent_catalog_question": True,
                "requires_business_agent": False,
                "resource_actions": [],
            }
            state["status"] = "intent_analyzed"
            return state

        prompt = f"""
你是 LingLearn 的用户交互智能体。你的任务只是理解用户本轮意图，不直接回答问题。

账号数据：{state['account_snapshot']}
附加上下文：{state['context']}
最近对话：
{_message_text(state['messages'])}

请严格输出 JSON：
{{
  "intent": "一句话描述用户当前诉求",
  "goal": "用户最终目标",
  "preferred_output": "例如 学习路线 / 资源建议 / 讲题答疑 / 学习报告 / 学情评估",
  "requires_business_agent": true,
  "resource_actions": [],
  "notes": "对路由有帮助的说明"
}}
"""
        try:
            raw = await _ask(self.llm, USER_INTERACTION_SKILL.system_prompt, prompt)
            parsed = _extract_json_object(raw)
        except Exception as exc:
            parsed = {
                "intent": latest_user_text or "用户需要学习帮助",
                "goal": latest_user_text or "需要帮助",
                "preferred_output": "待判定",
                "requires_business_agent": True,
                "resource_actions": [],
                "notes": f"intent-analysis-failed: {exc}",
                "fallback": True,
            }

        state["intent"] = parsed or {
            "intent": latest_user_text or "用户需要学习帮助",
            "goal": latest_user_text or "需要帮助",
            "preferred_output": "待判定",
            "requires_business_agent": True,
            "resource_actions": [],
            "notes": "Intent parser returned invalid JSON.",
            "fallback": True,
        }
        state["status"] = "intent_analyzed"
        return state

    async def _route_skills(self, state: UserInteractionState) -> UserInteractionState:
        if state["intent"].get("agent_catalog_question"):
            state["routing_plan"] = {}
            state["selected_skills"] = []
            state["tool_plan"] = {}
            state["status"] = "skills_routed"
            return state

        latest_user_text = self._latest_user_text(state)
        page_context = _page_context(state)
        if _page_context_prefers_video_content(latest_user_text, page_context):
            selected_skills = [VIDEO_CONTENT_SKILL.code]
            state["routing_plan"] = {
                "raw": None,
                "route_reason": "Page-aware route selected video content understanding based on the current video and requested artifact.",
            }
            state["selected_skills"] = selected_skills
            state["tool_plan"] = _sanitize_tool_plan({}, selected_skills)
            state["status"] = "skills_routed"
            return state
        if _page_context_prefers_resource_generation(latest_user_text, page_context):
            selected_skills = [RESOURCE_GENERATION_SKILL.code]
            state["routing_plan"] = {
                "raw": None,
                "route_reason": "Page-aware route selected resource generation based on the current video and requested actions.",
            }
            state["selected_skills"] = selected_skills
            state["tool_plan"] = _sanitize_tool_plan({}, selected_skills)
            state["status"] = "skills_routed"
            return state

        forced_skills = _fallback_skill_codes(latest_user_text)
        if forced_skills and forced_skills[0] != TUTOR_QA_SKILL.code:
            state["routing_plan"] = {
                "raw": None,
                "route_reason": "High-confidence rule-based route was used.",
            }
            state["selected_skills"] = forced_skills
            state["tool_plan"] = _sanitize_tool_plan({}, forced_skills)
            state["status"] = "skills_routed"
            return state

        prompt = f"""
你是 LingLearn 的用户交互智能体，现在只负责把用户意图路由到业务智能体。

AI 助手当前只集成以下业务智能体：
{build_chat_router_skill_catalog()}

规则：
1. 优先选择最直接能解决问题的 1 个主智能体。
2. 必要时再补充 1 个辅助智能体。
3. 不要选择特征抽取智能体。

用户意图：{state['intent']}
账号数据：{state['account_snapshot']}
最新用户消息：{latest_user_text}

请严格输出 JSON：
{{
  "selected_skills": ["resource_generation"],
  "tool_plan": {{
    "resource_generation": ["learning-goal-analyzer", "resource-candidate-reader"]
  }},
  "route_reason": "为什么这样路由"
}}
"""
        try:
            raw = await _ask(self.llm, USER_INTERACTION_SKILL.system_prompt, prompt)
            parsed = _extract_json_object(raw)
        except Exception as exc:
            parsed = {
                "selected_skills": _fallback_skill_codes(latest_user_text),
                "tool_plan": {},
                "route_reason": f"Routing failed, fallback used: {exc}",
            }

        selected_skills = _sanitize_skill_codes((parsed or {}).get("selected_skills", []))
        if not selected_skills:
            selected_skills = _fallback_skill_codes(latest_user_text)

        state["routing_plan"] = {
            "raw": parsed,
            "route_reason": (parsed or {}).get("route_reason") or "Fallback route was used.",
        }
        state["selected_skills"] = selected_skills
        state["tool_plan"] = _sanitize_tool_plan((parsed or {}).get("tool_plan"), selected_skills)
        state["status"] = "skills_routed"
        return state

    async def _manage_resource_actions(self, state: UserInteractionState) -> UserInteractionState:
        actions: list[dict[str, Any]] = []
        for action in state["intent"].get("resource_actions", []) or []:
            if action == "favorite_resource":
                actions.append({"action": "favorite_resource", "status": "pending"})
        state["resource_actions"] = actions
        state["status"] = "resource_actions_prepared"
        return state

    async def _invoke_delegates(self, state: UserInteractionState) -> UserInteractionState:
        delegated_results: dict[str, Any] = {}
        delegate_runner = state.get("delegate_runner")
        if not callable(delegate_runner):
            state["delegated_results"] = delegated_results
            state["status"] = "delegates_skipped"
            return state

        tasks = {
            skill_code: asyncio.create_task(delegate_runner(skill_code, state))
            for skill_code in state.get("selected_skills", [])
        }
        for skill_code, task in tasks.items():
            try:
                result = await task
            except Exception as exc:
                delegated_results[skill_code] = {"error": str(exc)}
                continue
            if result is not None:
                delegated_results[skill_code] = result

        state["delegated_results"] = delegated_results
        state["status"] = "delegates_completed"
        return state

    async def _generate_response(self, state: UserInteractionState) -> UserInteractionState:
        latest_user_text = self._latest_user_text(state)
        if state["intent"].get("agent_catalog_question") or _is_agent_catalog_question(latest_user_text):
            state["response"] = AGENT_CATALOG_MARKDOWN
            state["status"] = "completed"
            return state

        delegated_results = state.get("delegated_results") or {}
        ordered_parts: list[str] = []
        for skill_code in state.get("selected_skills", []):
            result = delegated_results.get(skill_code)
            if not isinstance(result, dict):
                continue
            text = _render_skill_result(skill_code, result)
            if text:
                ordered_parts.append(text)

        if ordered_parts:
            state["response"] = "\n\n".join(ordered_parts[:2])
        else:
            state["response"] = (
                f"我已经收到你的问题：**{latest_user_text or '当前学习问题'}**。\n\n"
                "当前业务智能体没有稳定返回结果，但交互智能体已经完成意图识别。"
                "你可以继续补充更具体的目标、题目、报错或课程方向，我会继续处理。"
            )
        page_awareness = _render_page_awareness(state)
        if page_awareness:
            state["response"] = f"{state['response'].strip()}\n\n{page_awareness}".strip()
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
    tool_context: dict[str, Any]
    dialogue_analysis: dict[str, Any]
    six_dimension_profile: dict[str, Any]
    quality_report: dict[str, Any]
    status: str


class FeatureExtractionAgent:
    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(FeatureExtractionState)
        graph.add_node("extract", self._extract)
        graph.set_entry_point("extract")
        graph.add_edge("extract", "__end__")
        return graph.compile()

    async def _extract(self, state: FeatureExtractionState) -> FeatureExtractionState:
        prompt = f"""
你是特征抽取智能体。请基于以下输入生成学习特征分析与六维态画像。

来源：{state['source_type']}#{state['source_ref_id']}
对话：{_message_text(state['conversations'])}
评测数据：{state['assessment_data']}
工具上下文：{state['tool_context']}

请严格输出 JSON：
{{
  "dialogue_analysis": "对话内容分析",
  "six_dimension_profile": "六维态画像",
  "quality_report": "图像或输入质量校验结论"
}}
"""
        raw = await _ask(self.llm, FEATURE_EXTRACTION_SKILL.system_prompt, prompt)
        parsed = _extract_json_object(raw) or {}
        state["dialogue_analysis"] = {"raw": parsed.get("dialogue_analysis") or raw}
        state["six_dimension_profile"] = {
            "raw": parsed.get("six_dimension_profile") or raw,
            "dimensions": ["knowledge", "logic", "expression", "habit", "motivation", "reflection"],
        }
        state["quality_report"] = {"raw": parsed.get("quality_report") or "No explicit quality report returned."}
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
    tool_context: dict[str, Any]
    goal_analysis: dict[str, Any]
    path_plan: dict[str, Any]
    generated_content: dict[str, Any]
    adjustments: dict[str, Any]
    quality_score: float
    status: str


class ResourceGenerationAgent:
    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(ResourceGenerationState)
        graph.add_node("generate", self._generate)
        graph.set_entry_point("generate")
        graph.add_edge("generate", "__end__")
        return graph.compile()

    async def _generate(self, state: ResourceGenerationState) -> ResourceGenerationState:
        prompt = f"""
你是资源生成智能体。请围绕“学习目标分析、路径智能规划、动态调整优化”直接给出可执行结果。

学习目标：{state['learning_goal']}
当前水平：{state['current_level']}
学习历史：{state['learning_history']}
画像：{state['profile']}
工具上下文：{state['tool_context']}

请严格输出 JSON：
{{
  "goal_analysis": "对目标的分析",
  "path_plan": "一份结构化学习路径，尽量用 Markdown",
  "generated_content": "课程、练习、复盘等资源建议",
  "adjustments": "动态调整优化建议"
}}
"""
        try:
            raw = await _ask(self.llm, RESOURCE_GENERATION_SKILL.system_prompt, prompt)
            parsed = _extract_json_object(raw) or {}
        except Exception:
            raw = ""
            parsed = {}

        fallback = _build_resource_generation_fallback(state)
        goal_analysis = str(parsed.get("goal_analysis") or fallback["goal_analysis"])
        path_plan = str(parsed.get("path_plan") or raw or fallback["path_plan"])
        generated_content = str(parsed.get("generated_content") or fallback["generated_content"])
        adjustments = str(parsed.get("adjustments") or fallback["adjustments"])
        state["goal_analysis"] = {"raw": goal_analysis}
        state["path_plan"] = {"raw": path_plan}
        state["generated_content"] = {"content": generated_content}
        state["adjustments"] = {"raw": adjustments}
        state["quality_score"] = min(1.0, max(0.55, len(path_plan) / 1200))
        state["status"] = "completed"
        return state

    async def run(self, state: ResourceGenerationState) -> ResourceGenerationState:
        return await self.graph.ainvoke(state)


class StudyPlanState(TypedDict):
    user_id: int
    evaluation_type: str
    data: dict[str, Any]
    tool_context: dict[str, Any]
    grading: dict[str, Any]
    mastery: dict[str, Any]
    report: dict[str, Any]
    status: str


class StudyPlanAgent:
    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(StudyPlanState)
        graph.add_node("evaluate", self._evaluate)
        graph.set_entry_point("evaluate")
        graph.add_edge("evaluate", "__end__")
        return graph.compile()

    async def _evaluate(self, state: StudyPlanState) -> StudyPlanState:
        prompt = f"""
你是学习评测智能体。请围绕“自动批改评分、掌握度判定、学习报告生成”直接给出结果。

评测类型：{state['evaluation_type']}
输入数据：{state['data']}
工具上下文：{state['tool_context']}

请严格输出 JSON：
{{
  "grading": "评分结论",
  "mastery": "掌握度判断",
  "report": "学习报告，尽量用 Markdown"
}}
"""
        try:
            raw = await _ask(self.llm, STUDY_PLAN_SKILL.system_prompt, prompt)
            parsed = _extract_json_object(raw) or {}
        except Exception:
            raw = ""
            parsed = {}

        fallback = _build_study_plan_fallback(state)
        grading = str(parsed.get("grading") or fallback["grading"])
        mastery = str(parsed.get("mastery") or fallback["mastery"])
        report = str(parsed.get("report") or raw or fallback["report"])
        state["grading"] = {"raw": grading}
        state["mastery"] = {"raw": mastery}
        state["report"] = {
            "summary": report,
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
    tool_context: dict[str, Any]
    intent: dict[str, Any]
    guidance: str
    wrong_question_analysis: dict[str, Any]
    answer: str
    status: str


class TutorQAAgent:
    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(TutorQAState)
        graph.add_node("answer_question", self._answer)
        graph.set_entry_point("answer_question")
        graph.add_edge("answer_question", "__end__")
        return graph.compile()

    async def _answer(self, state: TutorQAState) -> TutorQAState:
        prompt = f"""
你是智能答疑智能体。请围绕“多轮对话答疑、思维引导辅导、错题讲题分析”直接完成本轮回答。

问题：{state['question_content']}
历史对话：{_message_text(state['conversation_history'])}
学生答案：{state.get('user_answer')}
正确答案：{state.get('correct_answer')}
工具上下文：{state['tool_context']}

请严格输出 JSON：
{{
  "intent": "本题属于什么问题",
  "guidance": "思维引导内容",
  "wrong_question_analysis": "若存在错题则输出错题分析，否则写无",
  "answer": "最终完整答疑回复，尽量用 Markdown"
}}
"""
        try:
            raw = await _ask(self.llm, TUTOR_QA_SKILL.system_prompt, prompt)
            parsed = _extract_json_object(raw) or {}
        except Exception:
            raw = ""
            parsed = {}

        fallback = _build_tutor_qa_fallback(state)
        state["intent"] = {"raw": parsed.get("intent") or fallback["intent"]}
        state["guidance"] = str(parsed.get("guidance") or fallback["guidance"])
        state["wrong_question_analysis"] = {
            "raw": parsed.get("wrong_question_analysis") or fallback["wrong_question_analysis"]
        }
        state["answer"] = str(parsed.get("answer") or raw or fallback["answer"])
        state["status"] = "completed"
        return state

    async def run(self, state: TutorQAState) -> TutorQAState:
        return await self.graph.ainvoke(state)


class LearningEvaluationState(TypedDict):
    user_id: int
    month: str | None
    learning_data: dict[str, Any]
    path_progress: dict[str, Any]
    tool_context: dict[str, Any]
    diagnosis: dict[str, Any]
    learner_portrait: dict[str, Any]
    optimization: dict[str, Any]
    report_content: dict[str, Any]
    recommendations: list[dict[str, Any]]
    status: str


class LearningEvaluationAgent:
    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(LearningEvaluationState)
        graph.add_node("evaluate", self._evaluate)
        graph.set_entry_point("evaluate")
        graph.add_edge("evaluate", "__end__")
        return graph.compile()

    async def _evaluate(self, state: LearningEvaluationState) -> LearningEvaluationState:
        prompt = f"""
你是学习评估智能体。请围绕“学习效果诊断、学情画像生成、迭代优化建议”直接给出结果。

月份：{state.get('month')}
学习数据：{state['learning_data']}
路径进度：{state['path_progress']}
工具上下文：{state['tool_context']}

请严格输出 JSON：
{{
  "diagnosis": "学习效果诊断",
  "learner_portrait": "学情画像",
  "optimization": "迭代优化建议",
  "report_content": "完整阶段总结，尽量用 Markdown"
}}
"""
        try:
            raw = await _ask(self.llm, LEARNING_EVALUATION_SKILL.system_prompt, prompt)
            parsed = _extract_json_object(raw) or {}
        except Exception:
            raw = ""
            parsed = {}

        fallback = _build_learning_evaluation_fallback(state)
        diagnosis = str(parsed.get("diagnosis") or fallback["diagnosis"])
        learner_portrait = str(parsed.get("learner_portrait") or fallback["learner_portrait"])
        optimization = str(parsed.get("optimization") or fallback["optimization"])
        report_content = str(parsed.get("report_content") or raw or fallback["report_content"])
        state["diagnosis"] = {"raw": diagnosis}
        state["learner_portrait"] = {"raw": learner_portrait}
        state["optimization"] = {"raw": optimization}
        state["report_content"] = {"overview": report_content, "detailed_report": report_content}
        state["recommendations"] = [
            {"type": "optimization", "title": "下一轮优化建议", "description": optimization or "见报告内容"}
        ]
        state["status"] = "completed"
        return state

    async def run(self, state: LearningEvaluationState) -> LearningEvaluationState:
        return await self.graph.ainvoke(state)
