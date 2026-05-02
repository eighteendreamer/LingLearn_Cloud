import React, { useEffect, useState } from 'react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/app/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';
import { Badge } from '@/app/components/ui/badge';
import { Search, Ban, CheckCircle } from 'lucide-react';
import { adminApiRequest } from '@/app/lib/api';
import { toast } from 'sonner';

interface User {
  id: number;
  username: string;
  email: string;
  display_name?: string;
  status: string;
  followers_count?: number;
  following_count?: number;
  total_learning_minutes?: number;
  created_at: string;
}

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    fetchUsers();
  }, [page, statusFilter]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });

      if (keyword) params.append('keyword', keyword);
      if (statusFilter !== 'all') params.append('status', statusFilter);

      const data = await adminApiRequest<{ items: any[]; total: number; page: number; page_size: number }>(`/admin/management/users?${params}`);

      // 后端现在返回扁平化的对象
      setUsers(data.items);
      setTotal(data.total);
    } catch (error: any) {
      toast.error(error.message || '获取用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    fetchUsers();
  };

  const handleStatusChange = async (userId: number, newStatus: string) => {
    try {
      await adminApiRequest(`/admin/management/users/${userId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status: newStatus }),
      });

      toast.success('用户状态更新成功');
      fetchUsers();
    } catch (error: any) {
      toast.error(error.message || '更新用户状态失败');
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: any; label: string }> = {
      active: { variant: 'default', label: '正常' },
      suspended: { variant: 'secondary', label: '暂停' },
      banned: { variant: 'destructive', label: '封禁' },
    };
    const config = variants[status] || variants.active;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">用户管理</h1>
        <p className="text-gray-600 mt-2">管理平台用户账号和状态</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 flex gap-2">
              <Input
                placeholder="搜索用户名、邮箱..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button onClick={handleSearch}>
                <Search className="h-4 w-4 mr-2" />
                搜索
              </Button>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="状态筛选" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部状态</SelectItem>
                <SelectItem value="active">正常</SelectItem>
                <SelectItem value="suspended">暂停</SelectItem>
                <SelectItem value="banned">封禁</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">加载中...</div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>用户名</TableHead>
                    <TableHead>显示名称</TableHead>
                    <TableHead>邮箱</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead>粉丝/关注</TableHead>
                    <TableHead>学习时长</TableHead>
                    <TableHead>注册时间</TableHead>
                    <TableHead>操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell>{user.id}</TableCell>
                      <TableCell className="font-medium">{user.username}</TableCell>
                      <TableCell>{user.display_name || user.username}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>{getStatusBadge(user.status)}</TableCell>
                      <TableCell>
                        {user.followers_count || 0} / {user.following_count || 0}
                      </TableCell>
                      <TableCell>{Math.floor((user.total_learning_minutes || 0) / 60)}h</TableCell>
                      <TableCell>
                        {new Date(user.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          {user.status === 'active' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleStatusChange(user.id, 'suspended')}
                            >
                              <Ban className="h-3 w-3 mr-1" />
                              暂停
                            </Button>
                          )}
                          {user.status !== 'active' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleStatusChange(user.id, 'active')}
                            >
                              <CheckCircle className="h-3 w-3 mr-1" />
                              恢复
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              <div className="flex items-center justify-between mt-4">
                <div className="text-sm text-gray-600">
                  共 {total} 条记录，第 {page} / {Math.ceil(total / pageSize)} 页
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    disabled={page === 1}
                    onClick={() => setPage(page - 1)}
                  >
                    上一页
                  </Button>
                  <Button
                    variant="outline"
                    disabled={page >= Math.ceil(total / pageSize)}
                    onClick={() => setPage(page + 1)}
                  >
                    下一页
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
