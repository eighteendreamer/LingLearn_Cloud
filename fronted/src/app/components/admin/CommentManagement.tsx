import React, { useEffect, useState } from 'react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Card, CardContent, CardHeader } from '@/app/components/ui/card';
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
import { Search, Eye, EyeOff, Trash2 } from 'lucide-react';
import { adminApiRequest } from '@/app/lib/api';
import { toast } from 'sonner';

interface Comment {
  id: number;
  content_item_id: number;
  content_title?: string;
  user_id: number;
  username?: string;
  content: string;
  like_count: number;
  status: string;
  created_at: string;
}

export default function CommentManagement() {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    fetchComments();
  }, [page, statusFilter]);

  const fetchComments = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });

      if (keyword) params.append('keyword', keyword);
      if (statusFilter !== 'all') params.append('status', statusFilter);

      const data = await adminApiRequest<{ items: any[]; total: number }>(`/admin/management/comments?${params}`);

      setComments(data.items);
      setTotal(data.total);
    } catch (error: any) {
      toast.error(error.message || '获取评论列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (commentId: number, newStatus: string) => {
    try {
      await adminApiRequest(`/admin/management/comments/${commentId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status: newStatus }),
      });

      toast.success('评论状态更新成功');
      fetchComments();
    } catch (error: any) {
      toast.error(error.message || '更新评论状态失败');
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: any; label: string }> = {
      normal: { variant: 'default', label: '正常' },
      hidden: { variant: 'secondary', label: '已隐藏' },
      deleted: { variant: 'destructive', label: '已删除' },
    };
    const config = variants[status] || variants.normal;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">评论管理</h1>
        <p className="text-gray-600 mt-2">审核和管理用户评论</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 flex gap-2">
              <Input
                placeholder="搜索评论内容..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && fetchComments()}
              />
              <Button onClick={fetchComments}>
                <Search className="h-4 w-4 mr-2" />
                搜索
              </Button>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部状态</SelectItem>
                <SelectItem value="normal">正常</SelectItem>
                <SelectItem value="hidden">已隐藏</SelectItem>
                <SelectItem value="deleted">已删除</SelectItem>
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
                    <TableHead>用户</TableHead>
                    <TableHead>内容标题</TableHead>
                    <TableHead>评论内容</TableHead>
                    <TableHead>点赞数</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead>创建时间</TableHead>
                    <TableHead>操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {comments.map((comment) => (
                    <TableRow key={comment.id}>
                      <TableCell>{comment.id}</TableCell>
                      <TableCell>{comment.username || '未知用户'}</TableCell>
                      <TableCell className="max-w-xs truncate">
                        {comment.content_title || '未知内容'}
                      </TableCell>
                      <TableCell className="max-w-md">
                        <div className="truncate">{comment.content}</div>
                      </TableCell>
                      <TableCell>{comment.like_count}</TableCell>
                      <TableCell>{getStatusBadge(comment.status)}</TableCell>
                      <TableCell>
                        {new Date(comment.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {comment.status === 'normal' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleStatusChange(comment.id, 'hidden')}
                            >
                              <EyeOff className="h-3 w-3" />
                            </Button>
                          )}
                          {comment.status === 'hidden' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleStatusChange(comment.id, 'normal')}
                            >
                              <Eye className="h-3 w-3" />
                            </Button>
                          )}
                          {comment.status !== 'deleted' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleStatusChange(comment.id, 'deleted')}
                            >
                              <Trash2 className="h-3 w-3" />
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
