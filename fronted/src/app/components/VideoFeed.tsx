import type { MouseEvent, TouchEvent } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  Bookmark,
  BookOpen,
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
  X,
} from "lucide-react";
import { Link } from "react-router";

import { followUser, unfollowUser } from "../lib/account";
import {
  fetchContentComments,
  fetchContentQuizzes,
  fetchFeedVideos,
  fetchSearchContents,
  reportWatchProgress,
  shareContent,
  submitQuizAnswer,
  syncContentInteractionsBatch,
} from "../lib/content";
import {
  buildInteractionSyncPayload,
  buildPendingCommentResponse,
  createPendingCommentDraft,
  enqueueCommentAction,
  enqueueFavoriteAction,
  enqueueLikeAction,
  persistInteractionSyncQueue,
  readInteractionSyncQueue,
  removeSyncedQueueItems,
  type InteractionSyncQueue,
} from "../lib/interaction-sync";
import { getStoredSession, hasSession } from "../lib/session";
import type {
  ContentCommentResponse,
  ContentInteractionResponse,
  ContentQuizResponse,
  ContentVideoResponse,
} from "../lib/types";
import { usePageContextActions } from "../page-context";
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

const INTERACTION_SYNC_INTERVAL_MS = 10000;

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

function buildQueuedInteractionState(
  video: ContentVideoResponse,
  queue: InteractionSyncQueue,
): VideoInteractionState {
  const state = buildInitialInteractionState(video);
  const queuedLike = queue.likes[video.id];
  const queuedFavorite = queue.favorites[video.id];
  const queuedCommentCount = queue.comments.filter((item) => item.content_id === video.id).length;

  if (queuedLike && queuedLike.liked !== state.liked) {
    state.likesCount = Math.max(0, state.likesCount + (queuedLike.liked ? 1 : -1));
    state.liked = queuedLike.liked;
  }

  if (queuedFavorite && queuedFavorite.favorited !== state.favorited) {
    state.favoritesCount = Math.max(0, state.favoritesCount + (queuedFavorite.favorited ? 1 : -1));
    state.favorited = queuedFavorite.favorited;
  }

  if (queuedCommentCount) {
    state.commentsCount += queuedCommentCount;
  }

  return state;
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
  const { updatePageContext } = usePageContextActions();
  const currentSession = getStoredSession();
  const currentUserId = currentSession?.userId ?? null;
  const currentUserDisplayName = currentSession?.currentUser?.profile.display_name ?? "我";
  const currentUserAvatarUrl = null;
  const [videos, setVideos] = useState<ContentVideoResponse[]>([]);
  const [feedMode, setFeedMode] = useState<FeedMode>("for_you");
  const [interactionState, setInteractionState] = useState<Record<number, VideoInteractionState>>({});
  const [followState, setFollowState] = useState<Record<number, boolean>>({});
  const [resolvedDurations, setResolvedDurations] = useState<Record<number, number>>({});
  const [syncQueue, setSyncQueue] = useState<InteractionSyncQueue>(() => readInteractionSyncQueue());
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMoreVideos, setHasMoreVideos] = useState(false);
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
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<ContentVideoResponse[] | null>(null);
  const [isQuizOpen, setIsQuizOpen] = useState(false);
  const [quizItems, setQuizItems] = useState<ContentQuizResponse[]>([]);
  const [quizLoading, setQuizLoading] = useState(false);
  const [quizError, setQuizError] = useState("");
  const [selectedQuizOptions, setSelectedQuizOptions] = useState<Record<number, number>>({});
  const [submittingQuizId, setSubmittingQuizId] = useState<number | null>(null);

  const videoRefs = useRef<(HTMLVideoElement | null)[]>([]);
  const touchStartY = useRef(0);
  const previousActiveVideoIdRef = useRef<number | null>(null);
  const watchReportedSecondsRef = useRef<Record<number, number>>({});
  const syncQueueRef = useRef(syncQueue);
  const isFlushingQueueRef = useRef(false);

  const filteredVideos = useMemo(() => {
    if (searchResults) {
      return searchResults;
    }

    const keyword = searchQuery.trim().toLowerCase();
    if (!keyword) {
      return videos;
    }

    return videos.filter((video) => {
      const haystacks = [
        video.title,
        video.summary || "",
        video.author.display_name,
        video.category?.name || "",
        ...(video.hashtags || []),
      ];
      return haystacks.some((item) => item.toLowerCase().includes(keyword));
    });
  }, [searchQuery, videos]);

  const currentVideo = filteredVideos[currentIndex] ?? null;
  const currentInteraction = currentVideo
    ? interactionState[currentVideo.id] ?? buildInitialInteractionState(currentVideo)
    : null;
  const commentThreads = useMemo(() => buildCommentThreads(comments), [comments]);

  useEffect(() => {
    const currentVideoTitle = currentVideo?.title?.trim() || "当前视频";
    const titleParam = currentVideo ? encodeURIComponent(currentVideo.title) : "";
    const categoryParam = currentVideo?.category?.name ? encodeURIComponent(currentVideo.category.name) : "";
    const contentIdParam = currentVideo?.id ? `content_id=${currentVideo.id}` : "";
    const sourceQuery = currentVideo
      ? [contentIdParam, `title=${titleParam}`, categoryParam ? `category=${categoryParam}` : "", "source=video"]
          .filter(Boolean)
          .join("&")
      : "source=video";

    updatePageContext({
      page_type: "home_feed",
      page_title: "首页视频流",
      summary: currentVideo
        ? `当前正在浏览视频《${currentVideoTitle}》，可以围绕视频主题继续答疑、生成练习、规划学习路径。`
        : "正在浏览首页推荐视频流。",
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
      available_actions: currentVideo
        ? [
            {
              id: "explain-current-video",
              label: "解析当前视频知识点",
              description: "根据当前播放视频提炼重点知识点和学习建议。",
              type: "analyze",
            },
            {
              id: "generate-video-practice",
              label: "生成视频同主题练习",
              description: "围绕当前视频主题生成在线学习题库并跳转到练习页。",
              type: "generate",
              href: `/practice?${sourceQuery}`,
            },
            {
              id: "build-video-learning-path",
              label: "生成配套学习路径",
              description: "基于当前视频主题延伸生成下一步学习路线。",
              type: "navigate",
              href: `/learning-path?${sourceQuery}`,
            },
            {
              id: "evaluate-video-topic",
              label: "评估该主题掌握度",
              description: "围绕当前视频所属知识主题给出学习评估建议。",
              type: "navigate",
              href: `/assessment?${sourceQuery}`,
            },
          ]
        : [
            {
              id: "ask-current-video",
              label: "解析当前视频",
              description: "基于当前视频内容做知识点拆解和总结。",
              type: "analyze",
            },
          ],
      metadata: {
        section: "feed",
        feed_mode: feedMode,
        current_index: currentIndex,
        visible_video_count: filteredVideos.length,
      },
    });
  }, [currentIndex, currentVideo, feedMode, filteredVideos.length, updatePageContext]);

  const syncVideoDerivedState = (items: ContentVideoResponse[]) => {
    setResolvedDurations(
      items.reduce<Record<number, number>>((accumulator, item) => {
        if (item.duration_seconds && item.duration_seconds > 0) {
          accumulator[item.id] = item.duration_seconds;
        }
        return accumulator;
      }, {}),
    );
    setInteractionState(
      items.reduce<Record<number, VideoInteractionState>>((accumulator, item) => {
        accumulator[item.id] = buildQueuedInteractionState(item, syncQueueRef.current);
        return accumulator;
      }, {}),
    );
    setFollowState(
      items.reduce<Record<number, boolean>>((accumulator, item) => {
        accumulator[item.author.user_id] = item.author.is_following;
        return accumulator;
      }, {}),
    );
  };

  const applyFeedResponse = (
    items: ContentVideoResponse[],
    options?: {
      append?: boolean;
      nextCursor?: string | null;
      hasMore?: boolean;
    },
  ) => {
    const append = options?.append ?? false;
    setVideos((previous) => {
      const merged = append ? [...previous, ...items.filter((item) => !previous.some((video) => video.id === item.id))] : items;
      syncVideoDerivedState(merged);
      return merged;
    });
    if (!append) {
      setCurrentIndex(0);
    }
    setNextCursor(options?.nextCursor ?? null);
    setHasMoreVideos(options?.hasMore ?? false);
  };

  const handleVideoMetadataLoaded = (contentId: number, element: HTMLVideoElement | null) => {
    if (!element) {
      return;
    }
    const nextDuration = Math.max(0, Math.floor(element.duration || 0));
    if (!nextDuration) {
      return;
    }
    setResolvedDurations((previous) => {
      if (previous[contentId] === nextDuration) {
        return previous;
      }
      return {
        ...previous,
        [contentId]: nextDuration,
      };
    });
  };

  useEffect(() => {
    syncQueueRef.current = syncQueue;
    persistInteractionSyncQueue(syncQueue);
  }, [syncQueue]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      void flushInteractionQueue();
    }, INTERACTION_SYNC_INTERVAL_MS);

    const handleVisibilityChange = () => {
      if (document.visibilityState === "hidden") {
        void flushInteractionQueue();
      }
    };

    window.addEventListener("pagehide", handleVisibilityChange);
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("pagehide", handleVisibilityChange);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadFeed() {
      try {
        setIsLoading(true);
        const response = await fetchFeedVideos(undefined, feedMode);
        if (cancelled) {
          return;
        }
        applyFeedResponse(response.list, {
          append: false,
          nextCursor: response.next_cursor,
          hasMore: response.has_more,
        });
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
    const keyword = searchQuery.trim();
    if (!keyword) {
      setSearchResults(null);
      return;
    }

    let cancelled = false;
    async function loadSearchResults() {
      try {
        const response = await fetchSearchContents({ keyword, pageSize: 20 });
        if (cancelled) {
          return;
        }
        setSearchResults(response.list);
        syncVideoDerivedState(response.list);
      } catch (error) {
        if (cancelled) {
          return;
        }
        setSearchResults([]);
        setActionMessage(error instanceof Error ? error.message : "搜索失败");
      }
    }

    void loadSearchResults();
    return () => {
      cancelled = true;
    };
  }, [searchQuery]);

  useEffect(() => {
    let cancelled = false;

    async function loadMoreFeed() {
      if (!nextCursor || !hasMoreVideos || isLoading || isLoadingMore || isCommentOpen) {
        return;
      }
      if (currentIndex < Math.max(filteredVideos.length - 3, 0)) {
        return;
      }
      try {
        setIsLoadingMore(true);
        const response = await fetchFeedVideos(nextCursor, feedMode);
        if (cancelled) {
          return;
        }
        applyFeedResponse(response.list, {
          append: true,
          nextCursor: response.next_cursor,
          hasMore: response.has_more,
        });
      } catch {
        // best effort load more
      } finally {
        if (!cancelled) {
          setIsLoadingMore(false);
        }
      }
    }

    void loadMoreFeed();
    return () => {
      cancelled = true;
    };
  }, [currentIndex, feedMode, filteredVideos.length, hasMoreVideos, isCommentOpen, isLoading, isLoadingMore, nextCursor]);

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
    const isEventInsideFloatingAssistant = (target: EventTarget | null) => {
      if (!(target instanceof Element)) {
        return false;
      }
      return Boolean(target.closest("[data-floating-ai-chat='true']"));
    };

    const handleWheel = (event: WheelEvent) => {
      if (
        !filteredVideos.length ||
        isCommentOpen ||
        isEventInsideFloatingAssistant(event.target)
      ) {
        return;
      }
      event.preventDefault();
      if (event.deltaY > 0) {
        setCurrentIndex((previous) => Math.min(previous + 1, filteredVideos.length - 1));
      } else {
        setCurrentIndex((previous) => Math.max(previous - 1, 0));
      }
    };

    window.addEventListener("wheel", handleWheel, { passive: false });
    return () => window.removeEventListener("wheel", handleWheel);
  }, [filteredVideos.length, isCommentOpen]);

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

  const flushInteractionQueue = async () => {
    if (!hasSession() || isFlushingQueueRef.current) {
      return;
    }

    const snapshot = syncQueueRef.current;
    const payload = buildInteractionSyncPayload(snapshot);
    if (!payload.items.length) {
      return;
    }

    isFlushingQueueRef.current = true;
    try {
      const response = await syncContentInteractionsBatch(payload);
      response.items.forEach((item) => {
        setInteractionFromResponse(item.content_id, item.interaction);
        if (item.comment) {
          const matchedDraft = snapshot.comments.find((draft) => draft.client_id === item.client_id);
          if (!matchedDraft) {
            return;
          }
          setComments((previous) =>
            previous.map((comment) => (comment.id === matchedDraft.temp_comment_id ? item.comment! : comment)),
          );
        }
      });
      setSyncQueue((previous) => removeSyncedQueueItems(previous, snapshot));
    } catch {
      // best effort sync
    } finally {
      isFlushingQueueRef.current = false;
    }
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
    }, 8003);
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
      const pendingComments = syncQueueRef.current.comments
        .filter((item) => item.content_id === contentId)
        .map((item) => buildPendingCommentResponse(item, currentUserId ?? 0));
      setComments((previous) =>
        append ? [...previous, ...response.list] : [...pendingComments, ...response.list],
      );
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
    if (event.target instanceof Element && event.target.closest("[data-floating-ai-chat='true']")) {
      touchStartY.current = Number.NaN;
      return;
    }
    touchStartY.current = event.touches[0].clientY;
  };

  const handleTouchEnd = (event: TouchEvent) => {
    if (
      isCommentOpen ||
      Number.isNaN(touchStartY.current) ||
      (event.target instanceof Element && event.target.closest("[data-floating-ai-chat='true']"))
    ) {
      return;
    }
    const diff = touchStartY.current - event.changedTouches[0].clientY;
    if (Math.abs(diff) < 50) {
      return;
    }
    if (diff > 0) {
      setCurrentIndex((previous) => Math.min(previous + 1, filteredVideos.length - 1));
    } else {
      setCurrentIndex((previous) => Math.max(previous - 1, 0));
    }
  };

  useEffect(() => {
    setCurrentIndex(0);
  }, [feedMode, searchQuery]);

  useEffect(() => {
    if (!filteredVideos.length) {
      setCurrentIndex(0);
      return;
    }
    setCurrentIndex((previous) => Math.min(previous, filteredVideos.length - 1));
  }, [filteredVideos.length]);

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
      setVideos((previous) =>
        previous.map((item) =>
          item.author.user_id === authorUserId
            ? {
                ...item,
                author: {
                  ...item.author,
                  is_following: response.is_following,
                },
              }
            : item,
        ),
      );
      if (feedMode === "following") {
        const followingFeed = await fetchFeedVideos(undefined, "following");
        applyFeedResponse(followingFeed.list);
      }
      setActionMessage(response.is_following ? "已关注该作者" : "已取消关注");
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : "关注操作失败");
    } finally {
      setPendingAction("");
    }
  };

  const handleLike = async (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    if (!currentVideo) {
      return;
    }
    if (!hasSession()) {
      setActionMessage("请先登录后再点赞");
      return;
    }
    const nextLiked = !currentInteraction?.liked;
    setInteractionState((previous) => {
      const existing = previous[currentVideo.id] ?? buildQueuedInteractionState(currentVideo, syncQueueRef.current);
      return {
        ...previous,
        [currentVideo.id]: {
          ...existing,
          liked: nextLiked,
          likesCount: Math.max(0, existing.likesCount + (nextLiked ? 1 : -1)),
        },
      };
    });
    setSyncQueue((previous) => enqueueLikeAction(previous, currentVideo.id, nextLiked));
  };

  const handleFavorite = async (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    if (!currentVideo) {
      return;
    }
    if (!hasSession()) {
      setActionMessage("请先登录后再收藏");
      return;
    }
    const nextFavorited = !currentInteraction?.favorited;
    setInteractionState((previous) => {
      const existing = previous[currentVideo.id] ?? buildQueuedInteractionState(currentVideo, syncQueueRef.current);
      return {
        ...previous,
        [currentVideo.id]: {
          ...existing,
          favorited: nextFavorited,
          favoritesCount: Math.max(0, existing.favoritesCount + (nextFavorited ? 1 : -1)),
        },
      };
    });
    setSyncQueue((previous) => enqueueFavoriteAction(previous, currentVideo.id, nextFavorited));
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

  const handleOpenQuiz = async (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    if (!currentVideo || !currentVideo.has_quiz) {
      return;
    }
    if (!hasSession()) {
      setActionMessage("请先登录后再答题");
      return;
    }
    setIsQuizOpen(true);
    setQuizLoading(true);
    setQuizError("");
    try {
      const response = await fetchContentQuizzes(currentVideo.id);
      setQuizItems(response);
      setSelectedQuizOptions(
        response.reduce<Record<number, number>>((accumulator, quiz) => {
          if (quiz.selected_option_id) {
            accumulator[quiz.quiz_id] = quiz.selected_option_id;
          }
          return accumulator;
        }, {}),
      );
    } catch (error) {
      setQuizError(error instanceof Error ? error.message : "题目加载失败");
      setQuizItems([]);
    } finally {
      setQuizLoading(false);
    }
  };

  const handleSubmitQuiz = async (quizId: number) => {
    const selectedOptionId = selectedQuizOptions[quizId];
    if (!selectedOptionId || submittingQuizId) {
      return;
    }
    setSubmittingQuizId(quizId);
    setQuizError("");
    try {
      const response = await submitQuizAnswer(quizId, selectedOptionId);
      setQuizItems((previous) =>
        previous.map((quiz) =>
          quiz.quiz_id === quizId
            ? {
                ...quiz,
                total_votes: response.total_votes,
                has_submitted: true,
                selected_option_id: response.selected_option_id,
                options: response.options,
              }
            : quiz,
        ),
      );
      setActionMessage(response.is_correct ? "回答正确" : "已提交答案");
    } catch (error) {
      setQuizError(error instanceof Error ? error.message : "提交失败");
    } finally {
      setSubmittingQuizId(null);
    }
  };

  const handleSubmitComment = async () => {
    if (!currentVideo || !commentDraft.trim() || commentSubmitting) {
      return;
    }
    if (!hasSession() || currentUserId === null) {
      setCommentError("请先登录后再评论");
      return;
    }
    if ((replyTarget?.id ?? 0) < 0) {
      return;
    }

    const trimmedComment = commentDraft.trim();
    const pendingDraft = createPendingCommentDraft({
      contentId: currentVideo.id,
      content: trimmedComment,
      parentId: replyTarget?.id ?? null,
      displayName: currentUserDisplayName,
      avatarUrl: currentUserAvatarUrl,
      replyToDisplayName: replyTarget?.display_name ?? null,
    });

    setComments((previous) => [buildPendingCommentResponse(pendingDraft, currentUserId), ...previous]);
    setInteractionState((previous) => {
      const existing = previous[currentVideo.id] ?? buildQueuedInteractionState(currentVideo, syncQueueRef.current);
      return {
        ...previous,
        [currentVideo.id]: {
          ...existing,
          commentsCount: existing.commentsCount + 1,
        },
      };
    });
    setSyncQueue((previous) => enqueueCommentAction(previous, pendingDraft));
    setCommentDraft("");
    setReplyTarget(null);
    setCommentError("");
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

  if (!videos.length || !filteredVideos.length) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50 px-6">
        <div className="max-w-md rounded-2xl border border-emerald-100 bg-white p-6 text-center shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">
            {!videos.length
              ? feedMode === "following"
                ? "还没有关注内容"
                : "首页还没有视频"
              : "没有找到相关内容"}
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            {!videos.length
              ? feedMode === "following"
                ? "先去关注一些创作者，关注流就会展示他们的内容。"
                : "先去创作中心发布一条内容吧。"
              : `没有搜到和“${searchQuery.trim()}”相关的视频。`}
          </p>
          <div className="mt-4 flex items-center justify-center gap-3">
            {!videos.length && feedMode === "following" ? (
              <button
                type="button"
                onClick={() => setFeedMode("for_you")}
                className="inline-flex rounded-full border border-emerald-200 px-5 py-2 text-sm font-semibold text-emerald-600"
              >
                去看推荐
              </button>
            ) : null}
            {videos.length ? (
              <button
                type="button"
                onClick={() => {
                  setSearchQuery("");
                  setIsSearchOpen(false);
                }}
                className="inline-flex rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-white"
              >
                清空搜索
              </button>
            ) : (
              <Link
                to="/create"
                className="inline-flex rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-white"
              >
                去发布
              </Link>
            )}
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

          <div className="flex items-center gap-3">
            {isSearchOpen ? (
              <div className="flex items-center gap-2 rounded-full border border-white/15 bg-black/35 px-3 py-2 backdrop-blur-md">
                <Search className="h-4 w-4 text-white/80" />
                <input
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                  placeholder="搜索标题、作者、分类"
                  className="w-40 bg-transparent text-sm text-white placeholder:text-white/45 focus:outline-none"
                  onClick={(event) => event.stopPropagation()}
                />
                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    setIsSearchOpen(false);
                    setSearchQuery("");
                  }}
                  className="text-white/70 transition hover:text-white"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={(event) => {
                  event.stopPropagation();
                  setIsSearchOpen(true);
                }}
                className="rounded-2xl border border-white/20 bg-black/25 p-2.5 text-white backdrop-blur-md transition hover:bg-black/40"
              >
                <Search className="h-6 w-6" />
              </button>
            )}
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
          {filteredVideos.map((video, index) => {
            const state = interactionState[video.id] ?? buildInitialInteractionState(video);
            const isFollowing = followState[video.author.user_id] ?? video.author.is_following;

            return (
              <div
                key={video.id}
                className="relative flex h-screen w-screen items-center justify-center bg-black"
                onClick={() => setIsPlaying((previous) => !previous)}
              >
                {video.video_url ? (
                  <>
                    <div
                      className="absolute inset-0 bg-cover bg-center opacity-70 blur-2xl scale-110"
                      style={{ backgroundImage: video.cover_url ? `url(${video.cover_url})` : undefined }}
                    />
                    <video
                      ref={(element) => {
                        videoRefs.current[index] = element;
                      }}
                      onLoadedMetadata={(event) =>
                        handleVideoMetadataLoaded(video.id, event.currentTarget)
                      }
                      className="absolute inset-0 h-full w-full object-contain"
                      src={video.video_url}
                      loop
                      playsInline
                      poster={video.cover_url ?? undefined}
                    />
                  </>
                ) : (
                  <div
                    className="absolute inset-0 bg-contain bg-center bg-no-repeat"
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
                      {!isFollowing && currentUserId !== video.author.user_id ? (
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
                      <span className="text-xs font-medium text-white">
                        {formatDuration(resolvedDurations[video.id] ?? video.duration_seconds)}
                      </span>
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

                  {video.has_quiz ? (
                    <button onClick={handleOpenQuiz} className="flex flex-col items-center gap-1.5">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/20 bg-white/95 shadow-lg">
                        <BookOpen className="h-6 w-6 text-gray-700" />
                      </div>
                      <span className="rounded-full bg-black/45 px-2 py-0.5 text-[11px] font-semibold text-white shadow-sm backdrop-blur-sm">
                        答题
                      </span>
                    </button>
                  ) : null}

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
          {filteredVideos.map((_, index) => (
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

      <Drawer open={isQuizOpen} onOpenChange={setIsQuizOpen} direction="right">
        <DrawerContent className="h-screen w-full overflow-hidden p-0 sm:max-w-md">
          <DrawerHeader className="border-b px-6 py-4 text-left">
            <DrawerTitle>视频答题</DrawerTitle>
            <DrawerDescription>{currentVideo?.title || "当前视频"}</DrawerDescription>
          </DrawerHeader>

          <div className="flex h-full flex-col">
            <div className="min-h-0 flex-1 space-y-4 overflow-y-auto px-6 py-4">
              {quizLoading ? <p className="text-sm text-gray-500">正在加载题目...</p> : null}
              {quizError ? <p className="text-sm text-red-500">{quizError}</p> : null}
              {!quizLoading && !quizItems.length && !quizError ? (
                <div className="rounded-3xl border border-dashed border-gray-200 bg-gray-50 px-5 py-8 text-center">
                  <p className="text-sm font-medium text-gray-700">这个视频暂时没有题目</p>
                </div>
              ) : null}

              {quizItems.map((quiz, index) => (
                <div key={quiz.quiz_id} className="rounded-3xl border border-gray-100 bg-white p-4 shadow-sm">
                  <div className="mb-4">
                    <p className="text-xs font-medium text-emerald-600">题目 {index + 1}</p>
                    <h3 className="mt-1 text-base font-semibold text-gray-900">{quiz.title}</h3>
                    {quiz.description ? (
                      <p className="mt-1 text-sm leading-6 text-gray-500">{quiz.description}</p>
                    ) : null}
                  </div>

                  <div className="space-y-2">
                    {quiz.options.map((option) => {
                      const isSelected = selectedQuizOptions[quiz.quiz_id] === option.option_id;
                      const canReveal = quiz.has_submitted && option.is_correct !== null;
                      return (
                        <button
                          key={option.option_id}
                          type="button"
                          disabled={quiz.has_submitted}
                          onClick={() =>
                            setSelectedQuizOptions((previous) => ({
                              ...previous,
                              [quiz.quiz_id]: option.option_id,
                            }))
                          }
                          className={`w-full rounded-2xl border px-4 py-3 text-left text-sm transition ${
                            isSelected
                              ? "border-emerald-400 bg-emerald-50 text-emerald-800"
                              : "border-gray-200 bg-gray-50 text-gray-700"
                          }`}
                        >
                          <div className="flex items-center justify-between gap-3">
                            <span>{option.option_text}</span>
                            {canReveal ? (
                              <span className={option.is_correct ? "text-emerald-600" : "text-gray-400"}>
                                {option.is_correct ? "正确" : `${option.percent.toFixed(0)}%`}
                              </span>
                            ) : null}
                          </div>
                        </button>
                      );
                    })}
                  </div>

                  <button
                    type="button"
                    disabled={quiz.has_submitted || !selectedQuizOptions[quiz.quiz_id] || submittingQuizId === quiz.quiz_id}
                    onClick={() => void handleSubmitQuiz(quiz.quiz_id)}
                    className="mt-4 w-full rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-gray-300"
                  >
                    {quiz.has_submitted ? "已提交" : submittingQuizId === quiz.quiz_id ? "提交中..." : "提交答案"}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </DrawerContent>
      </Drawer>
    </>
  );
}
