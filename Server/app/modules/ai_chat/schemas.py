from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AIChatSessionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: int
    session_name: str | None
    scene_code: str
    model_name: str
    status: str
    summary: str | None
    last_message_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AIChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    message_type: str
    content: str
    token_count: int
    latency_ms: int | None
    error_code: str | None
    trace_id: str | None
    created_at: datetime


class AIChatSessionCreateRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    session_name: str | None = Field(None, max_length=120)
    scene_code: str = Field("study_assistant", max_length=32)
    model_name: str = Field("glm-4-flash", max_length=64)


class AIChatMessageSendRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    stream: bool = Field(False, description="Enable streaming response")
    page_context: dict = Field(default_factory=dict, description="Current frontend page context")


class StudentProfileWorkflowRequest(BaseModel):
    source_type: str = Field("assessment", max_length=32)
    source_ref_id: int | None = Field(None, gt=0)


class LearningPathWorkflowRequest(BaseModel):
    target_role: str | None = Field(None, max_length=64)
    current_level: str = Field("beginner", max_length=32)


class MonthlyReportWorkflowRequest(BaseModel):
    report_month: str = Field(..., pattern=r"^\d{4}-\d{2}$")


class ResourceGenerationWorkflowRequest(BaseModel):
    learning_goal: str = Field(..., min_length=1, max_length=1000)
    current_level: str = Field("beginner", max_length=32)
    learning_history: dict = Field(default_factory=dict)
    profile: dict = Field(default_factory=dict)


class StudyPlanWorkflowRequest(BaseModel):
    evaluation_type: str = Field("practice", max_length=32)
    data: dict = Field(default_factory=dict)


class TutorQAWorkflowRequest(BaseModel):
    question_content: str = Field(..., min_length=1, max_length=10000)
    question_id: int | None = Field(None, gt=0)
    user_answer: str | None = Field(None, max_length=10000)
    correct_answer: str | None = Field(None, max_length=10000)


class LearningEvaluationWorkflowRequest(BaseModel):
    month: str | None = Field(None, pattern=r"^\d{4}-\d{2}$")
    learning_data: dict = Field(default_factory=dict)
    path_progress: dict = Field(default_factory=dict)


class VideoContentWorkflowRequest(BaseModel):
    request_text: str = Field(..., min_length=1, max_length=5000)
    video_url: str = Field(..., min_length=1, max_length=2000)
    video_title: str | None = Field(default=None, max_length=200)
    video_summary: str | None = Field(default=None, max_length=1000)
    page_context: dict = Field(default_factory=dict)
