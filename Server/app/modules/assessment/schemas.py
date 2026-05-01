from datetime import date, datetime

from pydantic import BaseModel, Field


class AssessmentSnapshotResponse(BaseModel):
    id: int
    user_id: int
    assessment_type: str
    period_start: date
    period_end: date
    total_learning_minutes: int
    completed_courses: int
    average_score: float
    rank_percent: float | None
    correct_rate: float | None
    focus_rate: float | None
    metrics_json: dict | None
    created_at: datetime
    updated_at: datetime


class AssessmentTrendDataPoint(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    learning_minutes: int
    average_score: float
    correct_rate: float | None


class AssessmentTrendResponse(BaseModel):
    assessment_type: str = Field(..., description="daily, weekly, or monthly")
    data_points: list[AssessmentTrendDataPoint]


class AssessmentGenerateRequest(BaseModel):
    assessment_type: str = Field("weekly", description="daily, weekly, or monthly")
    force_regenerate: bool = Field(False, description="Force regenerate even if exists")
