import { useCallback, useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router";
import {
  ArrowLeft,
  CheckCircle2,
  ChevronRight,
  List,
  Play,
  X,
} from "lucide-react";
import Hls from "hls.js";

import { fetchCourseDetail } from "../lib/learning-api";
import { fetchContentDetail } from "../lib/content";
import type { ContentVideoResponse, CourseDetailResponse, CourseLessonResponse } from "../lib/types";

export function CourseLearn() {
  const navigate = useNavigate();
  const location = useLocation();
  const params = useParams<{ id: string }>();
  const courseId = Number(params.id) || 0;
  const initialLessonIndex = (location.state as { lessonIndex?: number } | null)?.lessonIndex ?? 0;

  const [course, setCourse] = useState<CourseDetailResponse | null>(null);
  const [currentLessonIndex, setCurrentLessonIndex] = useState(initialLessonIndex);
  const [videoContent, setVideoContent] = useState<ContentVideoResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [videoLoading, setVideoLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [error, setError] = useState("");

  const videoRef = useRef<HTMLVideoElement>(null);
  const hlsRef = useRef<Hls | null>(null);

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

  const currentLesson: CourseLessonResponse | null = course?.lessons[currentLessonIndex] ?? null;

  const loadLessonVideo = useCallback(async (lesson: CourseLessonResponse) => {
    if (!lesson.content_item_id) {
      setVideoContent(null);
      return;
    }
    try {
      setVideoLoading(true);
      const content = await fetchContentDetail(lesson.content_item_id, { cache: false });
      setVideoContent(content);
    } catch {
      setVideoContent(null);
    } finally {
      setVideoLoading(false);
    }
  }, []);

  useEffect(() => {
    if (currentLesson) void loadLessonVideo(currentLesson);
  }, [currentLesson, loadLessonVideo]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !videoContent) return;

    if (hlsRef.current) {
      hlsRef.current.destroy();
      hlsRef.current = null;
    }

    const hlsUrl = videoContent.hls_manifest_url;
    const directUrl = videoContent.video_url;

    if (hlsUrl && Hls.isSupported()) {
      const hls = new Hls({ enableWorker: true, lowLatencyMode: false });
      hlsRef.current = hls;
      hls.attachMedia(video);
      hls.loadSource(hlsUrl);
      hls.on(Hls.Events.ERROR, (_event, data) => {
        if (!data?.fatal) return;
        hls.destroy();
        hlsRef.current = null;
        if (directUrl) {
          video.src = directUrl;
          void video.play().catch(() => {});
        }
      });
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        void video.play().catch(() => {});
      });
    } else if (directUrl) {
      video.src = directUrl;
      void video.play().catch(() => {});
    }

    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy();
        hlsRef.current = null;
      }
    };
  }, [videoContent]);

  const selectLesson = (index: number) => {
    setCurrentLessonIndex(index);
    setSidebarOpen(false);
  };

  const handleNext = () => {
    if (course && currentLessonIndex < course.lessons.length - 1) {
      setCurrentLessonIndex(currentLessonIndex + 1);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-900">
        <div className="text-white/60">加载课程中...</div>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-4 bg-gray-900 px-6">
        <p className="text-white/60">{error || "课程不存在"}</p>
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-white"
        >
          返回
        </button>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-gray-900">
      <div className="flex items-center justify-between bg-gray-900/90 px-4 py-3 backdrop-blur">
        <button
          type="button"
          onClick={() => navigate(`/courses/${courseId}`)}
          className="flex items-center gap-1.5 text-sm text-white/70 transition hover:text-white"
        >
          <ArrowLeft className="h-4 w-4" />
          课程详情
        </button>
        <h2 className="max-w-[60%] truncate text-sm font-medium text-white">
          {currentLesson?.title || course.title}
        </h2>
        <button
          type="button"
          onClick={() => setSidebarOpen(true)}
          className="flex items-center gap-1 text-sm text-white/70 transition hover:text-white"
        >
          <List className="h-4 w-4" />
          目录
        </button>
      </div>

      <div className="relative flex-1">
        {videoLoading ? (
          <div className="flex h-full items-center justify-center">
            <div className="text-white/40">加载视频中...</div>
          </div>
        ) : videoContent ? (
          <video
            ref={videoRef}
            controls
            playsInline
            poster={videoContent.cover_url ?? undefined}
            className="h-full w-full object-contain"
          />
        ) : (
          <div className="flex h-full flex-col items-center justify-center gap-3">
            <Play className="h-12 w-12 text-white/20" />
            <p className="text-sm text-white/40">
              {currentLesson ? "该课时暂无视频内容" : "请选择一个课时"}
            </p>
          </div>
        )}
      </div>

      <div className="border-t border-white/10 bg-gray-800/90 px-4 py-3 backdrop-blur">
        <div className="flex items-center justify-between">
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-white">
              {currentLesson?.title || "未选择课时"}
            </p>
            <p className="mt-0.5 text-xs text-white/40">
              {currentLessonIndex + 1} / {course.lessons.length} 课时
              {currentLesson && ` · ${currentLesson.duration_minutes} 分钟`}
            </p>
          </div>
          {course.lessons.length > 0 && currentLessonIndex < course.lessons.length - 1 && (
            <button
              type="button"
              onClick={handleNext}
              className="flex items-center gap-1 rounded-full bg-emerald-500/20 px-3 py-1.5 text-xs font-medium text-emerald-300 transition hover:bg-emerald-500/30"
            >
              下一课
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>

      {sidebarOpen && (
        <div className="fixed inset-0 z-50 flex">
          <div
            className="flex-1 bg-black/50"
            onClick={() => setSidebarOpen(false)}
          />
          <div className="w-80 max-w-[85vw] overflow-y-auto bg-gray-900 shadow-2xl">
            <div className="sticky top-0 flex items-center justify-between border-b border-white/10 bg-gray-900/95 px-4 py-3 backdrop-blur">
              <h3 className="text-sm font-semibold text-white">课时目录</h3>
              <button
                type="button"
                onClick={() => setSidebarOpen(false)}
                className="rounded-lg p-1 text-white/50 transition hover:bg-white/10 hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="divide-y divide-white/5">
              {course.lessons.map((lesson, index) => {
                const isActive = index === currentLessonIndex;
                return (
                  <button
                    key={lesson.id}
                    type="button"
                    onClick={() => selectLesson(index)}
                    className={`flex w-full items-center gap-3 px-4 py-3 text-left transition ${
                      isActive
                        ? "bg-emerald-500/10 text-emerald-300"
                        : "text-white/70 hover:bg-white/5 hover:text-white"
                    }`}
                  >
                    <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-xs font-medium ${
                      isActive ? "bg-emerald-500/20" : "bg-white/10"
                    }`}>
                      {lesson.is_completed ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                      ) : (
                        index + 1
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm">{lesson.title}</p>
                      <p className="mt-0.5 text-xs text-white/30">
                        {lesson.duration_minutes} 分钟
                      </p>
                    </div>
                    {isActive && (
                      <span className="rounded bg-emerald-500/20 px-1.5 py-0.5 text-[10px] text-emerald-300">
                        播放中
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
