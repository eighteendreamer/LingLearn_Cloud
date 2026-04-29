import { useEffect, useRef, useState } from "react";
import {
  Bookmark,
  Heart,
  MessageCircle,
  Play,
  Search,
  Share2,
  Volume2,
  VolumeX,
} from "lucide-react";
import { Link } from "react-router";

import { fetchFeedVideos } from "../lib/content";
import type { ContentVideoResponse } from "../lib/types";

function formatCount(value: number) {
  if (value >= 10000) {
    return `${(value / 10000).toFixed(1)}w`;
  }
  return String(value);
}

function formatDuration(seconds: number | null) {
  if (!seconds || seconds <= 0) {
    return "00:00";
  }
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(remainder).padStart(2, "0")}`;
}

export function VideoFeed() {
  const [videos, setVideos] = useState<ContentVideoResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(true);
  const [videoStates, setVideoStates] = useState<
    Array<{ isLiked: boolean; isSaved: boolean; likes: number }>
  >([]);

  const videoRefs = useRef<(HTMLVideoElement | null)[]>([]);
  const touchStartY = useRef(0);

  useEffect(() => {
    let cancelled = false;

    async function loadFeed() {
      try {
        setIsLoading(true);
        const response = await fetchFeedVideos();
        if (cancelled) {
          return;
        }
        setVideos(response.list);
        setVideoStates(
          response.list.map((item) => ({
            isLiked: item.interaction.liked,
            isSaved: item.interaction.favorited,
            likes: item.interaction.likes_count,
          })),
        );
        setErrorMessage("");
      } catch (error) {
        if (cancelled) {
          return;
        }
        const message = error instanceof Error ? error.message : "加载首页 feed 失败。";
        setErrorMessage(message);
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadFeed();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    videoRefs.current.forEach((video, index) => {
      if (!video) {
        return;
      }
      if (index === currentIndex && isPlaying) {
        void video.play().catch(() => {});
      } else {
        video.pause();
      }
    });
  }, [currentIndex, isPlaying, videos.length]);

  useEffect(() => {
    videoRefs.current.forEach((video) => {
      if (video) {
        video.muted = isMuted;
      }
    });
  }, [isMuted]);

  useEffect(() => {
    const handleWheel = (event: WheelEvent) => {
      if (!videos.length) {
        return;
      }
      event.preventDefault();
      if (event.deltaY > 0) {
        setCurrentIndex((prev) => Math.min(prev + 1, videos.length - 1));
      } else {
        setCurrentIndex((prev) => Math.max(prev - 1, 0));
      }
    };

    window.addEventListener("wheel", handleWheel, { passive: false });
    return () => window.removeEventListener("wheel", handleWheel);
  }, [videos.length]);

  const handleTouchStart = (event: React.TouchEvent) => {
    touchStartY.current = event.touches[0].clientY;
  };

  const handleTouchEnd = (event: React.TouchEvent) => {
    const diff = touchStartY.current - event.changedTouches[0].clientY;
    if (Math.abs(diff) < 50) {
      return;
    }
    if (diff > 0) {
      setCurrentIndex((prev) => Math.min(prev + 1, videos.length - 1));
    } else {
      setCurrentIndex((prev) => Math.max(prev - 1, 0));
    }
  };

  const handleLike = () => {
    setVideoStates((prev) =>
      prev.map((item, index) =>
        index === currentIndex
          ? {
              ...item,
              isLiked: !item.isLiked,
              likes: item.isLiked ? item.likes - 1 : item.likes + 1,
            }
          : item,
      ),
    );
  };

  const handleSave = () => {
    setVideoStates((prev) =>
      prev.map((item, index) =>
        index === currentIndex ? { ...item, isSaved: !item.isSaved } : item,
      ),
    );
  };

  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50">
        <div className="text-gray-900">加载首页 feed 中...</div>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50 px-6">
        <div className="max-w-md rounded-2xl border border-red-100 bg-white p-6 text-center shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">首页内容暂时不可用</h2>
          <p className="mt-2 text-sm text-gray-600">{errorMessage}</p>
        </div>
      </div>
    );
  }

  if (!videos.length) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50 px-6">
        <div className="max-w-md rounded-2xl border border-emerald-100 bg-white p-6 text-center shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">首页还没有视频</h2>
          <p className="mt-2 text-sm text-gray-600">先去创作中心发布一条内容吧。</p>
          <Link
            to="/create"
            className="mt-4 inline-flex rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-white"
          >
            去发布
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div
      className="relative h-screen w-screen overflow-hidden bg-black"
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      <div className="absolute left-0 right-0 top-0 z-30 flex items-center justify-between bg-gradient-to-b from-black/50 to-transparent px-4 pb-8 pt-3">
        <div className="flex items-center gap-6">
          <span className="text-base font-bold text-white/60">关注</span>
          <span className="text-base font-bold text-white">
            推荐
            <div className="mx-auto mt-1 h-0.5 w-6 rounded-full bg-white" />
          </span>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/discover">
            <Search className="h-6 w-6 text-white" />
          </Link>
          <Link
            to="/create"
            className="rounded-full border border-white/30 bg-white/20 px-3 py-2 text-xs font-bold text-white backdrop-blur-sm"
          >
            发布
          </Link>
        </div>
      </div>

      <div
        className="absolute inset-0 transition-transform duration-500 ease-out"
        style={{ transform: `translateY(-${currentIndex * 100}vh)` }}
      >
        {videos.map((video, index) => {
          const state = videoStates[index];
          return (
            <div
              key={video.id}
              className="relative flex h-screen w-screen items-center justify-center bg-black"
              onClick={() => setIsPlaying((prev) => !prev)}
            >
              {video.video_url ? (
                <video
                  ref={(element) => {
                    videoRefs.current[index] = element;
                  }}
                  className="absolute inset-0 h-full w-full object-cover"
                  src={video.video_url}
                  loop
                  playsInline
                  poster={video.cover_url ?? undefined}
                />
              ) : (
                <div
                  className="absolute inset-0 bg-cover bg-center"
                  style={{ backgroundImage: video.cover_url ? `url(${video.cover_url})` : undefined }}
                />
              )}

              {!isPlaying && index === currentIndex ? (
                <div className="absolute inset-0 z-20 flex items-center justify-center">
                  <div className="flex h-20 w-20 items-center justify-center rounded-full bg-white/80 shadow-lg backdrop-blur-sm">
                    <Play className="ml-1 h-10 w-10 text-emerald-600" />
                  </div>
                </div>
              ) : null}

              <div className="absolute inset-0 z-10 bg-gradient-to-b from-black/10 via-transparent to-black/50" />

              <div className="absolute bottom-0 left-0 right-0 z-20 p-4 pb-24">
                <div className="mb-3 flex items-center gap-3">
                  <img
                    src={
                      video.author.avatar_url ||
                      "https://api.dicebear.com/7.x/avataaars/svg?seed=linglearn"
                    }
                    alt={video.author.display_name}
                    className="h-12 w-12 rounded-full border-2 border-white/80 shadow-lg"
                  />
                  <div className="flex-1">
                    <h3 className="font-bold text-white drop-shadow-lg">
                      {video.author.display_name}
                    </h3>
                    <p className="text-sm text-white/80 drop-shadow">
                      {video.category?.name || "未分类"}
                    </p>
                  </div>
                </div>

                <h2 className="mb-2 text-lg font-bold text-white drop-shadow-lg">{video.title}</h2>
                <p className="mb-3 text-sm leading-relaxed text-white/90 drop-shadow">
                  {video.summary || "这条内容还没有补充描述。"}
                </p>

                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1.5 rounded-lg bg-white/20 px-3 py-1.5 backdrop-blur-sm">
                    <Play className="h-3.5 w-3.5 text-white" />
                    <span className="text-xs font-medium text-white">
                      {formatDuration(video.duration_seconds)}
                    </span>
                  </div>
                  {video.category?.name ? (
                    <div className="rounded-lg bg-white/20 px-3 py-1.5 backdrop-blur-sm">
                      <span className="text-xs font-medium text-white"># {video.category.name}</span>
                    </div>
                  ) : null}
                </div>
              </div>

              <div className="absolute bottom-32 right-4 z-20 flex flex-col items-center gap-5">
                <button onClick={handleLike} className="flex flex-col items-center gap-1.5">
                  <div
                    className={`flex h-12 w-12 items-center justify-center rounded-xl shadow-lg ${
                      state?.isLiked
                        ? "bg-gradient-to-br from-red-500 to-pink-500"
                        : "bg-white"
                    }`}
                  >
                    <Heart
                      className={`h-6 w-6 ${
                        state?.isLiked ? "fill-white text-white" : "text-gray-700"
                      }`}
                    />
                  </div>
                  <span className="rounded-lg bg-white/80 px-2 py-0.5 text-xs font-medium text-gray-900 shadow-sm">
                    {formatCount(state?.likes ?? video.interaction.likes_count)}
                  </span>
                </button>

                <div className="flex flex-col items-center gap-1.5">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white shadow-lg">
                    <MessageCircle className="h-6 w-6 text-gray-700" />
                  </div>
                  <span className="rounded-lg bg-white/80 px-2 py-0.5 text-xs font-medium text-gray-900 shadow-sm">
                    {formatCount(video.interaction.comments_count)}
                  </span>
                </div>

                <button onClick={handleSave} className="flex flex-col items-center gap-1.5">
                  <div
                    className={`flex h-12 w-12 items-center justify-center rounded-xl shadow-lg ${
                      state?.isSaved
                        ? "bg-gradient-to-br from-yellow-500 to-orange-500"
                        : "bg-white"
                    }`}
                  >
                    <Bookmark
                      className={`h-6 w-6 ${
                        state?.isSaved ? "fill-white text-white" : "text-gray-700"
                      }`}
                    />
                  </div>
                  <span className="rounded-lg bg-white/80 px-2 py-0.5 text-xs font-medium text-gray-900 shadow-sm">
                    收藏
                  </span>
                </button>

                <div className="flex flex-col items-center gap-1.5">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white shadow-lg">
                    <Share2 className="h-6 w-6 text-gray-700" />
                  </div>
                  <span className="rounded-lg bg-white/80 px-2 py-0.5 text-xs font-medium text-gray-900 shadow-sm">
                    {formatCount(video.interaction.shares_count)}
                  </span>
                </div>

                <button
                  onClick={(event) => {
                    event.stopPropagation();
                    setIsMuted((prev) => !prev);
                  }}
                  className="flex flex-col items-center gap-1.5"
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white shadow-lg">
                    {isMuted ? (
                      <VolumeX className="h-6 w-6 text-gray-700" />
                    ) : (
                      <Volume2 className="h-6 w-6 text-gray-700" />
                    )}
                  </div>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="absolute left-1/2 top-6 z-30 flex -translate-x-1/2 gap-1">
        {videos.map((_, index) => (
          <div
            key={index}
            className={`h-1 rounded-full transition-all ${
              index === currentIndex ? "w-8 bg-emerald-500" : "w-1 bg-gray-400"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
