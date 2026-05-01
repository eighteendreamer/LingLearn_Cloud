from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.content.models import ContentQuiz, ContentQuizAttempt, ContentQuizOption
from app.modules.content.repository import ContentRepository


class QuizRepository:
    def __init__(self, *, content_repository: ContentRepository | None = None) -> None:
        self.content_repository = content_repository or ContentRepository()

    async def get_content_item_by_id(self, session: AsyncSession, content_id: int):
        return await self.content_repository.get_content_item_by_id(session, content_id)

    async def list_published_quizzes(
        self,
        session: AsyncSession,
        *,
        content_item_id: int,
    ) -> list[ContentQuiz]:
        return await self.content_repository.list_published_quizzes(
            session,
            content_item_id=content_item_id,
        )

    async def list_quiz_options(
        self,
        session: AsyncSession,
        *,
        quiz_ids: Sequence[int],
    ) -> list[ContentQuizOption]:
        return await self.content_repository.list_quiz_options(session, quiz_ids=quiz_ids)

    async def get_quiz_by_id(self, session: AsyncSession, quiz_id: int) -> ContentQuiz | None:
        return await self.content_repository.get_quiz_by_id(session, quiz_id)

    async def get_quiz_option_by_id(
        self,
        session: AsyncSession,
        option_id: int,
    ) -> ContentQuizOption | None:
        return await self.content_repository.get_quiz_option_by_id(session, option_id)

    async def get_quiz_attempt(
        self,
        session: AsyncSession,
        *,
        quiz_id: int,
        user_id: int,
    ) -> ContentQuizAttempt | None:
        return await self.content_repository.get_quiz_attempt(
            session,
            quiz_id=quiz_id,
            user_id=user_id,
        )

    async def create_quiz_attempt(
        self,
        session: AsyncSession,
        *,
        quiz_id: int,
        user_id: int,
        selected_option_id: int,
        is_correct: bool,
        client_ip: str | None,
    ) -> ContentQuizAttempt:
        return await self.content_repository.create_quiz_attempt(
            session,
            quiz_id=quiz_id,
            user_id=user_id,
            selected_option_id=selected_option_id,
            is_correct=is_correct,
            client_ip=client_ip,
        )

    async def increment_quiz_vote(
        self,
        session: AsyncSession,
        *,
        quiz_id: int,
        option_id: int,
    ) -> None:
        await self.content_repository.increment_quiz_vote(
            session,
            quiz_id=quiz_id,
            option_id=option_id,
        )
