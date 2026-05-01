from pydantic import BaseModel, Field


class QuizOptionResponse(BaseModel):
    option_id: int
    option_text: str
    vote_count: int
    percent: float
    is_correct: bool | None = None


class ContentQuizResponse(BaseModel):
    quiz_id: int
    content_id: int
    title: str
    description: str | None
    quiz_type: str
    total_votes: int
    has_submitted: bool = False
    selected_option_id: int | None = None
    options: list[QuizOptionResponse]


class QuizSubmitRequest(BaseModel):
    selected_option_id: int = Field(gt=0)


class QuizSubmitResponse(BaseModel):
    quiz_id: int
    selected_option_id: int
    is_correct: bool
    total_votes: int
    options: list[QuizOptionResponse]
