import { Check, Lock, PlayCircle, BookOpen, Brain, Lightbulb, Link as LinkIcon } from "lucide-react";
import { Link } from "react-router";

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
  // 学生画像数据（来自StudentProfile）
  const studentProfile = {
    逻辑思维: 85,
    创新能力: 72,
    学习专注: 90,
    团队协作: 68,
    问题解决: 78,
    知识掌握: 82,
  };

  // 根据学生画像动态生成学习路径
  const generateLearningPath = (): PathNode[] => {
    const allCourses = [
      {
        id: "1",
        title: "编程基础",
        description: "学习编程基本概念和Python语法",
        status: "completed" as const,
        lessons: 12,
        duration: "8小时",
        progress: 100,
        requiredAbilities: ["知识掌握"],
        recommendReason: "已完成基础课程，知识掌握能力强",
        matchedAbilities: ["知识掌握: 82分"],
      },
      {
        id: "2",
        title: "数据结构",
        description: "掌握数组、链表、栈、队列、树、图等核心数据结构",
        status: "completed" as const,
        lessons: 16,
        duration: "12小时",
        progress: 100,
        requiredAbilities: ["逻辑思维"],
        recommendReason: "逻辑思维能力优秀，适合深入学习数据结构",
        matchedAbilities: ["逻辑思维: 85分"],
      },
      {
        id: "3",
        title: "算法进阶",
        description: "学习排序、搜索、动态规划、贪心等经典算法",
        status: "current" as const,
        progress: 65,
        lessons: 20,
        duration: "15小时",
        requiredAbilities: ["逻辑思维", "问题解决"],
        recommendReason: "你的逻辑思维能力(85分)和问题解决能力(78分)都很强，继续发挥优势",
        matchedAbilities: ["逻辑思维: 85分", "问题解决: 78分"],
      },
      {
        id: "4",
        title: "创新设计思维",
        description: "培养创新思维，学习设计思维方法论和创意项目开发",
        status: "locked" as const,
        lessons: 18,
        duration: "14小时",
        requiredAbilities: ["创新能力"],
        recommendReason: "AI建议：提升创新能力(当前72分)，通过开放性问题训练创造力",
        matchedAbilities: ["创新能力: 72分 ⬆️"],
      },
      {
        id: "5",
        title: "团队协作项目",
        description: "参与真实团队项目，学习Git协作、代码审查和敏捷开发",
        status: "locked" as const,
        lessons: 16,
        duration: "12小时",
        requiredAbilities: ["团队协作"],
        recommendReason: "AI建议：加强团队协作能力(当前68分)，通过实践提升软技能",
        matchedAbilities: ["团队协作: 68分 ⬆️"],
      },
      {
        id: "6",
        title: "Web前端开发",
        description: "掌握HTML、CSS、JavaScript和React框架",
        status: "locked" as const,
        lessons: 24,
        duration: "18小时",
        requiredAbilities: ["学习专注", "知识掌握"],
        recommendReason: "学习专注度高(90分)，适合学习内容密集的前端技术栈",
        matchedAbilities: ["学习专注: 90分", "知识掌握: 82分"],
      },
      {
        id: "7",
        title: "全栈项目实战",
        description: "综合运用所学知识，独立完成全栈应用开发",
        status: "locked" as const,
        lessons: 20,
        duration: "25小时",
        requiredAbilities: ["问题解决", "创新能力", "团队协作"],
        recommendReason: "综合提升各项能力，完成完整项目作品集",
        matchedAbilities: ["综合能力提升"],
      },
    ];

    return allCourses;
  };

  const paths = generateLearningPath();

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
    paths.reduce((sum, node) => sum + (node.progress || 0), 0) / paths.length
  );

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
              {Object.entries(studentProfile).map(([dimension, value]) => (
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
                  <p>💡 <strong>成长：</strong>提升团队协作与创新</p>
                  <p>🎯 <strong>策略：</strong>先巩固算法，再补短板</p>
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
                    <button className="px-5 py-2.5 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors font-medium flex items-center gap-2">
                      <PlayCircle className="w-4 h-4" />
                      继续学习
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
