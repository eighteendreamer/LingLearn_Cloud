import { useEffect, useState } from "react";
import { Check, Lock, PlayCircle, BookOpen, Brain, Lightbulb, Link as LinkIcon } from "lucide-react";
import { Link } from "react-router";
import {
  fetchOrGenerateLearningPath,
  fetchOrGenerateSkillProfile,
  updateLearningPathNode,
} from "../lib/learning-api";
import type { SkillSnapshotResponse, UserLearningPathResponse } from "../lib/types";

interface PathNode {
  id: string;
  title: string;
  description: string;
  status: "completed" | "current" | "locked";
  progress?: number;
  lessons?: number;
  duration?: string;
  recommendReason?: string;
  matchedAbilities?: string[];
}

export function LearningPath() {
  const [profile, setProfile] = useState<SkillSnapshotResponse | null>(null);
  const [learningPath, setLearningPath] = useState<UserLearningPathResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadLearningPath = async () => {
      try {
        setLoading(true);
        const [profileData, pathData] = await Promise.all([
          fetchOrGenerateSkillProfile(),
          fetchOrGenerateLearningPath(),
        ]);
        setProfile(profileData);
        setLearningPath(pathData);
      } catch (error) {
        console.error("Failed to load learning path:", error);
      } finally {
        setLoading(false);
      }
    };

    void loadLearningPath();
  }, []);

  const studentProfile = Object.fromEntries(
    (profile?.scores.length ? profile.scores : []).map((score) => [score.name, Math.round(score.score)])
  ) as Record<string, number>;

  const profileEntries = Object.entries(studentProfile).length > 0
    ? Object.entries(studentProfile)
    : [
        ["编程基础", 78],
        ["算法思维", 72],
        ["数据库", 70],
        ["前端开发", 75],
        ["学习自驱", 82],
      ];

  const paths: PathNode[] = learningPath?.nodes.length
    ? learningPath.nodes.map((node, index) => {
        const isCurrent = learningPath.current_node_id === node.node_id || node.status === "in_progress" || node.status === "unlocked";
        return {
          id: String(node.node_id),
          title: node.title,
          description: node.description || "按计划完成该阶段学习任务。",
          status: node.status === "completed" ? "completed" : isCurrent ? "current" : "locked",
          progress: Math.round(node.progress_percent),
          lessons: Math.max(1, Math.ceil(node.estimated_minutes / 30)),
          duration: `${Math.max(1, Math.round(node.estimated_minutes / 60))}小时`,
          recommendReason: node.recommended_reason || learningPath.ai_summary || "根据能力画像生成的个性化学习节点。",
          matchedAbilities: profileEntries.slice(index, index + 2).map(([name, value]) => `${name}: ${value}分`),
        };
      })
    : [];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <Check className="w-5 h-5 text-white" />;
      case "current":
        return <PlayCircle className="w-5 h-5 text-white" />;
      case "locked":
        return <Lock className="w-5 h-5 text-white" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-emerald-500";
      case "current":
        return "bg-blue-500";
      case "locked":
        return "bg-gray-300";
      default:
        return "bg-gray-300";
    }
  };

  const totalProgress = Math.round(
    paths.length ? paths.reduce((sum, node) => sum + (node.progress || 0), 0) / paths.length : 0
  );

  const handleCompleteNode = async (node: PathNode) => {
    if (!learningPath) {
      return;
    }

    try {
      const updatedPath = await updateLearningPathNode(learningPath.id, Number(node.id), "completed", 100);
      setLearningPath(updatedPath);
    } catch (error) {
      console.error("Failed to update learning path node:", error);
    }
  };

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="p-8 max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-gray-800 mb-2 flex items-center gap-2">
            <Brain className="w-7 h-7 text-emerald-500" />
            AI定制学习路径
          </h1>
          <p className="text-gray-600">基于你的能力画像智能推荐学习计划</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          <div className="lg:col-span-2 bg-white rounded-xl p-5 shadow-md border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">你的能力画像</h3>
              <Link to="/student-profile" className="text-sm text-emerald-600 hover:text-emerald-700 flex items-center gap-1">
                查看详情
                <LinkIcon className="w-3 h-3" />
              </Link>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {profileEntries.map(([dimension, value]) => (
                <div key={dimension}>
                  <div className="flex justify-between text-sm mb-1.5">
                    <span className="text-gray-700">{dimension}</span>
                    <span className={`font-bold ${value >= 80 ? 'text-emerald-600' : value >= 70 ? 'text-blue-600' : 'text-orange-600'}`}>
                      {value}分
                    </span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full ${value >= 80 ? 'bg-gradient-to-r from-emerald-400 to-teal-500' : value >= 70 ? 'bg-gradient-to-r from-blue-400 to-indigo-500' : 'bg-gradient-to-r from-orange-400 to-amber-500'}`}
                      style={{ width: `${value}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl p-5 shadow-md">
            <div className="flex items-start gap-3">
              <Lightbulb className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-emerald-900 mb-2 text-sm">AI智能建议</h3>
                <div className="text-xs text-emerald-800 space-y-2">
                  <p>✅ <strong>优势：</strong>学习专注、逻辑思维强</p>
                  <p>💡 <strong>成长：</strong>{loading ? "正在生成后端建议" : (learningPath?.ai_summary || "按当前路径逐步推进")}</p>
                  <p>🎯 <strong>策略：</strong>优先完成当前节点，再解锁后续阶段</p>
                </div>
              </div>
            </div>
          </div>
        </div>

      <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">整体学习进度</h3>
            <p className="text-sm text-gray-600 mt-1">
              已完成 {paths.filter(p => p.status === "completed").length} / {paths.length} 个阶段
              <span className="ml-2 text-emerald-600">· 进行中 {paths.filter(p => p.status === "current").length} 个</span>
            </p>
          </div>
          <div className="text-4xl font-bold text-emerald-500">{totalProgress}%</div>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-emerald-400 to-teal-500 h-3 rounded-full transition-all shadow-sm"
            style={{ width: `${totalProgress}%` }}
          ></div>
        </div>
        <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
          <span>已投入 {paths.filter(p => p.status === "completed").length * 12}+ 小时</span>
          <span>预计总时长 {paths.reduce((sum, p) => sum + parseInt(p.duration || "0"), 0)} 小时</span>
        </div>
      </div>

      <div className="relative">
        {paths.map((node, index) => (
          <div key={node.id} className="relative pb-8 last:pb-0">
            {index !== paths.length - 1 && (
              <div className="absolute left-6 top-16 w-0.5 h-full bg-gray-200"></div>
            )}

            <div className="flex gap-6">
              <div className={`w-12 h-12 rounded-full ${getStatusColor(node.status)} flex items-center justify-center flex-shrink-0 relative z-10 shadow-md`}>
                {getStatusIcon(node.status)}
              </div>

              <div className={`flex-1 bg-white rounded-xl p-6 shadow-sm border-2 hover:shadow-md transition-shadow ${
                node.recommendReason?.includes("优秀") || node.recommendReason?.includes("强")
                  ? "border-emerald-200 bg-emerald-50/30"
                  : node.recommendReason?.includes("提升") || node.recommendReason?.includes("AI建议")
                  ? "border-orange-200 bg-orange-50/30"
                  : "border-gray-200"
              }`}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <h3 className="text-lg font-semibold text-gray-900">{node.title}</h3>
                      <span
                        className={`text-xs px-3 py-1 rounded-full font-medium ${
                          node.status === "completed"
                            ? "bg-emerald-100 text-emerald-700"
                            : node.status === "current"
                            ? "bg-blue-100 text-blue-700"
                            : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {node.status === "completed"
                          ? "已完成"
                          : node.status === "current"
                          ? "进行中"
                          : "未解锁"}
                      </span>
                      {node.recommendReason?.includes("优秀") || node.recommendReason?.includes("强") ? (
                        <span className="text-xs px-2 py-1 bg-emerald-100 text-emerald-700 rounded-full font-medium">
                          💪 发挥优势
                        </span>
                      ) : node.recommendReason?.includes("提升") || node.recommendReason?.includes("AI建议") ? (
                        <span className="text-xs px-2 py-1 bg-orange-100 text-orange-700 rounded-full font-medium">
                          📈 成长课程
                        </span>
                      ) : null}
                    </div>
                    <p className="text-gray-600 mb-3">{node.description}</p>

                    {node.recommendReason && (
                      <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <div className="flex items-start gap-2">
                          <Brain className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1">
                            <p className="text-sm text-blue-900 font-medium mb-1">AI推荐理由</p>
                            <p className="text-xs text-blue-800">{node.recommendReason}</p>
                            {node.matchedAbilities && node.matchedAbilities.length > 0 && (
                              <div className="flex flex-wrap gap-1.5 mt-2">
                                {node.matchedAbilities.map((ability, idx) => (
                                  <span
                                    key={idx}
                                    className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full"
                                  >
                                    {ability}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                      <div className="flex items-center gap-1">
                        <BookOpen className="w-4 h-4" />
                        <span>{node.lessons} 节课</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span>⏱️</span>
                        <span>{node.duration}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {node.status !== "locked" && node.progress !== undefined && (
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-700">学习进度</span>
                      <span className="text-emerald-600 font-semibold">{node.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-emerald-400 to-teal-500 h-2 rounded-full transition-all"
                        style={{ width: `${node.progress}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                <div className="flex gap-3">
                  {node.status === "current" && (
                    <button
                      onClick={() => void handleCompleteNode(node)}
                      className="px-5 py-2.5 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors font-medium flex items-center gap-2"
                    >
                      <PlayCircle className="w-4 h-4" />
                      标记完成
                    </button>
                  )}

                  {node.status === "completed" && (
                    <button className="px-5 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium">
                      复习课程
                    </button>
                  )}

                  {node.status === "locked" && (
                    <div className="px-5 py-2.5 bg-gray-50 text-gray-400 rounded-lg font-medium flex items-center gap-2">
                      <Lock className="w-4 h-4" />
                      完成前置课程后解锁
                    </div>
                  )}

                  {node.status !== "locked" && (
                    <button className="px-5 py-2.5 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium">
                      查看详情
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      </div>
    </div>
  );
}
