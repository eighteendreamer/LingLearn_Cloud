from datetime import datetime

from pydantic import BaseModel, Field


class CourseInstructorResponse(BaseModel):
    user_id: int
    display_name: str
    avatar_url: str | None


class CourseCategoryResponse(BaseModel):
    id: int
    name: str


class CourseListItemResponse(BaseModel):
    id: int
    title: str
    description: str | None
    instructor: CourseInstructorResponse
    category: CourseCategoryResponse | None
    cover_url: str | None
    level: str
    duration_minutes: int
    lesson_count: int
    enrollment_count: int
    rating: float
    is_enrolled: bool


class CourseLessonResponse(BaseModel):
    id: int
    title: str
    description: str | None
    content_item_id: int | None
    duration_minutes: int
    sort_order: int
    is_free: bool
    is_completed: bool
    progress_percent: float


class CourseDetailResponse(BaseModel):
    id: int
    title: str
    description: str | None
    instructor: CourseInstructorResponse
    category: CourseCategoryResponse | None
    cover_url: str | None
    level: str
    duration_minutes: int
    lesson_count: int
    enrollment_count: int
    rating: float
    is_enrolled: bool
    lessons: list[CourseLessonResponse]
    created_at: datetime


class CourseEnrollmentResponse(BaseModel):
    enrollment_id: int
    course_id: int
    enrolled_at: datetime


class UserLearningDashboardResponse(BaseModel):
    total_learning_minutes: int
    streak_days: int
    favorites_count: int
    completed_goals: int
    ongoing_courses: list[CourseListItemResponse]
    recent_contents: list[dict]


class UserCourseProgressResponse(BaseModel):
    id: int
    title: str
    instructor_name: str
    cover_url: str | None
    progress_percent: float
    completed_lessons: int
    total_lessons: int
    last_studied_at: datetime
