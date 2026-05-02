import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { adminApiRequest } from '@/app/lib/api';
import { toast } from 'sonner';

interface UserGrowthData {
  date: string;
  new_users: number;
  active_users: number;
}

interface ContentData {
  date: string;
  new_contents: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
}

interface CategoryData {
  category_id: number;
  category_name: string;
  content_count: number;
  total_views: number;
  total_likes: number;
}

export default function Statistics() {
  const [userGrowth, setUserGrowth] = useState<UserGrowthData[]>([]);
  const [contentStats, setContentStats] = useState<ContentData[]>([]);
  const [categoryStats, setCategoryStats] = useState<CategoryData[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState('30');

  useEffect(() => {
    fetchAllStats();
  }, [days]);

  const fetchAllStats = async () => {
    setLoading(true);
    try {
      const [userGrowthData, contentStatsData, categoryStatsData] = await Promise.all([
        adminApiRequest<UserGrowthData[]>(`/admin/statistics/user-growth?days=${days}`),
        adminApiRequest<ContentData[]>(`/admin/statistics/content?days=${days}`),
        adminApiRequest<CategoryData[]>('/admin/statistics/category'),
      ]);

      setUserGrowth(userGrowthData);
      setContentStats(contentStatsData);
      setCategoryStats(categoryStatsData);
    } catch (error: any) {
      toast.error(error.message || '获取统计数据失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">数据统计</h1>
          <p className="text-gray-600 mt-2">查看平台运营数据和趋势分析</p>
        </div>
        <Select value={days} onValueChange={setDays}>
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7">最近7天</SelectItem>
            <SelectItem value="30">最近30天</SelectItem>
            <SelectItem value="90">最近90天</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className="text-center py-12">加载中...</div>
      ) : (
        <Tabs defaultValue="user" className="space-y-6">
          <TabsList>
            <TabsTrigger value="user">用户增长</TabsTrigger>
            <TabsTrigger value="content">内容统计</TabsTrigger>
            <TabsTrigger value="category">分类分析</TabsTrigger>
          </TabsList>

          <TabsContent value="user" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>用户增长趋势</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={userGrowth}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="new_users"
                      stroke="#3b82f6"
                      name="新增用户"
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="active_users"
                      stroke="#10b981"
                      name="活跃用户"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-gray-600">
                    总新增用户
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {userGrowth.reduce((sum, item) => sum + item.new_users, 0)}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-gray-600">
                    日均新增
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {Math.round(
                      userGrowth.reduce((sum, item) => sum + item.new_users, 0) /
                        userGrowth.length
                    )}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-gray-600">
                    增长率
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-green-600">
                    {userGrowth.length > 1
                      ? (
                          ((userGrowth[userGrowth.length - 1].new_users -
                            userGrowth[0].new_users) /
                            userGrowth[0].new_users) *
                          100
                        ).toFixed(1)
                      : 0}
                    %
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="content" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>内容发布趋势</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={contentStats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="new_contents" fill="#3b82f6" name="新增内容" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>内容互动数据</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={contentStats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="total_views"
                      stroke="#8b5cf6"
                      name="浏览量"
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="total_likes"
                      stroke="#ef4444"
                      name="点赞数"
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="total_comments"
                      stroke="#f59e0b"
                      name="评论数"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="category" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>分类内容分布</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={categoryStats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category_name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="content_count" fill="#3b82f6" name="内容数量" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>分类数据详情</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {categoryStats.map((category) => (
                    <div
                      key={category.category_id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                    >
                      <div>
                        <h3 className="font-semibold">{category.category_name}</h3>
                        <p className="text-sm text-gray-600">
                          {category.content_count} 个内容
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-600">
                          浏览: {category.total_views.toLocaleString()}
                        </div>
                        <div className="text-sm text-gray-600">
                          点赞: {category.total_likes.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
