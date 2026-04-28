import { Clock, BookmarkCheck, TrendingUp, Target, Play, ChevronRight } from "lucide-react";

export function MyLearning() {
  const stats = [
    { label: "学习时长", value: "5", unit: "小时", icon: Clock, color: "emerald" },
    { label: "已收藏", value: "6", unit: "个", icon: BookmarkCheck, color: "blue" },
    { label: "连续天数", value: "3", unit: "天", icon: TrendingUp, color: "orange" },
    { label: "完成目标", value: "2", unit: "个", icon: Target, color: "purple" },
  ];

  const savedVideos = [
    {
      id: "1",
      title: "Python数据分析实战",
      author: "编程导师小李",
      duration: "12:34",
      thumbnail: "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=300",
      progress: 65,
    },
    {
      id: "2",
      title: "React Hooks完整教程",
      author: "前端大神王老师",
      duration: "18:22",
      thumbnail: "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=300",
      progress: 30,
    },
    {
      id: "3",
      title: "算法可视化系列",
      author: "算法讲解达人",
      duration: "25:16",
      thumbnail: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=300",
      progress: 0,
    },
    {
      id: "4",
      title: "数据库优化技巧",
      author: "数据库专家刘老师",
      duration: "15:47",
      thumbnail: "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=300",
      progress: 100,
    },
  ];

  const recentlyWatched = [
    {
      id: "1",
      title: "Git工作流最佳实践",
      author: "开发流程专家",
      thumbnail: "https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=300",
      watchedAt: "2小时前",
    },
    {
      id: "2",
      title: "CSS Grid布局详解",
      author: "前端布局大师",
      thumbnail: "https://images.unsplash.com/photo-1507721999472-8ed4421c4af2?w=300",
      watchedAt: "5小时前",
    },
    {
      id: "3",
      title: "Docker容器化部署",
      author: "运维工程师",
      thumbnail: "https://images.unsplash.com/photo-1605745341112-85968b19335b?w=300",
      watchedAt: "昨天",
    },
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, string> = {
      emerald: "from-emerald-400 to-teal-500",
      blue: "from-blue-400 to-indigo-500",
      orange: "from-orange-400 to-amber-500",
      purple: "from-purple-400 to-pink-500",
    };
    return colors[color] || "from-gray-400 to-gray-500";
  };

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="max-w-screen-xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">我的学习</h1>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {stats.map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <div
                key={idx}
                className="bg-white rounded-2xl p-5 border border-gray-200 shadow-md"
              >
                <div
                  className={`w-12 h-12 rounded-xl bg-gradient-to-br ${getColorClasses(
                    stat.color
                  )} flex items-center justify-center mb-3 shadow-sm`}
                >
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-1">
                  {stat.value}
                  <span className="text-lg text-gray-600 ml-1">{stat.unit}</span>
                </div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            );
          })}
        </div>

        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">我的收藏</h2>
            <button className="text-emerald-600 text-sm flex items-center gap-1 hover:text-emerald-700">
              查看全部
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {savedVideos.map((video) => (
              <div
                key={video.id}
                className="bg-white rounded-2xl overflow-hidden border border-gray-200 hover:border-emerald-500 transition-all cursor-pointer group shadow-md hover:shadow-lg"
              >
                <div className="relative">
                  <div className="aspect-video bg-gray-200 relative overflow-hidden">
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
                      <div className="w-14 h-14 rounded-full bg-emerald-500 flex items-center justify-center shadow-lg">
                        <Play className="w-6 h-6 text-white ml-1" />
                      </div>
                    </div>
                  </div>
                  {video.progress > 0 && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-300">
                      <div
                        className="h-full bg-emerald-500"
                        style={{ width: `${video.progress}%` }}
                      ></div>
                    </div>
                  )}
                </div>
                <div className="p-4">
                  <h3 className="text-gray-900 font-semibold mb-1 line-clamp-1">{video.title}</h3>
                  <p className="text-gray-600 text-sm">{video.author}</p>
                  {video.progress > 0 && video.progress < 100 && (
                    <p className="text-emerald-600 text-xs mt-2">已学习 {video.progress}%</p>
                  )}
                  {video.progress === 100 && (
                    <p className="text-emerald-600 text-xs mt-2">✓ 已完成</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">最近观看</h2>
            <button className="text-emerald-600 text-sm flex items-center gap-1 hover:text-emerald-700">
              查看全部
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          <div className="space-y-3">
            {recentlyWatched.map((video) => (
              <div
                key={video.id}
                className="flex gap-3 bg-white rounded-xl p-3 border border-gray-200 hover:border-emerald-500 transition-all cursor-pointer group shadow-sm hover:shadow-md"
              >
                <div className="w-32 h-20 bg-gray-200 rounded-lg flex-shrink-0 relative overflow-hidden">
                  <img
                    src={video.thumbnail}
                    alt={video.title}
                    className="absolute inset-0 w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-white/70 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <Play className="w-8 h-8 text-emerald-600" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-gray-900 font-semibold mb-1 line-clamp-1">{video.title}</h3>
                  <p className="text-gray-600 text-sm mb-2">{video.author}</p>
                  <p className="text-gray-500 text-xs">{video.watchedAt}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
