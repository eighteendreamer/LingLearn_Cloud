import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import {
  ArrowLeft,
  BookOpen,
  Clock,
  GraduationCap,
  Play,
  Star,
  Users,
  CheckCircle2,
  Lock,
} from "lucide-react";

import { fetchCourseDetail, enrollCourse } from "../lib/learning-api";
import { hasSession } from "../lib/session";
import type { CourseDetailResponse } from "../lib/types";

function formatLevel(level: string) {
  const map: Record<string, string> = {
    beginner: "入门",
    intermediate: "中级",
    advanced: "高级",
  };
  return map[level] || level;
}

export function CourseDetail() {
  const navigate = useNavigate();
  const params = useParams<{ id: string }>();
  const courseId = Number(params.id) || 0;

  const [course, setCourse] = useState<CourseDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [enrolling, setEnrolling] = useState(false);

  useEffect(() => {
    if (!courseId) return;
    let active = true;

    async function load() {
      try {
        setIsLoading(true);
        const data = await fetchCourseDetail(courseId);
        if (active) setCourse(data);
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : "加载课程失败");
      } finally {
        if (active) setIsLoading(false);
      }
    }

    void load();
    return () => { active = false; };
  }, [courseId]);

  const handleEnroll = async () => {
    if (!hasSession()) {
      navigate("/login");
      return;
    }
    try {
      setEnrolling(true);
      await enrollCourse(courseId);
      setCourse((prev) => prev ? { ...prev, is_enrolled: true, enrollment_count: prev.enrollment_count + 1 } : prev);
    } catch (err) {
      setError(err instanceof Error ? err.message : "报名失败");
    } finally {
      setEnrolling(false);
    }
  };

  const handleStartLearn = () => {
    navigate(`/courses/${courseId}/learn`);
  };

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-50">
        <div className="text-gray-500">加载课程中...</div>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-4 bg-gray-50 px-6">
        <p className="text-gray-500">{error || "课程不存在"}</p>
        <button
          type="button"
          onClick={() => navigate("/my-learning")}
          className="rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-white"
        >
          返回学习
        </button>
      </div>
    );
  }

  const completedLessons = course.lessons.filter((l) => l.is_completed).length;

  return (
    <div className="h-full overflow-y-auto bg-gray-50 pb-24">
      <div className="relative">
        {course.cover_url ? (
          <img
            src={course.cover_url}
            alt={course.title}
            className="h-56 w-full object-cover"
          />
        ) : (
          <div className="flex h-56 w-full items-center justify-center bg-gradient-to-br from-emerald-400 to-teal-600">
            <BookOpen className="h-16 w-16 text-white/60" />
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />

        <button
          type="button"
          onClick={() => navigate("/my-learning")}
          className="absolute left-4 top-4 flex items-center gap-1.5 rounded-full bg-black/30 px-3 py-2 text-sm text-white backdrop-blur"
        >
          <ArrowLeft className="h-4 w-4" />
          返回学习
        </button>

        <div className="absolute bottom-4 left-4 right-4">
          <h1 className="text-xl font-bold text-white drop-shadow">{course.title}</h1>
          <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-white/80">
            <span className="flex items-center gap-1">
              <GraduationCap className="h-3.5 w-3.5" />
              {course.instructor.display_name}
            </span>
            {course.category && (
              <span className="rounded-full bg-white/20 px-2 py-0.5 text-xs backdrop-blur">
                {course.category.name}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-3xl px-4 pt-5">
        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
          <span className="flex items-center gap-1">
            <Star className="h-4 w-4 text-amber-400" />
            {course.rating.toFixed(1)}
          </span>
          <span className="flex items-center gap-1">
            <Users className="h-4 w-4" />
            {course.enrollment_count} 人报名
          </span>
          <span className="flex items-center gap-1">
            <BookOpen className="h-4 w-4" />
            {course.lesson_count} 课时
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            {course.duration_minutes} 分钟
          </span>
          <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-medium text-emerald-700">
            {formatLevel(course.level)}
          </span>
        </div>

        {course.description && (
          <div className="mt-5">
            <h2 className="text-base font-semibold text-gray-900">课程简介</h2>
            <p className="mt-2 whitespace-pre-line text-sm leading-6 text-gray-600">{course.description}</p>
          </div>
        )}

        {course.is_enrolled && completedLessons > 0 && (
          <div className="mt-5 rounded-xl bg-emerald-50 p-4">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-emerald-800">学习进度</span>
              <span className="text-emerald-600">
                {completedLessons} / {course.lesson_count} 课时
              </span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-emerald-200">
              <div
                className="h-full rounded-full bg-emerald-500 transition-all"
                style={{ width: `${course.lesson_count ? (completedLessons / course.lesson_count) * 100 : 0}%` }}
              />
            </div>
          </div>
        )}

        <div className="mt-6">
          <h2 className="text-base font-semibold text-gray-900">课时列表</h2>
          <div className="mt-3 divide-y divide-gray-100 overflow-hidden rounded-xl border border-gray-100 bg-white">
            {course.lessons.map((lesson, index) => (
              <button
                key={lesson.id}
                type="button"
                onClick={() => {
                  if (course.is_enrolled || lesson.is_free) {
                    navigate(`/courses/${courseId}/learn`, { state: { lessonIndex: index } });
                  }
                }}
                disabled={!course.is_enrolled && !lesson.is_free}
                className="flex w-full items-center gap-3 px-4 py-3.5 text-left transition hover:bg-gray-50 disabled:opacity-50"
              >
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-100 text-sm font-medium text-gray-500">
                  {lesson.is_completed ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                  ) : (
                    index + 1
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-gray-900">{lesson.title}</p>
                  <p className="mt-0.5 text-xs text-gray-400">
                    {lesson.duration_minutes} 分钟
                    {lesson.is_free && !course.is_enrolled && (
                      <span className="ml-2 text-emerald-500">免费试看</span>
                    )}
                  </p>
                </div>
                {!course.is_enrolled && !lesson.is_free ? (
                  <Lock className="h-4 w-4 shrink-0 text-gray-300" />
                ) : (
                  <Play className="h-4 w-4 shrink-0 text-gray-400" />
                )}
              </button>
            ))}
            {course.lessons.length === 0 && (
              <div className="px-4 py-8 text-center text-sm text-gray-400">
                暂无课时
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-gray-100 bg-white/90 px-4 py-3 backdrop-blur-xl">
        <div className="mx-auto flex max-w-3xl items-center gap-3">
          {course.is_enrolled ? (
            <button
              type="button"
              onClick={handleStartLearn}
              className="flex-1 rounded-full bg-emerald-500 py-3 text-center text-sm font-semibold text-white shadow-lg transition hover:bg-emerald-600"
            >
              {completedLessons > 0 ? "继续学习" : "开始学习"}
            </button>
          ) : (
            <button
              type="button"
              onClick={handleEnroll}
              disabled={enrolling}
              className="flex-1 rounded-full bg-emerald-500 py-3 text-center text-sm font-semibold text-white shadow-lg transition hover:bg-emerald-600 disabled:opacity-60"
            >
              {enrolling ? "报名中..." : "免费报名"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
