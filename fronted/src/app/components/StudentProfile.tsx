import { useEffect, useState } from "react";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";
import { TrendingUp, Award, Target, Zap, ArrowLeft, Loader2, Sparkles, Brain, Compass, Lightbulb } from "lucide-react";
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
    icon: [Zap, Brain, Target][index] || Zap,
  }));

  const improvements = [...profileData].sort((a, b) => a.value - b.value).slice(0, 2).map((item, index) => ({
    title: item.dimension,
    score: item.value,
    description: item.insight,
    icon: [Compass, Lightbulb][index] || Compass,
  }));

  const averageScore = Math.round(
    profileData.reduce((sum, item) => sum + item.value, 0) / Math.max(profileData.length, 1)
  );

  const stats = [
    { label: "综合评分", value: String(Math.round(profile?.total_score ?? averageScore)), unit: "分", icon: Award },
    { label: "排名", value: `Top ${Math.max(1, Math.round(100 - (profile?.rank_percent ?? 85)))}%`, unit: "", icon: TrendingUp },
    { label: "优势项", value: String(strengths.length), unit: "个", icon: Zap },
    { label: "成长点", value: String(improvements.length), unit: "个", icon: Target },
  ];

  return (
    <div className="h-screen overflow-y-auto bg-slate-50 pb-24 font-sans text-slate-900 selection:bg-slate-200">
      
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-slate-200/60 bg-white/80 px-6 py-4 backdrop-blur-md">
        <div className="mx-auto flex max-w-[1200px] items-center gap-4">
          <Link
            to="/profile"
            className="flex h-10 w-10 items-center justify-center rounded-full transition-colors hover:bg-slate-100"
          >
            <ArrowLeft className="h-5 w-5 text-slate-600" />
          </Link>
          <div>
            <h1 className="text-xl font-medium tracking-tight text-slate-900">学生画像</h1>
            <p className="text-xs text-slate-500">基于学习数据的多维能力分析</p>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1200px] px-6 py-8">
        
        {loading && (
          <div className="mb-8 flex items-center justify-center rounded-xl border border-slate-200 bg-white py-12 text-sm text-slate-500 shadow-sm">
            <Loader2 className="mr-2 h-5 w-5 animate-spin text-emerald-500" />
            正在加载并生成能力画像...
          </div>
        )}

        <div className="grid grid-cols-1 items-start gap-8 lg:grid-cols-12">
          
          {/* Left Column: Stats & Radar */}
          <div className="space-y-8 lg:col-span-7 xl:col-span-8">
            
            {/* Overview Stats */}
            <section className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {stats.map((stat, idx) => {
                const Icon = stat.icon;
                return (
                  <div key={idx} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
                    <Icon className="mb-3 h-5 w-5 text-emerald-600" />
                    <div className="flex items-baseline gap-1">
                      <span className="text-2xl font-semibold tracking-tight text-slate-900">{stat.value}</span>
                      <span className="text-sm font-medium text-slate-500">{stat.unit}</span>
                    </div>
                    <div className="mt-1 text-xs text-slate-500">{stat.label}</div>
                  </div>
                );
              })}
            </section>

            {/* Radar Chart */}
            <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-6 flex items-center gap-2 text-lg font-medium text-slate-900">
                <Radar className="h-5 w-5 text-slate-400" />
                六维能力图谱
              </h2>
              <div className="h-[320px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={profileData} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis 
                      dataKey="dimension" 
                      tick={{ fill: "#475569", fontSize: 13, fontWeight: 500 }} 
                    />
                    <PolarRadiusAxis 
                      angle={90} 
                      domain={[0, 100]} 
                      tick={{ fill: "#94a3b8", fontSize: 11 }} 
                      axisLine={false}
                    />
                    <Radar 
                      name="能力值" 
                      dataKey="value" 
                      stroke="#059669" 
                      fill="#10b981" 
                      fillOpacity={0.25} 
                      strokeWidth={2} 
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </section>

            {/* Dimension Progress Bars */}
            <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-6 text-lg font-medium text-slate-900">维度详情分解</h2>
              <div className="grid gap-x-8 gap-y-6 sm:grid-cols-2">
                {profileData.map((item) => (
                  <div key={item.dimension}>
                    <div className="mb-2 flex items-center justify-between text-sm">
                      <span className="font-medium text-slate-700">{item.dimension}</span>
                      <span className="font-semibold text-emerald-600">{item.value} 分</span>
                    </div>
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-emerald-500 transition-all duration-500"
                        style={{ width: `${item.value}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* Right Column: Insights & Recommendations */}
          <div className="space-y-6 lg:col-span-5 xl:col-span-4">
            
            {/* Strengths */}
            <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-5 flex items-center gap-2 text-base font-medium text-slate-900">
                <Zap className="h-4 w-4 text-emerald-500" />
                核心优势
              </h2>
              <div className="space-y-4">
                {strengths.map((item, index) => {
                  const Icon = item.icon;
                  return (
                    <div key={index} className="rounded-lg border border-slate-100 bg-slate-50/50 p-4 transition-colors hover:bg-slate-50">
                      <div className="mb-2 flex items-start justify-between gap-3">
                        <div className="flex items-center gap-2">
                          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                            <Icon className="h-3.5 w-3.5" />
                          </div>
                          <span className="font-medium text-slate-900">{item.title}</span>
                        </div>
                        <span className="rounded-md bg-white px-2 py-0.5 text-xs font-semibold text-emerald-600 shadow-sm border border-slate-100">
                          {item.score} 分
                        </span>
                      </div>
                      <p className="text-sm leading-relaxed text-slate-600 ml-9">{item.description}</p>
                    </div>
                  );
                })}
              </div>
            </section>

            {/* Improvements */}
            <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-5 flex items-center gap-2 text-base font-medium text-slate-900">
                <Target className="h-4 w-4 text-slate-400" />
                成长空间
              </h2>
              <div className="space-y-4">
                {improvements.map((item, index) => {
                  const Icon = item.icon;
                  return (
                    <div key={index} className="rounded-lg border border-slate-100 bg-slate-50/50 p-4 transition-colors hover:bg-slate-50">
                      <div className="mb-2 flex items-start justify-between gap-3">
                        <div className="flex items-center gap-2">
                          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-200 text-slate-600">
                            <Icon className="h-3.5 w-3.5" />
                          </div>
                          <span className="font-medium text-slate-900">{item.title}</span>
                        </div>
                        <span className="rounded-md bg-white px-2 py-0.5 text-xs font-medium text-slate-500 shadow-sm border border-slate-100">
                          {item.score} 分
                        </span>
                      </div>
                      <p className="text-sm leading-relaxed text-slate-600 ml-9">{item.description}</p>
                    </div>
                  );
                })}
              </div>
            </section>

            {/* AI Suggestion */}
            <section className="rounded-xl border border-emerald-100 bg-emerald-50/50 p-5">
              <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-emerald-800">
                <Sparkles className="h-4 w-4" />
                AI 综合诊断
              </h2>
              <ul className="space-y-2.5 text-sm text-emerald-700/90">
                <li className="flex items-start gap-2">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
                  <span className="leading-relaxed">优先强化 <strong className="font-medium text-emerald-800">{improvements[0]?.title || "薄弱维度"}</strong>，建议在接下来的学习计划中增加相关练习。</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
                  <span className="leading-relaxed">继续保持 <strong className="font-medium text-emerald-800">{strengths[0]?.title || "优势能力"}</strong> 的领先，尝试将其应用到更复杂的实战项目中。</span>
                </li>
                {profile && (
                  <li className="flex items-start gap-2">
                    <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
                    <span className="text-xs opacity-80">报告生成于：{new Date(profile.generated_at).toLocaleString()}</span>
                  </li>
                )}
              </ul>
            </section>

          </div>
        </div>
      </main>
    </div>
  );
}
