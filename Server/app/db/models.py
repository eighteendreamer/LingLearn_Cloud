from app.db.base import Base
from app.modules.ai_chat.models import AIChatSession, AIChatMessage
from app.modules.ai_chat.workflow_models import AIWorkflowRun
from app.modules.assessment.models import AssessmentSnapshot
from app.modules.auth.models import UserRefreshToken, User
from app.modules.content.models import ContentCategory, Tag, ContentItem, ContentItemTag, ContentLike, \
    ContentFavorite, ContentComment, ContentShare, ContentViewHistory, ContentQuiz, ContentQuizOption, \
    ContentQuizAttempt
from app.modules.course.models import Course, UserCourseEnrollment, CourseLesson, UserLessonProgress
from app.modules.learning_path.models import (
    LearningPath,
    LearningPathNode,
    LearningPathNodeDimensionLink,
    SkillDimension,
    UserLearningPath,
    UserLearningPathNode,
    UserSkillScore,
    UserSkillSnapshot,
)
from app.modules.notification.models import Notification
from app.modules.practice.models import QuestionBank, Question, QuestionOption, PracticeSession, PracticeAnswer
from app.modules.recommendation.models import UserCategoryInterestProfile, UserTagInterestProfile, \
    ContentRecommendationImpression, UserAuthorInterestProfile
from app.modules.report.models import MonthlyReport, ReportAchievement
from app.modules.resource.models import Resource, UserResourceAccess
from app.modules.storage.models import MediaAsset
from app.modules.user.models import UserProfile, UserSettings, UserFollowRelation


__all__ = [
    "Base",
    "User",
    "UserRefreshToken",
    "MediaAsset",
    "ContentCategory",
    "Tag",
    "ContentItem",
    "ContentItemTag",
    "ContentLike",
    "ContentFavorite",
    "ContentComment",
    "ContentShare",
    "ContentViewHistory",
    "ContentQuiz",
    "ContentQuizOption",
    "ContentQuizAttempt",
    "UserCategoryInterestProfile",
    "UserTagInterestProfile",
    "UserAuthorInterestProfile",
    "ContentRecommendationImpression",
    "UserProfile",
    "UserSettings",
    "UserFollowRelation",
    "Course",
    "CourseLesson",
    "UserCourseEnrollment",
    "UserLessonProgress",
    "Resource",
    "UserResourceAccess",
    "QuestionBank",
    "Question",
    "QuestionOption",
    "PracticeSession",
    "PracticeAnswer",
    "AssessmentSnapshot",
    "SkillDimension",
    "UserSkillSnapshot",
    "UserSkillScore",
    "LearningPath",
    "LearningPathNode",
    "LearningPathNodeDimensionLink",
    "UserLearningPath",
    "UserLearningPathNode",
    "MonthlyReport",
    "ReportAchievement",
    "Notification",
    "AIChatSession",
    "AIChatMessage",
    "AIWorkflowRun",
]
