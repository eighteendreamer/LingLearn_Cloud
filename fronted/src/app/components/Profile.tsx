import { Link } from "react-router";
import { Settings, Grid3X3, Bookmark, Heart, MessageCircle, BarChart3, Target, BookOpen, Brain, Calendar } from "lucide-react";

export function Profile() {
  const stats = [
    { label: "获赞", value: "12.5k" },
    { label: "关注", value: "234" },
    { label: "粉丝", value: "1.2k" },
  ];

  const learningTools = [
    { name: "AI助手", path: "/ai-chat", icon: MessageCircle, desc: "智能学习对话", color: "from-blue-500 to-cyan-500" },
    { name: "学生画像", path: "/student-profile", icon: Brain, desc: "能力分析报告", color: "from-purple-500 to-pink-500" },
    { name: "学习路径", path: "/learning-path", icon: Target, desc: "个性化规划", color: "from-emerald-500 to-teal-500" },
    { name: "在线练习", path: "/practice", icon: BookOpen, desc: "题目训练", color: "from-orange-500 to-red-500" },
    { name: "学习评估", path: "/assessment", icon: BarChart3, desc: "数据分析", color: "from-indigo-500 to-purple-500" },
    { name: "学习报告", path: "/report", icon: Calendar, desc: "进度总结", color: "from-green-500 to-emerald-500" },
  ];

  const myVideos = [
    { id: "1", likes: "2.3k", views: "15.2k" },
    { id: "2", likes: "1.8k", views: "12.5k" },
    { id: "3", likes: "3.1k", views: "21.8k" },
    { id: "4", likes: "2.7k", views: "18.3k" },
    { id: "5", likes: "1.5k", views: "10.7k" },
    { id: "6", likes: "2.9k", views: "19.6k" },
  ];

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="max-w-screen-xl mx-auto">
        {/* 顶部区域 */}
        <div className="relative">
          <div className="h-40 bg-gradient-to-br from-emerald-400 via-teal-400 to-blue-400 relative overflow-hidden">
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSIyIi8+PC9nPjwvZz48L3N2Zz4=')] opacity-30"></div>
          </div>
          <div className="absolute -bottom-12 left-6">
            <div className="w-24 h-24 rounded-full border-4 border-white bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white text-3xl font-bold shadow-xl">
              张
            </div>
          </div>
          <Link to="/settings" className="absolute top-3 right-3">
            <div className="w-9 h-9 rounded-lg bg-white/90 backdrop-blur-sm flex items-center justify-center shadow-md hover:scale-105 transition-all">
              <Settings className="w-5 h-5 text-gray-700" />
            </div>
          </Link>
        </div>

        {/* 用户信息 */}
        <div className="px-6 pt-16 pb-4">
          <h1 className="text-xl font-bold text-gray-900 mb-1">张同学</h1>
          <p className="text-gray-600 text-sm mb-4">全栈开发 | 终身学习</p>

          {/* 统计数据 */}
          <div className="flex gap-6 mb-4">
            {stats.map((stat, idx) => (
              <div key={idx}>
                <span className="text-gray-900 font-bold mr-1">{stat.value}</span>
                <span className="text-gray-600 text-sm">{stat.label}</span>
              </div>
            ))}
          </div>

          {/* 编辑按钮 */}
          <Link
            to="/edit-profile"
            className="w-full py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-lg text-sm font-bold mb-4 hover:shadow-lg hover:scale-105 transition-all text-center block"
          >
            编辑资料
          </Link>
        </div>

        {/* 学习工具 */}
        <div className="px-6 mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-gray-900 font-semibold flex items-center gap-2">
              <span>🎓</span>
              学习工具
            </h3>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {learningTools.map((tool) => {
              const Icon = tool.icon;
              return (
                <Link
                  key={tool.path}
                  to={tool.path}
                  className="bg-white rounded-xl p-4 hover:shadow-md hover:scale-105 transition-all border border-gray-200 group"
                >
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${tool.color} flex items-center justify-center shadow-sm mb-2`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-gray-900 text-xs font-medium text-center block">{tool.name}</span>
                  <span className="text-gray-500 text-xs text-center block mt-0.5">{tool.desc}</span>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Tab 切换 */}
        <div className="border-t border-gray-200">
          <div className="flex border-b border-gray-200">
            <button className="flex-1 py-3 text-emerald-600 border-b-2 border-emerald-600 flex items-center justify-center gap-2 text-sm font-semibold">
              <Grid3X3 className="w-4 h-4" />
              作品
            </button>
            <button className="flex-1 py-3 text-gray-500 flex items-center justify-center gap-2 text-sm">
              <Bookmark className="w-4 h-4" />
              收藏
            </button>
            <button className="flex-1 py-3 text-gray-500 flex items-center justify-center gap-2 text-sm">
              <Heart className="w-4 h-4" />
              喜欢
            </button>
          </div>
        </div>

        {/* 作品网格 */}
        <div className="grid grid-cols-3 gap-px bg-gray-200">
          {myVideos.map((video) => (
            <div key={video.id} className="aspect-[9/16] bg-gradient-to-br from-gray-100 to-gray-200 relative group cursor-pointer">
              <div className="absolute inset-0 bg-white/80 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-3">
                <div className="flex items-center gap-1 text-gray-900">
                  <Heart className="w-4 h-4 fill-red-500 text-red-500" />
                  <span className="text-sm font-semibold">{video.likes}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
