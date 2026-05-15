import { Code, Laptop, Calculator, Database, Bot, Settings, Flame, Sparkles, Hash, Play, Search, TrendingUp } from "lucide-react";
import { useDeferredValue, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router";
import {
  fetchContentCategories,
  fetchDiscoverHotTags,
  fetchDiscoverHotTopics,
  fetchFeedVideos,
  fetchSearchContents,
} from "../lib/content";
import type {
  ContentCategoryResponse,
  ContentVideoResponse,
  DiscoverHotTagResponse,
  DiscoverHotTopicResponse,
} from "../lib/types";
import {
  readDiscoverPersistedState,
  writeDiscoverPersistedState,
  type DiscoverPersistedState,
  type DiscoverWatchNavigationState,
} from "../lib/discover-watch";

const categoryDecor = [
  { icon: <Code className="h-6 w-6" />, color: "from-blue-500 to-cyan-500" },
  { icon: <Laptop className="h-6 w-6" />, color: "from-purple-500 to-pink-500" },
  { icon: <Calculator className="h-6 w-6" />, color: "from-emerald-500 to-teal-500" },
  { icon: <Database className="h-6 w-6" />, color: "from-orange-500 to-red-500" },
  { icon: <Bot className="h-6 w-6" />, color: "from-indigo-500 to-purple-500" },
  { icon: <Settings className="h-6 w-6" />, color: "from-green-500 to-emerald-500" },
];

type RankingItem = {
  id: number;
  rank: number;
  title: string;
  views: string;
  trend: "热" | "新" | "";
};

function formatCompactCount(value: number) {
  if (value >= 10000) {
    return `${(value / 10000).toFixed(1).replace(/\.0$/, "")}万`;
  }
  return String(value);
}

function formatDuration(seconds?: number | null) {
  if (!seconds || seconds <= 0) {
    return "00:00";
  }

  const whole = Math.round(seconds);
  const minutes = Math.floor(whole / 60);
  const remain = whole % 60;
  const minuteText = String(minutes).padStart(2, "0");
  const secondText = String(remain).padStart(2, "0");
  return `${minuteText}:${secondText}`;
}

function deriveCategoryVideoCount(
  category: ContentCategoryResponse,
  hotTopics: DiscoverHotTopicResponse[],
  videos: ContentVideoResponse[],
) {
  const topic = hotTopics.find((item) => item.id === category.id);
  if (topic) {
    return topic.content_count;
  }
  return videos.filter((video) => video.category?.id === category.id).length;
}

export function Discover() {
  const navigate = useNavigate();
  const initialPersistedState = useMemo(() => readDiscoverPersistedState(), []);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const hasRestoredScrollRef = useRef(false);

  const [searchQuery, setSearchQuery] = useState(initialPersistedState.searchQuery);
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(initialPersistedState.selectedCategoryId);
  const deferredQuery = useDeferredValue(searchQuery.trim().toLowerCase());

  const [categories, setCategories] = useState<ContentCategoryResponse[]>([]);
  const [hotTopics, setHotTopics] = useState<DiscoverHotTopicResponse[]>([]);
  const [hotTags, setHotTags] = useState<DiscoverHotTagResponse[]>([]);
  const [recommendedVideos, setRecommendedVideos] = useState<ContentVideoResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorText, setErrorText] = useState<string | null>(null);

  const persistDiscoverState = (overrides?: Partial<DiscoverPersistedState>) => {
    writeDiscoverPersistedState({
      searchQuery,
      selectedCategoryId,
      scrollTop: containerRef.current?.scrollTop ?? 0,
      ...overrides,
    });
  };

  useEffect(() => {
    let active = true;

    async function loadDiscover() {
      try {
        setLoading(true);
        const videoRequest =
          deferredQuery || selectedCategoryId
            ? fetchSearchContents({
                keyword: deferredQuery,
                categoryId: selectedCategoryId,
                pageSize: 8,
              })
            : fetchFeedVideos(undefined, "hot", selectedCategoryId);
        const [categoryData, topicData, tagData, feedData] = await Promise.all([
          fetchContentCategories(),
          fetchDiscoverHotTopics(),
          fetchDiscoverHotTags(),
          videoRequest,
        ]);

        if (!active) {
          return;
        }

        setCategories(categoryData.slice(0, 6));
        setHotTopics(topicData.slice(0, 5));
        setHotTags(tagData.slice(0, 6));
        setRecommendedVideos(feedData.list);
        setErrorText(null);
      } catch (error) {
        if (!active) {
          return;
        }

        setErrorText(error instanceof Error ? error.message : "发现页加载失败。");
        setRecommendedVideos([]);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void loadDiscover();
    return () => {
      active = false;
    };
  }, [deferredQuery, selectedCategoryId]);

  useEffect(() => {
    persistDiscoverState();
  }, [searchQuery, selectedCategoryId]);

  useEffect(() => {
    if (loading || hasRestoredScrollRef.current) {
      return;
    }

    hasRestoredScrollRef.current = true;
    const targetScrollTop = initialPersistedState.scrollTop;
    if (!targetScrollTop) {
      return;
    }

    const frame = window.requestAnimationFrame(() => {
      if (containerRef.current) {
        containerRef.current.scrollTop = targetScrollTop;
      }
    });

    return () => window.cancelAnimationFrame(frame);
  }, [initialPersistedState.scrollTop, loading]);

  const filteredVideos = useMemo(() => {
    if (!deferredQuery) {
      return recommendedVideos;
    }

    return recommendedVideos.filter((video) => {
      const haystack = [
        video.title,
        video.summary || "",
        video.author.display_name,
        video.category?.name || "",
        ...video.hashtags,
      ]
        .join(" ")
        .toLowerCase();

      return haystack.includes(deferredQuery);
    });
  }, [deferredQuery, recommendedVideos]);

  const rankingItems: RankingItem[] = useMemo(
    () =>
      hotTopics.map((topic, index) => {
        let trend: RankingItem["trend"] = "";
        if (index === 0 || topic.trend_score >= 12) {
          trend = "热";
        } else if (index === 1) {
          trend = "新";
        }

        return {
          id: topic.id,
          rank: index + 1,
          title: `${topic.name}热门内容`,
          views: `${formatCompactCount(topic.views_count)} 观看`,
          trend,
        };
      }),
    [hotTopics],
  );

  const discoverVideos = filteredVideos.slice(0, 8);

  const openDiscoverWatch = (video: ContentVideoResponse, index: number) => {
    const nextPersistedState: DiscoverPersistedState = {
      searchQuery,
      selectedCategoryId,
      scrollTop: containerRef.current?.scrollTop ?? 0,
    };
    const navigationState: DiscoverWatchNavigationState = {
      source: "discover",
      videos: discoverVideos,
      currentIndex: index,
      persistedState: nextPersistedState,
    };

    writeDiscoverPersistedState(nextPersistedState);
    navigate(`/discover/watch/${video.id}`, { state: navigationState });
  };

  return (
    <div
      ref={containerRef}
      onScroll={() => persistDiscoverState()}
      className="h-full overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-24"
    >
      <div className="mx-auto max-w-screen-xl px-4 py-6">
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="搜索课程、话题、老师..."
              className="w-full rounded-2xl border border-gray-200 bg-white py-3.5 pl-12 pr-4 text-gray-900 placeholder-gray-500 shadow-sm transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>

        {errorText ? (
          <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {errorText}
          </div>
        ) : null}

        <div className="mb-8">
          <h2 className="mb-4 flex items-center gap-2 text-xl font-bold text-gray-900">
            <Flame className="h-6 w-6 text-orange-500" />
            热门分类
          </h2>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
            {loading
              ? [0, 1, 2, 3, 4, 5].map((index) => (
                  <div key={index} className="h-[140px] animate-pulse rounded-2xl bg-white shadow-md" />
                ))
              : categories.map((category, index) => {
                  const decor = categoryDecor[index % categoryDecor.length];
                  const isActive = selectedCategoryId === category.id;
                  const count = deriveCategoryVideoCount(category, hotTopics, recommendedVideos);

                  return (
                    <button
                      key={category.id}
                      type="button"
                      onClick={() =>
                        setSelectedCategoryId((current) => (current === category.id ? null : category.id))
                      }
                      className={`h-[140px] rounded-2xl bg-gradient-to-br ${decor.color} p-3.5 text-left text-white shadow-md transition-all hover:scale-[1.02] hover:shadow-lg ${
                        isActive ? "ring-4 ring-white/70" : ""
                      }`}
                    >
                      <div className="mb-2 flex items-center justify-center h-8 w-8 rounded-full bg-white/20 backdrop-blur-sm">{decor.icon}</div>
                      <div className="text-[1.75rem] font-semibold leading-none mt-1">{category.name}</div>
                      <div className="mt-2 text-base text-white/90">{formatCompactCount(count)} 视频</div>
                    </button>
                  );
                })}
          </div>
        </div>

        <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <h2 className="mb-4 flex items-center gap-2 text-xl font-bold text-gray-900">
              <TrendingUp className="h-6 w-6 text-emerald-500" />
              实时热榜
            </h2>
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-md">
              <div className="space-y-4">
                {loading
                  ? [0, 1, 2, 3, 4].map((index) => (
                      <div key={index} className="h-16 animate-pulse rounded-xl bg-gray-100" />
                    ))
                  : rankingItems.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => setSelectedCategoryId(item.id)}
                        className="group flex w-full items-center gap-4 rounded-xl p-3 text-left transition-colors hover:bg-gray-50"
                      >
                        <div
                          className={`flex h-10 w-10 items-center justify-center rounded-xl font-bold shadow ${
                            item.rank <= 3
                              ? "bg-gradient-to-br from-yellow-400 to-orange-500 text-white"
                              : "bg-gray-200 text-gray-600"
                          }`}
                        >
                          {item.rank}
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <h3 className="line-clamp-1 font-medium text-gray-900 transition-colors group-hover:text-emerald-600">
                              {item.title}
                            </h3>
                            {item.trend ? (
                              <span
                                className={`rounded px-2 py-1 text-xs font-bold text-white ${
                                  item.trend === "热"
                                    ? "bg-gradient-to-r from-red-500 to-pink-500"
                                    : "bg-gradient-to-r from-emerald-500 to-teal-500"
                                }`}
                              >
                                {item.trend}
                              </span>
                            ) : null}
                          </div>
                          <p className="mt-1 text-sm text-gray-600">{item.views}</p>
                        </div>
                      </button>
                    ))}
              </div>
            </div>
          </div>

          <div>
            <h2 className="mb-4 flex items-center gap-2 text-xl font-bold text-gray-900">
              <Hash className="h-6 w-6 text-emerald-500" />
              热门话题
            </h2>
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-md">
              <div className="space-y-3">
                {loading
                  ? [0, 1, 2, 3, 4, 5].map((index) => (
                      <div key={index} className="h-12 animate-pulse rounded-xl bg-gray-100" />
                    ))
                  : hotTags.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => setSearchQuery(item.name)}
                        className="group flex w-full items-center justify-between rounded-xl p-3 text-left transition-colors hover:bg-gray-50"
                      >
                        <div className="flex items-center gap-2">
                          <Hash className="h-4 w-4 text-emerald-500" />
                          <span className="font-medium text-gray-900 transition-colors group-hover:text-emerald-600">
                            {item.name}
                          </span>
                        </div>
                        <span className="text-sm text-gray-600">{formatCompactCount(item.views_count)}</span>
                      </button>
                    ))}
              </div>
            </div>
          </div>
        </div>

        <div>
          <h2 className="mb-4 flex items-center gap-2 text-xl font-bold text-gray-900">
            <Sparkles className="h-6 w-6 text-yellow-500" />
            推荐视频
          </h2>
          {loading ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
              {[0, 1, 2, 3].map((index) => (
                <div key={index} className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-md">
                  <div className="aspect-video animate-pulse bg-gray-100" />
                  <div className="space-y-3 p-4">
                    <div className="h-6 animate-pulse rounded bg-gray-100" />
                    <div className="h-4 w-2/3 animate-pulse rounded bg-gray-100" />
                    <div className="h-4 w-1/2 animate-pulse rounded bg-gray-100" />
                  </div>
                </div>
              ))}
            </div>
          ) : filteredVideos.length ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
              {discoverVideos.map((video, index) => (
                <button
                  key={video.id}
                  type="button"
                  onClick={() => openDiscoverWatch(video, index)}
                  className="group w-full overflow-hidden rounded-2xl border border-gray-200 bg-white text-left shadow-md transition-all hover:border-emerald-500 hover:shadow-lg"
                >
                  <div className="relative aspect-video overflow-hidden bg-gray-200">
                    {video.cover_url ? (
                      <img
                        src={video.cover_url}
                        alt={video.title}
                        className="absolute inset-0 h-full w-full object-cover"
                      />
                    ) : (
                      <video
                        src={video.video_url || undefined}
                        muted
                        playsInline
                        preload="metadata"
                        className="absolute inset-0 h-full w-full object-cover"
                      />
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
                    <div className="absolute bottom-2 right-2 rounded bg-black/70 px-2 py-1 text-xs text-white">
                      {formatDuration(video.duration_seconds)}
                    </div>
                    <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 opacity-0 transition-opacity group-hover:opacity-100">
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 shadow-lg">
                        <Play className="ml-1 h-6 w-6 text-white" />
                      </div>
                    </div>
                  </div>
                  <div className="p-4">
                    <h3 className="mb-2 line-clamp-2 text-sm font-semibold text-gray-900 transition-colors group-hover:text-emerald-600">
                      {video.title}
                    </h3>
                    <p className="mb-1 text-xs text-gray-600">{video.author.display_name}</p>
                    <p className="text-xs text-gray-500">
                      {formatCompactCount(video.interaction.views_count)} 观看
                    </p>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-gray-200 bg-white px-6 py-16 text-center text-gray-500 shadow-sm">
              暂时没有匹配的视频内容。
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
