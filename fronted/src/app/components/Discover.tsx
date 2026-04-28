import { Search, TrendingUp, Hash, Play } from "lucide-react";
import { useState } from "react";

export function Discover() {
  const [searchQuery, setSearchQuery] = useState("");

  const categories = [
    { id: "1", name: "Python", icon: "🐍", count: "2.3k", color: "from-blue-500 to-cyan-500" },
    { id: "2", name: "前端开发", icon: "💻", count: "3.8k", color: "from-purple-500 to-pink-500" },
    { id: "3", name: "算法", icon: "🧮", count: "1.9k", color: "from-emerald-500 to-teal-500" },
    { id: "4", name: "数据库", icon: "🗄️", count: "1.2k", color: "from-orange-500 to-red-500" },
    { id: "5", name: "AI/ML", icon: "🤖", count: "2.7k", color: "from-indigo-500 to-purple-500" },
    { id: "6", name: "后端", icon: "⚙️", count: "2.1k", color: "from-green-500 to-emerald-500" },
  ];

  const trending = [
    {
      id: "1",
      rank: 1,
      title: "ChatGPT提示词工程完整教程",
      views: "128万",
      trend: "热",
    },
    {
      id: "2",
      rank: 2,
      title: "Next.js 14 新特性详解",
      views: "95万",
      trend: "新",
    },
    {
      id: "3",
      rank: 3,
      title: "TypeScript高级类型系统",
      views: "87万",
      trend: "热",
    },
    {
      id: "4",
      rank: 4,
      title: "Docker容器化最佳实践",
      views: "76万",
      trend: "",
    },
    {
      id: "5",
      rank: 5,
      title: "LeetCode算法题解析",
      views: "68万",
      trend: "",
    },
  ];

  const popularHashtags = [
    { tag: "编程入门", count: "582万" },
    { tag: "前端面试", count: "421万" },
    { tag: "算法刷题", count: "368万" },
    { tag: "项目实战", count: "295万" },
    { tag: "代码优化", count: "247万" },
    { tag: "职场技能", count: "189万" },
  ];

  const recommendedVideos = [
    {
      id: "1",
      title: "React性能优化实战指南",
      author: "前端架构师",
      thumbnail: "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=300",
      views: "23.5万",
      duration: "15:24",
    },
    {
      id: "2",
      title: "Python爬虫从零到精通",
      author: "数据分析师",
      thumbnail: "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=300",
      views: "18.2万",
      duration: "22:16",
    },
    {
      id: "3",
      title: "深入理解Vue3响应式原理",
      author: "Vue专家",
      thumbnail: "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=300",
      views: "31.7万",
      duration: "18:45",
    },
    {
      id: "4",
      title: "MySQL数据库性能调优",
      author: "DBA工程师",
      thumbnail: "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=300",
      views: "15.8万",
      duration: "20:33",
    },
  ];

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="max-w-screen-xl mx-auto px-4 py-6">
        {/* 搜索框 */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索课程、话题、老师..."
              className="w-full pl-12 pr-4 py-3.5 bg-white border border-gray-200 rounded-2xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all shadow-sm"
            />
          </div>
        </div>

        {/* 热门分类 */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span className="text-xl">🔥</span>
            热门分类
          </h2>
          <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
            {categories.map((category) => (
              <div
                key={category.id}
                className={`bg-gradient-to-br ${category.color} rounded-2xl p-4 cursor-pointer hover:scale-105 hover:shadow-lg transition-all`}
              >
                <div className="text-3xl mb-2">{category.icon}</div>
                <div className="text-white font-semibold text-sm mb-1">{category.name}</div>
                <div className="text-white/80 text-xs">{category.count} 视频</div>
              </div>
            ))}
          </div>
        </div>

        {/* 热榜和热门话题 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* 实时热榜 */}
          <div className="lg:col-span-2">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-emerald-500" />
              实时热榜
            </h2>
            <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-md">
              <div className="space-y-4">
                {trending.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center gap-4 hover:bg-gray-50 p-3 rounded-xl transition-colors cursor-pointer group"
                  >
                    <div
                      className={`w-10 h-10 flex items-center justify-center rounded-xl font-bold shadow ${
                        item.rank <= 3
                          ? "bg-gradient-to-br from-yellow-400 to-orange-500 text-white"
                          : "bg-gray-200 text-gray-600"
                      }`}
                    >
                      {item.rank}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="text-gray-900 font-medium group-hover:text-emerald-600 transition-colors line-clamp-1">
                          {item.title}
                        </h3>
                        {item.trend && (
                          <span
                            className={`px-2 py-1 rounded text-xs font-bold ${
                              item.trend === "热"
                                ? "bg-gradient-to-r from-red-500 to-pink-500 text-white"
                                : "bg-gradient-to-r from-emerald-500 to-teal-500 text-white"
                            }`}
                          >
                            {item.trend}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-600 text-sm mt-1">{item.views} 观看</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 热门话题 */}
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Hash className="w-6 h-6 text-emerald-500" />
              热门话题
            </h2>
            <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-md">
              <div className="space-y-3">
                {popularHashtags.map((item, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between hover:bg-gray-50 p-3 rounded-xl transition-colors cursor-pointer group"
                  >
                    <div className="flex items-center gap-2">
                      <Hash className="w-4 h-4 text-emerald-500" />
                      <span className="text-gray-900 font-medium group-hover:text-emerald-600 transition-colors">
                        {item.tag}
                      </span>
                    </div>
                    <span className="text-gray-600 text-sm">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 推荐视频 */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span className="text-xl">✨</span>
            推荐视频
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {recommendedVideos.map((video) => (
              <div
                key={video.id}
                className="bg-white rounded-2xl overflow-hidden border border-gray-200 hover:border-emerald-500 hover:shadow-lg transition-all cursor-pointer group"
              >
                <div className="relative aspect-video bg-gray-200 overflow-hidden">
                  <img
                    src={video.thumbnail}
                    alt={video.title}
                    className="absolute inset-0 w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent"></div>
                  <div className="absolute bottom-2 right-2 px-2 py-1 bg-black/70 rounded text-white text-xs">
                    {video.duration}
                  </div>
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg">
                      <Play className="w-6 h-6 text-white ml-1" />
                    </div>
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="text-gray-900 font-semibold text-sm mb-2 line-clamp-2 group-hover:text-emerald-600 transition-colors">
                    {video.title}
                  </h3>
                  <p className="text-gray-600 text-xs mb-1">{video.author}</p>
                  <p className="text-gray-500 text-xs">{video.views} 观看</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
