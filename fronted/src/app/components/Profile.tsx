import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import {
  BarChart3,
  BookMarked,
  BookOpen,
  Brain,
  Calendar,
  Grid3X3,
  Heart,
  MapPin,
  MessageCircle,
  Settings,
  Sparkles,
  Target,
} from "lucide-react";

import { ApiError } from "../lib/api";
import {
  fetchCurrentUser,
  fetchMyLearningPreferences,
  fetchMyWorks,
} from "../lib/account";
import { getStoredCurrentUser, hasSession } from "../lib/session";
import type {
  CurrentUserResponse,
  UserLearningPreferenceInsightResponse,
  UserPreferenceContentItemResponse,
  UserWorkListItemResponse,
} from "../lib/types";

function formatInitial(name: string) {
  return name.trim().charAt(0).toUpperCase() || "L";
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
    return `${Math.floor(diffSeconds / 60)} 分钟前`;
  }
  if (diffSeconds < 86400) {
    return `${Math.floor(diffSeconds / 3600)} 小时前`;
  }
  return `${Math.floor(diffSeconds / 86400)} 天前`;
}

function PreferenceWorkCard({ item }: { item: UserPreferenceContentItemResponse }) {
  return (
    <div className="group cursor-pointer">
      <div className="relative mb-3 aspect-[4/3] overflow-hidden rounded-xl bg-slate-100">
        {item.cover_url ? (
          <img 
            src={item.cover_url} 
            alt={item.title} 
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" 
            loading="lazy" 
          />
        ) : (
          <div className="flex h-full items-center justify-center bg-slate-100 text-slate-400">
            <Grid3X3 className="h-8 w-8 opacity-20" />
          </div>
        )}
        
        {/* Interaction Badges */}
        <div className="absolute right-2 top-2 flex flex-col gap-1.5">
          {item.liked && (
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-black/40 text-white backdrop-blur-md" title="已点赞">
              <Heart className="h-3.5 w-3.5 fill-current" />
            </div>
          )}
          {item.favorited && (
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-black/40 text-white backdrop-blur-md" title="已收藏">
              <BookMarked className="h-3.5 w-3.5 fill-current" />
            </div>
          )}
        </div>
      </div>

      <h4 className="mb-1 line-clamp-2 text-sm font-medium leading-snug text-slate-900 group-hover:text-emerald-600 transition-colors">
        {item.title}
      </h4>
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span className="truncate">{item.author_name}</span>
        <span className="shrink-0">{formatRelativeTime(item.latest_acted_at)}</span>
      </div>
    </div>
  );
}

export function Profile() {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState<CurrentUserResponse | null>(getStoredCurrentUser());
  const [works, setWorks] = useState<UserWorkListItemResponse[]>([]);
  const [preferenceInsight, setPreferenceInsight] = useState<UserLearningPreferenceInsightResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"works" | "preferences">("works");
  const [preferenceFilter, setPreferenceFilter] = useState<string>("all");
  const [isLoading, setIsLoading] = useState(!getStoredCurrentUser());
  const [error, setError] = useState("");

  useEffect(() => {
    if (!hasSession()) {
      navigate("/login", { replace: true });
      return;
    }

    let active = true;
    const load = async () => {
      setIsLoading(true);
      setError("");
      try {
        const me = await fetchCurrentUser();
        const [workPage, preferenceData] = await Promise.all([
          fetchMyWorks(me.profile.user_id),
          fetchMyLearningPreferences(),
        ]);
        if (!active) {
          return;
        }
        setCurrentUser(me);
        setWorks(workPage.list);
        setPreferenceInsight(preferenceData);
      } catch (loadError) {
        if (loadError instanceof ApiError && loadError.status === 401) {
          navigate("/login", { replace: true });
          return;
        }
        if (!active) {
          return;
        }
        setError(loadError instanceof Error ? loadError.message : "加载个人信息失败");
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    void load();
    return () => {
      active = false;
    };
  }, [navigate]);

  const learningToolCards = [
    {
      name: "AI 助手",
      path: "/ai-chat",
      icon: MessageCircle,
      desc: "智能对话学习与即时答疑",
      color: "from-sky-500 to-cyan-500",
      badge: "推荐",
      meta: "对话答疑 · 学习建议",
    },
    {
      name: "学生画像",
      path: "/student-profile",
      icon: Brain,
      desc: "学习能力分析与阶段特征",
      color: "from-purple-500 to-pink-500",
      meta: "能力分析",
    },
    {
      name: "学习路径",
      path: "/learning-path",
      icon: Target,
      desc: "个性化规划与目标推进",
      color: "from-emerald-500 to-teal-500",
      meta: "规划路线",
    },
    {
      name: "在线练习",
      path: "/practice",
      icon: BookOpen,
      desc: "随时训练，快速进入练习状态",
      color: "from-orange-500 to-red-500",
      meta: "立即练习",
    },
    {
      name: "学习评估",
      path: "/assessment",
      icon: BarChart3,
      desc: "过程分析与薄弱项识别",
      color: "from-indigo-500 to-purple-500",
      meta: "查看评估",
    },
    {
      name: "学习报告",
      path: "/report",
      icon: Calendar,
      desc: "阶段总结与学习成果回顾",
      color: "from-green-500 to-emerald-500",
      meta: "阶段总结",
    },
  ];

  if (isLoading && !currentUser) {
    return (
      <div className="flex h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50">
        <div className="text-center">
          <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-500" />
          <p className="text-gray-600">正在加载个人中心...</p>
        </div>
      </div>
    );
  }

  if (!currentUser) {
    return (
      <div className="flex h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50 p-6">
        <div className="max-w-md rounded-3xl bg-white p-8 text-center shadow-xl">
          <h2 className="mb-3 text-2xl font-bold text-gray-900">还没有登录</h2>
          <p className="mb-6 text-gray-600">登录后才能查看你的个人内容和学习偏好作品。</p>
          <Link
            to="/login"
            className="inline-flex items-center justify-center rounded-xl bg-emerald-500 px-5 py-3 font-semibold text-white transition-colors hover:bg-emerald-600"
          >
            去登录
          </Link>
        </div>
      </div>
    );
  }

  const { profile } = currentUser;
  const stats = [
    { label: "获赞", value: profile.stats.likes_received_count.toLocaleString() },
    { label: "关注", value: profile.stats.following_count.toLocaleString() },
    { label: "粉丝", value: profile.stats.followers_count.toLocaleString() },
  ];

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="mx-auto max-w-screen-xl">
        <div className="relative">
          <div className="relative h-40 overflow-hidden bg-gradient-to-br from-emerald-400 via-teal-400 to-blue-400">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(255,255,255,0.35),_transparent_35%),radial-gradient(circle_at_bottom_left,_rgba(255,255,255,0.2),_transparent_30%)]" />
          </div>
          <div className="absolute -bottom-12 left-6">
            <div className="flex h-24 w-24 items-center justify-center rounded-full border-4 border-white bg-gradient-to-br from-emerald-500 to-teal-500 text-3xl font-bold text-white shadow-xl">
              {formatInitial(profile.display_name || profile.username)}
            </div>
          </div>
          <Link to="/settings" className="absolute right-3 top-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/90 shadow-md backdrop-blur-sm transition-all hover:scale-105">
              <Settings className="h-5 w-5 text-gray-700" />
            </div>
          </Link>
        </div>

        <div className="px-6 pb-4 pt-16">
          <h1 className="mb-1 text-xl font-bold text-gray-900">{profile.display_name}</h1>
          <p className="mb-2 text-sm text-gray-600">@{profile.username}</p>
          <p className="mb-4 text-sm text-gray-700">
            {profile.bio || profile.learning_goal || "这个同学还没有填写个人简介。"}
          </p>

          <div className="mb-4 flex flex-wrap gap-2">
            {profile.profession ? (
              <span className="inline-flex rounded-full bg-white px-3 py-1 text-xs text-gray-700 shadow-sm">
                {profile.profession}
              </span>
            ) : null}
            {profile.location ? (
              <span className="inline-flex items-center gap-1 rounded-full bg-white px-3 py-1 text-xs text-gray-700 shadow-sm">
                <MapPin className="h-3.5 w-3.5" />
                {profile.location}
              </span>
            ) : null}
            <span className="inline-flex items-center gap-1 rounded-full bg-white px-3 py-1 text-xs text-gray-700 shadow-sm">
              <Sparkles className="h-3.5 w-3.5" />
              连续学习 {profile.stats.streak_days} 天
            </span>
          </div>

          <div className="mb-4 flex gap-6">
            {stats.map((stat) => (
              <div key={stat.label}>
                <span className="mr-1 font-bold text-gray-900">{stat.value}</span>
                <span className="text-sm text-gray-600">{stat.label}</span>
              </div>
            ))}
          </div>

          <div className="mb-4 grid grid-cols-2 gap-3">
            <div className="rounded-2xl bg-white p-4 shadow-sm">
              <p className="mb-1 text-xs text-gray-500">累计学习时长</p>
              <p className="text-lg font-bold text-gray-900">{profile.stats.total_learning_minutes} 分钟</p>
            </div>
            <div className="rounded-2xl bg-white p-4 shadow-sm">
              <p className="mb-1 text-xs text-gray-500">界面语言</p>
              <p className="text-lg font-bold text-gray-900">{currentUser.settings.language}</p>
            </div>
          </div>

          <Link
            to="/edit-profile"
            className="block w-full rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 py-2.5 text-center text-sm font-bold text-white transition-all hover:scale-105 hover:shadow-lg"
          >
            编辑资料
          </Link>

          {error ? (
            <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
              {error}
            </div>
          ) : null}
        </div>

        <div className="mb-8 px-6">
          <div className="mb-4 flex items-end justify-between gap-4">
            <div>
              <h3 className="text-xl font-bold text-gray-900">学习工具</h3>
              <p className="mt-1 text-sm text-gray-500">把常用学习入口集中到一起，继续你的学习节奏。</p>
            </div>
            <div className="hidden rounded-full border border-emerald-100 bg-white/85 px-3 py-1 text-xs font-medium text-emerald-700 shadow-sm md:block">
              6 个工具可用
            </div>
          </div>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
            {learningToolCards.map((tool) => {
              const Icon = tool.icon;
              return (
                <Link
                  key={tool.path}
                  to={tool.path}
                  className="group relative overflow-hidden rounded-3xl border border-white/70 bg-white/90 p-4 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl"
                >
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(16,185,129,0.08),_transparent_30%),radial-gradient(circle_at_bottom_left,_rgba(59,130,246,0.06),_transparent_35%)] opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                  <div className="relative flex h-full flex-col">
                    <div className="flex items-start justify-between gap-3">
                      <div className={`flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${tool.color} shadow-lg shadow-black/10`}>
                        <Icon className="h-7 w-7 text-white" />
                      </div>
                      {tool.badge ? (
                        <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-[11px] font-semibold text-emerald-700">
                          {tool.badge}
                        </span>
                      ) : (
                        <span className="text-[11px] font-medium text-gray-400 transition-transform duration-300 group-hover:translate-x-1">
                          进入
                        </span>
                      )}
                    </div>
                    <div className="relative mt-5">
                      <h4 className="text-base font-semibold text-gray-900">{tool.name}</h4>
                      <p className="mt-1 text-sm leading-6 text-gray-500">{tool.desc}</p>
                    </div>
                    <div className="relative mt-4 flex items-center justify-between border-t border-gray-100 pt-3 text-xs text-gray-400">
                      <span>{tool.meta}</span>
                      <span className="font-medium text-gray-500 transition-transform duration-300 group-hover:translate-x-1">
                        →
                      </span>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        <div className="border-t border-gray-200">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab("works")}
              className={`flex flex-1 items-center justify-center gap-2 py-3 text-sm ${
                activeTab === "works"
                  ? "border-b-2 border-emerald-600 font-semibold text-emerald-600"
                  : "text-gray-500"
              }`}
            >
              <Grid3X3 className="h-4 w-4" />
              作品
            </button>
            <button
              onClick={() => setActiveTab("preferences")}
              className={`flex flex-1 items-center justify-center gap-2 py-3 text-sm ${
                activeTab === "preferences"
                  ? "border-b-2 border-emerald-600 font-semibold text-emerald-600"
                  : "text-gray-500"
              }`}
            >
              <Heart className="h-4 w-4" />
              学习偏好
            </button>
          </div>
        </div>

        {activeTab === "works" ? (
          works.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 p-6 md:grid-cols-2 xl:grid-cols-3">
              {works.map((work) => (
                <div
                  key={work.id}
                  className="rounded-3xl border border-gray-100 bg-white p-5 shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg"
                >
                  <div className="mb-4 aspect-[4/5] overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-100 via-teal-50 to-blue-100">
                    {work.cover_url ? (
                      <img
                        src={work.cover_url}
                        alt={work.title}
                        className="h-full w-full object-cover"
                        loading="lazy"
                      />
                    ) : null}
                  </div>
                  <h4 className="mb-2 font-semibold text-gray-900">{work.title}</h4>
                  <p className="line-clamp-3 text-sm text-gray-600">
                    {work.summary || "这条作品还没有补充简介。"}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="px-6 py-10">
              <div className="rounded-3xl border border-dashed border-gray-300 bg-white/80 p-10 text-center">
                <h3 className="mb-2 text-lg font-semibold text-gray-900">还没有公开作品</h3>
                <p className="mb-6 text-gray-600">内容模块接好后，这里会显示你发布的视频与学习作品。</p>
                <Link
                  to="/create"
                  className="inline-flex items-center justify-center rounded-xl bg-gray-900 px-5 py-3 font-semibold text-white transition-colors hover:bg-gray-800"
                >
                  去创作中心
                </Link>
              </div>
            </div>
          )
        ) : (
          <div className="px-6 py-8">
            {preferenceInsight?.grouped_works?.length ? (
              <div className="space-y-12">
                <div className="flex gap-2 pb-4 overflow-x-auto no-scrollbar">
                  <button
                    onClick={() => setPreferenceFilter("all")}
                    className={`shrink-0 rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                      preferenceFilter === "all"
                        ? "bg-emerald-600 text-white"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                  >
                    全部
                  </button>
                  {preferenceInsight.grouped_works.map((group) => (
                    <button
                      key={group.key}
                      onClick={() => setPreferenceFilter(group.key)}
                      className={`shrink-0 rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                        preferenceFilter === group.key
                          ? "bg-slate-900 text-white"
                          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                      }`}
                    >
                      {group.name}
                    </button>
                  ))}
                </div>

                {preferenceFilter === "all" ? (
                  <div className="grid grid-cols-2 gap-x-4 gap-y-8 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                    {Array.from(
                      new Map(
                        preferenceInsight.grouped_works
                          .flatMap((group) => group.items)
                          .map((item) => [item.content_id, item])
                      ).values()
                    ).sort((a, b) => new Date(b.latest_acted_at).getTime() - new Date(a.latest_acted_at).getTime())
                    .map((item) => (
                      <PreferenceWorkCard key={`all-${item.content_id}`} item={item} />
                    ))}
                  </div>
                ) : (
                  preferenceInsight.grouped_works
                    .filter((group) => preferenceFilter === group.key)
                    .map((group) => (
                      <section key={group.key}>
                        <div className="mb-6 flex items-center justify-between gap-4">
                          <div>
                            <h3 className="text-lg font-semibold text-slate-900">{group.name}</h3>
                            <p className="mt-1 text-sm text-slate-500">共 {group.item_count} 个作品</p>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-x-4 gap-y-8 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                          {group.items.map((item) => (
                            <PreferenceWorkCard key={`${group.key}-${item.content_id}`} item={item} />
                          ))}
                        </div>
                      </section>
                    ))
                )}
              </div>
            ) : (
              <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50/50 p-12 text-center">
                <h3 className="mb-2 text-base font-medium text-slate-900">还没有偏好作品</h3>
                <p className="text-sm text-slate-500">去发现页点赞或收藏一些内容后，这里会自动按分类展示。</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
