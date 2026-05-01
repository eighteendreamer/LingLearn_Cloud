import { useEffect, useState } from "react";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";
import { TrendingUp, Award, Target, Zap, ArrowLeft } from "lucide-react";
import { Link } from "react-router";
import { fetchOrGenerateSkillProfile } from "../lib/learning-api";
import type { SkillSnapshotResponse } from "../lib/types";

const fallbackProfileData = [
  { dimension: "逻辑思维", value: 85, fullMark: 100, insight: "在算法和数据结构方面表现出色" },
  { dimension: "创新能力", value: 72, fullMark: 100, insight: "可以尝试更多开放性问题和创意项目" },
  { dimension: "学习专注", value: 90, fullMark: 100, insight: "学习时长稳定，注意力集中度高" },
  { dimension: "团队协作", value: 68, fullMark: 100, insight: "建议多参与小组项目和讨论" },
  { dimension: "问题解决", value: 78, fullMark: 100, insight: "能较好拆解复杂问题" },
  { dimension: "知识掌握", value: 82, fullMark: 100, insight: "基础知识扎实，理解能力强" },
];

export function StudentProfile() {
  const [profile, setProfile] = useState<SkillSnapshotResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        const data = await fetchOrGenerateSkillProfile();
        setProfile(data);
      } catch (error) {
        console.error("Failed to load student profile:", error);
      } finally {
        setLoading(false);
      }
    };

    void loadProfile();
  }, []);

  const profileData = profile?.scores.length
    ? profile.scores.map((score) => ({
        dimension: score.name,
        value: Math.round(score.score),
        fullMark: 100,
        insight: score.insight || `${score.name}当前得分 ${Math.round(score.score)} 分。`,
      }))
    : fallbackProfileData;

  const sortedProfileData = [...profileData].sort((a, b) => b.value - a.value);
  const strengths = sortedProfileData.slice(0, 3).map((item, index) => ({
    title: item.dimension,
    score: item.value,
    description: item.insight,
    icon: ["🎯", "🧠", "📚"][index] || "⭐",
  }));

  const improvements = [...profileData].sort((a, b) => a.value - b.value).slice(0, 2).map((item, index) => ({
    title: item.dimension,
    score: item.value,
    description: item.insight,
    icon: ["💡", "🤝"][index] || "🎯",
  }));

  const averageScore = Math.round(
    profileData.reduce((sum, item) => sum + item.value, 0) / Math.max(profileData.length, 1)
  );

  const stats = [
    { label: "综合评分", value: String(Math.round(profile?.total_score ?? averageScore)), unit: "分", icon: Award, color: "emerald" },
    { label: "排名", value: `Top ${Math.max(1, Math.round(100 - (profile?.rank_percent ?? 85)))}%`, unit: "", icon: TrendingUp, color: "blue" },
    { label: "优势项", value: String(strengths.length), unit: "个", icon: Zap, color: "yellow" },
    { label: "成长点", value: String(improvements.length), unit: "个", icon: Target, color: "orange" },
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, string> = {
      emerald: "bg-emerald-100 text-emerald-600",
      blue: "bg-blue-100 text-blue-600",
      yellow: "bg-yellow-100 text-yellow-600",
      orange: "bg-orange-100 text-orange-600",
    };
    return colors[color] || "bg-gray-100 text-gray-600";
  };

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="sticky top-0 z-10 flex items-center gap-3 p-4 bg-white/95 backdrop-blur-lg border-b border-gray-200 shadow-sm">
        <Link to="/profile">
          <ArrowLeft className="w-6 h-6 text-gray-700" />
        </Link>
        <div>
          <h1 className="text-lg font-semibold text-gray-900">学生画像</h1>
          <p className="text-xs text-gray-600">能力分析报告</p>
        </div>
      </div>

      <div className="px-4 pt-2">
        {loading && (
          <div className="mb-4 rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            正在加载后端能力画像...
          </div>
        )}

        <div className="grid grid-cols-2 gap-3 mb-6">
          {stats.map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <div key={idx} className="bg-white rounded-2xl p-4 border border-gray-200 shadow-md">
                <Icon className="w-5 h-5 text-emerald-500 mb-2" />
                <div className="text-2xl font-bold text-gray-900 mb-1">
                  {stat.value}
                  <span className="text-sm text-gray-600 ml-1">{stat.unit}</span>
                </div>
                <div className="text-xs text-gray-600">{stat.label}</div>
              </div>
            );
          })}
        </div>

        <div className="bg-white rounded-2xl p-5 border border-gray-200 shadow-md mb-4">
          <h3 className="text-gray-900 font-semibold mb-4">六维能力雷达图</h3>
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={profileData}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="dimension" tick={{ fill: "#6b7280", fontSize: 12 }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: "#9ca3af" }} />
              <Radar name="能力值" dataKey="value" stroke="#10b981" fill="#10b981" fillOpacity={0.3} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-gray-200 shadow-md mb-4">
          <h3 className="text-gray-900 font-semibold mb-4">维度详情</h3>
          <div className="space-y-4">
            {profileData.map((item) => (
              <div key={item.dimension}>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-700">{item.dimension}</span>
                  <span className="text-emerald-600 font-bold">{item.value}分</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-emerald-400 to-teal-500 h-2 rounded-full"
                    style={{ width: `${item.value}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-3 mb-4">
          <h3 className="text-gray-900 font-semibold flex items-center gap-2">
            <span>⭐</span>
            优势能力
          </h3>
          {strengths.map((item, index) => (
            <div key={index} className="p-4 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl shadow-sm">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl">{item.icon}</span>
                <div className="flex-1 flex items-center justify-between">
                  <span className="font-semibold text-gray-900">{item.title}</span>
                  <span className="text-emerald-600 font-bold">{item.score}分</span>
                </div>
              </div>
              <p className="text-sm text-gray-700 ml-11">{item.description}</p>
            </div>
          ))}
        </div>

        <div className="space-y-3">
          <h3 className="text-gray-900 font-semibold flex items-center gap-2">
            <span>🎯</span>
            成长建议
          </h3>
          {improvements.map((item, index) => (
            <div key={index} className="p-4 bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-200 rounded-xl shadow-sm">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl">{item.icon}</span>
                <div className="flex-1 flex items-center justify-between">
                  <span className="font-semibold text-gray-900">{item.title}</span>
                  <span className="text-orange-600 font-bold">{item.score}分</span>
                </div>
              </div>
              <p className="text-sm text-gray-700 ml-11">{item.description}</p>
            </div>
          ))}

          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-xl shadow-sm">
            <h4 className="font-semibold text-blue-700 mb-3 flex items-center gap-2 text-sm">
              <span>📝</span>
              AI个性化建议
            </h4>
            <ul className="space-y-2 text-xs text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>优先强化 {improvements[0]?.title || "薄弱维度"}，配合练习和复盘形成闭环</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>继续保持 {strengths[0]?.title || "优势能力"}，把优势迁移到真实项目</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>{profile ? `画像生成时间：${new Date(profile.generated_at).toLocaleString()}` : "暂无后端画像时使用默认建议"}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
