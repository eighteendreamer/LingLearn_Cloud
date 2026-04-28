# LingLearn Cloud API 开发手册

## 1. 文档目标

本文档基于当前前端原型功能反推后端 API，目标是让后端团队可以直接按模块开工，覆盖以下前端能力：

- 登录 / 注册
- 个人资料编辑与设置
- 视频流、点赞、收藏、评论、分享
- 发现页、搜索、热门分类 / 热门标签
- 创作中心：上传视频与封面、发布作品
- 我的学习：学习进度、收藏、观看历史
- 学生画像、学习路径、在线练习、学习评估、学习报告
- AI 学习助手
- 资源中心

技术栈约定：

- 语言：Python 3.11+
- Web 框架：FastAPI
- ORM：SQLAlchemy 2.0
- 数据库：MySQL 8.0
- 工作流：LangGraph
- 对象存储：MinIO

## 2. 前后端边界

### 2.1 前端功能与后端模块映射

| 前端页面 | 后端模块 | 主要表 |
| --- | --- | --- |
| 登录 / 注册 | `auth` | `users`, `user_refresh_tokens` |
| 首页视频流 | `content`, `social` | `content_items`, `content_likes`, `content_favorites`, `content_comments`, `content_view_histories` |
| 视频内答题 | `quiz` | `content_quizzes`, `content_quiz_options`, `content_quiz_attempts` |
| 发现页 | `discover`, `search` | `content_categories`, `tags`, `content_items` |
| 创作中心 | `content`, `storage` | `media_assets`, `content_items`, `content_item_tags` |
| 我的学习 | `learning`, `content` | `user_course_enrollments`, `user_lesson_progress`, `content_view_histories` |
| 学生画像 | `profile`, `ai` | `user_skill_snapshots`, `user_skill_scores`, `ai_workflow_runs` |
| 学习路径 | `learning_path`, `ai` | `learning_paths`, `learning_path_nodes`, `user_learning_paths`, `user_learning_path_nodes` |
| 在线练习 | `practice` | `question_banks`, `questions`, `practice_sessions`, `practice_answers` |
| 学习评估 | `assessment` | `assessment_snapshots` |
| 学习报告 | `report`, `ai` | `monthly_reports`, `report_achievements` |
| AI 学习助手 | `ai_chat` | `ai_chat_sessions`, `ai_chat_messages`, `ai_workflow_runs` |
| 资源中心 | `resource`, `course` | `resources`, `courses`, `course_lessons` |
| 设置 / 通知 | `user`, `notification` | `user_settings`, `notifications` |

## 3. 通用约定

### 3.1 Base URL

```text
/api/v1
```

### 3.2 鉴权方式

- Access Token：JWT，放在 `Authorization: Bearer <token>`
- Refresh Token：长效 Token，建议放 HttpOnly Cookie 或安全存储后调用刷新接口

### 3.3 通用响应结构

```json
{
  "code": 0,
  "message": "ok",
  "data": {},
  "request_id": "01HV..."
}
```

### 3.4 分页结构

```json
{
  "list": [],
  "page": 1,
  "page_size": 20,
  "total": 100,
  "has_more": true
}
```

### 3.5 错误码建议

| code | 含义 |
| --- | --- |
| 0 | 成功 |
| 40001 | 参数校验失败 |
| 40101 | 未登录或 token 失效 |
| 40301 | 无权限 |
| 40401 | 资源不存在 |
| 40901 | 数据冲突 |
| 42901 | 频率限制 |
| 50001 | 系统异常 |
| 50011 | AI 服务异常 |
| 50021 | 对象存储异常 |

## 4. 模块 API 设计

## 4.1 Auth 模块

### POST `/auth/register`

创建账号。

请求体：

```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "StrongPass123",
  "display_name": "张三"
}
```

返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "user_id": 10001,
    "access_token": "jwt",
    "refresh_token": "refresh",
    "expires_in": 7200
  }
}
```

### POST `/auth/login`

支持用户名 / 邮箱登录。

请求体：

```json
{
  "account": "zhangsan@example.com",
  "password": "StrongPass123"
}
```

### POST `/auth/refresh`

刷新 access token。

### POST `/auth/logout`

注销当前设备 refresh token。

## 4.2 User 模块

### GET `/users/me`

返回当前登录用户基础信息、资料、统计数据。

### PUT `/users/me/profile`

更新个人资料，对应前端“编辑资料”页。

请求体：

```json
{
  "display_name": "张同学",
  "bio": "全栈开发 | 终身学习",
  "email": "zhang@example.com",
  "phone": "13800000000",
  "location": "北京市",
  "profession": "学生",
  "birthday": "2000-01-01",
  "learning_goal": "成为全栈工程师"
}
```

### PUT `/users/me/settings`

更新设置页数据。

请求体：

```json
{
  "theme": "light",
  "language": "zh-CN",
  "daily_reminder_enabled": true,
  "progress_notice_enabled": true,
  "badge_notice_enabled": false,
  "weekly_report_enabled": true,
  "two_factor_enabled": false,
  "profile_public": true,
  "learning_data_public": false
}
```

### GET `/users/{user_id}`

用户公开主页信息。

### POST `/users/{user_id}/follow`

关注用户。

### DELETE `/users/{user_id}/follow`

取消关注。

### GET `/users/{user_id}/works`

获取用户作品列表。

## 4.3 Storage 模块

### POST `/storage/presign-upload`

申请 MinIO 预签名上传地址。创作中心、头像上传、报告导出都走这套。

请求体：

```json
{
  "biz_type": "content_cover",
  "file_name": "cover.png",
  "file_size": 123456,
  "mime_type": "image/png"
}
```

返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "asset_id": 90001,
    "bucket_name": "linglearn",
    "object_key": "content/2026/04/cover.png",
    "upload_url": "https://minio-presigned-url",
    "headers": {
      "Content-Type": "image/png"
    }
  }
}
```

### POST `/storage/complete-upload`

客户端上传完成后回调，后端校验对象是否存在并激活 `media_assets`。

## 4.4 Content 模块

### GET `/feed/videos`

首页视频流。

查询参数：

- `cursor`
- `limit`
- `category_id`
- `recommend_type`：`for_you` / `following`

返回的单条视频结构建议包含：

```json
{
  "id": 20001,
  "title": "Python 入门：列表推导式",
  "summary": "超实用的 Python 技巧",
  "author": {
    "user_id": 10001,
    "display_name": "编程导师小李",
    "avatar_url": "https://..."
  },
  "category": {
    "id": 1,
    "name": "Python"
  },
  "cover_url": "https://...",
  "video_url": "https://...",
  "duration_seconds": 323,
  "bvid": null,
  "interaction": {
    "views_count": 1000,
    "likes_count": 200,
    "comments_count": 12,
    "favorites_count": 88,
    "shares_count": 9,
    "liked": false,
    "favorited": false
  },
  "has_quiz": true,
  "quiz_count": 2
}
```

### POST `/contents`

发布作品，对应创作中心。

请求体：

```json
{
  "title": "React Hooks 实战",
  "summary": "理解 useState",
  "category_id": 3,
  "cover_asset_id": 90001,
  "primary_media_asset_id": 90002,
  "content_type": "short_video",
  "hashtags": ["React", "前端"]
}
```

### GET `/contents/{content_id}`

获取内容详情。

### PUT `/contents/{content_id}`

编辑草稿 / 已发布作品。

### POST `/contents/{content_id}/like`

点赞。

### DELETE `/contents/{content_id}/like`

取消点赞。

### POST `/contents/{content_id}/favorite`

收藏。

### DELETE `/contents/{content_id}/favorite`

取消收藏。

### POST `/contents/{content_id}/share`

记录分享。

请求体：

```json
{
  "share_channel": "wechat"
}
```

### POST `/contents/{content_id}/watch-progress`

记录观看进度。

请求体：

```json
{
  "watch_seconds": 120,
  "watch_progress": 68.5,
  "last_position_seconds": 120,
  "completed": false
}
```

### GET `/users/me/favorites`

我的收藏视频列表。

### GET `/users/me/watch-history`

我的观看历史。

## 4.5 Comment 模块

### GET `/contents/{content_id}/comments`

分页获取评论树。

### POST `/contents/{content_id}/comments`

发表评论 / 回复。

请求体：

```json
{
  "content": "这个讲得很清楚",
  "parent_id": null,
  "reply_to_user_id": null
}
```

## 4.6 Discover / Search 模块

### GET `/discover/categories`

返回热门分类、视频数。

### GET `/discover/hot-topics`

返回热榜内容。

### GET `/discover/hot-tags`

返回热门标签。

### GET `/search/contents`

搜索课程、视频、老师、话题。

查询参数：

- `keyword`
- `category_id`
- `page`
- `page_size`

## 4.7 Quiz 模块

### GET `/contents/{content_id}/quizzes`

获取视频下互动题。

### POST `/quizzes/{quiz_id}/submit`

提交选项，返回正确答案和最新统计。

请求体：

```json
{
  "selected_option_id": 70001
}
```

返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "quiz_id": 60001,
    "selected_option_id": 70001,
    "is_correct": true,
    "total_votes": 1209,
    "options": [
      {
        "option_id": 70001,
        "option_text": "A",
        "vote_count": 700,
        "percent": 57.9,
        "is_correct": true
      }
    ]
  }
}
```

## 4.8 Course / Resource 模块

### GET `/courses`

资源中心课程列表 / 推荐课程。

### GET `/courses/{course_id}`

课程详情、课时列表。

### POST `/courses/{course_id}/enroll`

报名课程。

### GET `/users/me/learning/dashboard`

“我的学习”首页汇总：

- 学习时长
- 连续学习天数
- 收藏数量
- 完成目标数
- 正在学习课程
- 最近观看内容

### GET `/users/me/learning/courses`

我已报名 / 正在学习课程。

### GET `/resources`

资源中心文件列表。

查询参数：

- `resource_type`
- `category_id`
- `keyword`

### GET `/resources/recent`

最近文件。

## 4.9 Skill Profile 模块

### GET `/users/me/skill-profile/latest`

获取最近一次学生画像。

### POST `/users/me/skill-profile/generate`

触发 LangGraph 生成画像。输入源可以是观看记录、练习成绩、课程进度、互动行为。

返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "workflow_run_id": 81001,
    "status": "running"
  }
}
```

### GET `/users/me/skill-profile/history`

画像历史版本列表。

## 4.10 Learning Path 模块

### GET `/users/me/learning-paths/active`

获取当前激活学习路径。

### POST `/users/me/learning-paths/generate`

基于画像触发 LangGraph 生成个性化学习路径。

请求体：

```json
{
  "snapshot_id": 50001,
  "target_role": "fullstack_engineer"
}
```

### GET `/users/me/learning-paths/{user_path_id}`

获取路径节点、推荐理由、进度。

### PATCH `/users/me/learning-paths/{user_path_id}/nodes/{node_id}`

更新节点状态。

请求体：

```json
{
  "status": "completed",
  "progress_percent": 100
}
```

## 4.11 Practice 模块

### GET `/practice/banks`

题库列表。

### GET `/practice/banks/{bank_id}/questions`

开始练习前获取题目。

### POST `/practice/sessions`

创建练习会话。

请求体：

```json
{
  "bank_id": 30001,
  "session_type": "practice"
}
```

### POST `/practice/sessions/{session_id}/answers`

逐题保存答案。

### POST `/practice/sessions/{session_id}/submit`

提交试卷并返回成绩、错题解析。

### GET `/practice/sessions/{session_id}/result`

获取结果详情。

## 4.12 Assessment 模块

### GET `/users/me/assessments/latest`

返回当前评估卡片。

### GET `/users/me/assessments/trend`

返回周 / 月趋势图数据。

### POST `/users/me/assessments/generate`

重新生成评估快照。

## 4.13 Report 模块

### GET `/users/me/reports`

月份报告列表。

### GET `/users/me/reports/{report_month}`

获取某月学习报告。

### POST `/users/me/reports/{report_month}/generate`

调用 LangGraph 生成或重算月报。

### POST `/users/me/reports/{report_month}/export`

导出 PDF。

返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "asset_id": 99001,
    "download_url": "https://..."
  }
}
```

## 4.14 AI Chat 模块

### GET `/ai/chat/sessions`

会话列表。

### POST `/ai/chat/sessions`

新建会话。

### GET `/ai/chat/sessions/{session_id}/messages`

消息列表。

### POST `/ai/chat/sessions/{session_id}/messages`

发送消息。建议支持流式返回。

请求体：

```json
{
  "content": "如何学习数据结构？",
  "stream": true
}
```

### POST `/ai/workflows/student-profile`

触发画像工作流。

### POST `/ai/workflows/learning-path`

触发学习路径工作流。

### POST `/ai/workflows/monthly-report`

触发月报工作流。

## 4.15 Notification 模块

### GET `/users/me/notifications`

通知列表。

### PATCH `/users/me/notifications/{notification_id}/read`

单条已读。

### PATCH `/users/me/notifications/read-all`

全部已读。

## 5. 关键业务流程

## 5.1 创作中心发布流程

1. 前端调用 `/storage/presign-upload` 获取视频和封面上传地址
2. 客户端直传 MinIO
3. 调用 `/storage/complete-upload` 激活资源
4. 调用 `/contents` 创建作品
5. 审核通过后进入首页推荐池

## 5.2 首页视频观看流程

1. 拉取 `/feed/videos`
2. 用户观看时周期性调用 `/contents/{id}/watch-progress`
3. 用户点赞 / 收藏 / 评论后分别调用互动接口
4. 若视频有题目，打开 `/contents/{id}/quizzes`
5. 提交题目到 `/quizzes/{id}/submit`

## 5.3 学生画像与学习路径流程

1. 收集用户课程进度、做题成绩、观看行为
2. 触发 `/users/me/skill-profile/generate`
3. 画像落表 `user_skill_snapshots` 和 `user_skill_scores`
4. 触发 `/users/me/learning-paths/generate`
5. 路径结果落表 `user_learning_paths` 与 `user_learning_path_nodes`

## 5.4 学习报告流程

1. 定时聚合学习行为形成 `assessment_snapshots`
2. 月度任务调用 LangGraph 汇总 strengths / improvements / achievements
3. 数据落地 `monthly_reports`、`report_achievements`
4. 导出 PDF 时回写 `exported_pdf_asset_id`

## 6. 非功能要求

### 6.1 性能

- 视频流接口 P95 < 300ms
- 个人首页接口 P95 < 500ms
- AI 普通问答首包 < 3s，流式返回

### 6.2 幂等性

以下接口建议支持幂等：

- `/storage/complete-upload`
- `/contents/{id}/like`
- `/contents/{id}/favorite`
- `/practice/sessions/{id}/submit`
- `/users/me/reports/{month}/generate`

### 6.3 安全

- 密码使用 Argon2 或 bcrypt
- 上传文件做 MIME、大小、白名单校验
- 评论、标题、AI 输入输出做内容安全过滤
- 所有写接口记录 `audit_logs`

## 7. 后续建议

建议第一期优先落地模块顺序：

1. `auth`
2. `storage`
3. `content`
4. `social`
5. `learning`
6. `practice`
7. `assessment`
8. `report`
9. `ai_chat`

