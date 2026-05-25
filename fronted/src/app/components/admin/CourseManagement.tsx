import { useEffect, useRef, useState } from 'react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Textarea } from '@/app/components/ui/textarea';
import { Label } from '@/app/components/ui/label';
import { Card, CardContent, CardHeader } from '@/app/components/ui/card';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/app/components/ui/table';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/app/components/ui/select';
import { Badge } from '@/app/components/ui/badge';
import {
  Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle,
} from '@/app/components/ui/dialog';
import {
  Search, Plus, Pencil, Trash2, List, ArrowLeft, Upload, ImagePlus,
} from 'lucide-react';
import { adminApiRequest } from '@/app/lib/api';
import { adminUploadVideo, adminCreateContentItem, adminUploadCover } from '@/app/lib/admin-storage';
import { toast } from 'sonner';

interface CourseItem {
  id: number;
  title: string;
  summary: string | null;
  instructor_name: string;
  category_name: string | null;
  cover_asset_id: number | null;
  cover_url: string | null;
  level: string;
  lesson_count: number;
  enrollment_count: number;
  status: string;
  created_at: string;
}

interface LessonItem {
  id: number;
  title: string;
  description: string | null;
  content_item_id: number | null;
  content_title: string | null;
  duration_minutes: number;
  sort_order: number;
  is_free: string;
  status: string;
  created_at: string;
}

interface CategoryOption {
  id: number;
  name: string;
}

interface ContentItemOption {
  id: number;
  title: string;
  content_type: string;
  duration_seconds: number | null;
}

interface CourseForm {
  title: string;
  summary: string;
  description: string;
  category_id: string;
  cover_asset_id: number | null;
  cover_url: string;
  level: string;
  status: string;
}

interface LessonForm {
  title: string;
  description: string;
  content_item_id: string;
  duration_minutes: string;
  sort_order: string;
  is_free: string;
}

const LEVEL_MAP: Record<string, string> = {
  beginner: '入门',
  intermediate: '中级',
  advanced: '高级',
};

const emptyCourseForm: CourseForm = {
  title: '', summary: '', description: '', category_id: '', cover_asset_id: null, cover_url: '', level: 'beginner', status: 'draft',
};

const emptyLessonForm: LessonForm = {
  title: '', description: '', content_item_id: '', duration_minutes: '0', sort_order: '0', is_free: 'free',
};

export default function CourseManagement() {
  const [view, setView] = useState<'list' | 'lessons'>('list');
  const [courses, setCourses] = useState<CourseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  const [courseDialogOpen, setCourseDialogOpen] = useState(false);
  const [editingCourseId, setEditingCourseId] = useState<number | null>(null);
  const [courseForm, setCourseForm] = useState<CourseForm>(emptyCourseForm);
  const [categories, setCategories] = useState<CategoryOption[]>([]);
  const [saving, setSaving] = useState(false);

  const [selectedCourse, setSelectedCourse] = useState<CourseItem | null>(null);
  const [lessons, setLessons] = useState<LessonItem[]>([]);
  const [lessonsLoading, setLessonsLoading] = useState(false);

  const [lessonDialogOpen, setLessonDialogOpen] = useState(false);
  const [editingLessonId, setEditingLessonId] = useState<number | null>(null);
  const [lessonForm, setLessonForm] = useState<LessonForm>(emptyLessonForm);
  const [contentItems, setContentItems] = useState<ContentItemOption[]>([]);
  const [contentKeyword, setContentKeyword] = useState('');
  const [lessonSaving, setLessonSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const videoInputRef = useRef<HTMLInputElement>(null);
  const [coverUploading, setCoverUploading] = useState(false);
  const coverInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { fetchCourses(); }, [page, statusFilter]);

  const fetchCourses = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: page.toString(), page_size: pageSize.toString() });
      if (keyword) params.append('keyword', keyword);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      const data = await adminApiRequest<{ items: CourseItem[]; total: number }>(
        `/admin/management/courses?${params}`,
      );
      setCourses(data.items);
      setTotal(data.total);
    } catch (err: any) {
      toast.error(err.message || '获取课程列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const data = await adminApiRequest<{ items: CategoryOption[] }>(
        '/admin/management/categories?page_size=100',
      );
      setCategories(data.items);
    } catch { /* ignore */ }
  };

  const fetchContentItems = async (kw?: string) => {
    try {
      const params = new URLSearchParams({ page_size: '50' });
      if (kw) params.append('keyword', kw);
      const data = await adminApiRequest<{ items: ContentItemOption[] }>(
        `/admin/management/content-items?${params}`,
      );
      setContentItems(data.items);
    } catch { /* ignore */ }
  };

  const openCourseDialog = (course?: CourseItem) => {
    fetchCategories();
    if (course) {
      setEditingCourseId(course.id);
      setCourseForm({
        title: course.title,
        summary: course.summary || '',
        description: '',
        category_id: '',
        cover_asset_id: course.cover_asset_id ?? null,
        cover_url: course.cover_url || '',
        level: course.level,
        status: course.status,
      });
    } else {
      setEditingCourseId(null);
      setCourseForm(emptyCourseForm);
    }
    setCourseDialogOpen(true);
  };

  const saveCourse = async () => {
    if (!courseForm.title.trim()) { toast.error('请输入课程标题'); return; }
    setSaving(true);
    try {
      const body: any = {
        title: courseForm.title,
        summary: courseForm.summary || null,
        description: courseForm.description || null,
        category_id: courseForm.category_id ? Number(courseForm.category_id) : null,
        cover_asset_id: courseForm.cover_asset_id,
        level: courseForm.level,
        status: courseForm.status,
      };
      if (editingCourseId) {
        await adminApiRequest(`/admin/management/courses/${editingCourseId}`, {
          method: 'PUT', body: JSON.stringify(body),
        });
        toast.success('课程更新成功');
      } else {
        await adminApiRequest('/admin/management/courses', {
          method: 'POST', body: JSON.stringify(body),
        });
        toast.success('课程创建成功');
      }
      setCourseDialogOpen(false);
      fetchCourses();
    } catch (err: any) {
      toast.error(err.message || '保存课程失败');
    } finally {
      setSaving(false);
    }
  };

  const deleteCourse = async (id: number) => {
    if (!confirm('确定要删除这门课程吗？')) return;
    try {
      await adminApiRequest(`/admin/management/courses/${id}`, { method: 'DELETE' });
      toast.success('课程删除成功');
      fetchCourses();
    } catch (err: any) {
      toast.error(err.message || '删除课程失败');
    }
  };

  const openLessonsView = (course: CourseItem) => {
    setSelectedCourse(course);
    setView('lessons');
    fetchLessons(course.id);
  };

  const fetchLessons = async (courseId: number) => {
    setLessonsLoading(true);
    try {
      const data = await adminApiRequest<{ items: LessonItem[] }>(
        `/admin/management/courses/${courseId}/lessons`,
      );
      setLessons(data.items);
    } catch (err: any) {
      toast.error(err.message || '获取课时列表失败');
    } finally {
      setLessonsLoading(false);
    }
  };

  const openLessonDialog = (lesson?: LessonItem) => {
    fetchContentItems();
    if (lesson) {
      setEditingLessonId(lesson.id);
      setLessonForm({
        title: lesson.title,
        description: lesson.description || '',
        content_item_id: lesson.content_item_id ? String(lesson.content_item_id) : '',
        duration_minutes: String(lesson.duration_minutes),
        sort_order: String(lesson.sort_order),
        is_free: lesson.is_free,
      });
    } else {
      setEditingLessonId(null);
      setLessonForm({ ...emptyLessonForm, sort_order: String(lessons.length) });
    }
    setLessonDialogOpen(true);
  };

  const saveLesson = async () => {
    if (!selectedCourse) return;
    if (!lessonForm.title.trim()) { toast.error('请输入课时标题'); return; }
    setLessonSaving(true);
    try {
      const body: any = {
        title: lessonForm.title,
        description: lessonForm.description || null,
        content_item_id: lessonForm.content_item_id ? Number(lessonForm.content_item_id) : null,
        duration_minutes: Number(lessonForm.duration_minutes) || 0,
        sort_order: Number(lessonForm.sort_order) || 0,
        is_free: lessonForm.is_free,
      };
      if (editingLessonId) {
        await adminApiRequest(
          `/admin/management/courses/${selectedCourse.id}/lessons/${editingLessonId}`,
          { method: 'PUT', body: JSON.stringify(body) },
        );
        toast.success('课时更新成功');
      } else {
        await adminApiRequest(
          `/admin/management/courses/${selectedCourse.id}/lessons`,
          { method: 'POST', body: JSON.stringify(body) },
        );
        toast.success('课时创建成功');
      }
      setLessonDialogOpen(false);
      fetchLessons(selectedCourse.id);
    } catch (err: any) {
      toast.error(err.message || '保存课时失败');
    } finally {
      setLessonSaving(false);
    }
  };

  const deleteLesson = async (lessonId: number) => {
    if (!selectedCourse) return;
    if (!confirm('确定要删除这个课时吗？')) return;
    try {
      await adminApiRequest(
        `/admin/management/courses/${selectedCourse.id}/lessons/${lessonId}`,
        { method: 'DELETE' },
      );
      toast.success('课时删除成功');
      fetchLessons(selectedCourse.id);
    } catch (err: any) {
      toast.error(err.message || '删除课时失败');
    }
  };

  const handleCoverUpload = async (file: File) => {
    setCoverUploading(true);
    try {
      const result = await adminUploadCover(file);
      setCourseForm((prev) => ({
        ...prev,
        cover_asset_id: result.asset_id,
        cover_url: result.public_url || URL.createObjectURL(file),
      }));
      toast.success('封面上传成功');
    } catch (err: any) {
      toast.error(err.message || '封面上传失败');
    } finally {
      setCoverUploading(false);
    }
  };

  const handleVideoUpload = async (file: File) => {
    setUploading(true);
    setUploadProgress(0);
    try {
      toast.info('正在上传视频...');
      const asset = await adminUploadVideo(file, (p) => setUploadProgress(p));
      toast.success('视频上传完成，正在创建内容...');
      const contentItem = await adminCreateContentItem({
        title: lessonForm.title || file.name.replace(/\.[^.]+$/, ''),
        primary_media_asset_id: asset.asset_id,
      });
      setLessonForm((prev) => ({ ...prev, content_item_id: String(contentItem.id) }));
      fetchContentItems();
      toast.success('视频已上传并关联');
    } catch (err: any) {
      toast.error(err.message || '视频上传失败');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  if (view === 'lessons' && selectedCourse) {
    return (
      <div className="p-8">
        <div className="mb-6">
          <button
            onClick={() => { setView('list'); fetchCourses(); }}
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mb-3"
          >
            <ArrowLeft className="h-4 w-4" />
            返回课程列表
          </button>
          <h1 className="text-3xl font-bold text-gray-900">{selectedCourse.title}</h1>
          <p className="text-gray-600 mt-1">课时管理</p>
        </div>

        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">共 {lessons.length} 个课时</span>
              <Button onClick={() => openLessonDialog()}>
                <Plus className="h-4 w-4 mr-2" />
                添加课时
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {lessonsLoading ? (
              <div className="text-center py-8">加载中...</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16">序号</TableHead>
                    <TableHead>标题</TableHead>
                    <TableHead>关联内容</TableHead>
                    <TableHead className="w-20">时长</TableHead>
                    <TableHead className="w-20">类型</TableHead>
                    <TableHead className="w-20">状态</TableHead>
                    <TableHead className="w-24">操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {lessons.map((lesson) => (
                    <TableRow key={lesson.id}>
                      <TableCell>{lesson.sort_order + 1}</TableCell>
                      <TableCell className="font-medium">{lesson.title}</TableCell>
                      <TableCell className="text-sm text-gray-500">
                        {lesson.content_title || <span className="text-orange-500">未关联</span>}
                      </TableCell>
                      <TableCell>{lesson.duration_minutes} 分钟</TableCell>
                      <TableCell>
                        <Badge variant={lesson.is_free === 'free' ? 'default' : 'secondary'}>
                          {lesson.is_free === 'free' ? '免费' : '付费'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={lesson.status === 'published' ? 'default' : 'outline'}>
                          {lesson.status === 'published' ? '已发布' : '草稿'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button size="sm" variant="outline" onClick={() => openLessonDialog(lesson)}>
                            <Pencil className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => deleteLesson(lesson.id)}>
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                  {lessons.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-gray-400">
                        暂无课时，点击上方按钮添加
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Dialog open={lessonDialogOpen} onOpenChange={setLessonDialogOpen}>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>{editingLessonId ? '编辑课时' : '添加课时'}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>标题</Label>
                <Input
                  value={lessonForm.title}
                  onChange={(e) => setLessonForm({ ...lessonForm, title: e.target.value })}
                  placeholder="课时标题"
                />
              </div>
              <div>
                <Label>描述</Label>
                <Textarea
                  value={lessonForm.description}
                  onChange={(e) => setLessonForm({ ...lessonForm, description: e.target.value })}
                  placeholder="课时描述（选填）"
                  rows={2}
                />
              </div>
              <div>
                <Label>关联内容</Label>
                <div className="flex gap-2 mb-2">
                  <Input
                    placeholder="搜索内容..."
                    value={contentKeyword}
                    onChange={(e) => setContentKeyword(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && fetchContentItems(contentKeyword)}
                    className="flex-1"
                  />
                  <Button variant="outline" size="sm" onClick={() => fetchContentItems(contentKeyword)}>
                    <Search className="h-3 w-3" />
                  </Button>
                  <input
                    ref={videoInputRef}
                    type="file"
                    accept="video/*"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleVideoUpload(file);
                      e.target.value = '';
                    }}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={uploading}
                    onClick={() => videoInputRef.current?.click()}
                  >
                    <Upload className="h-3 w-3 mr-1" />
                    {uploading ? `${uploadProgress}%` : '上传视频'}
                  </Button>
                </div>
                {uploading && (
                  <div className="mb-2 h-1.5 overflow-hidden rounded-full bg-blue-100">
                    <div className="h-full bg-blue-500 transition-all" style={{ width: `${uploadProgress}%` }} />
                  </div>
                )}
                <Select
                  value={lessonForm.content_item_id || '__none__'}
                  onValueChange={(v) => setLessonForm({ ...lessonForm, content_item_id: v === '__none__' ? '' : v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="选择关联内容（选填）" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__none__">不关联</SelectItem>
                    {contentItems.map((ci) => (
                      <SelectItem key={ci.id} value={String(ci.id)}>
                        {ci.title} ({ci.content_type}{ci.duration_seconds ? `, ${Math.ceil(ci.duration_seconds / 60)}分钟` : ''})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label>时长（分钟）</Label>
                  <Input
                    type="number"
                    value={lessonForm.duration_minutes}
                    onChange={(e) => setLessonForm({ ...lessonForm, duration_minutes: e.target.value })}
                  />
                </div>
                <div>
                  <Label>排序</Label>
                  <Input
                    type="number"
                    value={lessonForm.sort_order}
                    onChange={(e) => setLessonForm({ ...lessonForm, sort_order: e.target.value })}
                  />
                </div>
                <div>
                  <Label>类型</Label>
                  <Select value={lessonForm.is_free} onValueChange={(v) => setLessonForm({ ...lessonForm, is_free: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="free">免费</SelectItem>
                      <SelectItem value="paid">付费</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setLessonDialogOpen(false)}>取消</Button>
              <Button onClick={saveLesson} disabled={lessonSaving}>
                {lessonSaving ? '保存中...' : '保存'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">课程管理</h1>
        <p className="text-gray-600 mt-2">管理平台课程和课时</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 flex gap-2">
              <Input
                placeholder="搜索课程标题..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && fetchCourses()}
              />
              <Button onClick={fetchCourses}>
                <Search className="h-4 w-4 mr-2" />
                搜索
              </Button>
            </div>
            <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
              <SelectTrigger className="w-[150px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部状态</SelectItem>
                <SelectItem value="draft">草稿</SelectItem>
                <SelectItem value="published">已发布</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={() => openCourseDialog()}>
              <Plus className="h-4 w-4 mr-2" />
              新建课程
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
                    <TableHead>标题</TableHead>
                    <TableHead>讲师</TableHead>
                    <TableHead>分类</TableHead>
                    <TableHead>级别</TableHead>
                    <TableHead>课时</TableHead>
                    <TableHead>报名数</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead>创建时间</TableHead>
                    <TableHead>操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {courses.map((course) => (
                    <TableRow key={course.id}>
                      <TableCell>{course.id}</TableCell>
                      <TableCell className="max-w-xs truncate font-medium">{course.title}</TableCell>
                      <TableCell>{course.instructor_name}</TableCell>
                      <TableCell>{course.category_name || '无'}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{LEVEL_MAP[course.level] || course.level}</Badge>
                      </TableCell>
                      <TableCell>{course.lesson_count}</TableCell>
                      <TableCell>{course.enrollment_count}</TableCell>
                      <TableCell>
                        <Badge variant={course.status === 'published' ? 'default' : 'secondary'}>
                          {course.status === 'published' ? '已发布' : '草稿'}
                        </Badge>
                      </TableCell>
                      <TableCell>{new Date(course.created_at).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button size="sm" variant="outline" onClick={() => openCourseDialog(course)} title="编辑">
                            <Pencil className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => openLessonsView(course)} title="管理课时">
                            <List className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => deleteCourse(course.id)} title="删除">
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
                  共 {total} 条记录，第 {page} / {Math.max(1, Math.ceil(total / pageSize))} 页
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" disabled={page === 1} onClick={() => setPage(page - 1)}>
                    上一页
                  </Button>
                  <Button variant="outline" disabled={page >= Math.ceil(total / pageSize)} onClick={() => setPage(page + 1)}>
                    下一页
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <Dialog open={courseDialogOpen} onOpenChange={setCourseDialogOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingCourseId ? '编辑课程' : '新建课程'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>标题</Label>
              <Input
                value={courseForm.title}
                onChange={(e) => setCourseForm({ ...courseForm, title: e.target.value })}
                placeholder="课程标题"
              />
            </div>
            <div>
              <Label>摘要</Label>
              <Input
                value={courseForm.summary}
                onChange={(e) => setCourseForm({ ...courseForm, summary: e.target.value })}
                placeholder="课程摘要（选填）"
              />
            </div>
            <div>
              <Label>详细描述</Label>
              <Textarea
                value={courseForm.description}
                onChange={(e) => setCourseForm({ ...courseForm, description: e.target.value })}
                placeholder="课程详细描述（选填）"
                rows={3}
              />
            </div>
            <div>
              <Label>课程封面</Label>
              <input
                ref={coverInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleCoverUpload(file);
                  e.target.value = '';
                }}
              />
              {courseForm.cover_url ? (
                <div className="relative mt-1 h-32 w-full overflow-hidden rounded-md border">
                  <img src={courseForm.cover_url} alt="封面" className="h-full w-full object-cover" />
                  <Button
                    type="button"
                    size="sm"
                    variant="secondary"
                    className="absolute bottom-2 right-2 opacity-80"
                    disabled={coverUploading}
                    onClick={() => coverInputRef.current?.click()}
                  >
                    {coverUploading ? '上传中...' : '更换封面'}
                  </Button>
                </div>
              ) : (
                <button
                  type="button"
                  disabled={coverUploading}
                  onClick={() => coverInputRef.current?.click()}
                  className="mt-1 flex h-32 w-full items-center justify-center rounded-md border-2 border-dashed border-gray-300 text-gray-400 hover:border-gray-400 hover:text-gray-500"
                >
                  {coverUploading ? (
                    <span className="text-sm">上传中...</span>
                  ) : (
                    <div className="flex flex-col items-center gap-1">
                      <ImagePlus className="h-8 w-8" />
                      <span className="text-sm">上传封面图</span>
                    </div>
                  )}
                </button>
              )}
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label>分类</Label>
                <Select value={courseForm.category_id || '__none__'} onValueChange={(v) => setCourseForm({ ...courseForm, category_id: v === '__none__' ? '' : v })}>
                  <SelectTrigger><SelectValue placeholder="选择分类" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__none__">无</SelectItem>
                    {categories.map((cat) => (
                      <SelectItem key={cat.id} value={String(cat.id)}>{cat.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>级别</Label>
                <Select value={courseForm.level} onValueChange={(v) => setCourseForm({ ...courseForm, level: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="beginner">入门</SelectItem>
                    <SelectItem value="intermediate">中级</SelectItem>
                    <SelectItem value="advanced">高级</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>状态</Label>
                <Select value={courseForm.status} onValueChange={(v) => setCourseForm({ ...courseForm, status: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">草稿</SelectItem>
                    <SelectItem value="published">已发布</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCourseDialogOpen(false)}>取消</Button>
            <Button onClick={saveCourse} disabled={saving}>
              {saving ? '保存中...' : '保存'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
