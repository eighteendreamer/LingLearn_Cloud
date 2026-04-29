import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import {
  BarChart3,
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
import { fetchCurrentUser, fetchMyWorks } from "../lib/account";
import { getStoredCurrentUser, hasSession } from "../lib/session";
import type { CurrentUserResponse, UserWorkListItemResponse } from "../lib/types";

function formatInitial(name: string) {
  return name.trim().charAt(0).toUpperCase() || "L";
}

export function Profile() {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState<CurrentUserResponse | null>(
    getStoredCurrentUser(),
  );
  const [works, setWorks] = useState<UserWorkListItemResponse[]>([]);
  const [isLoading, setIsLoading] = useState(!getStoredCurrentUser());
  const [error, setError] = useState("");

  useEffect(() => {
    if (!hasSession()) {
      navigate("/login", { replace: true });
      return;
    }

    const load = async () => {
      setIsLoading(true);
      setError("");
      try {
        const me = await fetchCurrentUser();
        setCurrentUser(me);
        const workPage = await fetchMyWorks(me.profile.user_id);
        setWorks(workPage.list);
      } catch (loadError) {
        if (loadError instanceof ApiError && loadError.status === 401) {
          navigate("/login", { replace: true });
          return;
        }
        setError(loadError instanceof Error ? loadError.message : "加载个人信息失败");
      } finally {
        setIsLoading(false);
      }
    };

    void load();
  }, [navigate]);

  const learningTools = [
    { name: "AI 助手", path: "/ai-chat", icon: MessageCircle, desc: "智能对话学习", color: "from-blue-500 to-cyan-500" },
    { name: "学生画像", path: "/student-profile", icon: Brain, desc: "学习能力分析", color: "from-purple-500 to-pink-500" },
    { name: "学习路径", path: "/learning-path", icon: Target, desc: "个性化规划", color: "from-emerald-500 to-teal-500" },
    { name: "在线练习", path: "/practice", icon: BookOpen, desc: "随时训练", color: "from-orange-500 to-red-500" },
    { name: "学习评估", path: "/assessment", icon: BarChart3, desc: "过程分析", color: "from-indigo-500 to-purple-500" },
    { name: "学习报告", path: "/report", icon: Calendar, desc: "阶段总结", color: "from-green-500 to-emerald-500" },
  ];

  if (isLoading && !currentUser) {
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50">
        <div className="text-center">
          <div className="mx-auto mb-4 h-12 w-12 rounded-full border-4 border-emerald-200 border-t-emerald-500 animate-spin"></div>
          <p className="text-gray-600">正在加载个人中心...</p>
        </div>
      </div>
    );
  }

  if (!currentUser) {
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50 p-6">
        <div className="max-w-md rounded-3xl bg-white p-8 shadow-xl text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-3">还没有登录</h2>
          <p className="text-gray-600 mb-6">登录后才能查看你的学习画像和个性化设置。</p>
          <Link
            to="/login"
            className="inline-flex items-center justify-center rounded-xl bg-emerald-500 px-5 py-3 font-semibold text-white hover:bg-emerald-600 transition-colors"
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
      <div className="max-w-screen-xl mx-auto">
        <div className="relative">
          <div className="h-40 bg-gradient-to-br from-emerald-400 via-teal-400 to-blue-400 relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(255,255,255,0.35),_transparent_35%),radial-gradient(circle_at_bottom_left,_rgba(255,255,255,0.2),_transparent_30%)]"></div>
          </div>
          <div className="absolute -bottom-12 left-6">
            <div className="w-24 h-24 rounded-full border-4 border-white bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white text-3xl font-bold shadow-xl">
              {formatInitial(profile.display_name || profile.username)}
            </div>
          </div>
          <Link to="/settings" className="absolute top-3 right-3">
            <div className="w-9 h-9 rounded-lg bg-white/90 backdrop-blur-sm flex items-center justify-center shadow-md hover:scale-105 transition-all">
              <Settings className="w-5 h-5 text-gray-700" />
            </div>
          </Link>
        </div>

        <div className="px-6 pt-16 pb-4">
          <h1 className="text-xl font-bold text-gray-900 mb-1">{profile.display_name}</h1>
          <p className="text-gray-600 text-sm mb-2">@{profile.username}</p>
          <p className="text-gray-700 text-sm mb-4">
            {profile.bio || profile.learning_goal || "这个同学还没有填写个人简介。"}
          </p>

          <div className="flex flex-wrap gap-2 mb-4">
            {profile.profession && (
              <span className="inline-flex items-center rounded-full bg-white px-3 py-1 text-xs text-gray-700 shadow-sm">
                {profile.profession}
              </span>
            )}
            {profile.location && (
              <span className="inline-flex items-center gap-1 rounded-full bg-white px-3 py-1 text-xs text-gray-700 shadow-sm">
                <MapPin className="w-3.5 h-3.5" />
                {profile.location}
              </span>
            )}
            <span className="inline-flex items-center gap-1 rounded-full bg-white px-3 py-1 text-xs text-gray-700 shadow-sm">
              <Sparkles className="w-3.5 h-3.5" />
              连续学习 {profile.stats.streak_days} 天
            </span>
          </div>

          <div className="flex gap-6 mb-4">
            {stats.map((stat) => (
              <div key={stat.label}>
                <span className="text-gray-900 font-bold mr-1">{stat.value}</span>
                <span className="text-gray-600 text-sm">{stat.label}</span>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="rounded-2xl bg-white p-4 shadow-sm">
              <p className="text-xs text-gray-500 mb-1">累计学习时长</p>
              <p className="text-lg font-bold text-gray-900">
                {profile.stats.total_learning_minutes} 分钟
              </p>
            </div>
            <div className="rounded-2xl bg-white p-4 shadow-sm">
              <p className="text-xs text-gray-500 mb-1">界面语言</p>
              <p className="text-lg font-bold text-gray-900">{profile.locale}</p>
            </div>
          </div>

          <Link
            to="/edit-profile"
            className="w-full py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-lg text-sm font-bold hover:shadow-lg hover:scale-105 transition-all text-center block"
          >
            编辑资料
          </Link>

          {error && (
            <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
              {error}
            </div>
          )}
        </div>

        <div className="px-6 mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-gray-900 font-semibold">学习工具</h3>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {learningTools.map((tool) => {
              const Icon = tool.icon;
              return (
                <Link
                  key={tool.path}
                  to={tool.path}
                  className="bg-white rounded-xl p-4 hover:shadow-md hover:scale-105 transition-all border border-gray-200 group"
                >
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${tool.color} flex items-center justify-center shadow-sm mb-2`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-gray-900 text-xs font-medium text-center block">{tool.name}</span>
                  <span className="text-gray-500 text-xs text-center block mt-0.5">{tool.desc}</span>
                </Link>
              );
            })}
          </div>
        </div>

        <div className="border-t border-gray-200">
          <div className="flex border-b border-gray-200">
            <div className="flex-1 py-3 text-emerald-600 border-b-2 border-emerald-600 flex items-center justify-center gap-2 text-sm font-semibold">
              <Grid3X3 className="w-4 h-4" />
              作品
            </div>
            <div className="flex-1 py-3 text-gray-500 flex items-center justify-center gap-2 text-sm">
              <Heart className="w-4 h-4" />
              学习偏好
            </div>
          </div>
        </div>

        {works.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 p-6">
            {works.map((work) => (
              <div
                key={work.id}
                className="rounded-3xl bg-white p-5 shadow-sm border border-gray-100 hover:-translate-y-1 hover:shadow-lg transition-all"
              >
                <div className="aspect-[4/5] overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-100 via-teal-50 to-blue-100 mb-4">
                  {work.cover_url ? (
                    <img
                      src={work.cover_url}
                      alt={work.title}
                      className="h-full w-full object-cover"
                      loading="lazy"
                    />
                  ) : null}
                </div>
                <h4 className="text-gray-900 font-semibold mb-2">{work.title}</h4>
                <p className="text-sm text-gray-600 line-clamp-3">
                  {work.summary || "这条作品还没有补充简介。"}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="px-6 py-10">
            <div className="rounded-3xl border border-dashed border-gray-300 bg-white/80 p-10 text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">还没有公开作品</h3>
              <p className="text-gray-600 mb-6">内容模块接好后，这里会显示你发布的视频与学习作品。</p>
              <Link
                to="/create"
                className="inline-flex items-center justify-center rounded-xl bg-gray-900 px-5 py-3 font-semibold text-white hover:bg-gray-800 transition-colors"
              >
                去创作中心
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
