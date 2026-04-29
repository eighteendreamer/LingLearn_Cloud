# LingLearn Cloud 后端开发 B 任务书

## 1. 角色定位

你负责本项目后端的“学习域”和“AI 域”，范围包括：

- 课程与资源中心
- 我的学习
- 在线练习
- 学习评估
- 学习路径
- 学习报告
- AI 学习助手
- 通知中心

你的工作会直接决定这个产品是否真正从“内容平台”升级成“学习平台”。

## 2. 你的模块边界

你负责以下模块：

- `course`
- `resource`
- `practice`
- `assessment`
- `learning_path`
- `report`
- `ai_chat`
- `notification`

你主要负责以下目录：

- `app/infra/ai/`
- `app/modules/course/`
- `app/modules/resource/`
- `app/modules/practice/`
- `app/modules/assessment/`
- `app/modules/learning_path/`
- `app/modules/report/`
- `app/modules/ai_chat/`
- `app/modules/notification/`

## 3. 你负责的数据表

### 3.1 课程与资源

- `resources`
- `courses`
- `course_lessons`
- `user_course_enrollments`
- `user_lesson_progress`

### 3.2 练习与评估

- `question_banks`
- `questions`
- `question_options`
- `practice_sessions`
- `practice_answers`
- `assessment_snapshots`

### 3.3 学习路径与画像

- `skill_dimensions`
- `user_skill_snapshots`
- `user_skill_scores`
- `learning_paths`
- `learning_path_nodes`
- `learning_path_node_dimension_links`
- `user_learning_paths`
- `user_learning_path_nodes`

### 3.4 报告、AI、通知

- `monthly_reports`
- `report_achievements`
- `ai_chat_sessions`
- `ai_chat_messages`
- `ai_workflow_runs`
- `notifications`

## 4. 你负责的接口

## 4.1 Course / Resource / Learning

- `GET /courses`
- `GET /courses/{course_id}`
- `POST /courses/{course_id}/enroll`
- `GET /users/me/learning/dashboard`
- `GET /users/me/learning/courses`
- `GET /resources`
- `GET /resources/recent`

## 4.2 Practice

- `GET /practice/banks`
- `GET /practice/banks/{bank_id}/questions`
- `POST /practice/sessions`
- `POST /practice/sessions/{session_id}/answers`
- `POST /practice/sessions/{session_id}/submit`
- `GET /practice/sessions/{session_id}/result`

## 4.3 Skill Profile / Learning Path

- `GET /users/me/skill-profile/latest`
- `POST /users/me/skill-profile/generate`
- `GET /users/me/skill-profile/history`
- `GET /users/me/learning-paths/active`
- `POST /users/me/learning-paths/generate`
- `GET /users/me/learning-paths/{user_path_id}`
- `PATCH /users/me/learning-paths/{user_path_id}/nodes/{node_id}`

## 4.4 Assessment / Report

- `GET /users/me/assessments/latest`
- `GET /users/me/assessments/trend`
- `POST /users/me/assessments/generate`
- `GET /users/me/reports`
- `GET /users/me/reports/{report_month}`
- `POST /users/me/reports/{report_month}/generate`
- `POST /users/me/reports/{report_month}/export`

## 4.5 AI Chat / Workflow / Notification

- `GET /ai/chat/sessions`
- `POST /ai/chat/sessions`
- `GET /ai/chat/sessions/{session_id}/messages`
- `POST /ai/chat/sessions/{session_id}/messages`
- `POST /ai/workflows/student-profile`
- `POST /ai/workflows/learning-path`
- `POST /ai/workflows/monthly-report`
- `GET /users/me/notifications`
- `PATCH /users/me/notifications/{notification_id}/read`
- `PATCH /users/me/notifications/read-all`

## 5. 你的开发前置条件

你的模块开发依赖后端 A 先提供以下能力：

- FastAPI 项目骨架
- 统一配置系统
- 数据库 Session
- JWT 鉴权
- 当前用户依赖注入
- 统一响应结构
- 公共异常处理

在 A 还没交付骨架前，你可以先完成：

- 模块设计
- Schema 设计
- Service 伪代码
- AI 工作流设计
- SQL 与接口的二次校对

## 6. 你负责的业务主线

你负责构建“学习闭环”，完整链路应当是：

1. 用户进入课程 / 资源中心
2. 用户报名课程并产生学习进度
3. 用户进入练习并提交结果
4. 系统生成评估快照
5. 系统生成学生画像
6. 系统生成学习路径
7. 系统生成月报
8. 用户通过 AI 助手获得学习建议

## 7. 分阶段任务

## 7.1 第一阶段

- `course`
- `resource`
- `learning dashboard`

完成标志：

- 能列课程、查课程详情、报名课程、展示学习概览

## 7.2 第二阶段

- `practice`
- `assessment`

完成标志：

- 能进入题库、创建练习会话、保存答案、提交并得到成绩

## 7.3 第三阶段

- `learning_path`
- `report`

完成标志：

- 能根据画像或评估生成学习路径和月报

## 7.4 第四阶段

- `ai_chat`
- `notification`
- `infra/ai`

完成标志：

- 能发起 AI 对话、记录消息、触发工作流、发站内通知

## 8. AI 相关职责

你负责 `LangGraph` 或等价 AI 工作流的业务编排，至少覆盖：

- 学生画像生成
- 学习路径生成
- 月报生成
- AI 学习助手对话

你要负责：

- 工作流输入输出 schema
- `ai_workflow_runs` 落库
- 失败重试与错误记录
- 模型调用封装
- 消息上下文组织

第一期可以先做“可运行版本”，不追求最复杂智能度。

## 9. 你和 A 的接口边界

### 9.1 你会依赖 A 的能力

- `users` 基础信息
- `media_assets` 文件信息
- 当前登录用户
- 通用分页
- 统一响应

### 9.2 你不要重复实现的能力

- JWT 登录鉴权
- MinIO 上传
- 视频 feed 推荐
- 点赞 / 收藏 / 评论主逻辑

### 9.3 你需要和 A 对齐的字段

- 用户信息返回结构
- 课程卡片作者信息是否复用 `user_profiles`
- 报告导出后的 `asset_id` 写法
- AI 工作流与通知是否需要审计日志

## 10. 你的测试任务

至少补这些测试：

- 课程报名成功 / 重复报名
- 题库拉取与练习提交流程
- 练习评分正确性
- 评估快照生成
- 学习路径节点状态更新
- 月报生成与导出
- AI Chat 消息写入
- 通知已读与全部已读

## 11. 你的交付标准

每个模块交付：

- `api.py`
- `schemas.py`
- `models.py`
- `repository.py`
- `service.py`
- 单元测试

AI 模块额外交付：

- LLM 客户端封装
- 工作流运行记录
- 错误日志
- 基础提示词模板或组装逻辑

## 12. 你当前最优开发顺序

建议按下面顺序推进：

1. `course`
2. `resource`
3. `practice`
4. `assessment`
5. `learning_path`
6. `report`
7. `ai_chat`
8. `notification`

原因：

- 先做课程和练习，后面的评估、画像、路径、报告才有数据来源
- AI 模块放在后面，可以直接消费前面沉淀的数据结构

## 13. 完成后的结果

你完成后，项目会形成完整学习闭环：

- 用户学什么
- 学了多少
- 做题情况如何
- 当前能力画像如何
- 接下来该学什么
- 月度表现如何
- AI 如何继续辅助

这是项目区别于普通短视频平台的核心价值。
