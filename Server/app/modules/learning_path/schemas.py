from datetime import datetime

from pydantic import BaseModel, Field


class SkillScoreResponse(BaseModel):
    dimension_id: int
    code: str
    name: str
    score: float
    percentile: float | None
    level: str | None
    insight: str | None


class SkillSnapshotResponse(BaseModel):
    id: int
    user_id: int
    source_type: str
    source_ref_id: int | None
    snapshot_version: int
    total_score: float | None
    rank_percent: float | None
    generated_by: str
    generated_at: datetime
    scores: list[SkillScoreResponse]


class SkillProfileGenerateRequest(BaseModel):
    source_type: str = Field("assessment", max_length=32)
    source_ref_id: int | None = Field(None, gt=0)


class LearningPathGenerateRequest(BaseModel):
    target_role: str | None = Field(None, max_length=64)
    current_level: str = Field("beginner", max_length=32)
    weekly_hours: int = Field(6, ge=1, le=40)
    route_count: int = Field(3, ge=2, le=4)
    preferred_resource_mode: str = Field("mixed", max_length=32)


class LearningPathStageResourceResponse(BaseModel):
    resource_type: str
    source: str
    title: str
    description: str | None = None
    content_id: int | None = None
    category_name: str | None = None
    cover_url: str | None = None
    video_url: str | None = None
    external_url: str | None = None


class LearningPathStageAssessmentResponse(BaseModel):
    mode: str
    question_count: int
    pass_score: int
    generated_bank_id: int | None = None
    generated_session_id: int | None = None


class LearningPathPlanStageResponse(BaseModel):
    stage_code: str
    title: str
    goal: str
    description: str | None = None
    estimated_hours: int
    recommended_reason: str | None = None
    resources: list[LearningPathStageResourceResponse] = Field(default_factory=list)
    assessment: LearningPathStageAssessmentResponse | None = None


class LearningPathPlanRouteResponse(BaseModel):
    route_code: str
    title: str
    summary: str
    fit_reason: str
    difficulty: str
    estimated_weeks: int
    stages: list[LearningPathPlanStageResponse] = Field(default_factory=list)


class LearningPathPlanResponse(BaseModel):
    planning_summary: str
    route_options: list[LearningPathPlanRouteResponse] = Field(default_factory=list)


class LearningPathActivateRequest(BaseModel):
    selected_route: LearningPathPlanRouteResponse


class LearningPathNodeResponse(BaseModel):
    id: int
    node_id: int
    title: str
    description: str | None
    node_type: str
    course_id: int | None
    status: str
    progress_percent: float
    sort_order: int
    recommended_reason: str | None
    estimated_minutes: int
    stage_code: str | None = None
    stage_goal: str | None = None
    resources: list[LearningPathStageResourceResponse] = Field(default_factory=list)
    assessment: LearningPathStageAssessmentResponse | None = None


class UserLearningPathResponse(BaseModel):
    id: int
    path_id: int
    name: str
    description: str | None
    target_role: str | None
    status: str
    progress_percent: float
    current_node_id: int | None
    ai_summary: str | None
    nodes: list[LearningPathNodeResponse]


class LearningPathNodeUpdateRequest(BaseModel):
    status: str = Field(max_length=20)
    progress_percent: float = Field(ge=0, le=100)


class LearningPathNodePracticeGenerateResponse(BaseModel):
    bank_id: int
    bank_title: str
    session_id: int
