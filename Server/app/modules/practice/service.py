import asyncio
import json
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginationParams, build_page_response
from app.common.utils import utc_now_naive
from app.core.exceptions import AuthorizationError, BadRequestError, InfrastructureError, NotFoundError
from app.infra.ai.agent_manager import AgentManager
from app.modules.practice.repository import PracticeRepository
from app.modules.practice.schemas import (
    PracticeAnswerResponse,
    PracticeAnswerSubmitRequest,
    PracticeSessionCreateRequest,
    PracticeSessionResponse,
    PracticeSessionResultResponse,
    PracticeSessionSubmitResponse,
    QuestionBankListItemResponse,
    QuestionOptionResponse,
    QuestionResponse,
    VideoPracticeGenerateRequest,
    VideoPracticeGenerateResponse,
)


class PracticeService:
    def __init__(self, *, repository: PracticeRepository | None = None) -> None:
        self.repository = repository or PracticeRepository()
        self.agent_manager = AgentManager()

    @staticmethod
    def _to_bank_list_item(bank) -> QuestionBankListItemResponse:
        return QuestionBankListItemResponse(
            id=bank.id,
            title=bank.title,
            description=bank.description,
            question_count=bank.question_count,
            difficulty=bank.difficulty,
        )

    @staticmethod
    def _to_session_response(practice_session) -> PracticeSessionResponse:
        return PracticeSessionResponse(
            id=practice_session.id,
            bank_id=practice_session.bank_id,
            session_type=practice_session.session_type,
            total_questions=practice_session.total_questions,
            answered_questions=practice_session.answered_questions,
            status=practice_session.status,
            created_at=practice_session.created_at,
        )

    @staticmethod
    def _extract_json_object(raw: str) -> dict[str, Any] | None:
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.S)
            if not match:
                return None
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None

    @staticmethod
    def _normalize_question_type(question_type: str, correct_count: int) -> str:
        normalized = (question_type or "").strip().lower()
        mapping = {
            "single": "single_choice",
            "single_choice": "single_choice",
            "single-choice": "single_choice",
            "multiple": "multiple_choice",
            "multiple_choice": "multiple_choice",
            "multiple-choice": "multiple_choice",
            "multi_choice": "multiple_choice",
        }
        resolved = mapping.get(normalized, "")
        if resolved:
            if resolved == "single_choice" and correct_count != 1:
                return "multiple_choice"
            return resolved
        return "multiple_choice" if correct_count > 1 else "single_choice"

    @classmethod
    def _normalize_generated_bank(
        cls,
        payload: dict[str, Any] | None,
        *,
        fallback_title: str,
        fallback_summary: str,
        question_count: int,
    ) -> dict[str, Any]:
        data = payload or {}
        bank_title = str(data.get("bank_title") or "").strip() or f"{fallback_title} Practice"
        bank_description = str(data.get("bank_description") or "").strip() or fallback_summary.strip()
        difficulty = str(data.get("difficulty") or "mixed").strip().lower()
        if difficulty not in {"easy", "medium", "hard", "mixed"}:
            difficulty = "mixed"

        normalized_questions: list[dict[str, Any]] = []
        for raw_question in data.get("questions") or []:
            if not isinstance(raw_question, dict):
                continue

            content = str(
                raw_question.get("content")
                or raw_question.get("question")
                or raw_question.get("stem")
                or ""
            ).strip()
            if not content:
                continue

            normalized_options: list[dict[str, Any]] = []
            for option_index, raw_option in enumerate(raw_question.get("options") or []):
                if not isinstance(raw_option, dict):
                    continue
                option_content = str(
                    raw_option.get("content")
                    or raw_option.get("text")
                    or raw_option.get("option_text")
                    or ""
                ).strip()
                if not option_content:
                    continue
                normalized_options.append(
                    {
                        "option_key": chr(65 + option_index),
                        "content": option_content,
                        "is_correct": bool(raw_option.get("is_correct")),
                        "sort_order": option_index + 1,
                    }
                )

            if len(normalized_options) < 2:
                continue

            correct_options = [option for option in normalized_options if option["is_correct"]]
            if not correct_options:
                continue

            question_type = cls._normalize_question_type(
                str(raw_question.get("question_type") or ""),
                len(correct_options),
            )
            question_difficulty = str(raw_question.get("difficulty") or difficulty).strip().lower()
            if question_difficulty not in {"easy", "medium", "hard"}:
                question_difficulty = "medium"

            normalized_questions.append(
                {
                    "content": content,
                    "question_type": question_type,
                    "difficulty": question_difficulty,
                    "explanation": str(raw_question.get("explanation") or "").strip() or None,
                    "correct_answer_text": ", ".join(
                        option["option_key"] for option in correct_options
                    ),
                    "options": normalized_options,
                    "sort_order": len(normalized_questions) + 1,
                }
            )
            if len(normalized_questions) >= question_count:
                break

        if len(normalized_questions) < 3:
            raise InfrastructureError(message="Video practice generation returned too few valid questions.")

        return {
            "bank_title": bank_title[:120],
            "bank_description": bank_description[:1000] if bank_description else None,
            "difficulty": difficulty,
            "questions": normalized_questions,
        }

    async def list_question_banks(
        self,
        session: AsyncSession,
        pagination: PaginationParams,
    ):
        banks, total = await self.repository.list_question_banks(
            session,
            offset=pagination.offset,
            limit=pagination.page_size,
        )

        items = [self._to_bank_list_item(bank) for bank in banks]
        return build_page_response(items, total, pagination)

    async def list_bank_questions(
        self,
        session: AsyncSession,
        bank_id: int,
    ) -> list[QuestionResponse]:
        bank = await self.repository.get_question_bank_by_id(session, bank_id)
        if not bank:
            raise NotFoundError(message="Question bank not found.")

        questions = await self.repository.list_questions_by_bank(session, bank_id)

        result = []
        for question in questions:
            options = await self.repository.list_question_options(session, question.id)
            result.append(
                QuestionResponse(
                    id=question.id,
                    question_type=question.question_type,
                    content=question.content,
                    difficulty=question.difficulty,
                    score=1,
                    options=[
                        QuestionOptionResponse(
                            id=opt.id,
                            content=opt.content,
                            sort_order=opt.sort_order,
                        )
                        for opt in options
                    ],
                )
            )

        return result

    async def create_practice_session(
        self,
        session: AsyncSession,
        user_id: int,
        payload: PracticeSessionCreateRequest,
    ) -> PracticeSessionResponse:
        bank = await self.repository.get_question_bank_by_id(session, payload.bank_id)
        if not bank:
            raise NotFoundError(message="Question bank not found.")

        questions = await self.repository.list_questions_by_bank(session, payload.bank_id)
        try:
            practice_session = await self.repository.create_practice_session(
                session,
                user_id=user_id,
                bank_id=payload.bank_id,
                session_type=payload.session_type,
                total_questions=len(questions),
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        return self._to_session_response(practice_session)

    async def get_practice_session(
        self,
        session: AsyncSession,
        user_id: int,
        session_id: int,
    ) -> PracticeSessionResponse:
        practice_session = await self.repository.get_practice_session_by_id(session, session_id)
        if not practice_session:
            raise NotFoundError(message="Practice session not found.")
        if practice_session.user_id != user_id:
            raise AuthorizationError(message="Not your practice session.")
        return self._to_session_response(practice_session)

    async def generate_video_practice(
        self,
        session: AsyncSession,
        user_id: int,
        payload: VideoPracticeGenerateRequest,
    ) -> VideoPracticeGenerateResponse:
        page_context = payload.page_context if isinstance(payload.page_context, dict) else {}
        current_video = page_context.get("current_video")
        if not isinstance(current_video, dict):
            raise BadRequestError(message="Current video context is required.")

        video_url = str(current_video.get("video_url") or "").strip()
        if not video_url:
            raise BadRequestError(message="Current video URL is required.")

        video_title = str(current_video.get("title") or "").strip() or "Current Video"
        video_summary = str(current_video.get("summary") or "").strip()
        category_name = str(current_video.get("category_name") or "").strip()
        request_text = (
            payload.request_text
            or "Please extract the key points from the current video and generate a practice bank that can be answered directly."
        )

        extracted = await self.agent_manager.run_video_content_agent(
            session,
            user_id=user_id,
            video_url=video_url,
            request_text=request_text,
            video_title=video_title,
            video_summary=video_summary,
            page_context=page_context,
        )

        prompt = f"""
You are generating a practice question bank for a learning platform.
Use the extracted video understanding to create {payload.question_count} high-quality questions.

Video title:
{video_title}

Video summary:
{video_summary or "Unknown"}

Extracted structured summary:
{str(extracted.get("generated_output") or "").strip() or "Unavailable"}

Extracted visual evidence:
{str(extracted.get("visual_analysis") or "").strip() or "Unavailable"}

Extracted audio transcript:
{str(extracted.get("transcript") or "").strip() or "Unavailable"}

Requirements:
- Return strict JSON only.
- Generate exactly {payload.question_count} questions if possible.
- Focus on the video's real teaching content, not generic trivia.
- Prefer single_choice unless multiple correct answers are clearly justified.
- Each question must include 4 options when possible.
- Explanations should be short and educational.

JSON schema:
{{
  "bank_title": "string",
  "bank_description": "string",
  "difficulty": "easy|medium|hard|mixed",
  "questions": [
    {{
      "question_type": "single_choice|multiple_choice",
      "content": "string",
      "difficulty": "easy|medium|hard",
      "explanation": "string",
      "options": [
        {{"content": "string", "is_correct": true}},
        {{"content": "string", "is_correct": false}}
      ]
    }}
  ]
}}
"""
        retry_prompt = f"""
Return a strict JSON object only, with no markdown fences and no explanation text.
Generate a practical question bank from the current video using as much real evidence as possible.

Video title: {video_title}
Video summary: {video_summary or "Unknown"}
Extracted summary: {str(extracted.get("generated_output") or "").strip() or "Unavailable"}
Transcript: {str(extracted.get("transcript") or "").strip() or "Unavailable"}

Rules:
- Output valid JSON only.
- Generate between 3 and {payload.question_count} questions.
- Prefer single_choice questions.
- Each question should have 4 options when possible.
- Mark at least 1 correct option per question.

JSON schema:
{{
  "bank_title": "string",
  "bank_description": "string",
  "difficulty": "easy|medium|hard|mixed",
  "questions": [
    {{
      "question_type": "single_choice|multiple_choice",
      "content": "string",
      "difficulty": "easy|medium|hard",
      "explanation": "string",
      "options": [
        {{"content": "string", "is_correct": true}},
        {{"content": "string", "is_correct": false}}
      ]
    }}
  ]
}}
"""
        try:
            normalized_bank = None
            prompts = [prompt, retry_prompt]
            last_error: Exception | None = None
            for current_prompt in prompts:
                try:
                    response = await asyncio.wait_for(
                        self.agent_manager.llm.ainvoke(
                            [
                                SystemMessage(
                                    content="You create production-ready practice banks from educational video evidence."
                                ),
                                HumanMessage(content=current_prompt),
                            ]
                        ),
                        timeout=60,
                    )
                    parsed = self._extract_json_object(str(getattr(response, "content", response)).strip())
                    normalized_bank = self._normalize_generated_bank(
                        parsed,
                        fallback_title=video_title,
                        fallback_summary=video_summary or str(extracted.get("generated_output") or ""),
                        question_count=payload.question_count,
                    )
                    break
                except InfrastructureError as exc:
                    last_error = exc
                    continue

            if normalized_bank is None:
                raise last_error or InfrastructureError(message="Failed to generate practice bank from video.")
        except InfrastructureError:
            raise
        except Exception as exc:
            raise InfrastructureError(message=f"Failed to generate practice bank from video: {exc}") from exc

        category = await self.repository.find_category_by_name(session, category_name)
        category_id = category.id if category else None
        try:
            bank = await self.repository.create_question_bank(
                session,
                title=normalized_bank["bank_title"],
                description=normalized_bank["bank_description"],
                category_id=category_id,
                difficulty=normalized_bank["difficulty"],
                question_count=len(normalized_bank["questions"]),
                created_by=user_id,
            )
            for question_data in normalized_bank["questions"]:
                question = await self.repository.create_question(
                    session,
                    bank_id=bank.id,
                    category_id=category_id,
                    question_type=question_data["question_type"],
                    content=question_data["content"],
                    explanation=question_data["explanation"],
                    correct_answer_text=question_data["correct_answer_text"],
                    difficulty=question_data["difficulty"],
                    sort_order=question_data["sort_order"],
                )
                for option_data in question_data["options"]:
                    await self.repository.create_question_option(
                        session,
                        question_id=question.id,
                        option_key=option_data["option_key"],
                        content=option_data["content"],
                        is_correct=option_data["is_correct"],
                        sort_order=option_data["sort_order"],
                    )

            practice_session = await self.repository.create_practice_session(
                session,
                user_id=user_id,
                bank_id=bank.id,
                session_type=payload.session_type,
                total_questions=len(normalized_bank["questions"]),
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        return VideoPracticeGenerateResponse(
            bank=self._to_bank_list_item(bank),
            session=self._to_session_response(practice_session),
        )

    async def submit_answer(
        self,
        session: AsyncSession,
        user_id: int,
        session_id: int,
        payload: PracticeAnswerSubmitRequest,
    ) -> PracticeAnswerResponse:
        try:
            practice_session = await self.repository.get_practice_session_by_id(session, session_id)
            if not practice_session:
                raise NotFoundError(message="Practice session not found.")

            if practice_session.user_id != user_id:
                raise AuthorizationError(message="Not your practice session.")

            if practice_session.status != "started":
                raise BadRequestError(message="Session is not in progress.")

            question = await self.repository.get_question_by_id(session, payload.question_id)
            if not question:
                raise NotFoundError(message="Question not found.")

            options = await self.repository.list_question_options(session, payload.question_id)
            correct_option_ids = {opt.id for opt in options if opt.is_correct}
            selected_set = set(payload.selected_option_ids)

            is_correct = selected_set == correct_option_ids
            earned_score = 1 if is_correct else 0

            existing = await self.repository.get_practice_answer(session, session_id, payload.question_id)
            if existing:
                raise BadRequestError(message="Answer already submitted for this question.")

            await self.repository.create_practice_answer(
                session,
                session_id=session_id,
                question_id=payload.question_id,
                selected_option_id=payload.selected_option_ids[0] if payload.selected_option_ids else None,
                is_correct=is_correct,
                earned_score=earned_score,
            )

            practice_session.answered_questions += 1
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        return PracticeAnswerResponse(
            question_id=payload.question_id,
            is_correct=is_correct,
            earned_score=earned_score,
        )

    async def submit_session(
        self,
        session: AsyncSession,
        user_id: int,
        session_id: int,
    ) -> PracticeSessionSubmitResponse:
        try:
            practice_session = await self.repository.get_practice_session_by_id(session, session_id)
            if not practice_session:
                raise NotFoundError(message="Practice session not found.")

            if practice_session.user_id != user_id:
                raise AuthorizationError(message="Not your practice session.")

            if practice_session.status != "started":
                raise BadRequestError(message="Session already submitted.")

            answers = await self.repository.list_session_answers(session, session_id)
            correct_count = sum(1 for ans in answers if ans.is_correct)
            earned_score = sum(ans.earned_score for ans in answers)
            total_score = practice_session.total_questions
            submitted_at = utc_now_naive()
            duration_seconds = max(
                0,
                int((submitted_at - practice_session.started_at).total_seconds()),
            )

            await self.repository.update_practice_session(
                session,
                session_id,
                {
                    "correct_answers": correct_count,
                    "earned_score": earned_score,
                    "status": "completed",
                    "submitted_at": submitted_at,
                    "finished_at": submitted_at,
                    "duration_seconds": duration_seconds,
                },
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        accuracy = (
            correct_count / practice_session.total_questions * 100
            if practice_session.total_questions > 0
            else 0
        )

        return PracticeSessionSubmitResponse(
            session_id=session_id,
            total_questions=practice_session.total_questions,
            correct_answers=correct_count,
            total_score=total_score,
            earned_score=int(earned_score),
            accuracy=round(accuracy, 2),
        )

    async def get_session_result(
        self,
        session: AsyncSession,
        user_id: int,
        session_id: int,
    ) -> PracticeSessionResultResponse:
        practice_session = await self.repository.get_practice_session_by_id(session, session_id)
        if not practice_session:
            raise NotFoundError(message="Practice session not found.")

        if practice_session.user_id != user_id:
            raise AuthorizationError(message="Not your practice session.")

        bank = await self.repository.get_question_bank_by_id(session, practice_session.bank_id)
        answers = await self.repository.list_session_answers(session, session_id)

        accuracy = (
            (practice_session.correct_answers / practice_session.total_questions * 100)
            if practice_session.total_questions > 0
            else 0
        )

        return PracticeSessionResultResponse(
            session_id=session_id,
            bank_title=bank.title if bank else "",
            total_questions=practice_session.total_questions,
            correct_answers=practice_session.correct_answers,
            total_score=practice_session.total_questions,
            earned_score=int(practice_session.earned_score),
            accuracy=round(accuracy, 2),
            submitted_at=practice_session.submitted_at or practice_session.created_at,
            answers=[
                {
                    "question_id": ans.question_id,
                    "is_correct": ans.is_correct,
                    "earned_score": int(ans.earned_score),
                }
                for ans in answers
            ],
        )
