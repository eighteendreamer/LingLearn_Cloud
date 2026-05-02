import { useEffect, useMemo, useState } from "react";
import {
  Calendar,
  ChevronLeft,
  Download,
  FileText,
  Loader2,
  Share2,
  Star,
  Target,
  Trophy,
} from "lucide-react";

import {
  exportMonthlyReport,
  fetchMonthlyReport,
  fetchMonthlyReports,
  generateMonthlyReport,
} from "../lib/learning-api";
import type { MonthlyReportResponse } from "../lib/types";

type ReportViewModel = {
  period: string;
  reportMonth: string;
  totalHours: number;
  completedCourses: number;
  averageScore: number;
  rank: number | null;
  achievements: { title: string; description: string; icon: string; color: string }[];
  strengths: string[];
  improvements: string[];
  summary: string;
  weeklyActivities: { day: string; hours: number }[];
};

const weekDays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];

function formatMonth(month: string) {
  const [year, value] = month.split("-");
  return year && value ? `${year}年${Number(value)}月` : month;
}

function iconLabel(icon: string | null | undefined) {
  const normalized = (icon || "").toLowerCase();
  if (normalized.includes("star")) return "★";
  if (normalized.includes("trophy")) return "奖";
  if (normalized.includes("target")) return "目";
  if (normalized.includes("report")) return "报";
  return "成";
}

function colorTokenToClass(colorToken: string | null | undefined) {
  switch (colorToken) {
    case "primary":
      return "from-blue-50 to-indigo-50 border-blue-300";
    case "warning":
      return "from-orange-50 to-amber-50 border-orange-300";
    case "success":
    default:
      return "from-emerald-50 to-teal-50 border-emerald-300";
  }
}

function buildWeeklyActivities(totalHours: number) {
  const baseDailyHours = Math.max(0.1, totalHours / 7);
  return weekDays.map((day, index) => ({
    day,
    hours: Number(Math.max(0.1, baseDailyHours * (0.8 + (index % 3) * 0.15)).toFixed(1)),
  }));
}

function toViewModel(report: MonthlyReportResponse): ReportViewModel {
  const totalHours = Number((report.total_learning_minutes / 60).toFixed(1));
  const achievements = report.achievements.length
    ? report.achievements.map((achievement) => ({
        title: achievement.title,
        description: achievement.description || "系统根据本月学习数据生成的阶段亮点。",
        icon: iconLabel(achievement.icon),
        color: colorTokenToClass(achievement.color_token),
      }))
    : [
        {
          title: "完成月度复盘",
          description: "系统已根据本月学习数据生成阶段总结。",
          icon: "报",
          color: "from-emerald-50 to-teal-50 border-emerald-300",
        },
      ];

  return {
    period: formatMonth(report.report_month),
    reportMonth: report.report_month,
    totalHours,
    completedCourses: report.completed_courses,
    averageScore: Math.round(report.average_score),
    rank: report.site_rank ?? null,
    achievements,
    strengths: report.strengths.length ? report.strengths.map((item) => String(item)) : ["本月学习数据已开始沉淀。"],
    improvements: report.improvements.length
      ? report.improvements.map((item) => String(item))
      : ["建议继续保持学习节奏，并增加练习后的复盘。"],
    summary: report.ai_summary || "本月学习报告已生成。",
    weeklyActivities: buildWeeklyActivities(totalHours),
  };
}

function currentMonthString() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

export function LearningReport() {
  const [backendReports, setBackendReports] = useState<MonthlyReportResponse[]>([]);
  const [selectedReport, setSelectedReport] = useState<MonthlyReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    void loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      setErrorMessage(null);
      const reports = await fetchMonthlyReports();
      setBackendReports(reports);
      setSelectedReport(reports[0] ?? null);
    } catch (error) {
      console.error("Failed to load monthly reports:", error);
      setErrorMessage(error instanceof Error ? error.message : "加载学习报告失败。");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCurrentMonth = async () => {
    try {
      setGenerating(true);
      setErrorMessage(null);
      const report = await generateMonthlyReport(currentMonthString());
      const reports = await fetchMonthlyReports();
      setBackendReports(reports);
      setSelectedReport(report);
    } catch (error) {
      console.error("Failed to generate monthly report:", error);
      setErrorMessage(error instanceof Error ? error.message : "生成学习报告失败，请稍后重试。");
    } finally {
      setGenerating(false);
    }
  };

  const handleSelectReport = async (reportMonth: string) => {
    try {
      setLoading(true);
      setErrorMessage(null);
      const report = await fetchMonthlyReport(reportMonth);
      setSelectedReport(report);
    } catch (error) {
      console.error("Failed to load report detail:", error);
      setErrorMessage(error instanceof Error ? error.message : "加载报告详情失败。");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    if (!selectedReport) return;
    try {
      setExporting(true);
      await exportMonthlyReport(selectedReport.report_month);
    } catch (error) {
      console.error("Failed to export monthly report:", error);
      setErrorMessage(error instanceof Error ? error.message : "导出 PDF 失败。");
    } finally {
      setExporting(false);
    }
  };

  const currentReport = useMemo(() => (selectedReport ? toViewModel(selectedReport) : null), [selectedReport]);
  const latestMonth = backendReports[0]?.report_month ?? null;
  const isViewingHistory = Boolean(selectedReport && latestMonth && selectedReport.report_month !== latestMonth);

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="mx-auto max-w-6xl p-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="mb-2 text-2xl font-semibold text-gray-800">学习报告</h1>
            <p className="text-gray-600">根据月度学习数据生成阶段总结，并支持查看历史报告详情。</p>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-gray-700 transition-colors hover:bg-gray-50">
              <Share2 className="h-4 w-4" />
              分享
            </button>
            <button
              onClick={() => void handleExport()}
              disabled={!selectedReport || exporting}
              className="flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 font-medium text-white transition-colors hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {exporting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
              导出 PDF
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {loading ? (
            <div className="rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
              正在加载学习报告...
            </div>
          ) : null}

          {errorMessage ? (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
              {errorMessage}
            </div>
          ) : null}

          {!currentReport ? (
            <div className="rounded-xl bg-white p-8 shadow-sm">
              <div className="mx-auto max-w-xl text-center">
                <h2 className="mb-3 text-xl font-semibold text-gray-900">还没有学习报告</h2>
                <p className="mb-6 text-sm leading-7 text-gray-600">
                  学习报告会根据你本月的学习时长、课程完成情况、练习得分和评估结果，
                  再结合学习评估智能体生成一份阶段总结。
                </p>
                <button
                  onClick={() => void handleGenerateCurrentMonth()}
                  disabled={generating}
                  className="inline-flex items-center gap-2 rounded-lg bg-emerald-500 px-6 py-3 text-white transition-colors hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-70"
                >
                  {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                  <span>{generating ? "正在生成本月报告..." : "生成本月报告"}</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="rounded-xl bg-white p-8 shadow-sm">
              {isViewingHistory ? (
                <button
                  onClick={() => setSelectedReport(backendReports[0] ?? selectedReport)}
                  className="mb-4 flex items-center gap-1 text-sm font-medium text-emerald-600 transition-colors hover:text-emerald-700"
                >
                  <ChevronLeft className="h-4 w-4" />
                  返回当前报告
                </button>
              ) : null}

              <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <Calendar className="h-6 w-6 text-emerald-600" />
                  <h3 className="text-xl font-semibold text-gray-900">报告周期：{currentReport.period}</h3>
                </div>
                <button
                  onClick={() => void handleGenerateCurrentMonth()}
                  disabled={generating}
                  className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700 transition-colors hover:bg-emerald-100 disabled:cursor-not-allowed disabled:opacity-70"
                >
                  {generating ? "正在重新生成..." : "重新生成本月报告"}
                </button>
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
                  <div className="mb-1 text-4xl font-bold text-orange-600">
                    {currentReport.rank != null ? `#${currentReport.rank}` : "--"}
                  </div>
                  <div className="text-sm text-gray-600">全站排名</div>
                </div>
              </div>

              <div className="mb-6 rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-4 text-sm leading-7 text-emerald-900">
                {currentReport.summary}
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
          )}

          <div className="rounded-xl bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between gap-3">
              <h4 className="text-lg font-semibold text-gray-900">历史报告</h4>
              <button
                onClick={() => void handleGenerateCurrentMonth()}
                disabled={generating}
                className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {generating ? "生成中..." : "生成本月报告"}
              </button>
            </div>
            {backendReports.length > 0 ? (
              <div className="space-y-3">
                {backendReports.map((report) => {
                  const viewModel = toViewModel(report);
                  const selected = selectedReport?.report_month === report.report_month;
                  return (
                    <div
                      key={report.report_month}
                      className={`flex items-center justify-between rounded-lg border p-4 transition-colors ${
                        selected ? "border-emerald-300 bg-emerald-50" : "border-gray-100 bg-gray-50 hover:bg-gray-100"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100">
                          <FileText className="h-5 w-5 text-emerald-600" />
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{viewModel.period}学习报告</div>
                          <div className="text-xs text-gray-500">
                            学习 {viewModel.totalHours}h · 完成 {viewModel.completedCourses} 门课程 · 均分 {viewModel.averageScore}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => void handleSelectReport(report.report_month)}
                        className="rounded-lg bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-600 transition-colors hover:bg-emerald-100 hover:text-emerald-700"
                      >
                        查看详情
                      </button>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="rounded-lg border border-dashed border-gray-200 px-4 py-6 text-center text-sm text-gray-500">
                还没有历史报告，先生成一份本月报告吧。
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
