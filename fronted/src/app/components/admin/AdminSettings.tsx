import React, { useEffect, useState } from 'react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/app/components/ui/dialog';
import { Label } from '@/app/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/app/components/ui/table';
import { Badge } from '@/app/components/ui/badge';
import { Plus, Edit, Shield } from 'lucide-react';
import { adminApiRequest } from '@/app/lib/api';
import { toast } from 'sonner';

interface AdminUser {
  id: number;
  username: string;
  email: string;
  real_name: string | null;
  role_id: number;
  role_name: string;
  status: string;
  last_login_at: string | null;
  created_at: string;
}

interface Role {
  id: number;
  name: string;
  description: string | null;
  permissions: string[];
  status: string;
  is_super: boolean;
}

export default function AdminSettings() {
  const [adminUsers, setAdminUsers] = useState<AdminUser[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<'user' | 'role'>('user');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    real_name: '',
    role_id: 0,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [usersData, rolesData] = await Promise.all([
        adminApiRequest<{ items: any[]; total: number }>('/admin/users?page_size=100'),
        adminApiRequest<{ items: any[]; total: number }>('/admin/roles?page_size=100'),
      ]);

      setAdminUsers(
        usersData.items.map((user: any) => ({
          ...user,
          role_name: user.role?.name || user.role_name || '未知角色',
        }))
      );
      
      setRoles(
        rolesData.items.map((role: any) => ({
          ...role,
          permissions: typeof role.permissions === 'string' 
            ? JSON.parse(role.permissions || '[]')
            : role.permissions || [],
        }))
      );
    } catch (error: any) {
      toast.error(error.message || '获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (type: 'user' | 'role') => {
    setDialogType(type);
    setFormData({
      username: '',
      email: '',
      password: '',
      real_name: '',
      role_id: roles[0]?.id || 0,
    });
    setDialogOpen(true);
  };

  const handleCreateUser = async () => {
    try {
      await adminApiRequest('/admin/users', {
        method: 'POST',
        body: JSON.stringify(formData),
      });

      toast.success('管理员创建成功');
      setDialogOpen(false);
      fetchData();
    } catch (error: any) {
      toast.error(error.message || '创建管理员失败');
    }
  };

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">系统设置</h1>
        <p className="text-gray-600 mt-2">管理管理员账号和角色权限</p>
      </div>

      <Tabs defaultValue="admins" className="space-y-6">
        <TabsList>
          <TabsTrigger value="admins">管理员管理</TabsTrigger>
          <TabsTrigger value="roles">角色管理</TabsTrigger>
          <TabsTrigger value="logs">操作日志</TabsTrigger>
        </TabsList>

        <TabsContent value="admins">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>管理员列表</CardTitle>
              <Button onClick={() => handleOpenDialog('user')}>
                <Plus className="h-4 w-4 mr-2" />
                添加管理员
              </Button>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">加载中...</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>ID</TableHead>
                      <TableHead>用户名</TableHead>
                      <TableHead>邮箱</TableHead>
                      <TableHead>真实姓名</TableHead>
                      <TableHead>角色</TableHead>
                      <TableHead>状态</TableHead>
                      <TableHead>最后登录</TableHead>
                      <TableHead>创建时间</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {adminUsers.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>{user.id}</TableCell>
                        <TableCell className="font-medium">{user.username}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>{user.real_name || '-'}</TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            <Shield className="h-3 w-3 mr-1" />
                            {user.role_name}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={user.status === 'active' ? 'default' : 'secondary'}
                          >
                            {user.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {user.last_login_at
                            ? new Date(user.last_login_at).toLocaleString()
                            : '从未登录'}
                        </TableCell>
                        <TableCell>
                          {new Date(user.created_at).toLocaleDateString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="roles">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>角色列表</CardTitle>
              <Button onClick={() => handleOpenDialog('role')}>
                <Plus className="h-4 w-4 mr-2" />
                添加角色
              </Button>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">加载中...</div>
              ) : (
                <div className="space-y-4">
                  {roles.map((role) => (
                    <Card key={role.id}>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <CardTitle className="text-lg">{role.name}</CardTitle>
                            {role.is_super && (
                              <Badge variant="destructive">超级管理员</Badge>
                            )}
                          </div>
                          <Badge variant={role.status === 'active' ? 'default' : 'secondary'}>
                            {role.status}
                          </Badge>
                        </div>
                        {role.description && (
                          <p className="text-sm text-gray-600">{role.description}</p>
                        )}
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-2">
                          {role.permissions.map((perm, idx) => (
                            <Badge key={idx} variant="outline">
                              {perm}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="logs">
          <Card>
            <CardHeader>
              <CardTitle>操作日志</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                操作日志功能开发中...
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {dialogType === 'user' ? '添加管理员' : '添加角色'}
            </DialogTitle>
            <DialogDescription>
              {dialogType === 'user' ? '创建新的管理员账号' : '创建新的角色'}
            </DialogDescription>
          </DialogHeader>
          {dialogType === 'user' && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="username">用户名</Label>
                <Input
                  id="username"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="email">邮箱</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="password">密码</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="real_name">真实姓名</Label>
                <Input
                  id="real_name"
                  value={formData.real_name}
                  onChange={(e) => setFormData({ ...formData, real_name: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="role">角色</Label>
                <select
                  id="role"
                  className="w-full border rounded-md p-2"
                  value={formData.role_id}
                  onChange={(e) =>
                    setFormData({ ...formData, role_id: parseInt(e.target.value) })
                  }
                >
                  {roles.map((role) => (
                    <option key={role.id} value={role.id}>
                      {role.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleCreateUser}>创建</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
