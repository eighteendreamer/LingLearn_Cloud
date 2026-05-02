import { useEffect, useState } from "react";
import {
  BookOpen,
  CheckCircle2,
  ChevronRight,
  Clock3,
  ExternalLink,
  History,
  PlayCircle,
  Route,
  Sparkles,
  Target,
} from "lucide-react";
import { Link, useNavigate } from "react-router";
import { MarkdownMessage } from "./MarkdownMessage";
import {
  activateLearningPath,
  fetchActiveLearningPath,
  fetchLearningPathById,
  fetchLearningPathHistory,
  fetchOrGenerateSkillProfile,
  generateLearningPathNodePractice,
  generateLearningPathPlan,
  updateLearningPathNode,
} from "../lib/learning-api";
import type {
  LearningPathGeneratePayload,
  LearningPathNodeResponse,
  LearningPathPlanResponse,
  LearningPathPlanRouteResponse,
  SkillSnapshotResponse,
  UserLearningPathResponse,
} from "../lib/types";

const defaultForm: LearningPathGeneratePayload = {
  target_role: "后端开发",
  current_level: "beginner",
  weekly_hours: 6,
  route_count: 3,
  preferred_resource_mode: "mixed",
};

const levelLabel: Record<string, string> = {
  beginner: "入门",
  intermediate: "进阶",
  advanced: "高级",
};

const statusLabel: Record<string, string> = {
  active: "当前路线",
  archived: "历史路线",
  completed: "已完成",
};

export function LearningPath() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<SkillSnapshotResponse | null>(null);
  const [activePath, setActivePath] = useState<UserLearningPathResponse | null>(null);
  const [displayPath, setDisplayPath] = useState<UserLearningPathResponse | null>(null);
  const [historyPaths, setHistoryPaths] = useState<UserLearningPathResponse[]>([]);
  const [planResult, setPlanResult] = useState<LearningPathPlanResponse | null>(null);
  const [form, setForm] = useState<LearningPathGeneratePayload>(defaultForm);
  const [loading, setLoading] = useState(true);
  const [planning, setPlanning] = useState(false);
  const [activatingRouteCode, setActivatingRouteCode] = useState<string | null>(null);
  const [loadingHistoryId, setLoadingHistoryId] = useState<number | null>(null);
  const [practiceNodeId, setPracticeNodeId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const [profileData, currentPath, history] = await Promise.all([
          fetchOrGenerateSkillProfile(),
          fetchActiveLearningPath(),
          fetchLearningPathHistory(),
        ]);
        setProfile(profileData);
        setActivePath(currentPath);
        setDisplayPath(currentPath ?? history[0] ?? null);
        setHistoryPaths(history);
      } catch (loadError) {
        console.error("Failed to load learning path page:", loadError);
        setError("加载学习路径页面失败，请稍后重试。");
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, []);

  const displayedCompletedCount = displayPath?.nodes.filter((node) => node.status === "completed").length ?? 0;
  const displayedNodeCount = displayPath?.nodes.length ?? 0;

  const refreshHistory = async (preferredPathId?: number) => {
    const history = await fetchLearningPathHistory();
    setHistoryPaths(history);
    if (preferredPathId) {
      const preferred = history.find((item) => item.id === preferredPathId);
      if (preferred) {
        setDisplayPath(preferred);
        if (preferred.status === "active") {
          setActivePath(preferred);
        }
        return;
      }
    }
    if (!displayPath) {
      setDisplayPath(history[0] ?? null);
    }
  };

  const handleGeneratePlan = async () => {
    try {
      setPlanning(true);
      setError(null);
      const result = await generateLearningPathPlan(form);
      setPlanResult(result);
    } catch (planError) {
      console.error("Failed to generate learning path plan:", planError);
      setError("生成学习规划失败，请稍后再试。");
    } finally {
      setPlanning(false);
    }
  };

  const handleActivateRoute = async (route: LearningPathPlanRouteResponse) => {
    try {
      setActivatingRouteCode(route.route_code);
      setError(null);
      const path = await activateLearningPath({ selected_route: route });
      setActivePath(path);
      setDisplayPath(path);
      setPlanResult(null);
      await refreshHistory(path.id);
    } catch (activateError) {
      console.error("Failed to activate route:", activateError);
      setError("激活学习路线失败，请稍后重试。");
    } finally {
      setActivatingRouteCode(null);
    }
  };

  const handleOpenHistory = async (userPathId: number) => {
    try {
      setLoadingHistoryId(userPathId);
      setError(null);
      const path = await fetchLearningPathById(userPathId);
      setDisplayPath(path);
      setPlanResult(null); // Switch back to path view
    } catch (historyError) {
      console.error("Failed to load history learning path:", historyError);
      setError("读取历史路线失败，请稍后重试。");
    } finally {
      setLoadingHistoryId(null);
    }
  };

  const handleCompleteNode = async (node: LearningPathNodeResponse) => {
    if (!displayPath) {
      return;
    }
    try {
      setError(null);
      const path = await updateLearningPathNode(displayPath.id, node.node_id, "completed", 100);
      if (activePath?.id === displayPath.id) {
        setActivePath(path);
      }
      setDisplayPath(path);
      await refreshHistory(path.id);
    } catch (updateError) {
      console.error("Failed to complete learning path node:", updateError);
      setError("更新阶段状态失败，请稍后再试。");
    }
  };

  const handleGeneratePractice = async (node: LearningPathNodeResponse) => {
    if (!displayPath) {
      return;
    }
    try {
      setPracticeNodeId(node.node_id);
      setError(null);
      const result = await generateLearningPathNodePractice(displayPath.id, node.node_id);
      navigate(`/practice?bank_id=${result.bank_id}&session_id=${result.session_id}`);
    } catch (practiceError) {
      console.error("Failed to generate stage practice:", practiceError);
      setError("生成阶段题库失败，请稍后重试。");
    } finally {
      setPracticeNodeId(null);
    }
  };

  return (
    <div className="h-screen overflow-y-auto bg-slate-50 pb-24 font-sans text-slate-900 selection:bg-slate-200">
      <div className="mx-auto max-w-[1200px] px-6 py-12">
        
        {/* Header */}
        <header className="mb-12 flex flex-col items-start justify-between gap-6 md:flex-row md:items-end">
          <div>
            <div className="mb-3 inline-flex items-center gap-1.5 rounded-md bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
              <Sparkles className="h-3.5 w-3.5" />
              AI 定制学习路径
            </div>
            <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
              学习路径
            </h1>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-slate-500">
              基于您的能力画像为您量身定制学习路线。系统将为您拆解每个阶段的学习目标，并推荐相关的学习资源和考核内容。
            </p>
          </div>
          <Link
            to="/student-profile"
            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 hover:text-slate-900"
          >
            查看能力画像
            <ExternalLink className="h-4 w-4" />
          </Link>
        </header>

        {error ? (
          <div className="mb-8 rounded-lg border border-red-100 bg-red-50 p-4 text-sm text-red-600">
            {error}
          </div>
        ) : null}

        <div className="grid grid-cols-1 items-start gap-10 lg:grid-cols-12">
          
          {/* Main Content (Left) */}
          <div className="lg:col-span-8 space-y-8">
            {planResult ? (
              <section>
                <div className="mb-6 flex items-center justify-between">
                  <h2 className="text-xl font-medium tracking-tight">为您生成的候选路线</h2>
                  <button 
                    onClick={() => setPlanResult(null)}
                    className="text-sm font-medium text-slate-500 transition-colors hover:text-slate-900"
                  >
                    取消并返回
                  </button>
                </div>
                
                <div className="mb-8 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                  <div className="prose prose-sm prose-slate max-w-none">
                    <MarkdownMessage content={planResult.planning_summary} />
                  </div>
                </div>

                <div className="space-y-6">
                  {planResult.route_options.map((route) => (
                    <article
                      key={route.route_code}
                      className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
                    >
                      <div className="mb-4 flex flex-wrap items-center gap-2">
                        <span className="rounded-md bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                          {levelLabel[route.difficulty] ?? route.difficulty}
                        </span>
                        <span className="rounded-md bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                          预计 {route.estimated_weeks} 周
                        </span>
                      </div>

                      <h3 className="text-lg font-medium">{route.title}</h3>
                      <p className="mt-2 text-sm leading-relaxed text-slate-600">{route.summary}</p>

                      <div className="mt-6">
                        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">适合理由</h4>
                        <div className="prose prose-sm prose-slate mt-2 max-w-none text-slate-600">
                          <MarkdownMessage content={route.fit_reason} />
                        </div>
                      </div>

                      <div className="mt-6 border-t border-slate-100 pt-6">
                        <h4 className="mb-4 text-sm font-medium">包含阶段 ({route.stages.length})</h4>
                        <div className="space-y-3">
                          {route.stages.map((stage, index) => (
                            <div key={stage.stage_code} className="flex gap-4">
                              <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-medium text-slate-600">
                                {index + 1}
                              </div>
                              <div>
                                <p className="text-sm font-medium">{stage.title}</p>
                                <p className="mt-1 text-sm text-slate-500">{stage.goal}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="mt-8">
                        <button
                          onClick={() => void handleActivateRoute(route)}
                          disabled={activatingRouteCode === route.route_code}
                          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-emerald-700 disabled:bg-slate-300"
                        >
                          <Route className="h-4 w-4" />
                          {activatingRouteCode === route.route_code ? "正在激活..." : "激活此路线"}
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            ) : (
              <section>
                <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
                  <div>
                    <h2 className="text-xl font-medium tracking-tight">
                      {displayPath?.status === "active" ? "当前主路线" : "路线详情"}
                    </h2>
                    {displayPath ? (
                      <p className="mt-1.5 text-sm text-slate-500">
                        {displayPath.name} · 已完成 {displayedCompletedCount}/{displayedNodeCount} 个阶段
                      </p>
                    ) : (
                      <p className="mt-1.5 text-sm text-slate-500">还没有可展示的学习路线。</p>
                    )}
                  </div>

                  {displayPath ? (
                    <div className="text-right">
                      <div className="text-3xl font-semibold tracking-tight text-slate-900">
                        {Math.round(displayPath.progress_percent)}%
                      </div>
                      <div className="mt-1 text-xs font-medium text-slate-500">
                        {statusLabel[displayPath.status] ?? "状态"}
                      </div>
                    </div>
                  ) : null}
                </div>

                {loading ? (
                  <div className="flex h-48 items-center justify-center rounded-xl border border-dashed border-slate-200 text-sm text-slate-500">
                    正在加载学习路径...
                  </div>
                ) : displayPath ? (
                  <div className="space-y-6">
                    {displayPath.nodes.map((node, index) => {
                      const locked = node.status === "locked";
                      const completed = node.status === "completed";
                      const sessionId = node.assessment?.generated_session_id;
                      const bankId = node.assessment?.generated_bank_id;

                      return (
                        <article
                          key={node.node_id}
                          className={`rounded-xl border bg-white p-6 shadow-sm transition-all ${
                            completed ? "border-slate-200" : locked ? "border-slate-100 opacity-75" : "border-slate-300 ring-1 ring-slate-100"
                          }`}
                        >
                          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                            <div className="flex-1">
                              <div className="mb-3 flex flex-wrap items-center gap-2">
                                <span className="rounded-md bg-slate-100 px-2 py-1 text-[11px] font-medium text-slate-600">
                                  阶段 {index + 1}
                                </span>
                                <span
                                  className={`rounded-md px-2 py-1 text-[11px] font-medium ${
                                    completed
                                      ? "bg-emerald-50 text-emerald-700"
                                      : locked
                                      ? "bg-slate-100 text-slate-500"
                                      : "bg-blue-50 text-blue-700"
                                  }`}
                                >
                                  {completed ? "已完成" : locked ? "待解锁" : "进行中"}
                                </span>
                                <span className="rounded-md bg-slate-100 px-2 py-1 text-[11px] font-medium text-slate-600">
                                  {Math.max(1, Math.round(node.estimated_minutes / 60))} 小时
                                </span>
                              </div>
                              <h3 className="text-lg font-medium text-slate-900">{node.title}</h3>
                              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                                {node.stage_goal || node.description || "按阶段推进学习任务，并完成对应练习与考核。"}
                              </p>
                              {node.recommended_reason && (
                                <div className="mt-3 inline-flex rounded-md bg-slate-50 px-3 py-2 text-xs leading-relaxed text-slate-600">
                                  <span className="mr-1 font-medium text-slate-700">推荐理由:</span>
                                  {node.recommended_reason}
                                </div>
                              )}
                            </div>

                            <div className="flex w-full shrink-0 flex-col items-end sm:w-32">
                              <span className="mb-2 text-xs font-medium text-slate-500">进度 {Math.round(node.progress_percent)}%</span>
                              <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                                <div
                                  className="h-full rounded-full bg-emerald-500 transition-all duration-500"
                                  style={{ width: `${Math.min(100, Math.max(0, Math.round(node.progress_percent)))}%` }}
                                />
                              </div>
                            </div>
                          </div>

                          <div className="grid gap-6 border-t border-slate-100 pt-6 lg:grid-cols-2">
                            {/* Resources */}
                            <div>
                              <h4 className="mb-4 flex items-center gap-2 text-sm font-medium text-slate-900">
                                <BookOpen className="h-4 w-4 text-slate-400" />
                                推荐资源
                              </h4>
                              {node.resources.length ? (
                                <div className="space-y-3">
                                  {node.resources.map((resource, resourceIndex) => (
                                    <div key={`${node.node_id}-${resourceIndex}`} className="rounded-lg border border-slate-100 bg-slate-50/50 p-3.5 transition-colors hover:bg-slate-50">
                                      <div className="mb-2 flex flex-wrap items-center gap-1.5">
                                        <span className="rounded border border-slate-100 bg-white px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-slate-500 shadow-sm">
                                          {resource.source === "system" ? "系统资源" : "线上资源"}
                                        </span>
                                        {resource.category_name && (
                                          <span className="rounded border border-slate-100 bg-white px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-slate-500 shadow-sm">
                                            {resource.category_name}
                                          </span>
                                        )}
                                      </div>
                                      <p className="text-sm font-medium text-slate-900">{resource.title}</p>
                                      {resource.description && (
                                        <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-slate-500" title={resource.description}>
                                          {resource.description}
                                        </p>
                                      )}
                                      {resource.external_url && (
                                        <a
                                          href={resource.external_url}
                                          target="_blank"
                                          rel="noreferrer"
                                          className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-slate-600 transition-colors hover:text-slate-900"
                                        >
                                          打开链接
                                          <ExternalLink className="h-3 w-3" />
                                        </a>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <div className="rounded-lg border border-dashed border-slate-200 bg-slate-50/50 py-6 text-center text-xs text-slate-500">
                                  暂无可展示的阶段资源。
                                </div>
                              )}
                            </div>

                            {/* Assessment */}
                            <div>
                              <h4 className="mb-4 flex items-center gap-2 text-sm font-medium text-slate-900">
                                <Clock3 className="h-4 w-4 text-slate-400" />
                                阶段考核
                              </h4>
                              <div className="flex h-full flex-col justify-between rounded-lg border border-slate-100 bg-slate-50/50 p-4">
                                <div className="mb-6 space-y-2 text-sm text-slate-600">
                                  <div className="flex justify-between border-b border-slate-200/60 pb-2">
                                    <span className="text-slate-500">考核模式</span>
                                    <span className="font-medium text-slate-900">{node.assessment?.mode === "generated_quiz" ? "AI生成测验" : (node.assessment?.mode ?? "未知")}</span>
                                  </div>
                                  <div className="flex justify-between border-b border-slate-200/60 pb-2">
                                    <span className="text-slate-500">题目数量</span>
                                    <span className="font-medium text-slate-900">{node.assessment?.question_count ?? 6} 题</span>
                                  </div>
                                  <div className="flex justify-between pb-1">
                                    <span className="text-slate-500">通过分数</span>
                                    <span className="font-medium text-slate-900">{node.assessment?.pass_score ?? 70} 分</span>
                                  </div>
                                </div>

                                <div className="space-y-2.5">
                                  {sessionId && bankId ? (
                                    <button
                                      onClick={() => navigate(`/practice?bank_id=${bankId}&session_id=${sessionId}`)}
                                      className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-emerald-700"
                                    >
                                      继续本阶段练习
                                    </button>
                                  ) : (
                                    <button
                                      onClick={() => void handleGeneratePractice(node)}
                                      disabled={locked || practiceNodeId === node.node_id}
                                      className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-emerald-700 disabled:bg-slate-300"
                                    >
                                      <PlayCircle className="h-4 w-4" />
                                      {practiceNodeId === node.node_id ? "正在生成题库..." : "生成题库并开始考核"}
                                    </button>
                                  )}

                                  {!locked && !completed ? (
                                    <button
                                      onClick={() => void handleCompleteNode(node)}
                                      className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 hover:text-slate-900"
                                    >
                                      <CheckCircle2 className="h-4 w-4" />
                                      标记阶段完成
                                    </button>
                                  ) : null}
                                </div>
                              </div>
                            </div>
                          </div>
                        </article>
                      );
                    })}
                  </div>
                ) : (
                  <div className="flex h-64 flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white text-center">
                    <p className="text-sm font-medium text-slate-900">暂无学习路线</p>
                    <p className="mt-1 text-sm text-slate-500">请在右侧表单生成新的学习规划</p>
                  </div>
                )}
              </section>
            )}
          </div>

          {/* Sidebar (Right) */}
          <div className="space-y-8 lg:col-span-4">
            
            {/* Generate Form */}
            <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-5">
                <h3 className="flex items-center gap-2 font-medium text-slate-900">
                  <Target className="h-4 w-4 text-slate-400" />
                  生成新规划
                </h3>
                <p className="mt-1.5 text-xs leading-relaxed text-slate-500">设定您的学习目标与时间，AI 将为您生成多条候选的学习路线。</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="mb-1.5 block text-xs font-medium text-slate-700">目标方向</label>
                  <input
                    value={form.target_role ?? ""}
                    onChange={(e) => setForm((prev) => ({ ...prev, target_role: e.target.value }))}
                    className="w-full rounded-lg border border-slate-200 bg-slate-50/50 px-3 py-2 text-sm text-slate-900 transition-colors focus:border-slate-400 focus:bg-white focus:outline-none"
                    placeholder="例如：后端开发 / Python 入门"
                  />
                </div>

                <div>
                  <label className="mb-1.5 block text-xs font-medium text-slate-700">当前水平</label>
                  <select
                    value={form.current_level ?? "beginner"}
                    onChange={(e) => setForm((prev) => ({ ...prev, current_level: e.target.value }))}
                    className="w-full rounded-lg border border-slate-200 bg-slate-50/50 px-3 py-2 text-sm text-slate-900 transition-colors focus:border-slate-400 focus:bg-white focus:outline-none"
                  >
                    <option value="beginner">入门</option>
                    <option value="intermediate">进阶</option>
                    <option value="advanced">高级</option>
                  </select>
                </div>

                <div>
                  <label className="mb-1.5 block text-xs font-medium text-slate-700">每周投入时长 (小时)</label>
                  <input
                    type="number"
                    min={1}
                    max={40}
                    value={form.weekly_hours ?? 6}
                    onChange={(e) => setForm((prev) => ({ ...prev, weekly_hours: Number(e.target.value) || 6 }))}
                    className="w-full rounded-lg border border-slate-200 bg-slate-50/50 px-3 py-2 text-sm text-slate-900 transition-colors focus:border-slate-400 focus:bg-white focus:outline-none"
                  />
                </div>

                <div>
                  <label className="mb-1.5 block text-xs font-medium text-slate-700">资源偏好</label>
                  <select
                    value={form.preferred_resource_mode ?? "mixed"}
                    onChange={(e) => setForm((prev) => ({ ...prev, preferred_resource_mode: e.target.value }))}
                    className="w-full rounded-lg border border-slate-200 bg-slate-50/50 px-3 py-2 text-sm text-slate-900 transition-colors focus:border-slate-400 focus:bg-white focus:outline-none"
                  >
                    <option value="mixed">混合资源</option>
                    <option value="system">优先系统资源</option>
                    <option value="online">优先线上资源</option>
                  </select>
                </div>

                <div>
                  <label className="mb-1.5 block text-xs font-medium text-slate-700">候选路线数量</label>
                  <select
                    value={form.route_count ?? 3}
                    onChange={(e) => setForm((prev) => ({ ...prev, route_count: Number(e.target.value) }))}
                    className="w-full rounded-lg border border-slate-200 bg-slate-50/50 px-3 py-2 text-sm text-slate-900 transition-colors focus:border-slate-400 focus:bg-white focus:outline-none"
                  >
                    <option value={2}>2 条</option>
                    <option value={3}>3 条</option>
                    <option value={4}>4 条</option>
                  </select>
                </div>

                <div className="pt-2">
                  <button
                    onClick={() => void handleGeneratePlan()}
                    disabled={planning}
                    className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 py-2.5 text-sm font-medium text-white transition-colors hover:bg-emerald-700 disabled:bg-slate-300"
                  >
                    <Sparkles className="h-4 w-4" />
                    {planning ? "正在生成..." : "生成学习规划"}
                  </button>
                </div>
              </div>
            </section>

            {/* History Paths */}
            <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="mb-4 flex items-center gap-2 font-medium text-slate-900">
                <History className="h-4 w-4 text-slate-400" />
                历史路线
              </h3>
              
              <div className="space-y-2">
                {historyPaths.length ? (
                  historyPaths.map((item) => {
                    const isSelected = displayPath?.id === item.id;
                    const completedCount = item.nodes.filter((node) => node.status === "completed").length;
                    
                    return (
                      <button
                        key={item.id}
                        onClick={() => void handleOpenHistory(item.id)}
                        className={`w-full rounded-lg border p-3 text-left transition-colors ${
                          isSelected
                            ? "border-emerald-200 bg-emerald-50/50 shadow-sm"
                            : "border-transparent hover:bg-slate-50"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0 flex-1">
                            <p className={`truncate text-sm font-medium ${isSelected ? 'text-emerald-900' : 'text-slate-900'}`}>{item.name}</p>
                            <div className="mt-1.5 flex flex-wrap items-center gap-2">
                              <span className="text-[11px] font-medium text-slate-500">
                                {statusLabel[item.status] ?? item.status}
                              </span>
                              <span className="text-[11px] font-medium text-slate-500">
                                进度 {Math.round(item.progress_percent)}%
                              </span>
                            </div>
                            <p className="mt-1 text-[11px] text-slate-400">
                              完成 {completedCount}/{item.nodes.length} 阶段
                            </p>
                          </div>
                          <ChevronRight className={`h-4 w-4 shrink-0 ${isSelected ? 'text-emerald-600' : 'text-slate-300'}`} />
                        </div>
                      </button>
                    );
                  })
                ) : (
                  <div className="py-6 text-center text-xs text-slate-500">
                    暂无历史路线
                  </div>
                )}
              </div>
            </section>
            
          </div>
        </div>
      </div>
    </div>
  );
}
