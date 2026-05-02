from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import utc_now_naive
from app.modules.content.models import ContentCategory
from app.modules.practice.models import (
    PracticeAnswer,
    PracticeSession,
    Question,
    QuestionBank,
    QuestionOption,
)


class PracticeRepository:
    async def list_question_banks(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[QuestionBank], int]:
        query = (
            select(QuestionBank)
            .where(QuestionBank.status == "published")
            .where(QuestionBank.bank_type == "practice")
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query) or 0

        query = query.order_by(QuestionBank.created_at.desc()).offset(offset).limit(limit)
        result = await session.execute(query)
        banks = list(result.scalars().all())

        return banks, total

    async def get_question_bank_by_id(
        self,
        session: AsyncSession,
        bank_id: int,
    ) -> QuestionBank | None:
        result = await session.execute(
            select(QuestionBank)
            .where(QuestionBank.id == bank_id)
            .where(QuestionBank.status == "published")
        )
        return result.scalar_one_or_none()

    async def list_questions_by_bank(
        self,
        session: AsyncSession,
        bank_id: int,
    ) -> list[Question]:
        result = await session.execute(
            select(Question)
            .where(Question.bank_id == bank_id)
            .where(Question.status == "published")
            .order_by(Question.sort_order)
        )
        return list(result.scalars().all())

    async def list_question_options(
        self,
        session: AsyncSession,
        question_id: int,
    ) -> list[QuestionOption]:
        result = await session.execute(
            select(QuestionOption)
            .where(QuestionOption.question_id == question_id)
            .order_by(QuestionOption.sort_order)
        )
        return list(result.scalars().all())

    async def get_question_by_id(
        self,
        session: AsyncSession,
        question_id: int,
    ) -> Question | None:
        result = await session.execute(
            select(Question).where(Question.id == question_id).where(Question.status == "published")
        )
        return result.scalar_one_or_none()

    async def create_practice_session(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        bank_id: int,
        session_type: str,
        total_questions: int,
    ) -> PracticeSession:
        practice_session = PracticeSession(
            user_id=user_id,
            bank_id=bank_id,
            session_type=session_type,
            total_questions=total_questions,
            started_at=utc_now_naive(),
        )
        session.add(practice_session)
        await session.flush()
        await session.refresh(practice_session)
        return practice_session

    async def create_question_bank(
        self,
        session: AsyncSession,
        *,
        title: str,
        description: str | None,
        category_id: int | None,
        difficulty: str,
        question_count: int,
        created_by: int,
    ) -> QuestionBank:
        bank = QuestionBank(
            title=title,
            description=description,
            category_id=category_id,
            bank_type="practice",
            difficulty=difficulty,
            question_count=question_count,
            status="published",
            created_by=created_by,
        )
        session.add(bank)
        await session.flush()
        await session.refresh(bank)
        return bank

    async def create_question(
        self,
        session: AsyncSession,
        *,
        bank_id: int,
        category_id: int | None,
        question_type: str,
        content: str,
        explanation: str | None,
        correct_answer_text: str | None,
        difficulty: str,
        sort_order: int,
    ) -> Question:
        question = Question(
            bank_id=bank_id,
            category_id=category_id,
            question_type=question_type,
            content=content,
            explanation=explanation,
            correct_answer_text=correct_answer_text,
            difficulty=difficulty,
            status="published",
            sort_order=sort_order,
        )
        session.add(question)
        await session.flush()
        await session.refresh(question)
        return question

    async def create_question_option(
        self,
        session: AsyncSession,
        *,
        question_id: int,
        option_key: str,
        content: str,
        is_correct: bool,
        sort_order: int,
    ) -> QuestionOption:
        option = QuestionOption(
            question_id=question_id,
            option_key=option_key,
            content=content,
            is_correct=is_correct,
            sort_order=sort_order,
            created_at=utc_now_naive(),
        )
        session.add(option)
        await session.flush()
        await session.refresh(option)
        return option

    async def get_practice_session_by_id(
        self,
        session: AsyncSession,
        session_id: int,
    ) -> PracticeSession | None:
        result = await session.execute(select(PracticeSession).where(PracticeSession.id == session_id))
        return result.scalar_one_or_none()

    async def create_practice_answer(
        self,
        session: AsyncSession,
        *,
        session_id: int,
        question_id: int,
        selected_option_id: int | None,
        is_correct: bool,
        earned_score: int,
    ) -> PracticeAnswer:
        answer = PracticeAnswer(
            session_id=session_id,
            question_id=question_id,
            selected_option_id=selected_option_id,
            is_correct=is_correct,
            earned_score=earned_score,
            answered_at=utc_now_naive(),
        )
        session.add(answer)
        await session.flush()
        await session.refresh(answer)
        return answer

    async def get_practice_answer(
        self,
        session: AsyncSession,
        session_id: int,
        question_id: int,
    ) -> PracticeAnswer | None:
        result = await session.execute(
            select(PracticeAnswer)
            .where(PracticeAnswer.session_id == session_id)
            .where(PracticeAnswer.question_id == question_id)
        )
        return result.scalar_one_or_none()

    async def list_session_answers(
        self,
        session: AsyncSession,
        session_id: int,
    ) -> list[PracticeAnswer]:
        result = await session.execute(
            select(PracticeAnswer).where(PracticeAnswer.session_id == session_id)
        )
        return list(result.scalars().all())

    async def update_practice_session(
        self,
        session: AsyncSession,
        session_id: int,
        values: dict,
    ) -> None:
        practice_session = await self.get_practice_session_by_id(session, session_id)
        if practice_session:
            for key, value in values.items():
                setattr(practice_session, key, value)

    async def list_user_sessions(
        self,
        session: AsyncSession,
        user_id: int,
        status: str | None = None,
        limit: int = 100,
    ) -> list[PracticeSession]:
        stmt = select(PracticeSession).where(PracticeSession.user_id == user_id)
        
        if status:
            stmt = stmt.where(PracticeSession.status == status)
        
        stmt = stmt.order_by(PracticeSession.created_at.desc()).limit(limit)
        
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def find_category_by_name(
        self,
        session: AsyncSession,
        name: str,
    ) -> ContentCategory | None:
        normalized = (name or "").strip()
        if not normalized:
            return None
        result = await session.execute(
            select(ContentCategory)
            .where(ContentCategory.name == normalized)
            .where(ContentCategory.status == "active")
        )
        return result.scalar_one_or_none()
