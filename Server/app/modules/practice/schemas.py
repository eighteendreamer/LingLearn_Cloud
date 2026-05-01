from datetime import datetime

from pydantic import BaseModel


class QuestionBankListItemResponse(BaseModel):
    id: int
    title: str
    description: str | None
    question_count: int
    difficulty: str


class QuestionOptionResponse(BaseModel):
    id: int
    content: str
    sort_order: int


class QuestionResponse(BaseModel):
    id: int
    question_type: str
    content: str
    difficulty: str
    score: int
    options: list[QuestionOptionResponse]


class PracticeSessionCreateRequest(BaseModel):
    bank_id: int
    session_type: str = "practice"


class PracticeSessionResponse(BaseModel):
    id: int
    bank_id: int
    session_type: str
    total_questions: int
    answered_questions: int
    status: str
    created_at: datetime


class PracticeAnswerSubmitRequest(BaseModel):
    question_id: int
    selected_option_ids: list[int]


class PracticeAnswerResponse(BaseModel):
    question_id: int
    is_correct: bool
    earned_score: int


class PracticeSessionSubmitResponse(BaseModel):
    session_id: int
    total_questions: int
    correct_answers: int
    total_score: int
    earned_score: int
    accuracy: float


class PracticeSessionResultResponse(BaseModel):
    session_id: int
    bank_title: str
    total_questions: int
    correct_answers: int
    total_score: int
    earned_score: int
    accuracy: float
    submitted_at: datetime
    answers: list[dict]
