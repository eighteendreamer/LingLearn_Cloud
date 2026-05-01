import { useEffect, useState } from "react";
import { FileText, Download, Share2, Calendar, Trophy, Star, Target, ChevronLeft } from "lucide-react";
import {
  exportMonthlyReport,
  fetchMonthlyReports,
  generateMonthlyReport,
} from "../lib/learning-api";
import type { MonthlyReportResponse } from "../lib/types";

const allReports: Record<string, {
  period: string;
  totalHours: number;
  completedCourses: number;
  averageScore: number;
  rank: number;
  achievements: { title: string; description: string; icon: string; color: string }[];
  strengths: string[];
  improvements: string[];
  weeklyActivities: { day: string; hours: number }[];
}> = {
  "2026年4月": {
    period: "2026年4月",
    totalHours: 5,
    completedCourses: 1,
    averageScore: 78,
    rank: 128,
    achievements: [
      { title: "初学乍练", description: "完成第一门课程", icon: "📖", color: "from-blue-50 to-indigo-50 border-blue-300" },
    ],
    strengths: ["学习态度积极，已经开始建立学习习惯"],
    improvements: ["建议每天固定时间学习，保持连续性", "多做一些课后练习巩固知识"],
    weeklyActivities: [
      { day: "周一", hours: 0.5 },
      { day: "周二", hours: 1.2 },
      { day: "周三", hours: 0.8 },
      { day: "周四", hours: 1.5 },
      { day: "周五", hours: 0.3 },
      { day: "周六", hours: 0.5 },
      { day: "周日", hours: 0.2 },
    ],
  },
  "2026年3月": {
    period: "2026年3月",
    totalHours: 128,
    completedCourses: 24,
    averageScore: 87,
    rank: 15,
    achievements: [
      { title: "算法大师", description: "完成所有算法课程", icon: "🏆", color: "from-yellow-50 to-amber-50 border-yellow-300" },
      { title: "编程新星", description: "连续学习30天", icon: "⭐", color: "from-blue-50 to-indigo-50 border-blue-300" },
      { title: "测评达人", description: "完成50次在线练习", icon: "🎯", color: "from-emerald-50 to-teal-50 border-emerald-300" },
    ],
    strengths: [
      "逻辑思维能力强，在算法问题上表现优秀",
      "学习专注度高，能够持续投入时间学习",
      "基础知识扎实，对新概念理解迅速",
    ],
    improvements: [
      "可以增加团队协作项目的参与",
      "尝试更多创新性的编程挑战",
      "平衡各学科学习时间分配",
    ],
    weeklyActivities: [
      { day: "周一", hours: 2.5 },
      { day: "周二", hours: 3.2 },
      { day: "周三", hours: 1.8 },
      { day: "周四", hours: 4.1 },
      { day: "周五", hours: 3.5 },
      { day: "周六", hours: 5.2 },
      { day: "周日", hours: 4.8 },
    ],
  },
  "2026年2月": {
    period: "2026年2月",
    totalHours: 96,
    completedCourses: 18,
    averageScore: 82,
    rank: 23,
    achievements: [
      { title: "坚持不懈", description: "连续学习21天", icon: "🔥", color: "from-orange-50 to-red-50 border-orange-300" },
      { title: "知识探索者", description: "学习3个不同领域", icon: "🔭", color: "from-purple-50 to-pink-50 border-purple-300" },
    ],
    strengths: [
      "Python基础掌握扎实，代码风格规范",
      "善于总结笔记，知识点记忆牢固",
    ],
    improvements: [
      "算法练习量可以再增加",
      "多参与项目实战，将理论转化为实践",
    ],
    weeklyActivities: [
      { day: "周一", hours: 1.8 },
      { day: "周二", hours: 2.4 },
      { day: "周三", hours: 3.1 },
      { day: "周四", hours: 2.0 },
      { day: "周五", hours: 1.5 },
      { day: "周六", hours: 4.0 },
      { day: "周日", hours: 3.2 },
    ],
  },
  "2026年1月": {
    period: "2026年1月",
    totalHours: 74,
    completedCourses: 12,
    averageScore: 76,
    rank: 45,
    achievements: [
      { title: "新年起步", description: "新年第一月坚持学习", icon: "🎉", color: "from-pink-50 to-rose-50 border-pink-300" },
    ],
    strengths: [
      "学习兴趣浓厚，探索了多个技术方向",
      "善于利用碎片时间进行学习",
    ],
    improvements: [
      "需要制定更系统的学习计划",
      "建议增加动手编程的时间比例",
      "可以多和同学交流讨论",
    ],
    weeklyActivities: [
      { day: "周一", hours: 1.2 },
      { day: "周二", hours: 2.0 },
      { day: "周三", hours: 1.5 },
      { day: "周四", hours: 2.8 },
      { day: "周五", hours: 1.0 },
      { day: "周六", hours: 3.5 },
      { day: "周日", hours: 2.5 },
    ],
  },
  "2025年12月": {
    period: "2025年12月",
    totalHours: 56,
    completedCourses: 8,
    averageScore: 71,
    rank: 68,
    achievements: [
      { title: "破冰之旅", description: "完成首次学习评估", icon: "❄️", color: "from-cyan-50 to-blue-50 border-cyan-300" },
    ],
    strengths: [
      "学习态度认真，按时完成课程任务",
      "笔记记录详细，方便复习回顾",
    ],
    improvements: [
      "学习时间还可以更加集中，减少分心",
      "多做一些综合练习提升应试能力",
    ],
    weeklyActivities: [
      { day: "周一", hours: 1.0 },
      { day: "周二", hours: 1.5 },
      { day: "周三", hours: 0.8 },
      { day: "周四", hours: 2.2 },
      { day: "周五", hours: 1.3 },
      { day: "周六", hours: 2.8 },
      { day: "周日", hours: 2.0 },
    ],
  },
};

export function LearningReport() {
  const [selectedMonth, setSelectedMonth] = useState<string | null>(null);
  const [backendReports, setBackendReports] = useState<MonthlyReportResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadReports = async () => {
      try {
        setLoading(true);
        let reports = await fetchMonthlyReports();
        if (reports.length === 0) {
          const now = new Date();
          const month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
          const generated = await generateMonthlyReport(month);
          reports = [generated];
        }
        setBackendReports(reports);
      } catch (error) {
        console.error("Failed to load monthly reports:", error);
      } finally {
        setLoading(false);
      }
    };

    void loadReports();
  }, []);

  const formatMonth = (month: string) => {
    const [year, value] = month.split("-");
    return year && value ? `${year}年${Number(value)}月` : month;
  };

  const backendReportMap = Object.fromEntries(
    backendReports.map((report) => {
      const key = formatMonth(report.report_month);
      const totalHours = Math.round(report.total_learning_minutes / 60);
      const weeklyHours = Math.max(0.2, totalHours / 7);
      return [
        key,
        {
          period: key,
          totalHours,
          completedCourses: report.completed_courses,
          averageScore: Math.round(report.average_score),
          rank: report.site_rank || Math.max(1, Math.round(100 - Math.min(99, report.average_score))),
          achievements: report.achievements.length
            ? report.achievements.map((achievement) => ({
                title: achievement.title,
                description: achievement.description || "后端学习报告生成的成就",
                icon: achievement.icon || "🏆",
                color: achievement.color_token === "primary"
                  ? "from-blue-50 to-indigo-50 border-blue-300"
                  : "from-emerald-50 to-teal-50 border-emerald-300",
              }))
            : [{ title: "完成月度复盘", description: "系统已生成本月学习报告", icon: "📖", color: "from-blue-50 to-indigo-50 border-blue-300" }],
          strengths: report.strengths.length ? report.strengths : [report.ai_summary || "本月学习数据已完成汇总"],
          improvements: report.improvements.length ? report.improvements : ["建议继续保持学习节奏，并补充阶段性练习"],
          weeklyActivities: ["周一", "周二", "周三", "周四", "周五", "周六", "周日"].map((day, index) => ({
            day,
            hours: Number(Math.max(0.1, weeklyHours * (0.75 + (index % 3) * 0.15)).toFixed(1)),
          })),
        },
      ];
    })
  );

  const reports = Object.keys(backendReportMap).length > 0 ? backendReportMap : allReports;
  const reportMonths = Object.keys(reports);
  const currentReport = selectedMonth
    ? reports[selectedMonth]
    : reports[reportMonths[0]] || allReports["2026年3月"];

  const handleExport = async () => {
    const report = backendReports.find((item) => formatMonth(item.report_month) === currentReport.period);
    if (!report) {
      return;
    }
    try {
      await exportMonthlyReport(report.report_month);
    } catch (error) {
      console.error("Failed to export monthly report:", error);
    }
  };

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="p-8 max-w-6xl mx-auto">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-800 mb-2">学习报告</h1>
            <p className="text-gray-600">生成和导出你的学习数据报告</p>
          </div>
          <div className="flex gap-3">
            <button className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2">
              <Share2 className="w-4 h-4" />
              分享
            </button>
            <button
              onClick={() => void handleExport()}
              className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors flex items-center gap-2 font-medium"
            >
              <Download className="w-4 h-4" />
              导出PDF
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {loading && (
            <div className="rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
              正在加载后端学习报告...
            </div>
          )}

          <div className="bg-white rounded-xl p-8 shadow-sm">
            {/* 返回按钮 */}
            {selectedMonth && (
              <button
                onClick={() => setSelectedMonth(null)}
                className="flex items-center gap-1 text-emerald-600 hover:text-emerald-700 text-sm font-medium mb-4 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
                返回当前报告
              </button>
            )}

            <div className="flex items-center gap-3 mb-6">
              <Calendar className="w-6 h-6 text-emerald-600" />
              <h3 className="text-xl font-semibold text-gray-900">报告周期：{currentReport.period}</h3>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="text-center p-6 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl border border-emerald-200">
                <div className="text-4xl font-bold text-emerald-600 mb-1">{currentReport.totalHours}</div>
                <div className="text-sm text-gray-600">学习时长(小时)</div>
              </div>
              <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                <div className="text-4xl font-bold text-blue-600 mb-1">{currentReport.completedCourses}</div>
                <div className="text-sm text-gray-600">完成课程(门)</div>
              </div>
              <div className="text-center p-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-200">
                <div className="text-4xl font-bold text-purple-600 mb-1">{currentReport.averageScore}</div>
                <div className="text-sm text-gray-600">平均分数</div>
              </div>
              <div className="text-center p-6 bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl border border-orange-200">
                <div className="text-4xl font-bold text-orange-600 mb-1">#{currentReport.rank}</div>
                <div className="text-sm text-gray-600">全站排名</div>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-6 mb-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Trophy className="w-5 h-5 text-yellow-500" />
                获得成就
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {currentReport.achievements.map((achievement, index) => (
                  <div key={index} className={`p-5 bg-gradient-to-br ${achievement.color} border rounded-xl transform hover:scale-105 transition-transform`}>
                    <div className="text-4xl mb-3">{achievement.icon}</div>
                    <div className="font-semibold text-gray-900 mb-1">{achievement.title}</div>
                    <div className="text-sm text-gray-600">{achievement.description}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-t border-gray-200 pt-6 mb-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">每周学习时长统计</h4>
              <div className="grid grid-cols-7 gap-2">
                {currentReport.weeklyActivities.map((activity, idx) => (
                  <div key={idx} className="text-center">
                    <div className="text-xs text-gray-500 mb-2">{activity.day.slice(1)}</div>
                    <div className="h-24 bg-gray-100 rounded-lg relative overflow-hidden">
                      <div
                        className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-emerald-500 to-teal-400 rounded-t-lg"
                        style={{ height: `${(activity.hours / 6) * 100}%` }}
                      ></div>
                    </div>
                    <div className="text-xs font-semibold text-gray-700 mt-1">{activity.hours}h</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 border-t border-gray-200 pt-6">
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Star className="w-5 h-5 text-emerald-500" />
                  优势表现
                </h4>
                <ul className="space-y-3">
                  {currentReport.strengths.map((strength, index) => (
                    <li key={index} className="flex gap-3 items-start">
                      <span className="text-emerald-500 font-bold text-lg">✓</span>
                      <span className="text-gray-700 flex-1">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Target className="w-5 h-5 text-blue-500" />
                  改进建议
                </h4>
                <ul className="space-y-3">
                  {currentReport.improvements.map((improvement, index) => (
                    <li key={index} className="flex gap-3 items-start">
                      <span className="text-blue-500 font-bold text-lg">→</span>
                      <span className="text-gray-700 flex-1">{improvement}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">历史报告</h4>
            <div className="space-y-3">
              {reportMonths.map((month) => (
                <div
                  key={month}
                  className={`flex items-center justify-between p-4 rounded-lg transition-colors cursor-pointer border ${
                    selectedMonth === month
                      ? "bg-emerald-50 border-emerald-300"
                      : "bg-gray-50 border-gray-100 hover:bg-gray-100"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-emerald-600" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{month}学习报告</div>
                      <div className="text-xs text-gray-500">学习 {allReports[month].totalHours}h · 完成 {allReports[month].completedCourses}门课程 · 均分 {allReports[month].averageScore}</div>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedMonth(month)}
                    className="text-emerald-600 hover:text-emerald-700 text-sm font-medium px-4 py-2 bg-emerald-50 rounded-lg hover:bg-emerald-100 transition-colors"
                  >
                    查看详情
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
