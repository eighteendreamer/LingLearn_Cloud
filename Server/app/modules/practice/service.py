from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginationParams, build_page_response
from app.common.utils import utc_now_naive
from app.core.exceptions import AuthorizationError, BadRequestError, NotFoundError
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
)


class PracticeService:
    def __init__(self, *, repository: PracticeRepository | None = None) -> None:
        self.repository = repository or PracticeRepository()

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

        items = [
            QuestionBankListItemResponse(
                id=bank.id,
                title=bank.title,
                description=bank.description,
                question_count=bank.question_count,
                difficulty=bank.difficulty,
            )
            for bank in banks
        ]

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

        return PracticeSessionResponse(
            id=practice_session.id,
            bank_id=practice_session.bank_id,
            session_type=practice_session.session_type,
            total_questions=practice_session.total_questions,
            answered_questions=practice_session.answered_questions,
            status=practice_session.status,
            created_at=practice_session.created_at,
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

            await self.repository.update_practice_session(
                session,
                session_id,
                {
                    "correct_answers": correct_count,
                    "earned_score": earned_score,
                    "status": "submitted",
                    "submitted_at": utc_now_naive(),
                },
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        accuracy = (correct_count / practice_session.total_questions * 100) if practice_session.total_questions > 0 else 0

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
