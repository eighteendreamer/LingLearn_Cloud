import { useEffect, useState } from "react";
import { Outlet, Link, useLocation } from "react-router";
import { LayoutDashboard, User, MessageSquare, Route, BookOpen, PenTool, BarChart3, FileText, Settings, Bell } from "lucide-react";
import { apiRequest } from "../lib/api";
import type { NotificationUnreadCountResponse } from "../lib/types";

const navigation = [
  { name: "总览", path: "/", icon: LayoutDashboard },
  { name: "学生画像", path: "/profile", icon: User },
  { name: "AI对话", path: "/ai-chat", icon: MessageSquare },
  { name: "学习路径", path: "/learning-path", icon: Route },
  { name: "资源中心", path: "/resources", icon: BookOpen },
  { name: "在线练习", path: "/practice", icon: PenTool },
  { name: "学习评估", path: "/assessment", icon: BarChart3 },
  { name: "学习报告", path: "/report", icon: FileText },
  { name: "个人设置", path: "/settings", icon: Settings },
];

export function RootLayout() {
  const location = useLocation();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    loadUnreadCount();
    // 每30秒刷新一次未读数量
    const interval = setInterval(loadUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadUnreadCount = async () => {
    try {
      const data = await apiRequest<NotificationUnreadCountResponse>(
        "/users/me/notifications/unread-count"
      );
      setUnreadCount(data.unread_count);
    } catch (error) {
      console.error("Failed to load unread count:", error);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-16 bg-white border-r border-gray-200 flex flex-col items-center py-6">
        <div className="mb-8">
          <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-teal-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">L</span>
          </div>
        </div>
        <nav className="flex-1 w-full">
          <ul className="space-y-4">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex flex-col items-center justify-center py-3 relative group ${
                      isActive ? "text-emerald-500" : "text-gray-400 hover:text-gray-600"
                    }`}
                    title={item.name}
                  >
                    <Icon className="w-6 h-6" />
                    {isActive && (
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-emerald-500 rounded-r"></div>
                    )}
                    <span className="absolute left-16 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap pointer-events-none z-10">
                      {item.name}
                    </span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
        <button 
          className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center relative"
          onClick={() => {
            // 可以在这里添加打开通知面板的逻辑
            console.log("Open notifications");
          }}
        >
          <Bell className="w-5 h-5 text-gray-600" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </button>
      </aside>
      <main className="flex-1 overflow-y-auto bg-gray-50">
        <Outlet />
      </main>
    </div>
  );
}
