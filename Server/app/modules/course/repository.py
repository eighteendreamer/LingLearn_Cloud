from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.course.models import Course, CourseLesson, UserCourseEnrollment, UserLessonProgress


class CourseRepository:
    async def list_courses(
        self,
        session: AsyncSession,
        *,
        category_id: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict], int]:
        from app.modules.storage.models import MediaAsset
        from app.modules.user.models import UserProfile

        query = (
            select(
                Course.id,
                Course.title,
                Course.description,
                Course.instructor_id,
                Course.category_id,
                Course.cover_asset_id,
                Course.level,
                Course.duration_minutes,
                Course.lesson_count,
                Course.enrollment_count,
                Course.rating,
                UserProfile.display_name.label("instructor_name"),
                MediaAsset.object_key.label("cover_object_key"),
                MediaAsset.public_url.label("cover_public_url"),
            )
            .join(UserProfile, Course.instructor_id == UserProfile.user_id)
            .outerjoin(MediaAsset, Course.cover_asset_id == MediaAsset.id)
            .where(Course.deleted_at.is_(None))
            .where(Course.status == "published")
        )

        if category_id is not None:
            query = query.where(Course.category_id == category_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query) or 0

        query = query.order_by(Course.created_at.desc()).offset(offset).limit(limit)
        result = await session.execute(query)
        rows = [dict(row._mapping) for row in result]

        return rows, total

    async def get_course_by_id(self, session: AsyncSession, course_id: int) -> Course | None:
        result = await session.execute(
            select(Course).where(Course.id == course_id).where(Course.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_course_detail_row(self, session: AsyncSession, course_id: int) -> dict | None:
        from app.modules.storage.models import MediaAsset
        from app.modules.user.models import UserProfile

        query = (
            select(
                Course.id,
                Course.title,
                Course.description,
                Course.instructor_id,
                Course.category_id,
                Course.cover_asset_id,
                Course.level,
                Course.duration_minutes,
                Course.lesson_count,
                Course.enrollment_count,
                Course.rating,
                Course.created_at,
                UserProfile.display_name.label("instructor_name"),
                MediaAsset.object_key.label("cover_object_key"),
                MediaAsset.public_url.label("cover_public_url"),
            )
            .join(UserProfile, Course.instructor_id == UserProfile.user_id)
            .outerjoin(MediaAsset, Course.cover_asset_id == MediaAsset.id)
            .where(Course.id == course_id)
            .where(Course.deleted_at.is_(None))
            .where(Course.status == "published")
        )

        result = await session.execute(query)
        row = result.first()
        return dict(row._mapping) if row else None

    async def list_course_lessons(
        self,
        session: AsyncSession,
        course_id: int,
    ) -> list[CourseLesson]:
        result = await session.execute(
            select(CourseLesson)
            .where(CourseLesson.course_id == course_id)
            .where(CourseLesson.deleted_at.is_(None))
            .where(CourseLesson.status == "published")
            .order_by(CourseLesson.sort_order)
        )
        return list(result.scalars().all())

    async def get_enrollment(
        self,
        session: AsyncSession,
        user_id: int,
        course_id: int,
    ) -> UserCourseEnrollment | None:
        result = await session.execute(
            select(UserCourseEnrollment)
            .where(UserCourseEnrollment.user_id == user_id)
            .where(UserCourseEnrollment.course_id == course_id)
        )
        return result.scalar_one_or_none()

    async def create_enrollment(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        course_id: int,
        enrolled_at,
    ) -> UserCourseEnrollment:
        enrollment = UserCourseEnrollment(
            user_id=user_id,
            course_id=course_id,
            enrolled_at=enrolled_at,
        )
        session.add(enrollment)
        await session.flush()
        await session.refresh(enrollment)
        return enrollment

    async def increment_enrollment_count(
        self,
        session: AsyncSession,
        course_id: int,
    ) -> None:
        await session.execute(
            select(Course)
            .where(Course.id == course_id)
            .with_for_update()
        )
        course = await self.get_course_by_id(session, course_id)
        if course:
            course.enrollment_count += 1

    async def list_user_enrollments(
        self,
        session: AsyncSession,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict], int]:
        from app.modules.storage.models import MediaAsset
        from app.modules.user.models import UserProfile

        query = (
            select(
                UserCourseEnrollment.id.label("enrollment_id"),
                UserCourseEnrollment.progress_percent,
                UserCourseEnrollment.completed_lessons,
                UserCourseEnrollment.updated_at.label("last_studied_at"),
                Course.id.label("course_id"),
                Course.title,
                Course.lesson_count,
                Course.cover_asset_id,
                UserProfile.display_name.label("instructor_name"),
                MediaAsset.object_key.label("cover_object_key"),
                MediaAsset.public_url.label("cover_public_url"),
            )
            .join(Course, UserCourseEnrollment.course_id == Course.id)
            .join(UserProfile, Course.instructor_id == UserProfile.user_id)
            .outerjoin(MediaAsset, Course.cover_asset_id == MediaAsset.id)
            .where(UserCourseEnrollment.user_id == user_id)
            .where(Course.deleted_at.is_(None))
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query) or 0

        query = query.order_by(UserCourseEnrollment.updated_at.desc()).offset(offset).limit(limit)
        result = await session.execute(query)
        rows = [dict(row._mapping) for row in result]

        return rows, total

    async def get_lesson_progress(
        self,
        session: AsyncSession,
        user_id: int,
        lesson_id: int,
    ) -> UserLessonProgress | None:
        result = await session.execute(
            select(UserLessonProgress)
            .where(UserLessonProgress.user_id == user_id)
            .where(UserLessonProgress.lesson_id == lesson_id)
        )
        return result.scalar_one_or_none()

    async def list_lesson_progress_by_enrollment(
        self,
        session: AsyncSession,
        enrollment_id: int,
    ) -> list[UserLessonProgress]:
        result = await session.execute(
            select(UserLessonProgress)
            .where(UserLessonProgress.enrollment_id == enrollment_id)
        )
        return list(result.scalars().all())
