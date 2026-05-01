import { useEffect, useMemo, useState } from "react";
import { Clock, BookmarkCheck, TrendingUp, Target, Play, ChevronRight } from "lucide-react";

import { fetchCurrentUser, fetchMyFavorites, fetchMyWatchHistory } from "../lib/account";
import { hasSession } from "../lib/session";
import type {
  ContentFavoriteItemResponse,
  ContentVideoResponse,
  ContentWatchHistoryItemResponse,
  CurrentUserResponse,
} from "../lib/types";

function formatDuration(seconds?: number | null) {
  if (!seconds || seconds <= 0) {
    return "00:00";
  }
  const minutes = Math.floor(seconds / 60);
  const remain = Math.floor(seconds % 60);
  return `${String(minutes).padStart(2, "0")}:${String(remain).padStart(2, "0")}`;
}

function formatRelativeTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  const diffSeconds = Math.max(0, Math.floor((Date.now() - date.getTime()) / 1000));
  if (diffSeconds < 60) {
    return "刚刚";
  }
  if (diffSeconds < 3600) {
    return `${Math.floor(diffSeconds / 60)}分钟前`;
  }
  if (diffSeconds < 86400) {
    return `${Math.floor(diffSeconds / 3600)}小时前`;
  }
  return `${Math.floor(diffSeconds / 86400)}天前`;
}

function getAuthorName(video: ContentVideoResponse) {
  return video.author.display_name || "LingLearn 创作者";
}

export function MyLearning() {
  const [currentUser, setCurrentUser] = useState<CurrentUserResponse | null>(null);
  const [favoriteItems, setFavoriteItems] = useState<ContentFavoriteItemResponse[]>([]);
  const [watchItems, setWatchItems] = useState<ContentWatchHistoryItemResponse[]>([]);
  const [favoritesTotal, setFavoritesTotal] = useState(0);
  const [watchTotal, setWatchTotal] = useState(0);

  useEffect(() => {
    if (!hasSession()) {
      return;
    }

    let active = true;
    async function loadLearningData() {
      try {
        const [me, favoritesPage, watchHistoryPage] = await Promise.all([
          fetchCurrentUser(),
          fetchMyFavorites(1, 6),
          fetchMyWatchHistory(1, 6),
        ]);
        if (!active) {
          return;
        }
        setCurrentUser(me);
        setFavoriteItems(favoritesPage.list);
        setWatchItems(watchHistoryPage.list);
        setFavoritesTotal(favoritesPage.total);
        setWatchTotal(watchHistoryPage.total);
      } catch {
        if (!active) {
          return;
        }
        setFavoriteItems([]);
        setWatchItems([]);
      }
    }

    void loadLearningData();
    return () => {
      active = false;
    };
  }, []);

  const completedCount = useMemo(
    () => watchItems.filter((item) => item.completed || item.watch_progress >= 100).length,
    [watchItems],
  );
  const watchedMinutes = useMemo(
    () => watchItems.reduce((total, item) => total + Math.floor(item.watch_seconds / 60), 0),
    [watchItems],
  );
  const learningMinutes = currentUser?.profile.stats.total_learning_minutes || watchedMinutes;

  const stats = [
    { label: "学习时长", value: String(Math.max(0, Math.round(learningMinutes / 60))), unit: "小时", icon: Clock, color: "emerald" },
    { label: "已收藏", value: String(favoritesTotal), unit: "个", icon: BookmarkCheck, color: "blue" },
    { label: "连续天数", value: String(currentUser?.profile.stats.streak_days ?? 0), unit: "天", icon: TrendingUp, color: "orange" },
    { label: "完成目标", value: String(completedCount || watchTotal), unit: "个", icon: Target, color: "purple" },
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, string> = {
      emerald: "from-emerald-400 to-teal-500",
      blue: "from-blue-400 to-indigo-500",
      orange: "from-orange-400 to-amber-500",
      purple: "from-purple-400 to-pink-500",
    };
    return colors[color] || "from-gray-400 to-gray-500";
  };

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="max-w-screen-xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">我的学习</h1>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {stats.map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <div
                key={idx}
                className="bg-white rounded-2xl p-5 border border-gray-200 shadow-md"
              >
                <div
                  className={`w-12 h-12 rounded-xl bg-gradient-to-br ${getColorClasses(
                    stat.color
                  )} flex items-center justify-center mb-3 shadow-sm`}
                >
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-1">
                  {stat.value}
                  <span className="text-lg text-gray-600 ml-1">{stat.unit}</span>
                </div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            );
          })}
        </div>

        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">我的收藏</h2>
            <button className="text-emerald-600 text-sm flex items-center gap-1 hover:text-emerald-700">
              查看全部
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {favoriteItems.map(({ content }) => {
              const progress = watchItems.find((item) => item.content.id === content.id)?.watch_progress ?? 0;
              const Wrapper = content.video_url ? "a" : "div";
              return (
                <Wrapper
                  key={content.id}
                  {...(content.video_url ? { href: content.video_url, target: "_blank", rel: "noreferrer" } : {})}
                  className="bg-white rounded-2xl overflow-hidden border border-gray-200 hover:border-emerald-500 transition-all cursor-pointer group shadow-md hover:shadow-lg"
                >
                  <div className="relative">
                    <div className="aspect-video bg-gray-200 relative overflow-hidden">
                      {content.cover_url ? (
                        <img
                          src={content.cover_url}
                          alt={content.title}
                          className="absolute inset-0 w-full h-full object-cover"
                        />
                      ) : null}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent"></div>
                      <div className="absolute bottom-2 right-2 px-2 py-1 bg-black/70 rounded text-white text-xs">
                        {formatDuration(content.duration_seconds)}
                      </div>
                      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="w-14 h-14 rounded-full bg-emerald-500 flex items-center justify-center shadow-lg">
                          <Play className="w-6 h-6 text-white ml-1" />
                        </div>
                      </div>
                    </div>
                    {progress > 0 && (
                      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-300">
                        <div
                          className="h-full bg-emerald-500"
                          style={{ width: `${Math.min(progress, 100)}%` }}
                        ></div>
                      </div>
                    )}
                  </div>
                  <div className="p-4">
                    <h3 className="text-gray-900 font-semibold mb-1 line-clamp-1">{content.title}</h3>
                    <p className="text-gray-600 text-sm">{getAuthorName(content)}</p>
                    {progress > 0 && progress < 100 && (
                      <p className="text-emerald-600 text-xs mt-2">已学习 {Math.round(progress)}%</p>
                    )}
                    {progress >= 100 && (
                      <p className="text-emerald-600 text-xs mt-2">已完成</p>
                    )}
                  </div>
                </Wrapper>
              );
            })}
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">最近观看</h2>
            <button className="text-emerald-600 text-sm flex items-center gap-1 hover:text-emerald-700">
              查看全部
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          <div className="space-y-3">
            {watchItems.map(({ content, last_viewed_at }) => {
              const Wrapper = content.video_url ? "a" : "div";
              return (
                <Wrapper
                  key={content.id}
                  {...(content.video_url ? { href: content.video_url, target: "_blank", rel: "noreferrer" } : {})}
                  className="flex gap-3 bg-white rounded-xl p-3 border border-gray-200 hover:border-emerald-500 transition-all cursor-pointer group shadow-sm hover:shadow-md"
                >
                  <div className="w-32 h-20 bg-gray-200 rounded-lg flex-shrink-0 relative overflow-hidden">
                    {content.cover_url ? (
                      <img
                        src={content.cover_url}
                        alt={content.title}
                        className="absolute inset-0 w-full h-full object-cover"
                      />
                    ) : null}
                    <div className="absolute inset-0 bg-white/70 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <Play className="w-8 h-8 text-emerald-600" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-gray-900 font-semibold mb-1 line-clamp-1">{content.title}</h3>
                    <p className="text-gray-600 text-sm mb-2">{getAuthorName(content)}</p>
                    <p className="text-gray-500 text-xs">{formatRelativeTime(last_viewed_at)}</p>
                  </div>
                </Wrapper>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
