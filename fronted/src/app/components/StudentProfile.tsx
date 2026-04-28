import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";
import { TrendingUp, Award, Target, Zap, ArrowLeft } from "lucide-react";
import { Link } from "react-router";

export function StudentProfile() {
  const profileData = [
    { dimension: "逻辑思维", value: 85, fullMark: 100 },
    { dimension: "创新能力", value: 72, fullMark: 100 },
    { dimension: "学习专注", value: 90, fullMark: 100 },
    { dimension: "团队协作", value: 68, fullMark: 100 },
    { dimension: "问题解决", value: 78, fullMark: 100 },
    { dimension: "知识掌握", value: 82, fullMark: 100 },
  ];

  const stats = [
    { label: "综合评分", value: "79", unit: "分", icon: Award, color: "emerald" },
    { label: "排名", value: "Top 15%", unit: "", icon: TrendingUp, color: "blue" },
    { label: "优势项", value: "3", unit: "个", icon: Zap, color: "yellow" },
    { label: "成长点", value: "2", unit: "个", icon: Target, color: "orange" },
  ];

  const strengths = [
    { title: "学习专注", score: 90, description: "学习时长稳定，注意力集中度高", icon: "🎯" },
    { title: "逻辑思维", score: 85, description: "在算法和数据结构方面表现出色", icon: "🧠" },
    { title: "知识掌握", score: 82, description: "基础知识扎实，理解能力强", icon: "📚" },
  ];

  const improvements = [
    { title: "创新能力", score: 72, description: "可以尝试更多开放性问题和创意项目", icon: "💡" },
    { title: "团队协作", score: 68, description: "建议多参与小组项目和讨论", icon: "🤝" },
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
                <span>每周参加至少一次团队讨论或编程竞赛</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>尝试独立设计创新项目，培养创造力</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>保持现有学习习惯，继续发挥优势</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
