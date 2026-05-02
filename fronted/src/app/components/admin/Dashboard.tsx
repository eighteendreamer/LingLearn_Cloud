import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Users, FileText, MessageSquare, Eye, TrendingUp, AlertCircle } from 'lucide-react';
import { adminApiRequest } from '@/app/lib/api';
import { toast } from 'sonner';

interface DashboardStats {
  total_users: number;
  active_users: number;
  new_users_today: number;
  total_contents: number;
  pending_audit_contents: number;
  new_contents_today: number;
  total_comments: number;
  pending_comments: number;
  total_views_today: number;
  total_interactions_today: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await adminApiRequest<DashboardStats>('/admin/statistics/dashboard');
      setStats(data);
    } catch (error: any) {
      toast.error(error.message || '获取统计数据失败');
      console.error('Fetch stats error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      title: '总用户数',
      value: stats?.total_users || 0,
      subtitle: `今日新增: ${stats?.new_users_today || 0}`,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: '总内容数',
      value: stats?.total_contents || 0,
      subtitle: `今日新增: ${stats?.new_contents_today || 0}`,
      icon: FileText,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: '待审核内容',
      value: stats?.pending_audit_contents || 0,
      subtitle: `总评论: ${stats?.total_comments || 0}`,
      icon: AlertCircle,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
    {
      title: '今日浏览量',
      value: stats?.total_views_today || 0,
      subtitle: `今日互动: ${stats?.total_interactions_today || 0}`,
      icon: Eye,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">仪表盘</h1>
        <p className="text-gray-600 mt-2">欢迎回来，这是您的系统概览</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  {card.title}
                </CardTitle>
                <div className={`p-2 rounded-lg ${card.bgColor}`}>
                  <Icon className={`h-5 w-5 ${card.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{card.value.toLocaleString()}</div>
                <p className="text-xs text-gray-500 mt-1">{card.subtitle}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <Card>
          <CardHeader>
            <CardTitle>快速操作</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <a
              href="/admin/contents?audit_status=pending"
              className="block p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">审核待处理内容</span>
                <span className="text-sm text-gray-500">
                  {stats?.pending_audit_contents || 0} 条
                </span>
              </div>
            </a>
            <a
              href="/admin/comments?status=pending"
              className="block p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">审核待处理评论</span>
                <span className="text-sm text-gray-500">
                  {stats?.pending_comments || 0} 条
                </span>
              </div>
            </a>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>系统状态</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">活跃用户</span>
              <span className="font-semibold">{stats?.active_users || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">今日新增用户</span>
              <span className="font-semibold text-green-600">
                +{stats?.new_users_today || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">今日新增内容</span>
              <span className="font-semibold text-blue-600">
                +{stats?.new_contents_today || 0}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
