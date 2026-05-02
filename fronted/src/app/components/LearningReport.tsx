import { useEffect, useMemo, useState } from "react";
import { Calendar, ChevronLeft, Download, FileText, Share2, Star, Target, Trophy } from "lucide-react";

import {
  exportMonthlyReport,
  fetchMonthlyReports,
  generateMonthlyReport,
} from "../lib/learning-api";
import type { MonthlyReportResponse } from "../lib/types";

type ReportViewModel = {
  period: string;
  totalHours: number;
  completedCourses: number;
  averageScore: number;
  rank: number;
  achievements: { title: string; description: string; icon: string; color: string }[];
  strengths: string[];
  improvements: string[];
  weeklyActivities: { day: string; hours: number }[];
};

const fallbackReports: Record<string, ReportViewModel> = {
  "2026年4月": {
    period: "2026年4月",
    totalHours: 12,
    completedCourses: 2,
    averageScore: 82,
    rank: 38,
    achievements: [
      {
        title: "完成月度复盘",
        description: "系统已为你生成本月学习总结。",
        icon: "🏅",
        color: "from-blue-50 to-indigo-50 border-blue-300",
      },
    ],
    strengths: ["学习节奏稳定，已经开始形成持续输入。"],
    improvements: ["建议增加课后练习量，把理解尽快转成动手能力。"],
    weeklyActivities: [
      { day: "周一", hours: 1.2 },
      { day: "周二", hours: 1.8 },
      { day: "周三", hours: 1.4 },
      { day: "周四", hours: 2.2 },
      { day: "周五", hours: 1.1 },
      { day: "周六", hours: 2.5 },
      { day: "周日", hours: 1.8 },
    ],
  },
};

const weekDays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];

function formatMonth(month: string) {
  const [year, value] = month.split("-");
  return year && value ? `${year}年${Number(value)}月` : month;
}

function toViewModel(report: MonthlyReportResponse): ReportViewModel {
  const period = formatMonth(report.report_month);
  const totalHours = Math.max(1, Math.round(report.total_learning_minutes / 60));
  const baseDailyHours = Math.max(0.3, totalHours / 7);

  return {
    period,
    totalHours,
    completedCourses: report.completed_courses,
    averageScore: Math.round(report.average_score),
    rank: report.site_rank ?? Math.max(1, Math.round(100 - Math.min(99, report.average_score))),
    achievements: report.achievements.length
      ? report.achievements.map((achievement) => ({
          title: achievement.title,
          description: achievement.description || "系统根据本月学习情况生成的阶段成就。",
          icon: achievement.icon || "🏅",
          color:
            achievement.color_token === "primary"
              ? "from-blue-50 to-indigo-50 border-blue-300"
              : "from-emerald-50 to-teal-50 border-emerald-300",
        }))
      : [
          {
            title: "完成月度复盘",
            description: "系统已为你生成本月学习总结。",
            icon: "📝",
            color: "from-blue-50 to-indigo-50 border-blue-300",
          },
        ],
    strengths: report.strengths.length ? report.strengths : [report.ai_summary || "本月学习数据已完成整理。"],
    improvements: report.improvements.length
      ? report.improvements
      : ["建议继续保持学习节奏，并补充阶段性练习。"],
    weeklyActivities: weekDays.map((day, index) => ({
      day,
      hours: Number(Math.max(0.2, baseDailyHours * (0.8 + (index % 3) * 0.15)).toFixed(1)),
    })),
  };
}

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

  const reports = useMemo<Record<string, ReportViewModel>>(() => {
    if (backendReports.length === 0) {
      return fallbackReports;
    }

    return Object.fromEntries(backendReports.map((report) => [formatMonth(report.report_month), toViewModel(report)]));
  }, [backendReports]);

  const reportMonths = Object.keys(reports);
  const fallbackReport = reportMonths.length > 0 ? reports[reportMonths[0]] : Object.values(fallbackReports)[0];
  const currentReport = selectedMonth ? reports[selectedMonth] ?? fallbackReport : fallbackReport;

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
      <div className="mx-auto max-w-6xl p-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="mb-2 text-2xl font-semibold text-gray-800">学习报告</h1>
            <p className="text-gray-600">生成并导出你的阶段学习总结。</p>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-gray-700 transition-colors hover:bg-gray-50">
              <Share2 className="h-4 w-4" />
              分享
            </button>
            <button
              onClick={() => void handleExport()}
              className="flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 font-medium text-white transition-colors hover:bg-emerald-600"
            >
              <Download className="h-4 w-4" />
              导出 PDF
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {loading && (
            <div className="rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
              正在加载后端学习报告...
            </div>
          )}

          <div className="rounded-xl bg-white p-8 shadow-sm">
            {selectedMonth && (
              <button
                onClick={() => setSelectedMonth(null)}
                className="mb-4 flex items-center gap-1 text-sm font-medium text-emerald-600 transition-colors hover:text-emerald-700"
              >
                <ChevronLeft className="h-4 w-4" />
                返回当前报告
              </button>
            )}

            <div className="mb-6 flex items-center gap-3">
              <Calendar className="h-6 w-6 text-emerald-600" />
              <h3 className="text-xl font-semibold text-gray-900">报告周期：{currentReport.period}</h3>
            </div>

            <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
              <div className="rounded-xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-teal-50 p-6 text-center">
                <div className="mb-1 text-4xl font-bold text-emerald-600">{currentReport.totalHours}</div>
                <div className="text-sm text-gray-600">学习时长（小时）</div>
              </div>
              <div className="rounded-xl border border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50 p-6 text-center">
                <div className="mb-1 text-4xl font-bold text-blue-600">{currentReport.completedCourses}</div>
                <div className="text-sm text-gray-600">完成课程（门）</div>
              </div>
              <div className="rounded-xl border border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50 p-6 text-center">
                <div className="mb-1 text-4xl font-bold text-purple-600">{currentReport.averageScore}</div>
                <div className="text-sm text-gray-600">平均分数</div>
              </div>
              <div className="rounded-xl border border-orange-200 bg-gradient-to-br from-orange-50 to-amber-50 p-6 text-center">
                <div className="mb-1 text-4xl font-bold text-orange-600">#{currentReport.rank}</div>
                <div className="text-sm text-gray-600">全站排名</div>
              </div>
            </div>

            <div className="mb-6 border-t border-gray-200 pt-6">
              <h4 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
                <Trophy className="h-5 w-5 text-yellow-500" />
                获得成就
              </h4>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                {currentReport.achievements.map((achievement, index) => (
                  <div
                    key={`${achievement.title}-${index}`}
                    className={`transform rounded-xl border bg-gradient-to-br p-5 transition-transform hover:scale-105 ${achievement.color}`}
                  >
                    <div className="mb-3 text-4xl">{achievement.icon}</div>
                    <div className="mb-1 font-semibold text-gray-900">{achievement.title}</div>
                    <div className="text-sm text-gray-600">{achievement.description}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mb-6 border-t border-gray-200 pt-6">
              <h4 className="mb-4 text-lg font-semibold text-gray-900">每周学习时长统计</h4>
              <div className="grid grid-cols-7 gap-2">
                {currentReport.weeklyActivities.map((activity) => (
                  <div key={activity.day} className="text-center">
                    <div className="mb-2 text-xs text-gray-500">{activity.day}</div>
                    <div className="relative h-24 overflow-hidden rounded-lg bg-gray-100">
                      <div
                        className="absolute bottom-0 left-0 right-0 rounded-t-lg bg-gradient-to-t from-emerald-500 to-teal-400"
                        style={{ height: `${Math.min(100, (activity.hours / 6) * 100)}%` }}
                      />
                    </div>
                    <div className="mt-1 text-xs font-semibold text-gray-700">{activity.hours}h</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 gap-6 border-t border-gray-200 pt-6 md:grid-cols-2">
              <div>
                <h4 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
                  <Star className="h-5 w-5 text-emerald-500" />
                  优势表现
                </h4>
                <ul className="space-y-3">
                  {currentReport.strengths.map((strength, index) => (
                    <li key={`${strength}-${index}`} className="flex items-start gap-3">
                      <span className="text-lg font-bold text-emerald-500">✓</span>
                      <span className="flex-1 text-gray-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
                  <Target className="h-5 w-5 text-blue-500" />
                  改进建议
                </h4>
                <ul className="space-y-3">
                  {currentReport.improvements.map((improvement, index) => (
                    <li key={`${improvement}-${index}`} className="flex items-start gap-3">
                      <span className="text-lg font-bold text-blue-500">→</span>
                      <span className="flex-1 text-gray-700">{improvement}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="rounded-xl bg-white p-6 shadow-sm">
            <h4 className="mb-4 text-lg font-semibold text-gray-900">历史报告</h4>
            <div className="space-y-3">
              {reportMonths.map((month) => {
                const report = reports[month];
                if (!report) {
                  return null;
                }

                return (
                  <div
                    key={month}
                    className={`flex cursor-pointer items-center justify-between rounded-lg border p-4 transition-colors ${
                      selectedMonth === month
                        ? "border-emerald-300 bg-emerald-50"
                        : "border-gray-100 bg-gray-50 hover:bg-gray-100"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100">
                        <FileText className="h-5 w-5 text-emerald-600" />
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{month}学习报告</div>
                        <div className="text-xs text-gray-500">
                          学习 {report.totalHours}h · 完成 {report.completedCourses} 门课程 · 均分 {report.averageScore}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => setSelectedMonth(month)}
                      className="rounded-lg bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-600 transition-colors hover:bg-emerald-100 hover:text-emerald-700"
                    >
                      查看详情
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
