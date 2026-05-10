# LingLearn Cloud - 智慧学习平台

<div align="center">

一个现代化的智能学习平台，提供个性化内容推荐、AI 辅助学习和社交互动功能。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](#english) | [中文](#chinese)

</div>

---

## 📋 目录

- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [开发指南](#开发指南)
- [API 文档](#api-文档)
- [后台管理系统](#后台管理系统)
- [部署](#部署)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 🎯 项目简介

LingLearn Cloud 是一个全栈智慧学习平台，旨在通过 AI 技术和个性化推荐算法，为用户提供高效、有趣的学习体验。平台集成了视频内容管理、社交互动、学习路径规划、在线练习和智能评估等功能。

### 项目规模

- **后端模块**: 20+ 个业务模块
- **API 端点**: 100+ 个 RESTful 接口
- **数据库表**: 30+ 张表
- **前端页面**: 15+ 个功能页面
- **管理后台**: 完整的后台管理系统
- **代码量**: 15000+ 行代码

### 主要特点

- 🤖 **AI 智能助手** - 基于 LangGraph 的多智能体工作流，支持学习辅导、内容分析、路径规划
- 📊 **个性化推荐** - 多路召回 + 规则排序，支持冷启动和兴趣建模
- 🎥 **视频学习** - 支持视频上传、播放、进度跟踪和互动测验
- 📚 **学习路径** - AI 生成个性化学习路径，技能维度评估
- 💬 **社交互动** - 评论、点赞、收藏、分享和关注功能，交互同步机制
- 📈 **学习报告** - 月度学习报告生成，数据可视化分析
- 🎯 **在线练习** - 题库管理、练习会话、自动判分
- 🏆 **学习评估** - 能力评估、诊断报告、技能快照
- 🔐 **后台管理** - 完整的内容审核、用户管理、统计分析系统

---

## 🚀 核心功能

### 用户功能
- **用户认证** - 注册、登录、JWT 令牌刷新、登出
- **个人资料** - 用户信息管理、头像上传、个性化设置
- **社交关系** - 关注/取消关注用户、查看粉丝和关注列表
- **用户主页** - 展示个人作品、学习数据、社交关系

### 内容管理
- **内容创作** - 创建、编辑、发布学习内容（视频、文章）
- **内容浏览** - 视频流、分类浏览、搜索功能
- **内容互动** - 点赞、收藏、评论、分享
- **观看历史** - 记录学习进度和观看位置（8秒间隔上报）
- **内容测验** - 嵌入式测验题，即时反馈
- **交互同步** - 本地队列缓存 + 批量同步机制（10秒间隔）

### AI 功能
- **智能对话** - AI 聊天助手，提供学习指导和问答
- **内容分析** - 视频内容自动分析和摘要生成
- **学习路径生成** - AI 自动生成个性化学习路径
- **学生画像** - 基于学习行为的能力画像分析
- **月度报告** - AI 生成学习总结和建议
- **资源推荐** - 智能推荐学习资源
- **学习评估** - AI 驱动的能力评估和诊断

### 推荐系统
- **多路召回** - 热门视频、关注作者、相似标签、新内容
- **冷启动推荐** - 50% 热门 + 30% 新内容 + 20% 探索
- **兴趣建模** - 基于分类、标签、作者三维度的兴趣画像
- **排序策略** - 结合热度、时效性、去重、探索因子
- **行为采集** - 观看、点赞、收藏、评论、分享行为追踪
- **曝光日志** - 推荐效果追踪和优化

### 学习工具
- **学习路径** - 结构化课程和学习计划，节点进度跟踪
- **技能维度** - 多维度技能评估和成长追踪
- **在线练习** - 题库管理、练习会话、自动判分
- **学习评估** - 能力测评、诊断报告、技能快照
- **学习报告** - 学习时长、进度、成就统计、月度报告
- **课程管理** - 课程结构、课时管理、学习进度

### 资源中心
- **资源库** - 学习资料、文档、工具集合
- **资源访问** - 访问记录、权限管理
- **发现页** - 探索热门内容、分类、标签

### 后台管理
- **管理员认证** - 独立的管理员登录系统
- **用户管理** - 用户列表、详情查看、状态管理
- **内容审核** - 内容列表、审核状态、发布管理、删除
- **评论管理** - 评论列表、状态更新、批量操作
- **分类管理** - 分类 CRUD、排序、层级管理
- **标签管理** - 标签 CRUD、搜索、使用统计
- **统计分析** - 用户增长、内容统计、分类分析、数据可视化
- **角色权限** - 超级管理员、内容审核员、用户管理员、运营管理员
- **操作日志** - 审计追踪、操作记录

---

## 🏗️ 系统架构

### 后端架构（模块化单体）

采用"模块化单体"架构，清晰的模块边界和分层设计：

```
┌─────────────────────────────────────────────────────────┐
│                     API 层 (FastAPI)                     │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │  认证    │  用户    │  内容    │  推荐    │  AI    │ │
│  └──────────┴──────────┴──────────┴──────────┴────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Service 层 (业务逻辑)                   │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │ 事务边界 │ 业务编排 │ 规则判断 │ 数据聚合 │ 调用   │ │
│  └──────────┴──────────┴──────────┴──────────┴────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                Repository 层 (数据访问)                   │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │  CRUD    │  查询    │  聚合    │  事务    │  缓存  │ │
│  └──────────┴──────────┴──────────┴──────────┴────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                基础设施层 (Infra)                         │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │  MySQL   │  Redis   │  MinIO   │LangGraph │  日志  │ │
│  └──────────┴──────────┴──────────┴──────────┴────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 前端架构（React SPA）

```
┌─────────────────────────────────────────────────────────┐
│                   React 应用层                            │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │  路由    │  组件    │  状态    │  样式    │  工具  │ │
│  └──────────┴──────────┴──────────┴──────────┴────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   API 客户端层                            │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │ 请求封装 │ 认证管理 │ 错误处理 │ 响应解析 │ 拦截器 │ │
│  └──────────┴──────────┴──────────┴──────────┴────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↓
                    后端 API (FastAPI)
```

### 业务模块（20+ 个）

#### 核心模块
1. **auth** - 用户认证（注册、登录、令牌刷新）
2. **user** - 用户管理（资料、设置、关注关系）
3. **admin** - 后台管理（管理员、角色、权限、日志）
4. **content** - 内容管理（创作、浏览、元数据）
5. **social** - 社交互动（点赞、收藏、评论、分享）
6. **storage** - 对象存储（MinIO 文件管理）

#### 推荐与发现
7. **recommendation** - 推荐系统（召回、排序、兴趣建模）
8. **discover** - 发现页（热门分类、标签、话题）
9. **search** - 搜索功能（内容搜索、过滤、聚合）

#### 学习功能
10. **learning_path** - 学习路径（路径生成、节点管理、进度跟踪）
11. **practice** - 在线练习（题库、会话、判分）
12. **assessment** - 学习评估（能力分析、快照记录）
13. **report** - 学习报告（月度报告、数据导出）
14. **course** - 课程管理（课程结构、学习进度）
15. **quiz** - 内容测验（测验题、选项、答题记录）

#### AI 与智能
16. **ai_chat** - AI 对话（会话管理、消息流、上下文）
17. **notification** - 通知系统（站内通知、已读状态）

#### 其他
18. **resource** - 资源中心（文档、附件、链接）
19. **learning** - 学习数据（统计、历史、收藏）

### AI 智能体系统

LingLearn Cloud 采用基于 LangGraph 的多智能体协作架构，共有 **7 个专业智能体**：

#### 智能体列表

```
┌─────────────────────────────────────────────────────────────┐
│                    用户交互智能体 (总调度)                    │
│  - 意图识别  - 技能选择  - 工具规划  - 结果整合            │
└─────────────────────────────────────────────────────────────┘
                            ↓ 委托执行
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ 视频内容理解 │   │ 资源生成     │   │ 学习评测     │
│ 智能体       │   │ 智能体       │   │ 智能体       │
│              │   │              │   │              │
│ - 画面理解   │   │ - 目标分析   │   │ - 自动批改   │
│ - 语音提取   │   │ - 路径规划   │   │ - 掌握度判定 │
│ - 内容生成   │   │ - 动态优化   │   │ - 报告生成   │
└──────────────┘   └──────────────┘   └──────────────┘

        ↓                   ↓                   ↓
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ 智能答疑     │   │ 学习评估     │   │ 特征抽取     │
│ 智能体       │   │ 智能体       │   │ 智能体       │
│              │   │              │   │              │
│ - 对话答疑   │   │ - 效果诊断   │   │ - 对话分析   │
│ - 思维引导   │   │ - 学情画像   │   │ - 六维画像   │
│ - 错题讲解   │   │ - 优化建议   │   │ - 质量校验   │
└──────────────┘   └──────────────┘   └──────────────┘
```

#### 1. 用户交互智能体 (user_interaction)
**职责**: 作为 AI 助手统一入口，负责多轮对话交互和智能路由

**核心功能**:
- 理解用户意图，决定调用哪些业务智能体
- 整合多个智能体的结果，生成统一回复
- 管理对话上下文和会话状态
- 处理资源收藏等会话级动作

**调用方式**:
```typescript
// 前端：通过聊天会话自动路由
POST /api/v1/ai/chat/sessions/{session_id}/messages
{
  "content": "帮我分析这个视频并生成练习题",
  "context": { page_context: {...} }
}
```

#### 2. 视频内容理解智能体 (video_content)
**职责**: 提取视频画面与讲解语音，生成学习内容

**核心功能**:
- 视频画面理解（抽帧分析）
- 讲解语音提取（语音转文字）
- 知识点整理和总结
- 生成题库、笔记、报告

**调用方式**:
```python
# 后端：直接调用
manager = AgentManager()
result = await manager.run_video_content_agent(
    db_session,
    user_id=user_id,
    video_url="https://...",
    request_text="生成这个视频的练习题",
    video_title="Python 基础教程"
)

# 前端：通过 API
POST /api/v1/ai/workflows/video-content
{
  "video_url": "https://...",
  "request_text": "总结视频内容",
  "video_title": "...",
  "video_summary": "..."
}
```

#### 3. 资源生成智能体 (resource_generation)
**职责**: 学习目标分析、路径智能规划和动态调整优化

**核心功能**:
- 分析学习目标和当前水平
- 生成个性化学习路径
- 推荐学习资源
- 动态调整学习计划

**调用方式**:
```python
# 后端
result = await manager.run_resource_generation_agent(
    db_session,
    user_id=user_id,
    learning_goal="成为 Python 开发工程师",
    current_level="beginner",
    learning_history={...}
)

# 前端
POST /api/v1/ai/workflows/resource-generation
POST /api/v1/ai/workflows/learning-path  # 学习路径生成
```

#### 4. 学习评测智能体 (study_plan)
**职责**: 自动批改评分、掌握度判定和学习报告生成

**核心功能**:
- 自动批改练习和测验
- 判定知识点掌握程度
- 生成学习报告
- 提供改进建议

**调用方式**:
```python
# 后端
result = await manager.run_study_plan_agent(
    db_session,
    user_id=user_id,
    evaluation_type="practice_session",
    data={...}
)

# 前端
POST /api/v1/ai/workflows/study-plan
```

#### 5. 智能答疑智能体 (tutor_qa)
**职责**: 多轮对话答疑、思维引导辅导和错题讲解分析

**核心功能**:
- 概念讲解和代码辅导
- 启发式思维引导
- 错题分析和讲解
- 多轮对话答疑

**调用方式**:
```python
# 后端
result = await manager.run_tutor_qa_agent(
    db_session,
    user_id=user_id,
    question_content="什么是闭包？",
    user_answer="...",
    correct_answer="..."
)

# 前端
POST /api/v1/ai/workflows/tutor-qa
```

#### 6. 学习评估智能体 (learning_evaluation)
**职责**: 学习效果诊断、学情画像生成和迭代优化建议

**核心功能**:
- 阶段性学习效果诊断
- 生成学习画像和总结
- 月度报告生成
- 提出优化建议

**调用方式**:
```python
# 后端
result = await manager.run_learning_evaluation_agent(
    db_session,
    user_id=user_id,
    month="2024-05",
    learning_data={...}
)

# 前端
POST /api/v1/ai/workflows/learning-evaluation
POST /api/v1/ai/workflows/monthly-report  # 月度报告
```

#### 7. 特征抽取智能体 (feature_extraction)
**职责**: 对话内容分析、六维态内容生成和图像质量校验

**核心功能**:
- 从对话中提取学习特征
- 生成六维能力画像
- 质量评估和校验
- 为其他智能体提供数据支持

**调用方式**:
```python
# 后端（通常由其他功能调用，不直接暴露给用户）
result = await manager.run_feature_extraction(
    db_session,
    user_id=user_id,
    source_type="assessment",
    source_ref_id=snapshot_id,
    conversations=[...]
)

# 前端
POST /api/v1/ai/workflows/student-profile  # 学生画像生成
```

#### 智能体协作流程

**示例：用户请求"帮我分析当前视频并生成练习题"**

```
1. 用户交互智能体接收请求
   ↓
2. 意图识别：视频分析 + 练习题生成
   ↓
3. 技能选择：[video_content, resource_generation]
   ↓
4. 委托执行：
   4.1 调用视频内容理解智能体
       - 提取视频画面和语音
       - 分析知识点
   4.2 调用资源生成智能体
       - 基于视频内容生成练习题
   ↓
5. 结果整合：
   "我已经分析了视频内容，主要讲解了...
    为你生成了以下练习题：
    1. ...
    2. ..."
   ↓
6. 返回用户
```

#### 智能体管理

**位置**: `Server/app/infra/ai/`

```
ai/
├── agent_manager.py       # 智能体管理器（统一调度）
├── agent_skills.py        # 智能体定义和配置
├── langgraph_runtime.py   # LangGraph 运行时
├── llm_client.py          # LLM 客户端
├── graphs/                # 智能体实现
│   ├── six_agents.py      # 6 个主要智能体
│   └── video_content_graph.py  # 视频内容智能体
└── ...
```

#### 获取智能体列表

```bash
# API 调用
GET /api/v1/ai/agents

# 返回
{
  "code": 0,
  "data": [
    {
      "code": "user_interaction",
      "name": "用户交互智能体",
      "summary": "负责多轮对话交互、流式输出组织和资源收藏管理",
      "responsibilities": ["多轮对话交互", "流式输出展示", "资源收藏管理"],
      "supported_tools": [...],
      "chat_enabled": true,
      "standalone_enabled": true
    },
    // ... 其他智能体
  ]
}
```

#### 工作流记录

所有智能体执行都会记录在数据库：

```sql
-- ai_workflow_runs 表
CREATE TABLE ai_workflow_runs (
    id INT PRIMARY KEY,
    workflow_type VARCHAR(50),  -- 智能体类型
    user_id INT,
    biz_type VARCHAR(50),
    biz_id INT,
    input_json JSON,            -- 输入参数
    output_json JSON,           -- 输出结果
    status VARCHAR(20),         -- init, running, completed, failed
    started_at DATETIME,
    completed_at DATETIME
);
```

---

## 🛠 技术栈

### 后端 (Server)
- **框架**: FastAPI 0.115+ (高性能异步 Web 框架)
- **语言**: Python 3.10+
- **数据库**: MySQL 5.7+ (通过 aiomysql 异步驱动)
- **ORM**: SQLAlchemy 2.0+ (异步 ORM)
- **缓存**: Redis 5.2+ (可选，用于会话和缓存)
- **对象存储**: MinIO 7.2+ (S3 兼容对象存储)
- **认证**: JWT (PyJWT 2.8+)
- **数据库迁移**: Alembic 1.13+
- **AI 集成**: 
  - LangGraph (AI 工作流编排)
  - 支持智谱 AI、DeepSeek、Qwen 等大语言模型
  - 多智能体协作框架
- **异步运行时**: Uvicorn (ASGI 服务器)
- **数据验证**: Pydantic 2.0+
- **HTTP 客户端**: httpx (异步 HTTP 客户端)

### 前端 (fronted)
- **框架**: React 18.3.1 (函数式组件 + Hooks)
- **路由**: React Router 7.13.0
- **构建工具**: Vite 6.3.5 (快速构建和热更新)
- **语言**: TypeScript 5.x
- **样式**: 
  - Tailwind CSS 4.1.12 (原子化 CSS)
  - PostCSS (CSS 处理)
- **UI 组件**: 
  - Radix UI (无障碍组件库)
  - Material-UI 7.3.5
  - Shadcn UI 组件集合
- **状态管理**: React Hooks (useState, useEffect, useContext)
- **表单**: React Hook Form 7.55.0 (高性能表单库)
- **图表**: Recharts 2.15.2 (数据可视化)
- **动画**: Motion 12.23.24 (流畅动画)
- **图标**: Lucide React, MUI Icons
- **拖拽**: React DnD 16.0.1
- **通知**: Sonner 2.0.3 (优雅的通知提示)
- **其他**: 
  - Canvas Confetti (庆祝动画)
  - React Markdown (Markdown 渲染)
  - date-fns (日期处理)

### 开发工具
- **代码规范**: 
  - 后端: Ruff (Python linter & formatter)
  - 前端: ESLint + Prettier
- **版本控制**: Git
- **API 文档**: OpenAPI 3.0 (Swagger UI + ReDoc)
- **测试**: pytest (后端单元测试和集成测试)

---

## 📁 项目结构

```
LingLearn_Cloud/
├── Server/                          # 后端服务
│   ├── app/
│   │   ├── api/                     # API 路由和依赖
│   │   │   ├── routes/              # 路由定义
│   │   │   │   └── health.py        # 健康检查
│   │   │   ├── deps.py              # 依赖注入（数据库会话、当前用户）
│   │   │   └── router.py            # 主路由器（聚合所有模块路由）
│   │   ├── common/                  # 公共工具
│   │   │   ├── constants.py         # 常量定义
│   │   │   ├── pagination.py        # 分页工具
│   │   │   └── utils.py             # 工具函数
│   │   ├── core/                    # 核心配置
│   │   │   ├── config.py            # 应用配置（环境变量加载）
│   │   │   ├── enums.py             # 枚举类型
│   │   │   ├── exceptions.py        # 异常处理
│   │   │   ├── logging.py           # 日志配置
│   │   │   ├── response.py          # 统一响应格式
│   │   │   └── security.py          # 安全工具（JWT、密码哈希）
│   │   ├── db/                      # 数据库
│   │   │   ├── migrations/          # Alembic 迁移脚本
│   │   │   ├── base.py              # 数据库基类
│   │   │   ├── mixins.py            # 模型混入（时间戳、软删除）
│   │   │   ├── models.py            # 模型导出（聚合所有模型）
│   │   │   └── session.py           # 数据库会话管理
│   │   ├── infra/                   # 基础设施
│   │   │   ├── ai/                  # AI 集成
│   │   │   │   ├── agent_manager.py # AI 智能体管理器
│   │   │   │   ├── agent_skills.py  # 智能体技能定义
│   │   │   │   ├── langgraph_runtime.py # LangGraph 运行时
│   │   │   │   └── llm_client.py    # LLM 客户端
│   │   │   ├── cache/               # 缓存
│   │   │   │   └── redis_client.py  # Redis 客户端
│   │   │   ├── storage/             # 对象存储
│   │   │   │   ├── minio_client.py  # MinIO 客户端
│   │   │   │   └── service.py       # 存储服务
│   │   │   └── tasks/               # 后台任务
│   │   ├── modules/                 # 业务模块（20+ 个）
│   │   │   ├── admin/               # 后台管理
│   │   │   │   ├── api.py           # 管理员 API
│   │   │   │   ├── models.py        # 管理员模型
│   │   │   │   ├── schemas.py       # 请求/响应模式
│   │   │   │   ├── service.py       # 业务逻辑
│   │   │   │   └── deps.py          # 管理员认证依赖
│   │   │   ├── ai_chat/             # AI 聊天
│   │   │   │   ├── api.py           # AI 对话 API
│   │   │   │   ├── models.py        # 会话和消息模型
│   │   │   │   ├── schemas.py       # 请求/响应模式
│   │   │   │   ├── service.py       # 对话服务
│   │   │   │   └── workflow_models.py # 工作流模型
│   │   │   ├── assessment/          # 学习评估
│   │   │   ├── auth/                # 用户认证
│   │   │   │   ├── api.py           # 认证 API
│   │   │   │   ├── models.py        # 用户和令牌模型
│   │   │   │   ├── schemas.py       # 请求/响应模式
│   │   │   │   └── service.py       # 认证服务
│   │   │   ├── content/             # 内容管理
│   │   │   │   ├── api.py           # 内容 API
│   │   │   │   ├── models.py        # 内容模型
│   │   │   │   ├── schemas.py       # 请求/响应模式
│   │   │   │   ├── service.py       # 内容服务
│   │   │   │   └── repository.py    # 数据访问层
│   │   │   ├── course/              # 课程管理
│   │   │   ├── discover/            # 发现页
│   │   │   ├── learning/            # 学习数据
│   │   │   ├── learning_path/       # 学习路径
│   │   │   ├── notification/        # 通知
│   │   │   ├── practice/            # 在线练习
│   │   │   ├── quiz/                # 内容测验
│   │   │   ├── recommendation/      # 推荐算法
│   │   │   ├── report/              # 学习报告
│   │   │   ├── resource/            # 资源中心
│   │   │   ├── search/              # 搜索功能
│   │   │   ├── social/              # 社交功能（已整合到 content）
│   │   │   ├── storage/             # 存储服务
│   │   │   └── user/                # 用户管理
│   │   │       ├── api.py           # 用户 API
│   │   │       ├── models.py        # 用户资料模型
│   │   │       ├── schemas.py       # 请求/响应模式
│   │   │       └── service.py       # 用户服务
│   │   ├── tests/                   # 测试
│   │   │   ├── e2e/                 # 端到端测试
│   │   │   ├── integration/         # 集成测试
│   │   │   └── unit/                # 单元测试
│   │   └── main.py                  # 应用入口
│   ├── docs/                        # 文档
│   │   ├── backend_development_spec.md # 后端开发规范
│   │   └── ...
│   ├── scripts/                     # 脚本
│   │   ├── init_admin.py            # 初始化管理员
│   │   ├── fix_admin_password.py    # 修复管理员密码
│   │   ├── generate_password_hash.py # 生成密码哈希
│   │   └── batch_upload_videos.py   # 批量上传视频
│   ├── sql/                         # SQL 脚本
│   │   └── init_admin_tables.sql    # 管理员表初始化
│   ├── .env.example                 # 环境变量示例
│   ├── pyproject.toml               # Python 项目配置
│   ├── alembic.ini                  # Alembic 配置
│   └── README.md
│
├── fronted/                         # 前端应用
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/          # React 组件
│   │   │   │   ├── admin/           # 后台管理组件
│   │   │   │   │   ├── AdminLayout.tsx      # 管理后台布局
│   │   │   │   │   ├── AdminLogin.tsx       # 管理员登录
│   │   │   │   │   ├── Dashboard.tsx        # 仪表盘
│   │   │   │   │   ├── UserManagement.tsx   # 用户管理
│   │   │   │   │   ├── ContentManagement.tsx # 内容管理
│   │   │   │   │   ├── CommentManagement.tsx # 评论管理
│   │   │   │   │   ├── CategoryManagement.tsx # 分类管理
│   │   │   │   │   ├── TagManagement.tsx    # 标签管理
│   │   │   │   │   ├── Statistics.tsx       # 统计分析
│   │   │   │   │   └── AdminSettings.tsx    # 管理设置
│   │   │   │   ├── ui/              # UI 基础组件（Shadcn UI）
│   │   │   │   │   ├── button.tsx
│   │   │   │   │   ├── card.tsx
│   │   │   │   │   ├── dialog.tsx
│   │   │   │   │   ├── input.tsx
│   │   │   │   │   ├── table.tsx
│   │   │   │   │   └── ...
│   │   │   │   ├── AIChat.tsx       # AI 聊天
│   │   │   │   ├── Auth.tsx         # 认证页面
│   │   │   │   ├── Create.tsx       # 内容创作
│   │   │   │   ├── Discover.tsx     # 发现页
│   │   │   │   ├── EditProfile.tsx  # 编辑资料
│   │   │   │   ├── Home.tsx         # 首页
│   │   │   │   ├── LearningAssessment.tsx # 学习评估
│   │   │   │   ├── LearningPath.tsx # 学习路径
│   │   │   │   ├── LearningReport.tsx # 学习报告
│   │   │   │   ├── MyLearning.tsx   # 我的学习
│   │   │   │   ├── OnlinePractice.tsx # 在线练习
│   │   │   │   ├── Profile.tsx      # 个人主页
│   │   │   │   ├── ResourceCenter.tsx # 资源中心
│   │   │   │   ├── Settings.tsx     # 设置
│   │   │   │   ├── StudentProfile.tsx # 学生画像
│   │   │   │   ├── VideoFeed.tsx    # 视频流
│   │   │   │   ├── VideoFeedLayout.tsx # 视频流布局
│   │   │   │   └── ...
│   │   │   ├── lib/                 # 工具库
│   │   │   │   ├── api.ts           # API 客户端
│   │   │   │   ├── account.ts       # 账户管理
│   │   │   │   ├── ai-chat.ts       # AI 聊天工具
│   │   │   │   ├── assistant-context.ts # 助手上下文
│   │   │   │   ├── content.ts       # 内容管理
│   │   │   │   ├── interaction-sync.ts # 交互同步
│   │   │   │   ├── learning-api.ts  # 学习 API
│   │   │   │   ├── runtime-i18n.ts  # 国际化
│   │   │   │   ├── session.ts       # 会话管理
│   │   │   │   ├── storage.ts       # 存储工具
│   │   │   │   ├── types.ts         # 类型定义
│   │   │   │   └── user-preferences.ts # 用户偏好
│   │   │   ├── App.tsx              # 应用根组件
│   │   │   ├── page-context.tsx     # 页面上下文
│   │   │   └── routes.ts            # 路由配置
│   │   ├── imports/                 # 静态资源
│   │   ├── styles/                  # 样式文件
│   │   │   ├── fonts.css
│   │   │   ├── index.css
│   │   │   ├── tailwind.css
│   │   │   └── theme.css
│   │   ├── main.tsx                 # 应用入口
│   │   └── vite-env.d.ts
│   ├── guidelines/                  # 开发指南
│   │   └── Guidelines.md
│   ├── dist/                        # 构建输出
│   ├── .env.example                 # 环境变量示例
│   ├── index.html                   # HTML 模板
│   ├── package.json                 # 依赖配置
│   ├── tsconfig.json                # TypeScript 配置
│   ├── vite.config.ts               # Vite 配置
│   ├── tailwind.config.ts           # Tailwind 配置
│   ├── postcss.config.mjs           # PostCSS 配置
│   ├── ATTRIBUTIONS.md              # 开源许可声明
│   └── README.md
│
├── .gitignore                       # Git 忽略配置
├── README.md                        # 项目说明文档
├── ADMIN_SYSTEM_README.md           # 管理系统说明
├── ADMIN_QUICK_START.md             # 管理系统快速开始
└── ADMIN_DEPLOYMENT_CHECKLIST.md    # 管理系统部署清单
```

---

## 🚀 快速开始

### 前置要求

- **Python**: 3.10 或更高版本
- **Node.js**: 18.x 或更高版本
- **MySQL**: 5.7 或更高版本
- **Redis**: 5.2 或更高版本 (可选)
- **MinIO**: 7.2 或更高版本 (对象存储)

### 后端启动

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd LingLearn_Cloud/Server
   ```

2. **安装依赖**
   ```bash
   pip install -e .
   # 或安装开发依赖
   pip install -e ".[dev]"
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置数据库、Redis、MinIO 等
   ```

4. **初始化数据库**
   ```bash
   # 运行数据库迁移
   alembic upgrade head
   ```

5. **启动服务**
   ```bash
   # 开发模式
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8003
   
   # 或使用 Python 直接运行
   python -m app.main
   ```

6. **访问 API 文档**
   - Swagger UI: http://127.0.0.1:8003/docs
   - ReDoc: http://127.0.0.1:8003/redoc

### 前端启动

1. **进入前端目录**
   ```bash
   cd fronted
   ```

2. **安装依赖**
   ```bash
   npm install
   # 或使用 pnpm
   pnpm install
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件
   ```

4. **启动开发服务器**
   ```bash
   npm run dev
   ```

5. **访问应用**
   - 前端应用: http://localhost:5173 (默认 Vite 端口)

---

## ⚙️ 环境配置

### 后端环境变量 (.env)

```env
# ============ 应用配置 ============
APP_NAME=LingLearn Cloud API
APP_ENV=dev                          # dev, staging, production
DEBUG=true
API_V1_PREFIX=/api/v1
HOST=127.0.0.1
PORT=8003

# ============ 日志和 CORS ============
LOG_LEVEL=INFO                       # DEBUG, INFO, WARNING, ERROR, CRITICAL
CORS_ORIGINS=*                       # 生产环境请设置具体域名，如: http://localhost:5173,https://your-domain.com

# ============ 数据库配置 ============
DATABASE_URL=mysql+aiomysql://root:password@127.0.0.1:3306/linglearn_cloud
DB_ECHO=false                        # 是否打印 SQL 语句
DB_POOL_RECYCLE=3600                 # 连接池回收时间（秒）

# ============ Redis 配置（可选）============
REDIS_ENABLED=false                  # 是否启用 Redis
REDIS_URL=redis://127.0.0.1:6379/0  # Redis 连接 URL
# 如果有密码: redis://:password@127.0.0.1:6379/0
REDIS_PREFIX=linglearn               # Redis 键前缀
REDIS_DEFAULT_TTL_SECONDS=300        # 默认过期时间（秒）

# ============ JWT 认证 ============
JWT_SECRET_KEY=your-secret-key-change-in-production  # ⚠️ 生产环境必须修改
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120      # 访问令牌过期时间（分钟）
REFRESH_TOKEN_EXPIRE_DAYS=30         # 刷新令牌过期时间（天）

# ============ 大语言模型配置 ============
# 主 LLM（用于对话、推理）
LLM_API_KEY=your-api-key-here
LLM_MODEL=deepseek-ai/DeepSeek-V4-Flash
LLM_BASE_URL=https://api-inference.modelscope.cn/v1
LLM_TIMEOUT_SECONDS=60

# 视频音频分析（可选）
VIDEO_AUDIO_API_KEY=your-dashscope-api-key
VIDEO_AUDIO_MODEL=qwen3-omni-30b-a3b-captioner
VIDEO_AUDIO_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
VIDEO_AUDIO_TIMEOUT_SECONDS=120

# 视频视觉分析（可选）
VIDEO_VISION_API_KEY=your-api-key
VIDEO_VISION_MODEL=Qwen/Qwen3.5-122B-A10B
VIDEO_VISION_BASE_URL=https://api-inference.modelscope.cn/v1
VIDEO_VISION_TIMEOUT_SECONDS=120

# 视频提取配置
VIDEO_EXTRACT_MAX_FRAMES=6           # 最大提取帧数
VIDEO_EXTRACT_INTERVAL_SECONDS=20    # 提取间隔（秒）
VIDEO_EXTRACT_AUDIO_FORMAT=mp3       # 音频格式

# ============ MinIO 对象存储 ============
MINIO_ENDPOINT=127.0.0.1:9000        # MinIO 服务地址
MINIO_ACCESS_KEY=minioadmin          # 访问密钥
MINIO_SECRET_KEY=minioadmin          # 密钥
MINIO_BUCKET_NAME=linglearn-cloud    # 存储桶名称
MINIO_SECURE=false                   # 是否使用 HTTPS
MINIO_PUBLIC_BASE_URL=               # 公开访问 URL（可选）
MINIO_PRESIGN_EXPIRE_SECONDS=3600    # 预签名 URL 过期时间（秒）
MINIO_AUTO_CREATE_BUCKET=true        # 自动创建存储桶

# ============ API 文档配置 ============
DOCS_URL=/docs                       # Swagger UI 路径
REDOC_URL=/redoc                     # ReDoc 路径
OPENAPI_URL=/openapi.json            # OpenAPI JSON 路径
```

### 前端环境变量 (.env)

```env
# ============ API 配置 ============
VITE_API_BASE_URL=/api/v1            # API 基础路径
VITE_API_PROXY_TARGET=http://127.0.0.1:8003  # 开发代理目标（仅开发环境）
```

### 环境变量说明

#### 必需配置
- `DATABASE_URL` - 数据库连接字符串
- `JWT_SECRET_KEY` - JWT 密钥（生产环境必须修改）
- `MINIO_ENDPOINT` - MinIO 服务地址
- `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` - MinIO 凭证

#### 可选配置
- `REDIS_ENABLED` - 是否启用 Redis 缓存
- `LLM_API_KEY` - AI 功能需要配置
- `VIDEO_AUDIO_API_KEY` / `VIDEO_VISION_API_KEY` - 视频分析功能需要配置

#### 生产环境注意事项
1. 修改 `JWT_SECRET_KEY` 为强密码
2. 设置具体的 `CORS_ORIGINS`
3. 启用 `REDIS_ENABLED=true`
4. 设置 `MINIO_SECURE=true` 并配置 HTTPS
5. 设置 `DEBUG=false`
6. 设置 `DB_ECHO=false`
7. 配置 `MINIO_PUBLIC_BASE_URL` 为 CDN 地址

---

## 💻 开发指南

### 后端开发

#### 模块结构
每个业务模块遵循以下结构：
```
module_name/
├── __init__.py
├── api.py          # API 路由
├── models.py       # 数据模型
├── schemas.py      # Pydantic 模式
├── service.py      # 业务逻辑
└── repository.py   # 数据访问层 (可选)
```

#### 添加新模块
1. 在 `app/modules/` 下创建模块目录
2. 定义数据模型 (models.py)
3. 定义 API 模式 (schemas.py)
4. 实现业务逻辑 (service.py)
5. 定义 API 路由 (api.py)
6. 在 `app/api/router.py` 中注册路由
7. 在 `app/db/models.py` 中导出模型

#### 数据库迁移
```bash
# 创建新迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

#### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest app/tests/unit/test_auth.py

# 查看覆盖率
pytest --cov=app
```

#### 代码规范
```bash
# 使用 Ruff 进行代码检查和格式化
ruff check .
ruff format .
```

### 前端开发

#### 组件开发
- 使用函数式组件和 Hooks
- 遵循 Shadcn UI 设计系统
- 保持组件小而专注
- 使用 TypeScript 类型定义

#### API 调用
```typescript
import { apiRequest } from '@/app/lib/api';

// GET 请求
const data = await apiRequest<ResponseType>('/endpoint');

// POST 请求
const result = await apiRequest<ResponseType>('/endpoint', {
  method: 'POST',
  body: JSON.stringify(payload),
});
```

#### 路由添加
在 `src/app/routes.ts` 中添加新路由：
```typescript
{
  path: "/new-page",
  Component: NewPageComponent,
}
```

#### 构建生产版本
```bash
npm run build
# 输出到 dist/ 目录
```

---

## 📚 API 文档

### 主要 API 端点

#### 认证 (Auth)
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新令牌
- `POST /api/v1/auth/logout` - 用户登出

#### 用户 (Users)
- `GET /api/v1/users/me` - 获取当前用户信息
- `PUT /api/v1/users/me/profile` - 更新个人资料
- `PUT /api/v1/users/me/settings` - 更新用户设置
- `GET /api/v1/users/{user_id}` - 获取用户公开信息
- `POST /api/v1/users/{user_id}/follow` - 关注用户
- `DELETE /api/v1/users/{user_id}/follow` - 取消关注
- `GET /api/v1/users/{user_id}/followers` - 获取粉丝列表
- `GET /api/v1/users/{user_id}/following` - 获取关注列表
- `GET /api/v1/users/{user_id}/works` - 获取用户作品

#### 内容 (Contents)
- `GET /api/v1/feed/videos` - 获取视频流（推荐算法）
- `POST /api/v1/contents` - 创建内容
- `GET /api/v1/contents/{content_id}` - 获取内容详情
- `PUT /api/v1/contents/{content_id}` - 更新内容
- `DELETE /api/v1/contents/{content_id}` - 删除内容
- `POST /api/v1/contents/{content_id}/like` - 点赞
- `DELETE /api/v1/contents/{content_id}/like` - 取消点赞
- `POST /api/v1/contents/{content_id}/favorite` - 收藏
- `DELETE /api/v1/contents/{content_id}/favorite` - 取消收藏
- `POST /api/v1/contents/{content_id}/share` - 分享
- `GET /api/v1/contents/{content_id}/comments` - 获取评论
- `POST /api/v1/contents/{content_id}/comments` - 发表评论
- `POST /api/v1/contents/{content_id}/watch-progress` - 上报观看进度

#### AI 聊天 (AI Chat)
- `GET /api/v1/ai/agents` - 获取可用 AI 智能体列表
- `GET /api/v1/ai/chat/sessions` - 获取对话会话列表
- `POST /api/v1/ai/chat/sessions` - 创建对话会话
- `GET /api/v1/ai/chat/sessions/{session_id}/messages` - 获取会话消息
- `POST /api/v1/ai/chat/sessions/{session_id}/messages` - 发送消息（支持流式响应）
- `POST /api/v1/ai/workflows/student-profile` - 生成学生画像
- `POST /api/v1/ai/workflows/learning-path` - 生成学习路径
- `POST /api/v1/ai/workflows/monthly-report` - 生成月度报告
- `POST /api/v1/ai/workflows/video-content` - 分析视频内容

#### 学习路径 (Learning Path)
- `GET /api/v1/learning-paths` - 获取学习路径列表
- `POST /api/v1/learning-paths/generate` - AI 生成学习路径
- `GET /api/v1/learning-paths/{path_id}` - 获取路径详情
- `POST /api/v1/learning-paths/{path_id}/enroll` - 加入学习路径
- `PUT /api/v1/learning-paths/{path_id}/nodes/{node_id}/progress` - 更新节点进度

#### 在线练习 (Practice)
- `GET /api/v1/practice/banks` - 获取题库列表
- `POST /api/v1/practice/sessions` - 创建练习会话
- `GET /api/v1/practice/sessions/{session_id}` - 获取会话详情
- `POST /api/v1/practice/sessions/{session_id}/answers` - 提交答案
- `POST /api/v1/practice/sessions/{session_id}/complete` - 完成练习

#### 学习报告 (Report)
- `GET /api/v1/users/me/reports` - 获取学习报告列表
- `GET /api/v1/users/me/reports/{month}` - 获取指定月份报告
- `POST /api/v1/users/me/reports/{month}/generate` - 生成月度报告

#### 存储 (Storage)
- `POST /api/v1/storage/upload` - 上传文件
- `GET /api/v1/storage/{asset_id}` - 获取文件信息
- `GET /api/v1/storage/{asset_id}/download-url` - 获取下载链接

#### 发现 (Discover)
- `GET /api/v1/discover` - 获取发现页内容
- `GET /api/v1/discover/categories` - 获取热门分类
- `GET /api/v1/discover/tags` - 获取热门标签

#### 搜索 (Search)
- `GET /api/v1/search` - 搜索内容
- `GET /api/v1/search/suggestions` - 获取搜索建议

#### 课程 (Courses)
- `GET /api/v1/courses` - 获取课程列表
- `GET /api/v1/courses/{course_id}` - 获取课程详情
- `POST /api/v1/courses/{course_id}/enroll` - 加入课程
- `GET /api/v1/courses/{course_id}/lessons` - 获取课时列表
- `PUT /api/v1/courses/{course_id}/lessons/{lesson_id}/progress` - 更新课时进度

#### 资源中心 (Resources)
- `GET /api/v1/resources` - 获取资源列表
- `GET /api/v1/resources/{resource_id}` - 获取资源详情
- `POST /api/v1/resources/{resource_id}/access` - 记录资源访问

#### 通知 (Notifications)
- `GET /api/v1/notifications` - 获取通知列表
- `PUT /api/v1/notifications/{notification_id}/read` - 标记已读
- `PUT /api/v1/notifications/read-all` - 全部标记已读

#### 健康检查 (Health)
- `GET /api/v1/health` - 服务健康检查

### 后台管理 API

#### 管理员认证
- `POST /api/v1/admin/auth/login` - 管理员登录
- `POST /api/v1/admin/auth/refresh` - 刷新管理员令牌
- `POST /api/v1/admin/auth/logout` - 管理员登出

#### 用户管理
- `GET /api/v1/admin/management/users` - 获取用户列表
- `GET /api/v1/admin/management/users/{user_id}` - 获取用户详情
- `PUT /api/v1/admin/management/users/{user_id}/status` - 更新用户状态

#### 内容管理
- `GET /api/v1/admin/management/contents` - 获取内容列表
- `GET /api/v1/admin/management/contents/{content_id}` - 获取内容详情
- `PUT /api/v1/admin/management/contents/{content_id}/audit` - 审核内容
- `DELETE /api/v1/admin/management/contents/{content_id}` - 删除内容

#### 评论管理
- `GET /api/v1/admin/management/comments` - 获取评论列表
- `PUT /api/v1/admin/management/comments/{comment_id}/status` - 更新评论状态
- `DELETE /api/v1/admin/management/comments/{comment_id}` - 删除评论

#### 分类管理
- `GET /api/v1/admin/management/categories` - 获取分类列表
- `POST /api/v1/admin/management/categories` - 创建分类
- `PUT /api/v1/admin/management/categories/{category_id}` - 更新分类
- `DELETE /api/v1/admin/management/categories/{category_id}` - 删除分类

#### 标签管理
- `GET /api/v1/admin/management/tags` - 获取标签列表
- `POST /api/v1/admin/management/tags` - 创建标签
- `PUT /api/v1/admin/management/tags/{tag_id}` - 更新标签
- `DELETE /api/v1/admin/management/tags/{tag_id}` - 删除标签

#### 统计分析
- `GET /api/v1/admin/statistics/dashboard` - 获取仪表盘统计
- `GET /api/v1/admin/statistics/user-growth` - 获取用户增长数据
- `GET /api/v1/admin/statistics/content` - 获取内容统计数据
- `GET /api/v1/admin/statistics/category` - 获取分类统计数据

#### 管理员管理
- `GET /api/v1/admin/users` - 获取管理员列表
- `POST /api/v1/admin/users` - 创建管理员
- `GET /api/v1/admin/roles` - 获取角色列表
- `GET /api/v1/admin/logs` - 获取操作日志

### API 响应格式

所有 API 响应遵循统一格式：

```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "request_id": "uuid"
}
```

- `code`: 0 表示成功，非 0 表示错误
- `message`: 响应消息
- `data`: 响应数据
- `request_id`: 请求追踪 ID

### 认证

#### 用户认证
API 使用 JWT Bearer Token 认证：

```
Authorization: Bearer <access_token>
```

#### 管理员认证
管理员 API 使用独立的 JWT Token：

```
Authorization: Bearer <admin_access_token>
```

### 分页

支持分页的接口使用以下参数：

- `page`: 页码（从 1 开始）
- `page_size`: 每页数量（默认 20，最大 100）

响应格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

---

## 🔐 后台管理系统

### 功能概览

LingLearn Cloud 提供完整的后台管理系统，用于内容审核、用户管理和数据分析。

### 管理员角色

1. **超级管理员** - 拥有所有权限
2. **内容审核员** - 内容审核、评论管理
3. **用户管理员** - 用户管理、状态控制
4. **运营管理员** - 数据统计、报表查看

### 管理功能

#### 1. 仪表盘
- 实时统计数据（用户数、内容数、互动数）
- 今日新增数据
- 待处理任务提醒
- 快速操作入口

#### 2. 用户管理
- 用户列表（搜索、筛选、分页）
- 用户详情查看
- 用户状态管理（激活/禁用）
- 用户数据导出

#### 3. 内容管理
- 内容列表（按状态筛选）
- 内容审核（通过/拒绝）
- 内容详情查看
- 批量操作
- 内容删除

#### 4. 评论管理
- 评论列表
- 评论状态更新（显示/隐藏）
- 评论删除
- 批量操作

#### 5. 分类管理
- 分类 CRUD 操作
- 分类排序
- 层级管理
- 图标设置

#### 6. 标签管理
- 标签 CRUD 操作
- 标签搜索
- 使用统计
- 标签类型管理

#### 7. 统计分析
- 用户增长趋势图
- 内容发布统计
- 互动数据分析
- 分类内容分布
- 数据导出

#### 8. 系统设置
- 管理员账号管理
- 角色权限配置
- 操作日志查看
- 系统参数设置

### 访问地址

- 管理后台登录: `http://your-domain.com/admin/login`
- 管理后台首页: `http://your-domain.com/admin/dashboard`

### 默认管理员账号

```
用户名: admin
密码: admin123
```

**⚠️ 生产环境请务必修改默认密码！**

### 初始化管理员系统

```bash
cd Server
python scripts/init_admin.py
```

### 修改管理员密码

```bash
cd Server
python scripts/fix_admin_password.py
```

详细文档请参考：
- [管理系统说明](ADMIN_SYSTEM_README.md)
- [快速开始指南](ADMIN_QUICK_START.md)
- [部署清单](ADMIN_DEPLOYMENT_CHECKLIST.md)

---

---

## 💡 技术亮点

### 1. 模块化架构设计
- **清晰的模块边界**: 20+ 个独立业务模块，每个模块包含 api、service、repository、schemas
- **分层架构**: API → Service → Repository → Domain，职责清晰
- **依赖注入**: 使用 FastAPI 的依赖注入系统，便于测试和维护

### 2. AI 工作流编排
- **LangGraph 集成**: 支持复杂的多步推理和智能体协作
- **多智能体系统**: 学生画像、学习路径、月度报告、视频分析等专用智能体
- **流式响应**: 支持 AI 对话的流式输出，提升用户体验
- **上下文管理**: 智能管理对话上下文，支持长对话

### 3. 推荐系统
- **多路召回策略**: 
  - 热门视频召回
  - 关注作者召回
  - 相似标签召回
  - 新内容探索
- **冷启动解决方案**: 50% 热门 + 30% 新内容 + 20% 探索
- **兴趣建模**: 基于分类、标签、作者三维度的用户画像
- **排序算法**: 结合热度、时效性、去重、探索因子的综合排序
- **效果追踪**: 曝光日志记录，支持推荐效果分析

### 4. 异步架构
- **全异步设计**: FastAPI + aiomysql + httpx，充分利用异步 I/O
- **高并发支持**: 异步数据库操作，提升系统吞吐量
- **连接池管理**: 数据库连接池自动管理，避免连接泄漏

### 5. 交互优化
- **本地队列缓存**: 点赞、收藏、评论等操作先缓存到本地队列
- **批量同步机制**: 10 秒间隔批量同步，减少网络请求
- **乐观更新**: UI 立即响应，后台异步同步
- **观看进度上报**: 8 秒间隔上报，完播判定（进度 ≥ 98%）

### 6. 后台管理系统
- **独立认证系统**: 管理员独立的 JWT 认证
- **角色权限管理**: 超级管理员、内容审核员、用户管理员、运营管理员
- **操作日志审计**: 记录所有管理操作，支持追溯
- **数据可视化**: Recharts 图表展示用户增长、内容统计等数据

### 7. 现代前端技术
- **React 18**: 使用最新的 React 特性，函数式组件 + Hooks
- **Vite 构建**: 快速的开发体验和构建速度
- **Tailwind CSS**: 原子化 CSS，快速开发响应式界面
- **Shadcn UI**: 高质量的无障碍组件库
- **TypeScript**: 类型安全，减少运行时错误

### 8. 数据库设计
- **30+ 张表**: 完整的业务数据模型
- **软删除支持**: 重要数据支持软删除，可恢复
- **时间戳混入**: 自动记录创建和更新时间
- **索引优化**: 关键查询字段建立索引，提升查询性能

### 9. 对象存储
- **MinIO 集成**: S3 兼容的对象存储
- **预签名 URL**: 安全的文件上传和下载
- **自动桶管理**: 自动创建和管理存储桶
- **元数据管理**: 完整的文件元数据记录

### 10. 开发体验
- **API 文档自动生成**: OpenAPI 3.0 规范，Swagger UI + ReDoc
- **代码规范**: Ruff (Python) + ESLint (TypeScript)
- **类型标注**: 完整的类型标注，IDE 友好
- **环境变量管理**: 统一的配置管理，支持多环境

---

## 🚢 部署

### 后端部署

#### 方式一：使用 Docker (推荐)

1. **构建镜像**
```bash
cd Server
docker build -t linglearn-cloud-server:latest .
```

2. **运行容器**
```bash
docker run -d \
  --name linglearn-server \
  -p 8003:8003 \
  --env-file .env \
  --restart unless-stopped \
  linglearn-cloud-server:latest
```

3. **使用 Docker Compose**
```yaml
version: '3.8'

services:
  api:
    build: ./Server
    ports:
      - "8003:8003"
    env_file:
      - ./Server/.env
    depends_on:
      - mysql
      - redis
      - minio
    restart: unless-stopped

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: linglearn_cloud
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    restart: unless-stopped

volumes:
  mysql_data:
  minio_data:
```

启动所有服务：
```bash
docker-compose up -d
```

#### 方式二：使用 Systemd

1. **创建服务文件** `/etc/systemd/system/linglearn.service`
```ini
[Unit]
Description=LingLearn Cloud API
After=network.target mysql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/Server
Environment="PATH=/path/to/venv/bin"
EnvironmentFile=/path/to/Server/.env
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8003 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **启动服务**
```bash
sudo systemctl daemon-reload
sudo systemctl enable linglearn
sudo systemctl start linglearn
sudo systemctl status linglearn
```

3. **查看日志**
```bash
sudo journalctl -u linglearn -f
```

#### 方式三：使用 Supervisor

1. **安装 Supervisor**
```bash
sudo apt-get install supervisor
```

2. **创建配置文件** `/etc/supervisor/conf.d/linglearn.conf`
```ini
[program:linglearn]
command=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8003 --workers 4
directory=/path/to/Server
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/linglearn/access.log
stderr_logfile=/var/log/linglearn/error.log
```

3. **启动服务**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start linglearn
sudo supervisorctl status linglearn
```

### 前端部署

#### 1. 构建静态文件
```bash
cd fronted
npm install
npm run build
# 输出到 dist/ 目录
```

#### 2. 使用 Nginx

**Nginx 配置示例** `/etc/nginx/sites-available/linglearn`
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    root /path/to/fronted/dist;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 1000;

    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://127.0.0.1:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/linglearn /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 3. 使用 HTTPS (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx
```

### 数据库初始化

1. **创建数据库**
```sql
CREATE DATABASE linglearn_cloud CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. **运行迁移**
```bash
cd Server
alembic upgrade head
```

3. **初始化管理员**
```bash
python scripts/init_admin.py
```

### 生产环境检查清单

#### 安全配置
- [ ] 修改 `JWT_SECRET_KEY` 为强密码
- [ ] 设置具体的 `CORS_ORIGINS`
- [ ] 启用 HTTPS
- [ ] 配置防火墙规则
- [ ] 修改默认管理员密码
- [ ] 设置 MinIO 访问密钥
- [ ] 配置数据库访问权限

#### 性能优化
- [ ] 启用 Redis 缓存 (`REDIS_ENABLED=true`)
- [ ] 配置数据库连接池
- [ ] 使用 CDN 加速静态资源
- [ ] 启用 Gzip 压缩
- [ ] 配置 Nginx 缓存
- [ ] 设置合适的 worker 数量

#### 监控和日志
- [ ] 配置日志收集（如 ELK Stack）
- [ ] 设置性能监控（如 Prometheus + Grafana）
- [ ] 配置错误追踪（如 Sentry）
- [ ] 设置告警通知
- [ ] 配置日志轮转

#### 备份
- [ ] 配置数据库定时备份
- [ ] 配置 MinIO 数据备份
- [ ] 测试备份恢复流程
- [ ] 设置备份保留策略

### 扩展部署

#### 负载均衡

使用 Nginx 作为负载均衡器：

```nginx
upstream linglearn_backend {
    least_conn;
    server 127.0.0.1:8003 weight=1;
    server 127.0.0.1:8001 weight=1;
    server 127.0.0.1:8002 weight=1;
}

server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://linglearn_backend;
        # ... 其他配置
    }
}
```

#### 数据库主从复制

配置 MySQL 主从复制以提高读性能和数据可靠性。

#### Redis 集群

配置 Redis Sentinel 或 Cluster 以提高可用性。

### 监控示例

#### Prometheus 配置

```yaml
scrape_configs:
  - job_name: 'linglearn'
    static_configs:
      - targets: ['localhost:8003']
```

#### Grafana 仪表盘

导入预配置的仪表盘模板，监控：
- API 请求量和响应时间
- 数据库连接数和查询性能
- Redis 命中率
- 系统资源使用情况

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是报告 bug、提出新功能建议、改进文档还是提交代码。

### 贡献流程

1. **Fork 本仓库**
   ```bash
   # 点击 GitHub 页面右上角的 Fork 按钮
   ```

2. **克隆到本地**
   ```bash
   git clone https://github.com/your-username/LingLearn_Cloud.git
   cd LingLearn_Cloud
   ```

3. **创建特性分支**
   ```bash
   git checkout -b feature/AmazingFeature
   # 或修复 bug
   git checkout -b fix/SomeBug
   ```

4. **进行更改**
   - 遵循项目的代码规范
   - 添加必要的测试
   - 更新相关文档

5. **提交更改**
   ```bash
   git add .
   git commit -m 'feat: Add some AmazingFeature'
   ```

6. **推送到分支**
   ```bash
   git push origin feature/AmazingFeature
   ```

7. **开启 Pull Request**
   - 在 GitHub 上打开 Pull Request
   - 填写 PR 模板，描述你的更改
   - 等待代码审查

### 代码规范

#### 后端 (Python)
- 遵循 PEP 8 规范
- 使用 Ruff 进行代码检查和格式化
- 所有函数必须有类型标注
- 添加必要的文档字符串

```bash
# 运行代码检查
ruff check .

# 自动格式化
ruff format .
```

#### 前端 (TypeScript)
- 遵循 ESLint 规则
- 使用 Prettier 格式化代码
- 使用 TypeScript 类型定义
- 组件使用函数式组件 + Hooks

```bash
# 运行代码检查
npm run lint

# 自动格式化
npm run format
```

### 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例**:
```
feat(auth): add OAuth2 login support

Implement OAuth2 authentication flow for Google and GitHub providers.

Closes #123
```

### 开发指南

#### 后端开发

1. **设置开发环境**
   ```bash
   cd Server
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

2. **运行测试**
   ```bash
   pytest
   pytest --cov=app  # 查看覆盖率
   ```

3. **创建数据库迁移**
   ```bash
   alembic revision --autogenerate -m "描述"
   alembic upgrade head
   ```

#### 前端开发

1. **设置开发环境**
   ```bash
   cd fronted
   npm install
   ```

2. **运行开发服务器**
   ```bash
   npm run dev
   ```

3. **构建生产版本**
   ```bash
   npm run build
   ```

### 问题反馈

如果您发现 bug 或有功能建议，请在 [GitHub Issues](https://github.com/your-repo/LingLearn_Cloud/issues) 中提出。

**报告 Bug 时请包含**:
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（操作系统、Python/Node 版本等）
- 相关日志或截图

**功能建议请包含**:
- 功能描述
- 使用场景
- 预期效果
- 可能的实现方案（可选）

### 文档贡献

文档改进同样重要！您可以：
- 修正文档中的错误
- 改进文档的清晰度
- 添加示例和教程
- 翻译文档到其他语言

### 行为准则

参与本项目即表示您同意遵守我们的行为准则：

- 尊重所有贡献者
- 接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

```
MIT License

Copyright (c) 2024 LingLearn Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 联系方式

- **项目主页**: [GitHub Repository](https://github.com/your-repo/LingLearn_Cloud)
- **问题反馈**: [GitHub Issues](https://github.com/your-repo/LingLearn_Cloud/issues)
- **文档**: [项目文档](./Server/docs/)
- **邮箱**: contact@linglearn.com

---

## 🙏 致谢

感谢所有为本项目做出贡献的开发者！

### 开源项目

本项目使用了以下优秀的开源项目：

#### 后端
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL 工具包和 ORM
- [Pydantic](https://docs.pydantic.dev/) - 数据验证库
- [Alembic](https://alembic.sqlalchemy.org/) - 数据库迁移工具
- [Uvicorn](https://www.uvicorn.org/) - ASGI 服务器
- [MinIO](https://min.io/) - 高性能对象存储
- [Redis](https://redis.io/) - 内存数据库
- [LangGraph](https://github.com/langchain-ai/langgraph) - AI 工作流编排

#### 前端
- [React](https://react.dev/) - 用户界面库
- [Vite](https://vitejs.dev/) - 前端构建工具
- [Tailwind CSS](https://tailwindcss.com/) - CSS 框架
- [Radix UI](https://www.radix-ui.com/) - 无障碍组件库
- [Material-UI](https://mui.com/) - React UI 组件库
- [Recharts](https://recharts.org/) - 图表库
- [React Router](https://reactrouter.com/) - 路由库
- [React Hook Form](https://react-hook-form.com/) - 表单库

### 特别感谢

- 所有贡献者和测试用户
- 开源社区的支持和帮助
- 各大 AI 模型提供商

---

## 📈 项目状态

![GitHub stars](https://img.shields.io/github/stars/your-repo/LingLearn_Cloud?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-repo/LingLearn_Cloud?style=social)
![GitHub issues](https://img.shields.io/github/issues/your-repo/LingLearn_Cloud)
![GitHub pull requests](https://img.shields.io/github/issues-pr/your-repo/LingLearn_Cloud)
![GitHub last commit](https://img.shields.io/github/last-commit/your-repo/LingLearn_Cloud)

---

## 🗺️ 路线图

### v1.0 (当前版本)
- [x] 用户认证和授权
- [x] 内容管理和视频流
- [x] 社交互动功能
- [x] AI 聊天助手
- [x] 推荐系统
- [x] 学习路径
- [x] 在线练习
- [x] 学习报告
- [x] 后台管理系统

### v1.1 (计划中)
- [ ] 实时通知推送
- [ ] 直播功能
- [ ] 移动端适配优化
- [ ] 多语言支持
- [ ] 更多 AI 智能体
- [ ] 社区论坛

### v2.0 (未来)
- [ ] 微服务架构重构
- [ ] GraphQL API
- [ ] 移动应用 (React Native)
- [ ] 桌面应用 (Electron)
- [ ] 区块链证书
- [ ] VR/AR 学习体验

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个 Star！⭐**

Made with ❤️ by LingLearn Team

[⬆ 回到顶部](#linglearn-cloud---智慧学习平台)

</div>
