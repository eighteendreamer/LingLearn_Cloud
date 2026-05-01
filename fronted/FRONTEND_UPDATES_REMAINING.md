# 前端对接剩余更新

## 已完成 ✅
1. ✅ 更新类型定义 (`fronted/src/app/lib/types.ts`)
2. ✅ 更新 MyLearning 组件对接后端
3. ✅ 更新 OnlinePractice 组件对接后端

## 待完成 ⏭️

### 4. LearningAssessment.tsx
需要对接评估 API，获取真实的评估数据和趋势。

### 5. AIChat.tsx  
需要对接 AI Chat API，实现真实的对话功能。

### 6. RootLayout.tsx
需要对接通知 API，显示未读通知数量。

## 详细更新说明

由于代码较长，请按照以下步骤手动更新或使用提供的完整文件。

---

## 环境变量配置

在 `fronted/.env` 中添加：

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## API 端点映射

### 我的学习 (MyLearning)
- `GET /users/me/learning/dashboard` - 学习仪表盘
- `GET /users/me/learning/courses` - 我的课程列表

### 在线练习 (OnlinePractice)
- `GET /practice/question-banks` - 题库列表
- `GET /practice/question-banks/{bank_id}/questions` - 题目列表
- `POST /practice/sessions` - 创建练习会话
- `POST /practice/sessions/{session_id}/answers` - 提交答案
- `POST /practice/sessions/{session_id}/complete` - 完成练习

### 学习评估 (LearningAssessment)
- `GET /users/me/assessments/latest` - 最新评估
- `GET /users/me/assessments/trend?assessment_type=weekly` - 评估趋势
- `POST /users/me/assessments/generate` - 生成评估

### AI 对话 (AIChat)
- `GET /ai/chat/sessions` - 会话列表
- `POST /ai/chat/sessions` - 创建会话
- `GET /ai/chat/sessions/{session_id}/messages` - 消息列表
- `POST /ai/chat/sessions/{session_id}/messages` - 发送消息

### 通知 (RootLayout)
- `GET /users/me/notifications/unread-count` - 未读数量
- `GET /users/me/notifications?read_status=false` - 通知列表
- `PATCH /users/me/notifications/{notification_id}/read` - 标记已读

---

## 测试步骤

1. **启动后端服务**
```bash
cd Server
python main.py
```

2. **启动前端服务**
```bash
cd fronted
npm run dev
```

3. **测试流程**
- 登录系统
- 访问"我的学习"页面，查看学习数据
- 访问"在线练习"页面，完成练习
- 访问"学习评估"页面，查看评估报告
- 访问"AI对话"页面，与AI助手对话
- 查看通知铃铛，确认未读数量

---

## 注意事项

1. **认证**: 所有 API 请求需要携带 JWT Token
2. **错误处理**: 已在 `apiRequest` 中统一处理 401 错误
3. **加载状态**: 各组件已添加 loading 状态
4. **数据为空**: 已处理数据为空的情况
5. **字段名称**: 使用新的字段名称（如 `body`, `read_status`, `session_name` 等）

---

## 下一步

请继续更新以下文件：
- `fronted/src/app/components/LearningAssessment.tsx`
- `fronted/src/app/components/AIChat.tsx`
- `fronted/src/app/components/RootLayout.tsx`

参考已完成的 MyLearning 和 OnlinePractice 组件的实现方式。
