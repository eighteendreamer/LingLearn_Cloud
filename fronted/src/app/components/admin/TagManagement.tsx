import React, { useEffect, useState } from 'react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Card, CardContent, CardHeader } from '@/app/components/ui/card';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';
import { Badge } from '@/app/components/ui/badge';
import { Plus, Edit, Trash2, Search } from 'lucide-react';
import { adminApiRequest } from '@/app/lib/api';
import { toast } from 'sonner';

interface Tag {
  id: number;
  name: string;
  slug: string;
  tag_type: string;
  status: string;
  use_count: number;
  created_at: string;
}

export default function TagManagement() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    tag_type: 'topic',
  });
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 50;

  useEffect(() => {
    fetchTags();
  }, [page]);

  const fetchTags = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });
      if (keyword) params.append('keyword', keyword);

      const data = await adminApiRequest<{ items: Tag[]; total: number }>(
        `/admin/management/tags?${params}`
      );

      setTags(data.items);
      setTotal(data.total);
    } catch (error: any) {
      toast.error(error.message || '获取标签列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (tag?: Tag) => {
    if (tag) {
      setEditingTag(tag);
      setFormData({
        name: tag.name,
        slug: tag.slug,
        tag_type: tag.tag_type,
      });
    } else {
      setEditingTag(null);
      setFormData({
        name: '',
        slug: '',
        tag_type: 'topic',
      });
    }
    setDialogOpen(true);
  };

  const handleSubmit = async () => {
    try {
      const url = editingTag
        ? `/admin/management/tags/${editingTag.id}`
        : '/admin/management/tags';
      const method = editingTag ? 'PUT' : 'POST';

      await adminApiRequest(url, {
        method,
        body: JSON.stringify(formData),
      });

      toast.success(editingTag ? '标签更新成功' : '标签创建成功');
      setDialogOpen(false);
      fetchTags();
    } catch (error: any) {
      toast.error(error.message || '操作失败');
    }
  };

  const handleDelete = async (tagId: number) => {
    if (!confirm('确定要删除这个标签吗？')) return;

    try {
      await adminApiRequest(`/admin/management/tags/${tagId}`, {
        method: 'DELETE',
      });

      toast.success('标签删除成功');
      fetchTags();
    } catch (error: any) {
      toast.error(error.message || '删除标签失败');
    }
  };

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">标签管理</h1>
          <p className="text-gray-600 mt-2">管理内容标签和分类标记</p>
        </div>
        <Button onClick={() => handleOpenDialog()}>
          <Plus className="h-4 w-4 mr-2" />
          添加标签
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex gap-2">
            <Input
              placeholder="搜索标签名称..."
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && fetchTags()}
            />
            <Button onClick={fetchTags}>
              <Search className="h-4 w-4 mr-2" />
              搜索
            </Button>
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
                    <TableHead>标签名称</TableHead>
                    <TableHead>标识</TableHead>
                    <TableHead>类型</TableHead>
                    <TableHead>使用次数</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead>创建时间</TableHead>
                    <TableHead>操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tags.map((tag) => (
                    <TableRow key={tag.id}>
                      <TableCell>{tag.id}</TableCell>
                      <TableCell className="font-medium">
                        <Badge variant="outline">{tag.name}</Badge>
                      </TableCell>
                      <TableCell>
                        <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                          {tag.slug}
                        </code>
                      </TableCell>
                      <TableCell>{tag.tag_type}</TableCell>
                      <TableCell>
                        <span className="font-semibold text-blue-600">
                          {tag.use_count.toLocaleString()}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={tag.status === 'active' ? 'default' : 'secondary'}>
                          {tag.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {new Date(tag.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleOpenDialog(tag)}
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDelete(tag.id)}
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

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingTag ? '编辑标签' : '添加标签'}</DialogTitle>
            <DialogDescription>
              {editingTag ? '修改标签信息' : '创建新的内容标签'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">标签名称</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="例如：Python"
              />
            </div>
            <div>
              <Label htmlFor="slug">标识（英文）</Label>
              <Input
                id="slug"
                value={formData.slug}
                onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                placeholder="例如：python"
              />
            </div>
            <div>
              <Label htmlFor="tag_type">标签类型</Label>
              <Select
                value={formData.tag_type}
                onValueChange={(value) => setFormData({ ...formData, tag_type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="topic">主题</SelectItem>
                  <SelectItem value="skill">技能</SelectItem>
                  <SelectItem value="level">难度</SelectItem>
                  <SelectItem value="language">语言</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSubmit}>{editingTag ? '保存' : '创建'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
