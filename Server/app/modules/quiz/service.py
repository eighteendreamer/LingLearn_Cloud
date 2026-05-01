from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.modules.quiz.repository import QuizRepository
from app.modules.quiz.schemas import (
    ContentQuizResponse,
    QuizOptionResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
)


class QuizService:
    def __init__(self, *, repository: QuizRepository | None = None) -> None:
        self.repository = repository or QuizRepository()

    async def list_content_quizzes(
        self,
        session: AsyncSession,
        *,
        content_id: int,
        viewer_user_id: int | None,
    ) -> list[ContentQuizResponse]:
        await self._ensure_public_content(session, content_id)
        quizzes = await self.repository.list_published_quizzes(session, content_item_id=content_id)
        options = await self.repository.list_quiz_options(
            session,
            quiz_ids=[quiz.id for quiz in quizzes],
        )
        options_by_quiz: dict[int, list] = defaultdict(list)
        for option in options:
            options_by_quiz[option.quiz_id].append(option)

        responses: list[ContentQuizResponse] = []
        for quiz in quizzes:
            attempt = None
            if viewer_user_id is not None:
                attempt = await self.repository.get_quiz_attempt(
                    session,
                    quiz_id=quiz.id,
                    user_id=viewer_user_id,
                )
            responses.append(
                ContentQuizResponse(
                    quiz_id=quiz.id,
                    content_id=quiz.content_item_id,
                    title=quiz.title,
                    description=quiz.description,
                    quiz_type=quiz.quiz_type,
                    total_votes=quiz.total_votes,
                    has_submitted=attempt is not None,
                    selected_option_id=attempt.selected_option_id if attempt else None,
                    options=self._build_options(
                        options_by_quiz[quiz.id],
                        total_votes=quiz.total_votes,
                        reveal_correct=attempt is not None,
                    ),
                )
            )
        return responses

    async def submit_quiz(
        self,
        session: AsyncSession,
        *,
        quiz_id: int,
        user_id: int,
        payload: QuizSubmitRequest,
        client_ip: str | None,
    ) -> QuizSubmitResponse:
        selected_option_id = payload.selected_option_id
        async with session.begin():
            quiz = await self.repository.get_quiz_by_id(session, quiz_id)
            if quiz is None or quiz.status != "published":
                raise NotFoundError(message="Quiz not found.")
            await self._ensure_public_content(session, quiz.content_item_id)

            option = await self.repository.get_quiz_option_by_id(session, selected_option_id)
            if option is None or option.quiz_id != quiz_id:
                raise BadRequestError(message="Selected option does not belong to this quiz.")

            existing_attempt = await self.repository.get_quiz_attempt(
                session,
                quiz_id=quiz_id,
                user_id=user_id,
            )
            if existing_attempt is not None:
                if existing_attempt.selected_option_id != selected_option_id:
                    raise ConflictError(message="Quiz has already been submitted.")
                selected_option_id = existing_attempt.selected_option_id
            else:
                await self.repository.create_quiz_attempt(
                    session,
                    quiz_id=quiz_id,
                    user_id=user_id,
                    selected_option_id=selected_option_id,
                    is_correct=bool(option.is_correct),
                    client_ip=client_ip,
                )
                await self.repository.increment_quiz_vote(
                    session,
                    quiz_id=quiz_id,
                    option_id=selected_option_id,
                )

        session.expire_all()
        quiz = await self.repository.get_quiz_by_id(session, quiz_id)
        options = await self.repository.list_quiz_options(session, quiz_ids=[quiz_id])
        selected = next((option for option in options if option.id == selected_option_id), None)
        if quiz is None or selected is None:
            raise NotFoundError(message="Quiz result not found.")

        return QuizSubmitResponse(
            quiz_id=quiz.id,
            selected_option_id=selected_option_id,
            is_correct=bool(selected.is_correct),
            total_votes=quiz.total_votes,
            options=self._build_options(
                options,
                total_votes=quiz.total_votes,
                reveal_correct=True,
            ),
        )

    async def _ensure_public_content(self, session: AsyncSession, content_id: int) -> None:
        item = await self.repository.get_content_item_by_id(session, content_id)
        if item is None or item.deleted_at is not None:
            raise NotFoundError(message="Content not found.")
        if item.visibility != "public" or item.audit_status != "approved" or item.publish_status != "published":
            raise NotFoundError(message="Content not found.")

    @staticmethod
    def _build_options(
        options: list,
        *,
        total_votes: int,
        reveal_correct: bool,
    ) -> list[QuizOptionResponse]:
        total = max(int(total_votes or 0), 0)
        responses: list[QuizOptionResponse] = []
        for option in options:
            vote_count = int(option.vote_count or 0)
            percent = round((vote_count / total) * 100, 1) if total else 0.0
            responses.append(
                QuizOptionResponse(
                    option_id=option.id,
                    option_text=option.option_text,
                    vote_count=vote_count,
                    percent=percent,
                    is_correct=bool(option.is_correct) if reveal_correct else None,
                )
            )
        return responses
