import type { MouseEvent, TouchEvent } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  Bookmark,
  ChevronDown,
  ChevronUp,
  Heart,
  MessageCircle,
  Play,
  Plus,
  Search,
  Share2,
  Volume2,
  VolumeX,
} from "lucide-react";
import { Link } from "react-router";

import { followUser, unfollowUser } from "../lib/account";
import {
  createContentComment,
  favoriteContent,
  fetchContentComments,
  fetchFeedVideos,
  likeContent,
  reportWatchProgress,
  shareContent,
  unfavoriteContent,
  unlikeContent,
} from "../lib/content";
import { hasSession } from "../lib/session";
import type {
  ContentCommentResponse,
  ContentInteractionResponse,
  ContentVideoResponse,
} from "../lib/types";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
} from "./ui/drawer";
import { Textarea } from "./ui/textarea";

const MUTE_STORAGE_KEY = "linglearn.cloud.video-feed.muted";

type FeedMode = "for_you" | "following";

type VideoInteractionState = {
  liked: boolean;
  favorited: boolean;
  likesCount: number;
  commentsCount: number;
  favoritesCount: number;
  sharesCount: number;
};

type CommentThread = {
  root: ContentCommentResponse;
  replies: ContentCommentResponse[];
};

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

function formatCommentTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return `${date.getMonth() + 1}-${date.getDate()} ${String(date.getHours()).padStart(2, "0")}:${String(
    date.getMinutes(),
  ).padStart(2, "0")}`;
}

function buildInitialInteractionState(video: ContentVideoResponse): VideoInteractionState {
  return {
    liked: video.interaction.liked,
    favorited: video.interaction.favorited,
    likesCount: video.interaction.likes_count,
    commentsCount: video.interaction.comments_count,
    favoritesCount: video.interaction.favorites_count,
    sharesCount: video.interaction.shares_count,
  };
}

function buildCommentThreads(items: ContentCommentResponse[]): CommentThread[] {
  const roots = items
    .filter((item) => item.parent_id === null)
    .sort((left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime());

  const repliesByRootId = items
    .filter((item) => item.parent_id !== null)
    .reduce<Record<number, ContentCommentResponse[]>>((accumulator, item) => {
      const rootId = item.root_id ?? item.parent_id ?? item.id;
      const bucket = accumulator[rootId] ?? [];
      bucket.push(item);
      accumulator[rootId] = bucket;
      return accumulator;
    }, {});

  Object.values(repliesByRootId).forEach((bucket) => {
    bucket.sort((left, right) => new Date(left.created_at).getTime() - new Date(right.created_at).getTime());
  });

  return roots.map((root) => ({
    root,
    replies: repliesByRootId[root.id] ?? [],
  }));
}

export function VideoFeed() {
  const [videos, setVideos] = useState<ContentVideoResponse[]>([]);
  const [feedMode, setFeedMode] = useState<FeedMode>("for_you");
  const [interactionState, setInteractionState] = useState<Record<number, VideoInteractionState>>({});
  const [followState, setFollowState] = useState<Record<number, boolean>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [actionMessage, setActionMessage] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isMuted, setIsMuted] = useState(() => {
    if (typeof window === "undefined") {
      return false;
    }
    return window.localStorage.getItem(MUTE_STORAGE_KEY) === "1";
  });
  const [isPlaying, setIsPlaying] = useState(true);
  const [pendingAction, setPendingAction] = useState("");
  const [isCommentOpen, setIsCommentOpen] = useState(false);
  const [comments, setComments] = useState<ContentCommentResponse[]>([]);
  const [commentPage, setCommentPage] = useState(1);
  const [commentHasMore, setCommentHasMore] = useState(false);
  const [commentLoading, setCommentLoading] = useState(false);
  const [commentSubmitting, setCommentSubmitting] = useState(false);
  const [commentDraft, setCommentDraft] = useState("");
  const [commentError, setCommentError] = useState("");
  const [replyTarget, setReplyTarget] = useState<ContentCommentResponse | null>(null);
  const [expandedReplyRootIds, setExpandedReplyRootIds] = useState<number[]>([]);

  const videoRefs = useRef<(HTMLVideoElement | null)[]>([]);
  const touchStartY = useRef(0);
  const previousActiveVideoIdRef = useRef<number | null>(null);
  const watchReportedSecondsRef = useRef<Record<number, number>>({});

  const currentVideo = videos[currentIndex] ?? null;
  const currentInteraction = currentVideo
    ? interactionState[currentVideo.id] ?? buildInitialInteractionState(currentVideo)
    : null;
  const commentThreads = useMemo(() => buildCommentThreads(comments), [comments]);

  useEffect(() => {
    let cancelled = false;

    async function loadFeed() {
      try {
        setIsLoading(true);
        const response = await fetchFeedVideos(undefined, feedMode);
        if (cancelled) {
          return;
        }
        setVideos(response.list);
        setCurrentIndex(0);
        setInteractionState(
          response.list.reduce<Record<number, VideoInteractionState>>((accumulator, item) => {
            accumulator[item.id] = buildInitialInteractionState(item);
            return accumulator;
          }, {}),
        );
        setFollowState(
          response.list.reduce<Record<number, boolean>>((accumulator, item) => {
            accumulator[item.author.user_id] = item.author.is_following;
            return accumulator;
          }, {}),
        );
        setErrorMessage("");
      } catch (error) {
        if (cancelled) {
          return;
        }
        setErrorMessage(error instanceof Error ? error.message : "加载首页失败");
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
  }, [feedMode]);

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
    if (typeof window !== "undefined") {
      window.localStorage.setItem(MUTE_STORAGE_KEY, isMuted ? "1" : "0");
    }
  }, [isMuted]);

  useEffect(() => {
    const handleWheel = (event: WheelEvent) => {
      if (!videos.length || isCommentOpen) {
        return;
      }
      event.preventDefault();
      if (event.deltaY > 0) {
        setCurrentIndex((previous) => Math.min(previous + 1, videos.length - 1));
      } else {
        setCurrentIndex((previous) => Math.max(previous - 1, 0));
      }
    };

    window.addEventListener("wheel", handleWheel, { passive: false });
    return () => window.removeEventListener("wheel", handleWheel);
  }, [videos.length, isCommentOpen]);

  useEffect(() => {
    if (!actionMessage) {
      return;
    }
    const timer = window.setTimeout(() => setActionMessage(""), 2400);
    return () => window.clearTimeout(timer);
  }, [actionMessage]);

  const setInteractionFromResponse = (contentId: number, interaction: ContentInteractionResponse) => {
    setInteractionState((previous) => ({
      ...previous,
      [contentId]: {
        liked: interaction.liked,
        favorited: interaction.favorited,
        likesCount: interaction.likes_count,
        commentsCount: interaction.comments_count,
        favoritesCount: interaction.favorites_count,
        sharesCount: interaction.shares_count,
      },
    }));
  };

  const submitWatchProgress = async (contentId: number, force = false) => {
    if (!hasSession()) {
      return;
    }
    const targetIndex = videos.findIndex((item) => item.id === contentId);
    const video = videoRefs.current[targetIndex];
    if (!video) {
      return;
    }

    const currentTime = Math.max(0, Math.floor(video.currentTime || 0));
    const duration = Math.max(0, Math.floor(video.duration || 0));
    const previousReported = watchReportedSecondsRef.current[contentId] ?? 0;
    if (!force && currentTime <= previousReported + 4) {
      return;
    }

    watchReportedSecondsRef.current[contentId] = Math.max(previousReported, currentTime);

    try {
      const response = await reportWatchProgress(contentId, {
        watch_seconds: currentTime,
        watch_progress: duration > 0 ? Number(((currentTime / duration) * 100).toFixed(2)) : 0,
        last_position_seconds: currentTime,
        completed: duration > 0 && currentTime >= Math.max(duration - 2, 1),
      });
      setInteractionFromResponse(contentId, response.interaction);
    } catch {
      // best effort
    }
  };

  useEffect(() => {
    if (!currentVideo || !isPlaying) {
      return;
    }
    const timer = window.setInterval(() => {
      void submitWatchProgress(currentVideo.id);
    }, 8000);
    return () => window.clearInterval(timer);
  }, [currentVideo?.id, isPlaying]);

  useEffect(() => {
    const previousVideoId = previousActiveVideoIdRef.current;
    if (previousVideoId && previousVideoId !== currentVideo?.id) {
      void submitWatchProgress(previousVideoId, true);
    }
    previousActiveVideoIdRef.current = currentVideo?.id ?? null;
  }, [currentVideo?.id]);

  useEffect(() => {
    return () => {
      const activeVideoId = previousActiveVideoIdRef.current;
      if (activeVideoId) {
        void submitWatchProgress(activeVideoId, true);
      }
    };
  }, []);

  const loadComments = async (contentId: number, page = 1, append = false) => {
    try {
      setCommentLoading(page === 1);
      const response = await fetchContentComments(contentId, page, 20);
      setComments((previous) => (append ? [...previous, ...response.list] : response.list));
      setCommentPage(response.page);
      setCommentHasMore(response.has_more);
      setCommentError("");
    } catch (error) {
      setCommentError(error instanceof Error ? error.message : "加载评论失败");
    } finally {
      setCommentLoading(false);
    }
  };

  useEffect(() => {
    if (!isCommentOpen || !currentVideo) {
      return;
    }
    setReplyTarget(null);
    setCommentDraft("");
    setExpandedReplyRootIds([]);
    void loadComments(currentVideo.id, 1, false);
  }, [isCommentOpen, currentVideo?.id]);

  const handleTouchStart = (event: TouchEvent) => {
    touchStartY.current = event.touches[0].clientY;
  };

  const handleTouchEnd = (event: TouchEvent) => {
    if (isCommentOpen) {
      return;
    }
    const diff = touchStartY.current - event.changedTouches[0].clientY;
    if (Math.abs(diff) < 50) {
      return;
    }
    if (diff > 0) {
      setCurrentIndex((previous) => Math.min(previous + 1, videos.length - 1));
    } else {
      setCurrentIndex((previous) => Math.max(previous - 1, 0));
    }
  };

  const handleToggleFollow = async (event: MouseEvent<HTMLButtonElement>, authorUserId: number) => {
    event.stopPropagation();
    if (!hasSession()) {
      setActionMessage("请先登录后再关注作者");
      return;
    }
    if (pendingAction) {
      return;
    }
    const isFollowing = followState[authorUserId] ?? false;
    try {
      setPendingAction(`follow-${authorUserId}`);
      const response = isFollowing ? await unfollowUser(authorUserId) : await followUser(authorUserId);
      setFollowState((previous) => ({
        ...previous,
        [authorUserId]: response.is_following,
      }));
      setActionMessage(response.is_following ? "已关注该作者" : "已取消关注");
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : "关注操作失败");
    } finally {
      setPendingAction("");
    }
  };

  const handleLike = async (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    if (!currentVideo || pendingAction) {
      return;
    }
    try {
      setPendingAction(`like-${currentVideo.id}`);
      const response = currentInteraction?.liked
        ? await unlikeContent(currentVideo.id)
        : await likeContent(currentVideo.id);
      setInteractionFromResponse(currentVideo.id, response.interaction);
      setActionMessage(currentInteraction?.liked ? "已取消点赞" : "点赞成功");
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : "点赞失败");
    } finally {
      setPendingAction("");
    }
  };

  const handleFavorite = async (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    if (!currentVideo || pendingAction) {
      return;
    }
    try {
      setPendingAction(`favorite-${currentVideo.id}`);
      const response = currentInteraction?.favorited
        ? await unfavoriteContent(currentVideo.id)
        : await favoriteContent(currentVideo.id);
      setInteractionFromResponse(currentVideo.id, response.interaction);
      setActionMessage(currentInteraction?.favorited ? "已取消收藏" : "已收藏");
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : "收藏失败");
    } finally {
      setPendingAction("");
    }
  };

  const handleShare = async (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    if (!currentVideo || pendingAction) {
      return;
    }

    const shareUrl = typeof window !== "undefined" ? `${window.location.origin}/?video=${currentVideo.id}` : "";
    try {
      if (typeof navigator !== "undefined" && navigator.share) {
        await navigator.share({
          title: currentVideo.title,
          text: currentVideo.summary || currentVideo.title,
          url: shareUrl,
        });
      } else if (typeof navigator !== "undefined" && navigator.clipboard) {
        await navigator.clipboard.writeText(shareUrl);
      }

      setPendingAction(`share-${currentVideo.id}`);
      const response = await shareContent(currentVideo.id, { share_channel: "web" });
      setInteractionFromResponse(currentVideo.id, response.interaction);
      setActionMessage("分享链接已就绪");
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : "分享失败");
    } finally {
      setPendingAction("");
    }
  };

  const handleOpenComments = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    if (!currentVideo) {
      return;
    }
    setIsCommentOpen(true);
  };

  const handleSubmitComment = async () => {
    if (!currentVideo || !commentDraft.trim() || commentSubmitting) {
      return;
    }
    try {
      setCommentSubmitting(true);
      const created = await createContentComment(currentVideo.id, {
        content: commentDraft.trim(),
        parent_id: replyTarget?.id ?? null,
      });
      setComments((previous) => [created, ...previous]);
      setInteractionState((previous) => {
        const existing = previous[currentVideo.id] ?? buildInitialInteractionState(currentVideo);
        return {
          ...previous,
          [currentVideo.id]: {
            ...existing,
            commentsCount: existing.commentsCount + 1,
          },
        };
      });
      setCommentDraft("");
      setReplyTarget(null);
      setCommentError("");
      setActionMessage("评论已发布");
    } catch (error) {
      setCommentError(error instanceof Error ? error.message : "评论发布失败");
    } finally {
      setCommentSubmitting(false);
    }
  };

  const toggleReplies = (rootId: number) => {
    setExpandedReplyRootIds((previous) =>
      previous.includes(rootId) ? previous.filter((item) => item !== rootId) : [...previous, rootId],
    );
  };

  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50">
        <div className="text-gray-900">正在加载首页内容...</div>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50 px-6">
        <div className="max-w-md rounded-2xl border border-red-100 bg-white p-6 text-center shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">首页内容暂不可用</h2>
          <p className="mt-2 text-sm text-gray-600">{errorMessage}</p>
        </div>
      </div>
    );
  }

  if (!videos.length) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50 px-6">
        <div className="max-w-md rounded-2xl border border-emerald-100 bg-white p-6 text-center shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">
            {feedMode === "following" ? "还没有关注内容" : "首页还没有视频"}
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            {feedMode === "following" ? "先去关注一些创作者，关注流就会展示他们的内容。" : "先去创作中心发布一条内容吧。"}
          </p>
          <div className="mt-4 flex items-center justify-center gap-3">
            {feedMode === "following" ? (
              <button
                type="button"
                onClick={() => setFeedMode("for_you")}
                className="inline-flex rounded-full border border-emerald-200 px-5 py-2 text-sm font-semibold text-emerald-600"
              >
                去看推荐
              </button>
            ) : null}
            <Link
              to="/create"
              className="inline-flex rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-white"
            >
              去发布
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div
        className="relative h-screen w-screen overflow-hidden bg-black"
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
      >
        <div className="absolute left-0 right-0 top-0 z-30 flex items-center justify-between bg-gradient-to-b from-black/65 via-black/20 to-transparent px-4 pb-8 pt-3">
          <div className="flex items-center gap-6">
            <button
              type="button"
              onClick={() => setFeedMode("following")}
              className={`text-base font-bold transition ${feedMode === "following" ? "text-white" : "text-white/60"}`}
            >
              关注
              {feedMode === "following" ? <div className="mx-auto mt-1 h-0.5 w-6 rounded-full bg-white" /> : null}
            </button>
            <button
              type="button"
              onClick={() => setFeedMode("for_you")}
              className={`text-base font-bold transition ${feedMode === "for_you" ? "text-white" : "text-white/60"}`}
            >
              推荐
              {feedMode === "for_you" ? <div className="mx-auto mt-1 h-0.5 w-6 rounded-full bg-white" /> : null}
            </button>
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

        {actionMessage ? (
          <div className="absolute left-1/2 top-20 z-40 -translate-x-1/2 rounded-full bg-black/60 px-4 py-2 text-sm text-white backdrop-blur-sm">
            {actionMessage}
          </div>
        ) : null}

        <div
          className="absolute inset-0 transition-transform duration-500 ease-out"
          style={{ transform: `translateY(-${currentIndex * 100}vh)` }}
        >
          {videos.map((video, index) => {
            const state = interactionState[video.id] ?? buildInitialInteractionState(video);
            const isFollowing = followState[video.author.user_id] ?? video.author.is_following;

            return (
              <div
                key={video.id}
                className="relative flex h-screen w-screen items-center justify-center bg-black"
                onClick={() => setIsPlaying((previous) => !previous)}
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

                <div className="absolute inset-0 z-10 bg-gradient-to-b from-black/10 via-transparent to-black/55" />

                <div className="absolute bottom-0 left-0 right-0 z-20 p-4 pb-24">
                  <div className="mb-3 flex items-center gap-3">
                    <div className="relative shrink-0">
                      <img
                        src={video.author.avatar_url || "https://api.dicebear.com/7.x/avataaars/svg?seed=linglearn"}
                        alt={video.author.display_name}
                        className="h-12 w-12 rounded-full border-2 border-white/80 shadow-lg"
                      />
                      {!isFollowing ? (
                        <button
                          type="button"
                          onClick={(event) => handleToggleFollow(event, video.author.user_id)}
                          className="absolute -bottom-1 left-1/2 flex h-5 w-5 -translate-x-1/2 items-center justify-center rounded-full border-2 border-white bg-red-500 text-white shadow-lg transition hover:scale-105"
                          aria-label={`关注 ${video.author.display_name}`}
                        >
                          <Plus className="h-3 w-3 stroke-[3]" />
                        </button>
                      ) : null}
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="truncate font-bold text-white drop-shadow-lg">{video.author.display_name}</h3>
                      <p className="text-sm text-white/80 drop-shadow">{video.category?.name || "未分类"}</p>
                    </div>
                  </div>

                  <h2 className="mb-2 text-lg font-bold text-white drop-shadow-lg">{video.title}</h2>
                  <p className="mb-3 text-sm leading-relaxed text-white/90 drop-shadow">
                    {video.summary || "这条内容还没有补充描述。"}
                  </p>

                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1.5 rounded-lg bg-white/20 px-3 py-1.5 backdrop-blur-sm">
                      <Play className="h-3.5 w-3.5 text-white" />
                      <span className="text-xs font-medium text-white">{formatDuration(video.duration_seconds)}</span>
                    </div>
                    {video.category?.name ? (
                      <div className="rounded-lg bg-white/20 px-3 py-1.5 backdrop-blur-sm">
                        <span className="text-xs font-medium text-white"># {video.category.name}</span>
                      </div>
                    ) : null}
                  </div>
                </div>

                <div className="absolute bottom-28 right-3 z-20 rounded-[28px] border border-white/10 bg-black/20 px-2 py-3 shadow-2xl backdrop-blur-md">
                  <div className="flex flex-col items-center gap-3">
                  <button onClick={handleLike} className="flex flex-col items-center gap-1.5">
                    <div
                      className={`flex h-12 w-12 items-center justify-center rounded-2xl border border-white/20 shadow-lg ${
                        state.liked ? "bg-gradient-to-br from-red-500 to-pink-500" : "bg-white/95"
                      }`}
                    >
                      <Heart className={`h-6 w-6 ${state.liked ? "fill-white text-white" : "text-gray-700"}`} />
                    </div>
                    <span className="min-w-7 rounded-full bg-black/45 px-2 py-0.5 text-center text-[11px] font-semibold text-white shadow-sm backdrop-blur-sm">
                      {formatCount(state.likesCount)}
                    </span>
                  </button>

                  <button onClick={handleOpenComments} className="flex flex-col items-center gap-1.5">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/20 bg-white/95 shadow-lg">
                      <MessageCircle className="h-6 w-6 text-gray-700" />
                    </div>
                    <span className="min-w-7 rounded-full bg-black/45 px-2 py-0.5 text-center text-[11px] font-semibold text-white shadow-sm backdrop-blur-sm">
                      {formatCount(state.commentsCount)}
                    </span>
                  </button>

                  <button onClick={handleFavorite} className="flex flex-col items-center gap-1.5">
                    <div
                      className={`flex h-12 w-12 items-center justify-center rounded-2xl border border-white/20 shadow-lg ${
                        state.favorited ? "bg-gradient-to-br from-yellow-500 to-orange-500" : "bg-white/95"
                      }`}
                    >
                      <Bookmark
                        className={`h-6 w-6 ${state.favorited ? "fill-white text-white" : "text-gray-700"}`}
                      />
                    </div>
                    <span className="min-w-7 rounded-full bg-black/45 px-2 py-0.5 text-center text-[11px] font-semibold text-white shadow-sm backdrop-blur-sm">
                      {formatCount(state.favoritesCount)}
                    </span>
                  </button>

                  <button onClick={handleShare} className="flex flex-col items-center gap-1.5">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/20 bg-white/95 shadow-lg">
                      <Share2 className="h-6 w-6 text-gray-700" />
                    </div>
                    <span className="min-w-7 rounded-full bg-black/45 px-2 py-0.5 text-center text-[11px] font-semibold text-white shadow-sm backdrop-blur-sm">
                      {formatCount(state.sharesCount)}
                    </span>
                  </button>

                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      setIsMuted((previous) => !previous);
                    }}
                    className="flex flex-col items-center gap-1.5"
                  >
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/20 bg-white/95 shadow-lg">
                      {isMuted ? <VolumeX className="h-6 w-6 text-gray-700" /> : <Volume2 className="h-6 w-6 text-gray-700" />}
                    </div>
                    <span className="rounded-full bg-black/45 px-2 py-0.5 text-[11px] font-semibold text-white shadow-sm backdrop-blur-sm">
                      {isMuted ? "静音" : "声音"}
                    </span>
                  </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="absolute left-1/2 top-6 z-30 flex -translate-x-1/2 gap-1">
          {videos.map((_, index) => (
            <div
              key={index}
              className={`h-1 rounded-full transition-all ${index === currentIndex ? "w-8 bg-emerald-500" : "w-1 bg-gray-400"}`}
            />
          ))}
        </div>
      </div>

      <Drawer open={isCommentOpen} onOpenChange={setIsCommentOpen} direction="right">
        <DrawerContent className="h-screen w-full overflow-hidden p-0 sm:max-w-md">
          <DrawerHeader className="border-b px-6 py-4 text-left">
            <DrawerTitle>评论</DrawerTitle>
            <DrawerDescription>{currentVideo?.title || "当前视频"}</DrawerDescription>
          </DrawerHeader>

          <div className="flex h-full flex-col">
            <div className="min-h-0 flex-1 space-y-4 overflow-y-auto px-6 py-4">
              {commentLoading ? <p className="text-sm text-gray-500">正在加载评论...</p> : null}
              {!commentLoading && commentError ? <p className="text-sm text-red-500">{commentError}</p> : null}

              {!commentLoading && !comments.length && !commentError ? (
                <div className="rounded-3xl border border-dashed border-gray-200 bg-gray-50 px-5 py-8 text-center">
                  <p className="text-sm font-medium text-gray-700">还没有评论</p>
                  <p className="mt-1 text-xs text-gray-500">来发表第一条评论吧。</p>
                </div>
              ) : null}

              {commentThreads.map((thread) => (
                <div key={thread.root.id} className="border-b border-gray-100 py-4 last:border-b-0">
                  <div className="flex gap-3">
                    <img
                      src={thread.root.avatar_url || "https://api.dicebear.com/7.x/avataaars/svg?seed=comment-root"}
                      alt={thread.root.display_name}
                      className="h-10 w-10 rounded-full object-cover"
                    />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <p className="truncate text-sm font-semibold text-gray-900">{thread.root.display_name}</p>
                        <p className="text-xs text-gray-400">{formatCommentTime(thread.root.created_at)}</p>
                      </div>
                      <p className="mt-2 whitespace-pre-wrap text-[15px] leading-7 text-gray-800">{thread.root.content}</p>
                      <button
                        type="button"
                        onClick={() => {
                          setReplyTarget(thread.root);
                          setCommentDraft(`@${thread.root.display_name} `);
                        }}
                        className="mt-2 text-xs font-medium text-gray-500 hover:text-emerald-600"
                      >
                        回复
                      </button>

                      {thread.replies.length ? (
                        <div className="mt-3">
                          <button
                            type="button"
                            onClick={() => toggleReplies(thread.root.id)}
                            className="flex items-center gap-1 text-xs font-medium text-gray-500 hover:text-emerald-600"
                          >
                            {expandedReplyRootIds.includes(thread.root.id) ? (
                              <>
                                <ChevronUp className="h-3.5 w-3.5" />
                                收起 {thread.replies.length} 条回复
                              </>
                            ) : (
                              <>
                                <ChevronDown className="h-3.5 w-3.5" />
                                展开 {thread.replies.length} 条回复
                              </>
                            )}
                          </button>

                          {expandedReplyRootIds.includes(thread.root.id) ? (
                            <div className="mt-3 border-l-2 border-gray-100 pl-4">
                              <div className="space-y-3">
                                {thread.replies.map((reply) => (
                                  <div key={reply.id} className="flex gap-3">
                                    <img
                                      src={reply.avatar_url || "https://api.dicebear.com/7.x/avataaars/svg?seed=comment-reply"}
                                      alt={reply.display_name}
                                      className="mt-0.5 h-7 w-7 rounded-full object-cover"
                                    />
                                    <div className="min-w-0 flex-1">
                                      <div className="flex items-center gap-2">
                                        <span className="truncate text-xs font-semibold text-gray-900">{reply.display_name}</span>
                                        <span className="text-[11px] text-gray-400">{formatCommentTime(reply.created_at)}</span>
                                      </div>
                                      <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-gray-700">
                                        {reply.reply_to_display_name ? (
                                          <span className="mr-1 font-medium text-emerald-700">@{reply.reply_to_display_name}</span>
                                        ) : null}
                                        {reply.content}
                                      </p>
                                      <button
                                        type="button"
                                        onClick={() => {
                                          setReplyTarget(reply);
                                          setCommentDraft(`@${reply.display_name} `);
                                        }}
                                        className="mt-1 text-xs font-medium text-gray-500 hover:text-emerald-600"
                                      >
                                        回复
                                      </button>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ) : null}
                        </div>
                      ) : null}
                    </div>
                  </div>
                </div>
              ))}

              {!commentLoading && commentHasMore ? (
                <div className="flex justify-center">
                  <button
                    type="button"
                    onClick={() => currentVideo && void loadComments(currentVideo.id, commentPage + 1, true)}
                    className="rounded-full border border-emerald-200 px-4 py-2 text-sm font-medium text-emerald-600"
                  >
                    加载更多评论
                  </button>
                </div>
              ) : null}
            </div>

            <div className="border-t bg-white px-6 py-4">
              {replyTarget ? (
                <div className="mb-3 flex items-center justify-between rounded-2xl bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
                  <span>正在回复 @{replyTarget.display_name}</span>
                  <button
                    type="button"
                    onClick={() => {
                      setReplyTarget(null);
                      setCommentDraft("");
                    }}
                    className="font-semibold"
                  >
                    取消
                  </button>
                </div>
              ) : null}

              <Textarea
                value={commentDraft}
                onChange={(event) => setCommentDraft(event.target.value)}
                placeholder={replyTarget ? `回复 @${replyTarget.display_name}...` : "写下你的评论..."}
                className="min-h-24"
              />
              <div className="mt-3 flex items-center justify-between gap-3">
                <span className="text-xs text-gray-400">{commentDraft.trim().length}/1000</span>
                <button
                  type="button"
                  onClick={handleSubmitComment}
                  disabled={!commentDraft.trim() || commentSubmitting}
                  className="rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-gray-300"
                >
                  {commentSubmitting ? "发布中..." : "发表评论"}
                </button>
              </div>
            </div>
          </div>
        </DrawerContent>
      </Drawer>
    </>
  );
}
