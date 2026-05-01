from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentTool:
    key: str
    name: str
    description: str
    category: str


AGENT_TOOLS: dict[str, AgentTool] = {
    "workflow-router": AgentTool(
        key="workflow-router",
        name="Workflow Router",
        description="Decide which business agent should handle the current turn.",
        category="orchestration",
    ),
    "learning-context-reader": AgentTool(
        key="learning-context-reader",
        name="Learning Context Reader",
        description="Read profile, learning goal, preferences, and general account learning context.",
        category="context",
    ),
    "session-memory-reader": AgentTool(
        key="session-memory-reader",
        name="Session Memory Reader",
        description="Read recent chat history for multi-turn continuity.",
        category="context",
    ),
    "page-context-reader": AgentTool(
        key="page-context-reader",
        name="Page Context Reader",
        description="Read the current frontend route, page object, current content, and page metadata.",
        category="context",
    ),
    "page-action-planner": AgentTool(
        key="page-action-planner",
        name="Page Action Planner",
        description="Turn current page context into actionable next-step suggestions and jump targets.",
        category="orchestration",
    ),
    "favorite-resource-manager": AgentTool(
        key="favorite-resource-manager",
        name="Favorite Resource Manager",
        description="Recognize and manage favorite-resource actions in the current conversation.",
        category="action",
    ),
    "dialogue-evidence-reader": AgentTool(
        key="dialogue-evidence-reader",
        name="Dialogue Evidence Reader",
        description="Extract evidence snippets from dialogue for profile or feature analysis.",
        category="evidence",
    ),
    "six-dimension-profile-generator": AgentTool(
        key="six-dimension-profile-generator",
        name="Six Dimension Profile Generator",
        description="Organize six-dimension learner-profile signals for analysis.",
        category="analysis",
    ),
    "image-quality-validator": AgentTool(
        key="image-quality-validator",
        name="Image Quality Validator",
        description="Check whether image input is usable for OCR or content analysis.",
        category="validation",
    ),
    "assessment-snapshot-reader": AgentTool(
        key="assessment-snapshot-reader",
        name="Assessment Snapshot Reader",
        description="Read recent assessment snapshots for scoring and mastery judgment.",
        category="data",
    ),
    "course-progress-reader": AgentTool(
        key="course-progress-reader",
        name="Course Progress Reader",
        description="Read recent course progress, completion, and topic information.",
        category="data",
    ),
    "practice-history-reader": AgentTool(
        key="practice-history-reader",
        name="Practice History Reader",
        description="Read recent practice sessions, scores, and completion status.",
        category="data",
    ),
    "learning-path-reader": AgentTool(
        key="learning-path-reader",
        name="Learning Path Reader",
        description="Read the active learning path, nodes, and overall progress.",
        category="data",
    ),
    "resource-candidate-reader": AgentTool(
        key="resource-candidate-reader",
        name="Resource Candidate Reader",
        description="Organize candidate resources based on recent history and goals.",
        category="generation",
    ),
    "learning-goal-analyzer": AgentTool(
        key="learning-goal-analyzer",
        name="Learning Goal Analyzer",
        description="Break down the user's learning goal into staged objectives and prerequisites.",
        category="analysis",
    ),
    "mastery-scorer": AgentTool(
        key="mastery-scorer",
        name="Mastery Scorer",
        description="Estimate mastery level from practice and assessment signals.",
        category="analysis",
    ),
    "study-report-writer": AgentTool(
        key="study-report-writer",
        name="Study Report Writer",
        description="Prepare a structured basis for learning reports.",
        category="generation",
    ),
    "question-intent-parser": AgentTool(
        key="question-intent-parser",
        name="Question Intent Parser",
        description="Classify whether a question is concept explanation, debugging, path planning, or problem solving.",
        category="analysis",
    ),
    "socratic-hint-builder": AgentTool(
        key="socratic-hint-builder",
        name="Socratic Hint Builder",
        description="Produce step-by-step hints and guiding questions.",
        category="generation",
    ),
    "wrong-question-reader": AgentTool(
        key="wrong-question-reader",
        name="Wrong Question Reader",
        description="Read wrong-answer context, user answer, and correct answer information.",
        category="evidence",
    ),
    "concept-example-builder": AgentTool(
        key="concept-example-builder",
        name="Concept Example Builder",
        description="Prepare examples that make abstract concepts easier to understand.",
        category="generation",
    ),
    "assessment-trend-reader": AgentTool(
        key="assessment-trend-reader",
        name="Assessment Trend Reader",
        description="Read trend signals across recent assessments.",
        category="data",
    ),
    "monthly-report-reader": AgentTool(
        key="monthly-report-reader",
        name="Monthly Report Reader",
        description="Read the latest monthly report summary and improvement areas.",
        category="data",
    ),
    "learner-portrait-writer": AgentTool(
        key="learner-portrait-writer",
        name="Learner Portrait Writer",
        description="Organize learner portrait and staged diagnosis output.",
        category="generation",
    ),
    "optimization-suggester": AgentTool(
        key="optimization-suggester",
        name="Optimization Suggester",
        description="Generate the next round of optimization advice from progress and assessment signals.",
        category="analysis",
    ),
    "response-style-planner": AgentTool(
        key="response-style-planner",
        name="Response Style Planner",
        description="Choose the final response structure, tone, and level of detail.",
        category="orchestration",
    ),
}


SKILL_TOOL_MAPPING: dict[str, tuple[str, ...]] = {
    "user_interaction": (
        "workflow-router",
        "learning-context-reader",
        "session-memory-reader",
        "page-context-reader",
        "page-action-planner",
        "favorite-resource-manager",
        "response-style-planner",
    ),
    "feature_extraction": (
        "dialogue-evidence-reader",
        "six-dimension-profile-generator",
        "assessment-snapshot-reader",
        "image-quality-validator",
    ),
    "resource_generation": (
        "learning-goal-analyzer",
        "learning-context-reader",
        "page-context-reader",
        "course-progress-reader",
        "practice-history-reader",
        "resource-candidate-reader",
        "learning-path-reader",
    ),
    "study_plan": (
        "assessment-snapshot-reader",
        "practice-history-reader",
        "page-context-reader",
        "learning-path-reader",
        "mastery-scorer",
        "study-report-writer",
    ),
    "tutor_qa": (
        "question-intent-parser",
        "session-memory-reader",
        "page-context-reader",
        "wrong-question-reader",
        "socratic-hint-builder",
        "concept-example-builder",
    ),
    "learning_evaluation": (
        "assessment-trend-reader",
        "monthly-report-reader",
        "page-context-reader",
        "learning-path-reader",
        "learner-portrait-writer",
        "optimization-suggester",
    ),
}


def get_tool(key: str) -> AgentTool:
    return AGENT_TOOLS[key]


def list_tools() -> list[AgentTool]:
    return list(AGENT_TOOLS.values())


def list_tools_for_skill(skill_code: str) -> list[AgentTool]:
    keys = SKILL_TOOL_MAPPING.get(skill_code, ())
    return [AGENT_TOOLS[key] for key in keys if key in AGENT_TOOLS]


def default_tool_keys_for_skill(skill_code: str) -> list[str]:
    return list(SKILL_TOOL_MAPPING.get(skill_code, ()))


def render_tool_list(tool_keys: list[str]) -> str:
    if not tool_keys:
        return "- No tools"
    return "\n".join(
        f"- {AGENT_TOOLS[key].name}: {AGENT_TOOLS[key].description}"
        for key in tool_keys
        if key in AGENT_TOOLS
    )


def render_tool_catalog_for_skill(skill_code: str) -> str:
    return render_tool_list(default_tool_keys_for_skill(skill_code))
