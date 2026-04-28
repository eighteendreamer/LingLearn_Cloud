import { Search, BookOpen, Video, FileText, Image as ImageIcon } from "lucide-react";

interface Course {
  id: string;
  title: string;
  description: string;
  type: string;
  color: string;
  bgColor: string;
}

export function ResourceCenter() {
  const courses: Course[] = [
    {
      id: "1",
      title: "Python编程基础",
      description: "从零开始学习Python",
      type: "编程",
      color: "text-orange-600",
      bgColor: "bg-orange-50",
    },
    {
      id: "2",
      title: "数据结构与算法",
      description: "掌握核心数据结构",
      type: "算法",
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      id: "3",
      title: "Web前端开发",
      description: "HTML/CSS/JavaScript全栈",
      type: "前端",
      color: "text-emerald-600",
      bgColor: "bg-emerald-50",
    },
    {
      id: "4",
      title: "数据库设计",
      description: "SQL与数据库优化",
      type: "数据库",
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
    {
      id: "5",
      title: "机器学习入门",
      description: "AI与机器学习基础",
      type: "AI",
      color: "text-pink-600",
      bgColor: "bg-pink-50",
    },
    {
      id: "6",
      title: "React框架实战",
      description: "现代前端框架开发",
      type: "前端",
      color: "text-cyan-600",
      bgColor: "bg-cyan-50",
    },
    {
      id: "7",
      title: "算法竞赛训练",
      description: "提升算法竞赛能力",
      type: "算法",
      color: "text-indigo-600",
      bgColor: "bg-indigo-50",
    },
    {
      id: "8",
      title: "Node.js后端开发",
      description: "服务端JavaScript开发",
      type: "后端",
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
  ];

  const stats = [
    { label: "总课程数", value: "156", icon: BookOpen },
    { label: "视频资源", value: "89", icon: Video },
    { label: "文档资料", value: "234", icon: FileText },
    { label: "图片素材", value: "67", icon: ImageIcon },
  ];

  const recentFiles = [
    { name: "算法笔记.pdf", size: "2.4 MB", date: "今天" },
    { name: "Python速查表.pdf", size: "1.2 MB", date: "昨天" },
    { name: "数据结构总结.docx", size: "856 KB", date: "2天前" },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-800">资源中心</h1>
        <div className="relative w-96">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="搜索课程、资源..."
            className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {stats.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div key={idx} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                  <Icon className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-800">{stat.value}</div>
                  <div className="text-xs text-gray-500">{stat.label}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">推荐课程</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {courses.map((course) => (
            <div
              key={course.id}
              className="bg-white rounded-xl overflow-hidden shadow-sm border border-gray-100 hover:shadow-md transition-all cursor-pointer group"
            >
              <div className={`h-32 ${course.bgColor} flex items-center justify-center relative overflow-hidden`}>
                <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent"></div>
                <BookOpen className={`w-16 h-16 ${course.color} opacity-80 group-hover:scale-110 transition-transform`} />
              </div>
              <div className="p-4">
                <div className="mb-2">
                  <span className={`text-xs px-2 py-1 rounded ${course.bgColor} ${course.color} font-medium`}>
                    {course.type}
                  </span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">{course.title}</h3>
                <p className="text-sm text-gray-500">{course.description}</p>
                <button className="mt-4 w-full py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors text-sm font-medium">
                  开始学习
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
        <div className="lg:col-span-2 bg-white rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-800 mb-4">学习进度</h3>
          <div className="space-y-4">
            {["Python编程基础", "数据结构与算法", "Web前端开发"].map((course, idx) => (
              <div key={idx}>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-700">{course}</span>
                  <span className="text-emerald-600 font-semibold">{[78, 65, 42][idx]}%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className="bg-emerald-500 h-2 rounded-full transition-all"
                    style={{ width: `${[78, 65, 42][idx]}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-800 mb-4">最近文件</h3>
          <div className="space-y-3">
            {recentFiles.map((file, idx) => (
              <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-emerald-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 truncate">{file.name}</div>
                  <div className="text-xs text-gray-500">{file.size} · {file.date}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
