from datetime import datetime

from pydantic import BaseModel, Field


class ReportAchievementResponse(BaseModel):
    id: int
    title: str
    description: str | None
    icon: str | None
    color_token: str | None
    sort_order: int


class MonthlyReportResponse(BaseModel):
    id: int
    user_id: int
    report_month: str
    assessment_snapshot_id: int | None
    report_status: str
    total_learning_minutes: int
    completed_courses: int
    average_score: float
    site_rank: int | None
    strengths: list
    improvements: list
    ai_summary: str | None
    exported_pdf_asset_id: int | None
    generated_at: datetime
    achievements: list[ReportAchievementResponse] = Field(default_factory=list)


class ReportExportResponse(BaseModel):
    report_month: str
    exported_pdf_asset_id: int | None
    status: str
