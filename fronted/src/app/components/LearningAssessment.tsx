import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { TrendingUp, TrendingDown } from "lucide-react";

export function LearningAssessment() {
  const weeklyData = [
    { name: "周一", 学习时长: 2.5, 完成任务: 3 },
    { name: "周二", 学习时长: 3.2, 完成任务: 4 },
    { name: "周三", 学习时长: 1.8, 完成任务: 2 },
    { name: "周四", 学习时长: 4.1, 完成任务: 5 },
    { name: "周五", 学习时长: 3.5, 完成任务: 4 },
    { name: "周六", 学习时长: 5.2, 完成任务: 6 },
    { name: "周日", 学习时长: 4.8, 完成任务: 5 },
  ];

  const progressData = [
    { month: "1月", 进度: 45 },
    { month: "2月", 进度: 58 },
    { month: "3月", 进度: 72 },
    { month: "4月", 进度: 78 },
  ];

  const categoryData = [
    { name: "编程", value: 35, color: "#10b981" },
    { name: "算法", value: 25, color: "#3b82f6" },
    { name: "数据库", value: 20, color: "#f59e0b" },
    { name: "前端", value: 15, color: "#8b5cf6" },
    { name: "其他", value: 5, color: "#6b7280" },
  ];

  const performanceMetrics = [
    { label: "平均测试分数", value: "87", unit: "分", trend: "+5%", up: true },
    { label: "课程完成率", value: "92", unit: "%", trend: "+8%", up: true },
    { label: "练习正确率", value: "84", unit: "%", trend: "+3%", up: true },
    { label: "学习专注度", value: "89", unit: "%", trend: "+2%", up: true },
  ];

  const getTrendIcon = (up: boolean) => {
    if (up) return <TrendingUp className="w-4 h-4" />;
    return <TrendingDown className="w-4 h-4" />;
  };

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="p-8 max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-gray-800 mb-2">学习评估</h1>
          <p className="text-gray-600">通过数据可视化了解你的学习表现</p>
        </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {performanceMetrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-xl p-6 shadow-sm">
            <p className="text-sm text-gray-600 mb-3">{metric.label}</p>
            <div className="flex items-end justify-between mb-2">
              <div>
                <span className="text-3xl font-bold text-gray-900">{metric.value}</span>
                <span className="text-lg text-gray-500 ml-1">{metric.unit}</span>
              </div>
            </div>
            <div className={`flex items-center gap-1 text-sm font-semibold ${metric.up ? "text-emerald-600" : "text-red-600"}`}>
              {getTrendIcon(metric.up)}
              <span>{metric.trend}</span>
              <span className="text-gray-500 font-normal">vs 上月</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">每周学习数据</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fill: "#6b7280", fontSize: 12 }} />
              <YAxis tick={{ fill: "#6b7280", fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                }}
              />
              <Legend />
              <Bar dataKey="学习时长" fill="#10b981" radius={[8, 8, 0, 0]} />
              <Bar dataKey="完成任务" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">学习进度趋势</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={progressData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fill: "#6b7280", fontSize: 12 }} />
              <YAxis tick={{ fill: "#6b7280", fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="进度" stroke="#10b981" strokeWidth={3} dot={{ r: 5, fill: "#10b981" }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">学习类别分布</h3>
          <div className="flex items-center justify-center">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-3 mt-4">
            {categoryData.map((item, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                <span className="text-sm text-gray-700">{item.name}</span>
                <span className="text-sm font-semibold text-gray-900">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI 智能建议</h3>
          <div className="space-y-4">
            <div className="p-4 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl">
              <div className="flex items-start gap-3">
                <span className="text-2xl">💪</span>
                <div>
                  <p className="text-sm font-semibold text-emerald-900 mb-1">保持优势</p>
                  <p className="text-sm text-emerald-700">你在编程和算法方面表现出色，继续保持每日练习的习惯。</p>
                </div>
              </div>
            </div>
            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl">
              <div className="flex items-start gap-3">
                <span className="text-2xl">🎯</span>
                <div>
                  <p className="text-sm font-semibold text-blue-900 mb-1">提升重点</p>
                  <p className="text-sm text-blue-700">建议增加数据库相关学习时间，平衡各领域发展。</p>
                </div>
              </div>
            </div>
            <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-xl">
              <div className="flex items-start gap-3">
                <span className="text-2xl">⚡</span>
                <div>
                  <p className="text-sm font-semibold text-purple-900 mb-1">学习节奏</p>
                  <p className="text-sm text-purple-700">你的学习专注度很高，注意适当休息，保持可持续发展。</p>
                </div>
              </div>
            </div>
            <div className="p-4 bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-200 rounded-xl">
              <div className="flex items-start gap-3">
                <span className="text-2xl">📈</span>
                <div>
                  <p className="text-sm font-semibold text-orange-900 mb-1">进步显著</p>
                  <p className="text-sm text-orange-700">本月各项指标均有提升，保持这个势头！</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>
  );
}
