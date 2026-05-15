import type { TouchEvent, WheelEvent } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowLeft,
  Bookmark,
  Heart,
  MessageCircle,
  Play,
  Share2,
  Volume2,
  VolumeX,
} from "lucide-react";
import { useLocation, useNavigate, useParams } from "react-router";

import { fetchFeedVideos, fetchSearchContents, reportWatchProgress } from "../lib/content";
import {
  readDiscoverPersistedState,
  writeDiscoverPersistedState,
  VIDEO_FEED_MUTE_STORAGE_KEY,
  type ContentWatchSource,
  type DiscoverWatchNavigationState,
} from "../lib/discover-watch";
import type { ContentVideoResponse } from "../lib/types";
import { usePageContextActions } from "../page-context";

function formatCount(value: number) {
  if (value >= 10000) {
    return `${(value / 10000).toFixed(1).replace(/\\.0$/, "")}w`;
  }
  return String(value);
}

function formatDuration(seconds?: number | null) {
  if (!seconds || seconds <= 0) {
    return "00:00";
  }
  const whole = Math.floor(seconds);
  const minutes = Math.floor(whole / 60);
  const remain = whole % 60;
  return `${String(minutes).padStart(2, "0")}:${String(remain).padStart(2, "0")}`;
}

function buildFallbackRoute(contentId: number | null) {
  return contentId ? `/discover/watch/${contentId}` : "/discover";
}

function getWatchChrome(source: ContentWatchSource | null) {
  switch (source) {
    case "learning":
      return {
        backLabel: "返回学习",
        sourceLabel: "来自学习",
        fallbackPath: "/my-learning",
      };
    case "profile":
      return {
        backLabel: "返回我的",
        sourceLabel: "来自我的",
        fallbackPath: "/profile",
      };
    case "discover":
    default:
      return {
        backLabel: "返回发现",
        sourceLabel: "来自发现",
        fallbackPath: "/discover",
      };
  }
}

export function DiscoverWatch() {
  const { updatePageContext } = usePageContextActions();
  const navigate = useNavigate();
  const location = useLocation();
  const params = useParams<{ contentId: string }>();
  const navigationState = (location.state ?? null) as DiscoverWatchNavigationState | null;
  const routeContentId = Number(params.contentId ?? 0) || null;
  const chrome = getWatchChrome(navigationState?.source ?? null);

  const [videos, setVideos] = useState<ContentVideoResponse[]>(() => navigationState?.videos ?? []);
  const [isLoading, setIsLoading] = useState(() => !navigationState?.videos?.length);
  const [errorMessage, setErrorMessage] = useState("");
  const [currentIndex, setCurrentIndex] = useState(() => {
    if (!navigationState?.videos?.length) {
      return 0;
    }
    const stateIndex = Math.max(0, Math.min(navigationState.currentIndex, navigationState.videos.length - 1));
    if (!routeContentId) {
      return stateIndex;
    }
    const matchedIndex = navigationState.videos.findIndex((item) => item.id === routeContentId);
    return matchedIndex >= 0 ? matchedIndex : stateIndex;
  });
  const [isMuted, setIsMuted] = useState(() => {
    if (typeof window === "undefined") {
      return true;
    }
    const stored = window.localStorage.getItem(VIDEO_FEED_MUTE_STORAGE_KEY);
    if (stored === null) {
      return true;
    }
    return stored === "1";
  });
  const [isPlaying, setIsPlaying] = useState(true);
  const [actionMessage, setActionMessage] = useState("");

  const touchStartY = useRef(0);
  const videoRefs = useRef<(HTMLVideoElement | null)[]>([]);
  const watchReportedSecondsRef = useRef<Record<number, number>>({});
  const wheelLockedRef = useRef(false);

  const currentVideo = videos[currentIndex] ?? null;
  const canMovePrev = currentIndex > 0;
  const canMoveNext = currentIndex < videos.length - 1;

  const visibleIndicatorCount = useMemo(() => Math.min(videos.length, 8), [videos.length]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    window.localStorage.setItem(VIDEO_FEED_MUTE_STORAGE_KEY, isMuted ? "1" : "0");
  }, [isMuted]);

  useEffect(() => {
    const fallbackState = navigationState?.persistedState ?? readDiscoverPersistedState();
    writeDiscoverPersistedState(fallbackState);
  }, [navigationState]);

  useEffect(() => {
    let cancelled = false;

    async function loadFallbackVideos() {
      if (navigationState?.videos?.length) {
        return;
      }

      try {
        setIsLoading(true);
        const persistedState = readDiscoverPersistedState();
        const response =
          persistedState.searchQuery.trim() || persistedState.selectedCategoryId
            ? await fetchSearchContents({
                keyword: persistedState.searchQuery.trim() || undefined,
                categoryId: persistedState.selectedCategoryId,
                pageSize: 8,
              })
            : await fetchFeedVideos(undefined, "hot", persistedState.selectedCategoryId, {
                cache: false,
              });

        if (cancelled) {
          return;
        }

        const nextVideos = "list" in response ? response.list.slice(0, 8) : [];
        setVideos(nextVideos);

        const matchedIndex = routeContentId
          ? nextVideos.findIndex((item) => item.id === routeContentId)
          : -1;
        setCurrentIndex(matchedIndex >= 0 ? matchedIndex : 0);
        setErrorMessage("");
      } catch (error) {
        if (cancelled) {
          return;
        }

        setErrorMessage(error instanceof Error ? error.message : "发现播放页加载失败");
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadFallbackVideos();
    return () => {
      cancelled = true;
    };
  }, [navigationState, routeContentId]);

  useEffect(() => {
    updatePageContext({
      page_type: "discover_watch",
      page_title: currentVideo ? `发现播放 · ${currentVideo.title}` : "发现播放",
      summary: currentVideo
        ? `正在从发现页播放视频《${currentVideo.title}》，可以继续围绕当前内容进行学习和问答。`
        : "正在浏览发现页的沉浸式视频播放。",
      current_video: currentVideo
        ? {
            content_id: currentVideo.id,
            title: currentVideo.title,
            summary: currentVideo.summary,
            category_name: currentVideo.category?.name ?? null,
            author_name: currentVideo.author.display_name,
            hashtags: currentVideo.hashtags ?? [],
            has_quiz: currentVideo.has_quiz,
            quiz_count: currentVideo.quiz_count,
            duration_seconds: currentVideo.duration_seconds,
            video_url: currentVideo.video_url,
          }
        : null,
      available_actions: [],
      metadata: {
        section: "discover",
        current_index: currentIndex,
        visible_video_count: videos.length,
      },
    });
  }, [currentIndex, currentVideo, updatePageContext, videos.length]);

  useEffect(() => {
    videos.forEach((video, index) => {
      const element = videoRefs.current[index];
      if (!element) {
        return;
      }

      element.muted = isMuted;
      if (index === currentIndex && isPlaying) {
        void element.play().catch(() => {});
        return;
      }

      element.pause();
    });
  }, [currentIndex, isMuted, isPlaying, videos]);

  useEffect(() => {
    return () => {
      const activeVideo = videos[currentIndex];
      const element = videoRefs.current[currentIndex];
      if (!activeVideo || !element) {
        return;
      }

      const watchSeconds = Math.floor(element.currentTime || 0);
      const duration = Math.floor(element.duration || activeVideo.duration_seconds || 0);
      if (!watchSeconds || !duration) {
        return;
      }

      void reportWatchProgress(activeVideo.id, {
        watch_seconds: watchSeconds,
        watch_progress: Number(((watchSeconds / duration) * 100).toFixed(2)),
        last_position_seconds: watchSeconds,
        completed: watchSeconds >= duration - 1,
      }).catch(() => {});
    };
  }, [currentIndex, videos]);

  const attemptAutoplay = async (element: HTMLVideoElement) => {
    try {
      await element.play();
    } catch (error) {
      const canRetryMuted = error instanceof DOMException && error.name === "NotAllowedError" && !element.muted;
      if (!canRetryMuted) {
        return;
      }

      element.muted = true;
      setIsMuted(true);
      await element.play().catch(() => {});
    }
  };

  const submitWatchProgress = (index: number) => {
    const video = videos[index];
    const element = videoRefs.current[index];
    if (!video || !element) {
      return;
    }

    const watchSeconds = Math.floor(element.currentTime || 0);
    const duration = Math.floor(element.duration || video.duration_seconds || 0);
    const previousReported = watchReportedSecondsRef.current[video.id] ?? 0;
    if (!watchSeconds || !duration || watchSeconds <= previousReported) {
      return;
    }

    watchReportedSecondsRef.current[video.id] = watchSeconds;
    void reportWatchProgress(video.id, {
      watch_seconds: watchSeconds,
      watch_progress: Number(((watchSeconds / duration) * 100).toFixed(2)),
      last_position_seconds: watchSeconds,
      completed: watchSeconds >= duration - 1,
    }).catch(() => {});
  };

  const handleMove = (direction: "prev" | "next") => {
    setCurrentIndex((previous) => {
      if (direction === "prev") {
        return Math.max(0, previous - 1);
      }
      return Math.min(videos.length - 1, previous + 1);
    });
    setIsPlaying(true);
  };

  const handleTouchStart = (event: TouchEvent<HTMLDivElement>) => {
    touchStartY.current = event.changedTouches[0]?.clientY ?? 0;
  };

  const handleTouchEnd = (event: TouchEvent<HTMLDivElement>) => {
    const nextY = event.changedTouches[0]?.clientY ?? 0;
    const delta = touchStartY.current - nextY;
    if (Math.abs(delta) < 60) {
      return;
    }

    if (delta > 0 && canMoveNext) {
      handleMove("next");
    } else if (delta < 0 && canMovePrev) {
      handleMove("prev");
    }
  };

  const handleWheel = (event: WheelEvent<HTMLDivElement>) => {
    if (wheelLockedRef.current || Math.abs(event.deltaY) < 24) {
      return;
    }

    wheelLockedRef.current = true;
    if (event.deltaY > 0 && canMoveNext) {
      handleMove("next");
    } else if (event.deltaY < 0 && canMovePrev) {
      handleMove("prev");
    }

    window.setTimeout(() => {
      wheelLockedRef.current = false;
    }, 420);
  };

  const handleBack = () => {
    if (navigationState?.source) {
      navigate(-1);
      return;
    }
    navigate(chrome.fallbackPath, { replace: true });
  };

  const handleShare = async () => {
    if (!currentVideo) {
      return;
    }

    const shareUrl = `${window.location.origin}${buildFallbackRoute(currentVideo.id)}`;

    try {
      if (navigator.share) {
        await navigator.share({
          title: currentVideo.title,
          text: currentVideo.summary ?? currentVideo.title,
          url: shareUrl,
        });
      } else if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(shareUrl);
      }
      setActionMessage("链接已准备好，可以继续分享了");
    } catch {
      setActionMessage("暂时无法分享这条视频");
    }
  };

  useEffect(() => {
    if (!actionMessage) {
      return;
    }

    const timer = window.setTimeout(() => setActionMessage(""), 2200);
    return () => window.clearTimeout(timer);
  }, [actionMessage]);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center bg-black text-white">
        正在加载发现视频...
      </div>
    );
  }

  if (errorMessage || !videos.length) {
    return (
      <div className="flex h-full items-center justify-center bg-black px-6 text-white">
        <div className="max-w-md rounded-3xl border border-white/10 bg-white/5 p-6 text-center backdrop-blur">
          <h2 className="text-lg font-semibold">发现播放页暂时不可用</h2>
          <p className="mt-2 text-sm text-white/70">{errorMessage || "没有可播放的视频内容"}</p>
          <button
            type="button"
            onClick={handleBack}
            className="mt-5 rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-white"
          >
            返回发现
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className="relative h-full overflow-hidden bg-black"
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      onWheel={handleWheel}
    >
      <div className="absolute left-0 right-0 top-0 z-30 flex items-center justify-between bg-gradient-to-b from-black/70 via-black/25 to-transparent px-4 pb-8 pt-4">
        <button
          type="button"
          onClick={handleBack}
          className="flex items-center gap-2 rounded-full border border-white/15 bg-black/35 px-3 py-2 text-sm font-medium text-white backdrop-blur"
        >
          <ArrowLeft className="h-4 w-4" />
          {chrome.backLabel}
        </button>
        <div className="rounded-full border border-emerald-400/30 bg-emerald-500/15 px-3 py-2 text-xs font-semibold text-emerald-100 backdrop-blur">
          {chrome.sourceLabel}
        </div>
      </div>

      {actionMessage ? (
        <div className="absolute left-1/2 top-20 z-40 -translate-x-1/2 rounded-full bg-black/65 px-4 py-2 text-sm text-white backdrop-blur">
          {actionMessage}
        </div>
      ) : null}

      <div
        className="absolute inset-0 transition-transform duration-500 ease-out"
        style={{ transform: `translateY(-${currentIndex * 100}%)` }}
      >
        {videos.map((video, index) => {
          const isActive = index === currentIndex;
          const shouldAttachSource = Math.abs(index - currentIndex) <= 1;
          const sourceUrl = shouldAttachSource ? video.video_url || video.hls_manifest_url || undefined : undefined;

          return (
            <div
              key={video.id}
              className="relative flex h-full min-h-full w-full items-center justify-center bg-black"
              onClick={() => {
                if (!isActive) {
                  return;
                }
                setIsPlaying((previous) => !previous);
              }}
            >
              <div
                className="absolute inset-0 bg-cover bg-center opacity-70 blur-2xl scale-110"
                style={{ backgroundImage: video.cover_url ? `url(${video.cover_url})` : undefined }}
              />
              <video
                ref={(element) => {
                  videoRefs.current[index] = element;
                }}
                src={sourceUrl}
                loop
                playsInline
                muted={isMuted}
                poster={video.cover_url ?? undefined}
                preload={isActive ? "metadata" : "none"}
                onCanPlay={(event) => {
                  if (isActive && isPlaying) {
                    void attemptAutoplay(event.currentTarget);
                  }
                }}
                onPause={() => {
                  if (isActive) {
                    submitWatchProgress(index);
                  }
                }}
                className="absolute inset-0 h-full w-full object-contain"
              />

              {!isPlaying && isActive ? (
                <div className="absolute inset-0 z-20 flex items-center justify-center">
                  <div className="flex h-20 w-20 items-center justify-center rounded-full bg-white/80 shadow-lg backdrop-blur-sm">
                    <Play className="ml-1 h-10 w-10 text-emerald-600" />
                  </div>
                </div>
              ) : null}

              <div className="absolute inset-0 z-10 bg-gradient-to-b from-black/15 via-transparent to-black/60" />

              <div className="absolute bottom-0 left-0 right-0 z-20 p-4 pb-12 md:pb-8">
                <div className="flex items-end justify-between gap-4">
                  <div className="max-w-[min(70vw,34rem)]">
                    <div className="mb-3 flex items-center gap-3">
                      <img
                        src={video.author.avatar_url || "https://api.dicebear.com/7.x/avataaars/svg?seed=discover-watch"}
                        alt={video.author.display_name}
                        className="h-12 w-12 rounded-full border-2 border-white/80 shadow-lg"
                      />
                      <div className="min-w-0">
                        <p className="truncate text-base font-bold text-white">{video.author.display_name}</p>
                        <p className="truncate text-sm text-white/75">{video.category?.name || "未分类"}</p>
                      </div>
                    </div>

                    <h1 className="text-lg font-bold text-white drop-shadow md:text-xl">{video.title}</h1>
                    <p className="mt-2 line-clamp-3 text-sm leading-6 text-white/85">
                      {video.summary || "这条内容还没有补充简介，先开始看视频吧。"}
                    </p>

                    <div className="mt-3 flex flex-wrap items-center gap-2">
                      <span className="rounded-full bg-white/15 px-3 py-1 text-xs font-medium text-white backdrop-blur">
                        {formatDuration(video.duration_seconds)}
                      </span>
                      {(video.hashtags || []).slice(0, 3).map((tag) => (
                        <span
                          key={tag}
                          className="rounded-full bg-white/10 px-3 py-1 text-xs font-medium text-white/85 backdrop-blur"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div
                    onClick={(event) => event.stopPropagation()}
                    className="flex shrink-0 flex-col items-center gap-3 rounded-[28px] border border-white/10 bg-black/20 px-2 py-3 shadow-2xl backdrop-blur-md"
                  >
                    <div className="flex flex-col items-center gap-1.5">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/95 shadow-lg">
                        <Heart className="h-6 w-6 text-gray-700" />
                      </div>
                      <span className="rounded-full bg-black/45 px-2 py-0.5 text-[11px] font-semibold text-white">
                        {formatCount(video.interaction.likes_count)}
                      </span>
                    </div>

                    <div className="flex flex-col items-center gap-1.5">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/95 shadow-lg">
                        <MessageCircle className="h-6 w-6 text-gray-700" />
                      </div>
                      <span className="rounded-full bg-black/45 px-2 py-0.5 text-[11px] font-semibold text-white">
                        {formatCount(video.interaction.comments_count)}
                      </span>
                    </div>

                    <div className="flex flex-col items-center gap-1.5">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/95 shadow-lg">
                        <Bookmark className="h-6 w-6 text-gray-700" />
                      </div>
                      <span className="rounded-full bg-black/45 px-2 py-0.5 text-[11px] font-semibold text-white">
                        {formatCount(video.interaction.favorites_count)}
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation();
                        void handleShare();
                      }}
                      className="flex flex-col items-center gap-1.5"
                    >
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/95 shadow-lg">
                        <Share2 className="h-6 w-6 text-gray-700" />
                      </div>
                      <span className="rounded-full bg-black/45 px-2 py-0.5 text-[11px] font-semibold text-white">
                        {formatCount(video.interaction.shares_count)}
                      </span>
                    </button>

                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation();
                        setIsMuted((previous) => !previous);
                      }}
                      className="flex flex-col items-center gap-1.5"
                    >
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/95 shadow-lg">
                        {isMuted ? <VolumeX className="h-6 w-6 text-gray-700" /> : <Volume2 className="h-6 w-6 text-gray-700" />}
                      </div>
                      <span className="rounded-full bg-black/45 px-2 py-0.5 text-[11px] font-semibold text-white">
                        {isMuted ? "静音" : "声音"}
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="absolute left-1/2 top-6 z-30 flex -translate-x-1/2 gap-1">
        {Array.from({ length: visibleIndicatorCount }).map((_, index) => {
          const isActive = index === Math.min(currentIndex, visibleIndicatorCount - 1);
          return (
            <div
              key={index}
              className={`h-1 rounded-full transition-all ${isActive ? "w-8 bg-emerald-500" : "w-1 bg-white/45"}`}
            />
          );
        })}
      </div>
    </div>
  );
}
