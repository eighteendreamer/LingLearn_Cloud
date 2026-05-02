from __future__ import annotations

from dataclasses import dataclass

from app.infra.ai.agent_tools import default_tool_keys_for_skill, render_tool_catalog_for_skill


@dataclass(frozen=True)
class AgentSkill:
    code: str
    name: str
    summary: str
    description: str
    responsibilities: tuple[str, ...]
    supported_tools: tuple[str, ...]
    system_prompt: str
    chat_enabled: bool
    standalone_enabled: bool = True


USER_INTERACTION_SKILL = AgentSkill(
    code="user_interaction",
    name="用户交互智能体",
    summary="负责多轮对话交互、流式输出组织和资源收藏管理。",
    description="作为 AI 助手统一入口，负责理解用户意图、选择合适的业务智能体、整合最终回复，并处理会话级动作。",
    responsibilities=("多轮对话交互", "流式输出展示", "资源收藏管理"),
    supported_tools=tuple(default_tool_keys_for_skill("user_interaction")),
    system_prompt=(
        "你是 LingLearn 的用户交互智能体。"
        "你的职责是理解用户意图，决定是否需要调用其它业务智能体，"
        "并把业务结果整合成自然、专业、可执行的最终回复。"
    ),
    chat_enabled=True,
)

FEATURE_EXTRACTION_SKILL = AgentSkill(
    code="feature_extraction",
    name="特征抽取智能体",
    summary="负责对话内容分析、六维态内容生成和图像质量校验。",
    description="为画像、评测和内容分析场景服务，提取学习特征与证据，不直接作为 AI 聊天助手的默认集成智能体。",
    responsibilities=("对话内容分析", "六维态内容生成", "图像质量校验"),
    supported_tools=tuple(default_tool_keys_for_skill("feature_extraction")),
    system_prompt=(
        "你是 LingLearn 的特征抽取智能体。"
        "请从对话、练习、评测和图片输入中提取可解释、可追踪的学习特征，"
        "并生成清晰的画像结论。"
    ),
    chat_enabled=False,
)

RESOURCE_GENERATION_SKILL = AgentSkill(
    code="resource_generation",
    name="资源生成智能体",
    summary="负责学习目标分析、路径智能规划和动态调整优化。",
    description="围绕学习目标、当前水平和历史学习数据，生成资源推荐、学习路径和动态优化建议。",
    responsibilities=("学习目标分析", "路径智能规划", "动态调整优化"),
    supported_tools=tuple(default_tool_keys_for_skill("resource_generation")),
    system_prompt=(
        "你是 LingLearn 的资源生成智能体。"
        "请结合用户目标、当前能力和历史学习数据，输出务实的资源建议和学习路径。"
    ),
    chat_enabled=True,
)

STUDY_PLAN_SKILL = AgentSkill(
    code="study_plan",
    name="学习评测智能体",
    summary="负责自动批改评分、掌握度判定和学习报告生成。",
    description="围绕练习、测验、作业和阶段任务输出评测结论，并形成学习报告。",
    responsibilities=("自动批改评分", "掌握度判定", "学习报告生成"),
    supported_tools=tuple(default_tool_keys_for_skill("study_plan")),
    system_prompt=(
        "你是 LingLearn 的学习评测智能体。"
        "请根据练习、测验和阶段任务数据，完成评测、掌握度判断和学习报告输出。"
    ),
    chat_enabled=True,
)

TUTOR_QA_SKILL = AgentSkill(
    code="tutor_qa",
    name="智能答疑智能体",
    summary="负责多轮对话答疑、思维引导辅导和错题讲题分析。",
    description="用于概念讲解、代码辅导、题目思路引导和错题讲解。",
    responsibilities=("多轮对话答疑", "思维引导辅导", "错题讲题分析"),
    supported_tools=tuple(default_tool_keys_for_skill("tutor_qa")),
    system_prompt=(
        "你是 LingLearn 的智能答疑智能体。"
        "请优先通过启发式讲解、逐步引导和贴近用户水平的示例帮助用户理解问题。"
    ),
    chat_enabled=True,
)

LEARNING_EVALUATION_SKILL = AgentSkill(
    code="learning_evaluation",
    name="学习评估智能体",
    summary="负责学习效果诊断、学情画像生成和迭代优化建议。",
    description="用于阶段总结、月报诊断、进步分析和后续优化建议输出。",
    responsibilities=("学习效果诊断", "学情画像生成", "迭代优化建议"),
    supported_tools=tuple(default_tool_keys_for_skill("learning_evaluation")),
    system_prompt=(
        "你是 LingLearn 的学习评估智能体。"
        "请基于账号学习数据进行效果诊断、画像总结，并提出下一轮优化建议。"
    ),
    chat_enabled=True,
)

VIDEO_CONTENT_SKILL = AgentSkill(
    code="video_content",
    name="视频内容理解智能体",
    summary="负责提取视频画面与讲解语音，并按用户目标生成题库、总结、报告等内容。",
    description="围绕当前视频完成抽帧理解、语音内容提取、知识点整理，以及下游学习产物生成。",
    responsibilities=("视频画面理解", "讲解语音提取", "题库/总结/报告生成"),
    supported_tools=tuple(default_tool_keys_for_skill("video_content")),
    system_prompt=(
        "你是 LingLearn 的视频内容理解智能体。"
        "你的职责是读取视频的画面信息和讲解语音，并根据用户需求生成高质量学习内容。"
    ),
    chat_enabled=True,
)


AGENT_ORDER = (
    USER_INTERACTION_SKILL.code,
    FEATURE_EXTRACTION_SKILL.code,
    VIDEO_CONTENT_SKILL.code,
    RESOURCE_GENERATION_SKILL.code,
    STUDY_PLAN_SKILL.code,
    TUTOR_QA_SKILL.code,
    LEARNING_EVALUATION_SKILL.code,
)

AGENT_SKILLS: dict[str, AgentSkill] = {
    USER_INTERACTION_SKILL.code: USER_INTERACTION_SKILL,
    FEATURE_EXTRACTION_SKILL.code: FEATURE_EXTRACTION_SKILL,
    VIDEO_CONTENT_SKILL.code: VIDEO_CONTENT_SKILL,
    RESOURCE_GENERATION_SKILL.code: RESOURCE_GENERATION_SKILL,
    STUDY_PLAN_SKILL.code: STUDY_PLAN_SKILL,
    TUTOR_QA_SKILL.code: TUTOR_QA_SKILL,
    LEARNING_EVALUATION_SKILL.code: LEARNING_EVALUATION_SKILL,
}

CHAT_ASSISTANT_SKILL_CODES = (
    VIDEO_CONTENT_SKILL.code,
    RESOURCE_GENERATION_SKILL.code,
    STUDY_PLAN_SKILL.code,
    TUTOR_QA_SKILL.code,
    LEARNING_EVALUATION_SKILL.code,
)

AGENT_CATALOG_MARKDOWN = "\n".join(
    [
        "LingLearn 当前统一管理六个 LangGraph 智能体：",
        "",
        "1. 用户交互智能体：多轮对话交互、流式输出展示、资源收藏管理。",
        "2. 特征抽取智能体：对话内容分析、六维态内容生成、图像质量校验。",
        "3. 资源生成智能体：学习目标分析、路径智能规划、动态调整优化。",
        "4. 学习评测智能体：自动批改评分、掌握度判定、学习报告生成。",
        "5. 智能答疑智能体：多轮对话答疑、思维引导辅导、错题讲题分析。",
        "6. 学习评估智能体：学习效果诊断、学情画像生成、迭代优化建议。",
        "",
        "AI 会话助手当前集成：用户交互智能体、资源生成智能体、学习评测智能体、智能答疑智能体、学习评估智能体。",
        "特征抽取智能体保留为统一管理的独立业务智能体，由画像、评测等场景单独调用。",
    ]
)

AGENT_CATALOG_INSTRUCTION = (
    "当用户询问有哪些智能体、这些智能体做什么、AI 助手接入了哪些能力时，"
    "必须明确说明：AI 会话助手只集成用户交互、资源生成、学习评测、智能答疑、学习评估五类智能体；"
    "特征抽取智能体是统一管理但不直接挂入默认会话助手的独立能力。"
)


def get_skill(code: str) -> AgentSkill:
    return AGENT_SKILLS[code]


def list_skills() -> list[AgentSkill]:
    return [AGENT_SKILLS[code] for code in AGENT_ORDER]


def list_chat_skills() -> list[AgentSkill]:
    return [AGENT_SKILLS[code] for code in CHAT_ASSISTANT_SKILL_CODES]


def render_skill_list(skill_codes: list[str]) -> str:
    if not skill_codes:
        return "- No delegated business agent"
    return "\n".join(
        f"- {AGENT_SKILLS[code].name}: {AGENT_SKILLS[code].summary}"
        for code in skill_codes
        if code in AGENT_SKILLS
    )


def build_chat_router_skill_catalog() -> str:
    blocks: list[str] = []
    for code in CHAT_ASSISTANT_SKILL_CODES:
        skill = AGENT_SKILLS[code]
        blocks.append(
            "\n".join(
                [
                    f"[{skill.code}] {skill.name}",
                    f"职责：{skill.description}",
                    "可用工具：",
                    render_tool_catalog_for_skill(skill.code),
                ]
            )
        )
    return "\n\n".join(blocks)
