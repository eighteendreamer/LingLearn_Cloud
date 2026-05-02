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
import { Search, CheckCircle, XCircle, Eye, Trash2 } from 'lucide-react';
import { adminApiRequest } from '@/app/lib/api';
import { toast } from 'sonner';

interface Content {
  id: number;
  title: string;
  author_name?: string;
  content_type: string;
  category_name?: string;
  audit_status: string;
  publish_status: string;
  views_count: number;
  likes_count: number;
  comments_count: number;
  created_at: string;
}

export default function ContentManagement() {
  const [contents, setContents] = useState<Content[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState('');
  const [auditFilter, setAuditFilter] = useState('all');
  const [publishFilter, setPublishFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    fetchContents();
  }, [page, auditFilter, publishFilter]);

  const fetchContents = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });

      if (keyword) params.append('keyword', keyword);
      if (auditFilter !== 'all') params.append('audit_status', auditFilter);
      if (publishFilter !== 'all') params.append('publish_status', publishFilter);

      const data = await adminApiRequest<{ items: any[]; total: number }>(`/admin/management/contents?${params}`);

      setContents(data.items);
      setTotal(data.total);
    } catch (error: any) {
      toast.error(error.message || '获取内容列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAudit = async (contentId: number, status: string) => {
    try {
      await adminApiRequest(`/admin/management/contents/${contentId}/audit`, {
        method: 'PUT',
        body: JSON.stringify({ audit_status: status }),
      });

      toast.success('审核状态更新成功');
      fetchContents();
    } catch (error: any) {
      toast.error(error.message || '更新审核状态失败');
    }
  };

  const handleDelete = async (contentId: number) => {
    if (!confirm('确定要删除这条内容吗？')) return;

    try {
      await adminApiRequest(`/admin/management/contents/${contentId}`, {
        method: 'DELETE',
      });

      toast.success('内容删除成功');
      fetchContents();
    } catch (error: any) {
      toast.error(error.message || '删除内容失败');
    }
  };

  const getAuditBadge = (status: string) => {
    const variants: Record<string, { variant: any; label: string }> = {
      pending: { variant: 'secondary', label: '待审核' },
      approved: { variant: 'default', label: '已通过' },
      rejected: { variant: 'destructive', label: '已拒绝' },
    };
    const config = variants[status] || variants.pending;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">内容管理</h1>
        <p className="text-gray-600 mt-2">审核和管理平台内容</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 flex gap-2">
              <Input
                placeholder="搜索内容标题..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && fetchContents()}
              />
              <Button onClick={fetchContents}>
                <Search className="h-4 w-4 mr-2" />
                搜索
              </Button>
            </div>
            <Select value={auditFilter} onValueChange={setAuditFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部审核</SelectItem>
                <SelectItem value="pending">待审核</SelectItem>
                <SelectItem value="approved">已通过</SelectItem>
                <SelectItem value="rejected">已拒绝</SelectItem>
              </SelectContent>
            </Select>
            <Select value={publishFilter} onValueChange={setPublishFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部状态</SelectItem>
                <SelectItem value="draft">草稿</SelectItem>
                <SelectItem value="published">已发布</SelectItem>
                <SelectItem value="archived">已归档</SelectItem>
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
                    <TableHead>标题</TableHead>
                    <TableHead>作者</TableHead>
                    <TableHead>分类</TableHead>
                    <TableHead>审核状态</TableHead>
                    <TableHead>发布状态</TableHead>
                    <TableHead>数据</TableHead>
                    <TableHead>创建时间</TableHead>
                    <TableHead>操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {contents.map((content) => (
                    <TableRow key={content.id}>
                      <TableCell>{content.id}</TableCell>
                      <TableCell className="max-w-xs truncate font-medium">
                        {content.title}
                      </TableCell>
                      <TableCell>{content.author_name || '未知'}</TableCell>
                      <TableCell>{content.category_name || '未分类'}</TableCell>
                      <TableCell>{getAuditBadge(content.audit_status)}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{content.publish_status}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="text-xs space-y-1">
                          <div>👁 {content.views_count}</div>
                          <div>❤️ {content.likes_count}</div>
                          <div>💬 {content.comments_count}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {new Date(content.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {content.audit_status === 'pending' && (
                            <>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleAudit(content.id, 'approved')}
                              >
                                <CheckCircle className="h-3 w-3" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleAudit(content.id, 'rejected')}
                              >
                                <XCircle className="h-3 w-3" />
                              </Button>
                            </>
                          )}
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDelete(content.id)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
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
