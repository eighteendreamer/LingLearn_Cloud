import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { toast } from 'sonner';
import { adminApiRequest } from '@/app/lib/api';

export default function AdminLogin() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  // 如果已经登录，直接跳转到 dashboard
  useEffect(() => {
    const adminToken = localStorage.getItem('admin_token');
    if (adminToken) {
      navigate('/admin/dashboard', { replace: true });
    }
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // adminApiRequest 已经解包了 envelope，直接返回 data
      const data = await adminApiRequest<{
        access_token: string;
        refresh_token: string;
        token_type: string;
        admin_user: any;
      }>('/admin/auth/login', {
        method: 'POST',
        body: JSON.stringify(formData),
        auth: false, // 登录接口不需要认证
      });

      // 保存 token 和用户信息
      localStorage.setItem('admin_token', data.access_token);
      localStorage.setItem('admin_refresh_token', data.refresh_token);
      localStorage.setItem('admin_user', JSON.stringify(data.admin_user));
      
      toast.success('登录成功');
      
      // 使用 window.location 强制跳转
      window.location.href = '/admin/dashboard';
    } catch (error: any) {
      toast.error(error.message || '登录失败，请检查用户名和密码');
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">后台管理系统</CardTitle>
          <CardDescription className="text-center">
            请使用管理员账号登录
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">用户名</Label>
              <Input
                id="username"
                type="text"
                placeholder="请输入用户名"
                value={formData.username}
                onChange={(e) =>
                  setFormData({ ...formData, username: e.target.value })
                }
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">密码</Label>
              <Input
                id="password"
                type="password"
                placeholder="请输入密码"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                required
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? '登录中...' : '登录'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
