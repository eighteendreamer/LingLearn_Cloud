from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginationParams, build_page_response
from app.common.utils import utc_now_naive
from app.core.exceptions import ConflictError, NotFoundError
from app.infra.storage.service import StorageService
from app.modules.content.repository import ContentRepository
from app.modules.course.repository import CourseRepository
from app.modules.course.schemas import (
    CourseCategoryResponse,
    CourseDetailResponse,
    CourseEnrollmentResponse,
    CourseInstructorResponse,
    CourseLessonResponse,
    CourseListItemResponse,
    UserCourseProgressResponse,
    UserLearningDashboardResponse,
)
from app.modules.user.repository import UserRepository


class CourseService:
    def __init__(
        self,
        *,
        repository: CourseRepository | None = None,
        user_repository: UserRepository | None = None,
        content_repository: ContentRepository | None = None,
        storage_service: StorageService | None = None,
    ) -> None:
        self.repository = repository or CourseRepository()
        self.user_repository = user_repository or UserRepository()
        self.content_repository = content_repository or ContentRepository()
        self.storage_service = storage_service or StorageService()

    async def list_courses(
        self,
        session: AsyncSession,
        *,
        viewer_user_id: int | None,
        category_id: int | None,
        pagination: PaginationParams,
    ):
        rows, total = await self.repository.list_courses(
            session,
            category_id=category_id,
            offset=pagination.offset,
            limit=pagination.page_size,
        )

        enrollment_map = {}
        if viewer_user_id:
            course_ids = [row["id"] for row in rows]
            for course_id in course_ids:
                enrollment = await self.repository.get_enrollment(session, viewer_user_id, course_id)
                enrollment_map[course_id] = enrollment is not None

        items = []
        for row in rows:
            cover_url = await self.storage_service.build_access_url(
                object_key=row["cover_object_key"],
                public_url=row["cover_public_url"],
            )
            items.append(
                CourseListItemResponse(
                    id=row["id"],
                    title=row["title"],
                    description=row["description"],
                    instructor=CourseInstructorResponse(
                        user_id=row["instructor_id"],
                        display_name=row["instructor_name"],
                        avatar_url=None,
                    ),
                    category=CourseCategoryResponse(id=row["category_id"], name="") if row["category_id"] else None,
                    cover_url=cover_url,
                    level=row["level"],
                    duration_minutes=row["duration_minutes"],
                    lesson_count=row["lesson_count"],
                    enrollment_count=row["enrollment_count"],
                    rating=row["rating"],
                    is_enrolled=enrollment_map.get(row["id"], False),
                )
            )

        return build_page_response(items, total, pagination)

    async def get_course_detail(
        self,
        session: AsyncSession,
        *,
        course_id: int,
        viewer_user_id: int | None,
    ) -> CourseDetailResponse:
        row = await self.repository.get_course_detail_row(session, course_id)
        if not row:
            raise NotFoundError(message="Course not found.")

        lessons = await self.repository.list_course_lessons(session, course_id)
        enrollment = None
        lesson_progress_map = {}

        if viewer_user_id:
            enrollment = await self.repository.get_enrollment(session, viewer_user_id, course_id)
            if enrollment:
                progress_list = await self.repository.list_lesson_progress_by_enrollment(session, enrollment.id)
                lesson_progress_map = {p.lesson_id: p for p in progress_list}

        cover_url = await self.storage_service.build_access_url(
            object_key=row["cover_object_key"],
            public_url=row["cover_public_url"],
        )

        lesson_responses = []
        for lesson in lessons:
            progress = lesson_progress_map.get(lesson.id)
            lesson_responses.append(
                CourseLessonResponse(
                    id=lesson.id,
                    title=lesson.title,
                    description=lesson.description,
                    duration_minutes=lesson.duration_minutes,
                    sort_order=lesson.sort_order,
                    is_free=lesson.is_free,
                    is_completed=progress.completed if progress else False,
                    progress_percent=progress.progress_percent if progress else 0.0,
                )
            )

        return CourseDetailResponse(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            instructor=CourseInstructorResponse(
                user_id=row["instructor_id"],
                display_name=row["instructor_name"],
                avatar_url=None,
            ),
            category=CourseCategoryResponse(id=row["category_id"], name="") if row["category_id"] else None,
            cover_url=cover_url,
            level=row["level"],
            duration_minutes=row["duration_minutes"],
            lesson_count=row["lesson_count"],
            enrollment_count=row["enrollment_count"],
            rating=row["rating"],
            is_enrolled=enrollment is not None,
            lessons=lesson_responses,
            created_at=row["created_at"],
        )

    async def enroll_course(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        course_id: int,
    ) -> CourseEnrollmentResponse:
        async with session.begin():
            course = await self.repository.get_course_by_id(session, course_id)
            if not course:
                raise NotFoundError(message="Course not found.")

            existing = await self.repository.get_enrollment(session, user_id, course_id)
            if existing:
                raise ConflictError(message="Already enrolled in this course.")

            enrollment = await self.repository.create_enrollment(
                session,
                user_id=user_id,
                course_id=course_id,
                enrolled_at=utc_now_naive(),
            )
            await self.repository.increment_enrollment_count(session, course_id)

        return CourseEnrollmentResponse(
            enrollment_id=enrollment.id,
            course_id=course_id,
            enrolled_at=enrollment.enrolled_at,
        )

    async def get_learning_dashboard(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> UserLearningDashboardResponse:
        bundle = await self.user_repository.get_user_with_profile_and_settings(session, user_id)
        if not bundle:
            raise NotFoundError(message="User not found.")

        _, profile, _ = bundle

        rows, _ = await self.repository.list_user_enrollments(session, user_id, offset=0, limit=5)

        ongoing_courses = []
        for row in rows:
            cover_url = await self.storage_service.build_access_url(
                object_key=row["cover_object_key"],
                public_url=row["cover_public_url"],
            )
            ongoing_courses.append(
                CourseListItemResponse(
                    id=row["course_id"],
                    title=row["title"],
                    description=None,
                    instructor=CourseInstructorResponse(
                        user_id=0,
                        display_name=row["instructor_name"],
                        avatar_url=None,
                    ),
                    category=None,
                    cover_url=cover_url,
                    level="",
                    duration_minutes=0,
                    lesson_count=row["lesson_count"],
                    enrollment_count=0,
                    rating=0.0,
                    is_enrolled=True,
                )
            )

        favorites_rows, favorites_total = await self.content_repository.list_user_favorites(
            session,
            user_id=user_id,
            offset=0,
            limit=5,
        )

        return UserLearningDashboardResponse(
            total_learning_minutes=profile.total_learning_minutes,
            streak_days=profile.streak_days,
            favorites_count=favorites_total,
            completed_goals=2,
            ongoing_courses=ongoing_courses,
            recent_contents=[],
        )

    async def list_user_courses(
        self,
        session: AsyncSession,
        user_id: int,
        pagination: PaginationParams,
    ):
        rows, total = await self.repository.list_user_enrollments(
            session,
            user_id=user_id,
            offset=pagination.offset,
            limit=pagination.page_size,
        )

        items = []
        for row in rows:
            cover_url = await self.storage_service.build_access_url(
                object_key=row["cover_object_key"],
                public_url=row["cover_public_url"],
            )
            items.append(
                UserCourseProgressResponse(
                    id=row["course_id"],
                    title=row["title"],
                    instructor_name=row["instructor_name"],
                    cover_url=cover_url,
                    progress_percent=row["progress_percent"],
                    completed_lessons=row["completed_lessons"],
                    total_lessons=row["lesson_count"],
                    last_studied_at=row["last_studied_at"],
                )
            )

        return build_page_response(items, total, pagination)
