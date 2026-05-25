import React, { useState, useEffect } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router';
import {
  LayoutDashboard,
  Users,
  FileText,
  BookOpen,
  MessageSquare,
  FolderTree,
  Tags,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  X,
} from 'lucide-react';
import { Button } from '@/app/components/ui/button';

const menuItems = [
  { path: '/admin/dashboard', icon: LayoutDashboard, label: '仪表盘' },
  { path: '/admin/users', icon: Users, label: '用户管理' },
  { path: '/admin/contents', icon: FileText, label: '内容管理' },
  { path: '/admin/courses', icon: BookOpen, label: '课程管理' },
  { path: '/admin/comments', icon: MessageSquare, label: '评论管理' },
  { path: '/admin/categories', icon: FolderTree, label: '分类管理' },
  { path: '/admin/tags', icon: Tags, label: '标签管理' },
  { path: '/admin/statistics', icon: BarChart3, label: '数据统计' },
  { path: '/admin/settings', icon: Settings, label: '系统设置' },
];

export default function AdminLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // 检查管理员是否已登录
  useEffect(() => {
    const adminToken = localStorage.getItem('admin_token');
    if (!adminToken) {
      navigate('/admin/login', { replace: true });
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_refresh_token');
    localStorage.removeItem('admin_user');
    navigate('/admin/login');
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-white shadow-lg transition-all duration-300 flex flex-col`}
      >
        <div className="p-4 border-b flex items-center justify-between">
          {sidebarOpen && (
            <h1 className="text-xl font-bold text-gray-800">后台管理</h1>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </Button>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Icon size={20} />
                {sidebarOpen && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t">
          <Button
            variant="ghost"
            className="w-full justify-start gap-3"
            onClick={handleLogout}
          >
            <LogOut size={20} />
            {sidebarOpen && <span>退出登录</span>}
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
