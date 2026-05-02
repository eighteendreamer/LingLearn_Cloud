import { useEffect, useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { AlertCircle, Loader2, TrendingDown, TrendingUp } from "lucide-react";
import { apiRequest, ApiError } from "../lib/api";
import type { AssessmentSnapshotResponse, AssessmentTrendResponse } from "../lib/types";

type AssessmentMetrics = {
  profile?: {
    display_name?: string | null;
    learning_goal?: string | null;
    streak_days?: number | null;
  };
  watch_metrics?: {
    total_learning_minutes?: number;
    active_days?: number;
    period_days?: number;
    avg_watch_progress?: number;
    category_breakdown?: Array<{
      name: string;
      value: number;
      watch_minutes?: number;
    }>;
  };
  practice_metrics?: {
    session_count?: number;
    completed_session_count?: number;
    total_questions?: number;
    answered_questions?: number;
    correct_answers?: number;
  };
  course_metrics?: {
    completed_courses_total?: number;
    completed_courses_period?: number;
    active_courses_period?: number;
  };
  report?: {
    overview?: string;
    diagnosis?: string;
    learner_portrait?: string;
    optimization?: string;
    recommendations?: Array<{
      type?: string;
      title?: string;
      description?: string;
    }>;
  };
};

const PIE_COLORS = ["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#ef4444"];

function formatDelta(current: number | null | undefined, previous: number | null | undefined, suffix = "") {
  if (current == null || previous == null) {
    return "本周期";
  }
  const delta = current - previous;
  if (Math.abs(delta) < 0.01) {
    return `较上期持平${suffix}`;
  }
  return `${delta > 0 ? "+" : ""}${delta.toFixed(1)}${suffix}`;
}

function formatShortDate(input: string) {
  if (!input) {
    return "";
  }
  return input.slice(5);
}

export function LearningAssessment() {
  const [assessment, setAssessment] = useState<AssessmentSnapshotResponse | null>(null);
  const [trend, setTrend] = useState<AssessmentTrendResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    void loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setErrorMessage(null);
      const [assessmentData, trendData] = await Promise.all([
        apiRequest<AssessmentSnapshotResponse | null>("/users/me/assessments/latest"),
        apiRequest<AssessmentTrendResponse>("/users/me/assessments/trend?assessment_type=weekly"),
      ]);
      setAssessment(assessmentData);
      setTrend(trendData);
    } catch (error) {
      console.error("Failed to load assessment data:", error);
      setErrorMessage(error instanceof Error ? error.message : "加载学习评估失败。");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (forceRegenerate = false) => {
    try {
      setGenerating(true);
      setErrorMessage(null);
      const nextAssessment = await apiRequest<AssessmentSnapshotResponse>("/users/me/assessments/generate", {
        method: "POST",
        body: JSON.stringify({ assessment_type: "weekly", force_regenerate: forceRegenerate }),
      });
      setAssessment(nextAssessment);
      const nextTrend = await apiRequest<AssessmentTrendResponse>("/users/me/assessments/trend?assessment_type=weekly");
      setTrend(nextTrend);
    } catch (error) {
      console.error("Failed to generate assessment:", error);
      setErrorMessage(
        error instanceof ApiError ? error.message : "生成学习评估报告失败，请稍后重试。",
      );
    } finally {
      setGenerating(false);
    }
  };

  const metrics = (assessment?.metrics_json ?? {}) as AssessmentMetrics;
  const report = metrics.report ?? {};
  const watchMetrics = metrics.watch_metrics ?? {};
  const practiceMetrics = metrics.practice_metrics ?? {};
  const courseMetrics = metrics.course_metrics ?? {};
  const profile = metrics.profile ?? {};

  const previousPoint = trend && trend.data_points.length > 1 ? trend.data_points[trend.data_points.length - 2] : null;

  const performanceMetrics = useMemo(() => {
    if (!assessment) {
      return [];
    }
    return [
      {
        label: "学习时长",
        value: assessment.total_learning_minutes.toString(),
        unit: "分钟",
        trend: formatDelta(assessment.total_learning_minutes, previousPoint?.learning_minutes, " 分钟"),
        up: previousPoint ? assessment.total_learning_minutes >= previousPoint.learning_minutes : true,
      },
      {
        label: "练习均分",
        value: assessment.average_score.toFixed(0),
        unit: "分",
        trend: formatDelta(assessment.average_score, previousPoint?.average_score, " 分"),
        up: previousPoint ? assessment.average_score >= previousPoint.average_score : true,
      },
      {
        label: "练习正确率",
        value: assessment.correct_rate?.toFixed(0) || "0",
        unit: "%",
        trend: formatDelta(assessment.correct_rate, previousPoint?.correct_rate, "%"),
        up: previousPoint ? (assessment.correct_rate ?? 0) >= (previousPoint.correct_rate ?? 0) : true,
      },
      {
        label: "学习专注度",
        value: assessment.focus_rate?.toFixed(0) || "0",
        unit: "%",
        trend: "基于活跃天数、观看进度和完成度计算",
        up: true,
      },
    ];
  }, [assessment, previousPoint]);

  const weeklyData = useMemo(
    () =>
      trend?.data_points.map((point) => ({
        name: formatShortDate(point.date),
        learningHours: Number((point.learning_minutes / 60).toFixed(1)),
        averageScore: Number(point.average_score.toFixed(1)),
      })) ?? [],
    [trend],
  );

  const categoryData = useMemo(
    () =>
      (watchMetrics.category_breakdown ?? []).map((item, index) => ({
        ...item,
        color: PIE_COLORS[index % PIE_COLORS.length],
      })),
    [watchMetrics.category_breakdown],
  );

  const getTrendIcon = (up: boolean) => {
    if (up) return <TrendingUp className="w-4 h-4" />;
    return <TrendingDown className="w-4 h-4" />;
  };

  if (loading) {
    return (
      <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
        <div className="mx-auto max-w-7xl p-8">
          <div className="flex h-64 items-center justify-center gap-3 text-gray-500">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>正在加载学习评估...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!assessment) {
    return (
      <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
        <div className="mx-auto max-w-7xl p-8">
          <div className="mb-6">
            <h1 className="mb-2 text-2xl font-semibold text-gray-800">学习评估</h1>
            <p className="text-gray-600">通过真实学习数据和学习评估智能体，生成你的阶段性学习报告。</p>
          </div>

          <div className="rounded-2xl bg-white p-8 shadow-sm">
            <div className="mx-auto max-w-xl text-center">
              <h2 className="mb-3 text-xl font-semibold text-gray-900">还没有评估数据</h2>
              <p className="mb-6 text-sm leading-7 text-gray-600">
                评估报告会综合你最近的学习时长、练习成绩、课程推进和观看主题分布，
                再调用学习评估智能体生成诊断结论与改进建议。
              </p>
              {errorMessage ? (
                <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                  {errorMessage}
                </div>
              ) : null}
              <button
                onClick={() => void handleGenerate()}
                disabled={generating}
                className="inline-flex items-center gap-2 rounded-lg bg-emerald-500 px-6 py-3 text-white transition-colors hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                <span>{generating ? "正在生成评估报告..." : "生成评估报告"}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="mx-auto max-w-7xl p-8">
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="mb-2 text-2xl font-semibold text-gray-800">学习评估</h1>
            <p className="text-gray-600">
              用真实学习数据生成趋势图，并结合学习评估智能体输出阶段总结与优化建议。
            </p>
          </div>
          <button
            onClick={() => void handleGenerate(true)}
            disabled={generating}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-500 px-5 py-3 text-white transition-colors hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            <span>{generating ? "正在重新生成..." : "重新生成评估报告"}</span>
          </button>
        </div>

        {errorMessage ? (
          <div className="mb-6 flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        ) : null}

        <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {performanceMetrics.map((metric) => (
            <div key={metric.label} className="rounded-2xl bg-white p-6 shadow-sm">
              <p className="mb-3 text-sm text-gray-600">{metric.label}</p>
              <div className="mb-2 flex items-end justify-between">
                <div>
                  <span className="text-3xl font-bold text-gray-900">{metric.value}</span>
                  <span className="ml-1 text-lg text-gray-500">{metric.unit}</span>
                </div>
              </div>
              <div className={`flex items-center gap-1 text-sm font-semibold ${metric.up ? "text-emerald-600" : "text-red-600"}`}>
                {getTrendIcon(metric.up)}
                <span>{metric.trend}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="rounded-2xl bg-white p-6 shadow-sm">
            <p className="mb-1 text-sm text-gray-500">连续学习</p>
            <p className="text-2xl font-semibold text-gray-900">{profile.streak_days ?? 0} 天</p>
          </div>
          <div className="rounded-2xl bg-white p-6 shadow-sm">
            <p className="mb-1 text-sm text-gray-500">本周期完成课程</p>
            <p className="text-2xl font-semibold text-gray-900">{courseMetrics.completed_courses_period ?? 0} 门</p>
            <p className="mt-2 text-sm text-gray-500">累计完成 {courseMetrics.completed_courses_total ?? 0} 门</p>
          </div>
          <div className="rounded-2xl bg-white p-6 shadow-sm">
            <p className="mb-1 text-sm text-gray-500">练习完成情况</p>
            <p className="text-2xl font-semibold text-gray-900">
              {practiceMetrics.completed_session_count ?? 0} / {practiceMetrics.session_count ?? 0}
            </p>
            <p className="mt-2 text-sm text-gray-500">
              已答 {practiceMetrics.answered_questions ?? 0} 题，答对 {practiceMetrics.correct_answers ?? 0} 题
            </p>
          </div>
        </div>

        <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="rounded-2xl bg-white p-6 shadow-sm">
            <h3 className="mb-4 text-lg font-semibold text-gray-900">周度学习趋势</h3>
            {weeklyData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" tick={{ fill: "#6b7280", fontSize: 12 }} />
                  <YAxis tick={{ fill: "#6b7280", fontSize: 12 }} />
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      name === "learningHours" ? `${value} 小时` : `${value} 分`,
                      name === "learningHours" ? "学习时长" : "平均分",
                    ]}
                    contentStyle={{
                      backgroundColor: "#fff",
                      border: "1px solid #e5e7eb",
                      borderRadius: "8px",
                      boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                    }}
                  />
                  <Bar dataKey="learningHours" fill="#10b981" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="averageScore" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-[300px] items-center justify-center text-gray-500">暂无趋势数据</div>
            )}
          </div>

          <div className="rounded-2xl bg-white p-6 shadow-sm">
            <h3 className="mb-4 text-lg font-semibold text-gray-900">成绩变化曲线</h3>
            {weeklyData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" tick={{ fill: "#6b7280", fontSize: 12 }} />
                  <YAxis tick={{ fill: "#6b7280", fontSize: 12 }} />
                  <Tooltip
                    formatter={(value: number) => [`${value} 分`, "平均分"]}
                    contentStyle={{
                      backgroundColor: "#fff",
                      border: "1px solid #e5e7eb",
                      borderRadius: "8px",
                      boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                    }}
                  />
                  <Line type="monotone" dataKey="averageScore" stroke="#10b981" strokeWidth={3} dot={{ r: 5, fill: "#10b981" }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-[300px] items-center justify-center text-gray-500">暂无趋势数据</div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.1fr_1.4fr]">
          <div className="rounded-2xl bg-white p-6 shadow-sm">
            <h3 className="mb-4 text-lg font-semibold text-gray-900">学习主题分布</h3>
            {categoryData.length > 0 ? (
              <>
                <div className="flex items-center justify-center">
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={categoryData}
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        dataKey="value"
                        label={({ name, value }) => `${name} ${value}%`}
                      >
                        {categoryData.map((entry) => (
                          <Cell key={entry.name} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value: number) => [`${value}%`, "占比"]} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
                  {categoryData.map((item) => (
                    <div key={item.name} className="flex items-center justify-between rounded-xl border border-gray-100 px-3 py-2">
                      <div className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
                        <span className="text-sm text-gray-700">{item.name}</span>
                      </div>
                      <span className="text-sm font-semibold text-gray-900">
                        {item.value}%{item.watch_minutes != null ? ` / ${item.watch_minutes} 分钟` : ""}
                      </span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="flex h-[360px] items-center justify-center text-gray-500">
                当前周期还没有足够的观看分类数据
              </div>
            )}
          </div>

          <div className="rounded-2xl bg-white p-6 shadow-sm">
            <h3 className="mb-3 text-lg font-semibold text-gray-900">AI 学习评估报告</h3>
            <div className="mb-4 rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm leading-7 text-emerald-900">
              {report.overview || "评估报告已生成，正在等待智能体分析结果。"}
            </div>

            <div className="space-y-4">
              <div className="rounded-xl border border-gray-100 bg-gray-50 px-4 py-4">
                <p className="mb-2 text-sm font-semibold text-gray-900">学习效果诊断</p>
                <p className="text-sm leading-7 text-gray-700">{report.diagnosis || "暂无诊断结论。"}</p>
              </div>
              <div className="rounded-xl border border-gray-100 bg-gray-50 px-4 py-4">
                <p className="mb-2 text-sm font-semibold text-gray-900">学习者画像</p>
                <p className="text-sm leading-7 text-gray-700">{report.learner_portrait || "暂无画像描述。"}</p>
              </div>
              <div className="rounded-xl border border-gray-100 bg-gray-50 px-4 py-4">
                <p className="mb-2 text-sm font-semibold text-gray-900">下一步优化建议</p>
                <p className="text-sm leading-7 text-gray-700">{report.optimization || "暂无优化建议。"}</p>
              </div>
            </div>

            <div className="mt-5">
              <p className="mb-3 text-sm font-semibold text-gray-900">建议动作</p>
              <div className="space-y-3">
                {(report.recommendations ?? []).length > 0 ? (
                  report.recommendations?.map((item, index) => (
                    <div key={`${item.title ?? "recommendation"}-${index}`} className="rounded-xl border border-gray-100 px-4 py-3">
                      <p className="mb-1 text-sm font-semibold text-gray-900">{item.title || `建议 ${index + 1}`}</p>
                      <p className="text-sm leading-7 text-gray-600">{item.description || "暂无建议内容。"}</p>
                    </div>
                  ))
                ) : (
                  <div className="rounded-xl border border-dashed border-gray-200 px-4 py-3 text-sm text-gray-500">
                    暂无结构化建议，可重新生成评估报告以刷新结果。
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
