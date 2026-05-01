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
