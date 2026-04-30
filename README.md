# LingLearn Cloud - 智慧学习平台

<div align="center">

一个现代化的智能学习平台，提供个性化内容推荐、AI 辅助学习和社交互动功能。

[English](#english) | [中文](#chinese)

</div>

---

## 📋 目录

- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [开发指南](#开发指南)
- [API 文档](#api-文档)
- [部署](#部署)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 🎯 项目简介

LingLearn Cloud 是一个全栈智慧学习平台，旨在通过 AI 技术和个性化推荐算法，为用户提供高效、有趣的学习体验。平台集成了视频内容管理、社交互动、学习路径规划、在线练习和智能评估等功能。

### 主要特点

- 🤖 **AI 智能助手** - 基于大语言模型的学习辅导和问答
- 📊 **个性化推荐** - 基于用户兴趣和行为的内容推荐算法
- 🎥 **视频学习** - 支持视频内容的上传、播放和互动
- 📚 **学习路径** - 结构化的学习计划和进度跟踪
- 💬 **社交互动** - 评论、点赞、收藏、分享和关注功能
- 📈 **学习报告** - 详细的学习数据分析和可视化
- 🎯 **在线练习** - 互动式练习和即时反馈
- 🏆 **学习评估** - 智能测评和能力分析

---

## 🚀 核心功能

### 用户功能
- **用户认证** - 注册、登录、JWT 令牌刷新、登出
- **个人资料** - 用户信息管理、头像上传、个性化设置
- **社交关系** - 关注/取消关注用户、查看粉丝和关注列表

### 内容管理
- **内容创作** - 创建、编辑、发布学习内容
- **内容浏览** - 视频流、分类浏览、搜索功能
- **内容互动** - 点赞、收藏、评论、分享
- **观看历史** - 记录学习进度和观看位置

### AI 功能
- **智能对话** - AI 聊天助手，提供学习指导
- **内容推荐** - 基于用户画像的个性化推荐
- **学习分析** - AI 驱动的学习数据分析

### 学习工具
- **学习路径** - 结构化课程和学习计划
- **在线练习** - 互动式练习题和测验
- **学习评估** - 能力测评和诊断报告
- **学习报告** - 学习时长、进度、成就统计

### 资源中心
- **资源库** - 学习资料、文档、工具集合
- **发现页** - 探索热门内容和推荐资源

---

## 🛠 技术栈

### 后端 (Server)
- **框架**: FastAPI 0.115+
- **语言**: Python 3.10+
- **数据库**: MySQL (通过 aiomysql)
- **ORM**: SQLAlchemy 2.0+
- **缓存**: Redis 5.2+
- **对象存储**: MinIO 7.2+
- **认证**: JWT (PyJWT)
- **数据库迁移**: Alembic 1.13+
- **AI 集成**: 支持智谱 AI (GLM-4) 等大语言模型
- **异步运行时**: Uvicorn

### 前端 (fronted)
- **框架**: React 18.3.1
- **路由**: React Router 7.13.0
- **构建工具**: Vite 6.3.5
- **样式**: Tailwind CSS 4.1.12
- **UI 组件**: 
  - Radix UI (无障碍组件库)
  - Material-UI 7.3.5
  - Shadcn UI 组件
- **状态管理**: React Hooks
- **表单**: React Hook Form 7.55.0
- **图表**: Recharts 2.15.2
- **动画**: Motion 12.23.24
- **图标**: Lucide React, MUI Icons
- **其他**: 
  - Canvas Confetti (庆祝动画)
  - React DnD (拖拽功能)
  - Sonner (通知提示)

---

## 📁 项目结构

```
LingLearn_Cloud/
├── Server/                          # 后端服务
│   ├── app/
│   │   ├── api/                     # API 路由和依赖
│   │   │   ├── routes/              # 路由定义
│   │   │   ├── deps.py              # 依赖注入
│   │   │   └── router.py            # 主路由器
│   │   ├── common/                  # 公共工具
│   │   │   ├── constants.py         # 常量定义
│   │   │   ├── pagination.py        # 分页工具
│   │   │   └── utils.py             # 工具函数
│   │   ├── core/                    # 核心配置
│   │   │   ├── config.py            # 应用配置
│   │   │   ├── enums.py             # 枚举类型
│   │   │   ├── exceptions.py        # 异常处理
│   │   │   ├── logging.py           # 日志配置
│   │   │   ├── response.py          # 响应格式
│   │   │   └── security.py          # 安全工具
│   │   ├── db/                      # 数据库
│   │   │   ├── migrations/          # Alembic 迁移
│   │   │   ├── base.py              # 数据库基类
│   │   │   ├── mixins.py            # 模型混入
│   │   │   ├── models.py            # 模型导出
│   │   │   └── session.py           # 数据库会话
│   │   ├── infra/                   # 基础设施
│   │   │   ├── ai/                  # AI 集成
│   │   │   │   ├── langgraph_runtime.py
│   │   │   │   └── llm_client.py
│   │   │   ├── cache/               # 缓存
│   │   │   │   └── redis_client.py
│   │   │   ├── storage/             # 对象存储
│   │   │   │   ├── minio_client.py
│   │   │   │   └── service.py
│   │   │   └── tasks/               # 后台任务
│   │   ├── modules/                 # 业务模块
│   │   │   ├── ai_chat/             # AI 聊天
│   │   │   ├── assessment/          # 学习评估
│   │   │   ├── auth/                # 用户认证
│   │   │   ├── content/             # 内容管理
│   │   │   ├── course/              # 课程管理
│   │   │   ├── discover/            # 发现页
│   │   │   ├── learning_path/       # 学习路径
│   │   │   ├── notification/        # 通知
│   │   │   ├── practice/            # 在线练习
│   │   │   ├── recommendation/      # 推荐算法
│   │   │   ├── report/              # 学习报告
│   │   │   ├── resource/            # 资源中心
│   │   │   ├── search/              # 搜索功能
│   │   │   ├── social/              # 社交功能
│   │   │   ├── storage/             # 存储服务
│   │   │   └── user/                # 用户管理
│   │   ├── tests/                   # 测试
│   │   │   ├── e2e/                 # 端到端测试
│   │   │   ├── integration/         # 集成测试
│   │   │   └── unit/                # 单元测试
│   │   └── main.py                  # 应用入口
│   ├── docs/                        # 文档
│   ├── scripts/                     # 脚本
│   ├── sql/                         # SQL 脚本
│   ├── .env.example                 # 环境变量示例
│   └── pyproject.toml               # Python 项目配置
│
├── fronted/                         # 前端应用
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/          # React 组件
│   │   │   │   ├── ui/              # UI 基础组件
│   │   │   │   ├── AIChat.tsx       # AI 聊天
│   │   │   │   ├── Auth.tsx         # 认证页面
│   │   │   │   ├── Create.tsx       # 内容创作
│   │   │   │   ├── Discover.tsx     # 发现页
│   │   │   │   ├── Home.tsx         # 首页
│   │   │   │   ├── LearningAssessment.tsx
│   │   │   │   ├── LearningPath.tsx
│   │   │   │   ├── LearningReport.tsx
│   │   │   │   ├── MyLearning.tsx   # 我的学习
│   │   │   │   ├── OnlinePractice.tsx
│   │   │   │   ├── Profile.tsx      # 个人主页
│   │   │   │   ├── ResourceCenter.tsx
│   │   │   │   ├── Settings.tsx     # 设置
│   │   │   │   ├── VideoFeed.tsx    # 视频流
│   │   │   │   └── ...
│   │   │   ├── lib/                 # 工具库
│   │   │   │   ├── api.ts           # API 客户端
│   │   │   │   ├── account.ts       # 账户管理
│   │   │   │   ├── content.ts       # 内容管理
│   │   │   │   ├── session.ts       # 会话管理
│   │   │   │   ├── storage.ts       # 存储工具
│   │   │   │   └── types.ts         # 类型定义
│   │   │   ├── App.tsx              # 应用根组件
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
│   ├── dist/                        # 构建输出
│   ├── .env.example                 # 环境变量示例
│   ├── index.html                   # HTML 模板
│   ├── package.json                 # 依赖配置
│   ├── vite.config.ts               # Vite 配置
│   └── README.md
│
└── .gitignore                       # Git 忽略配置
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
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   
   # 或使用 Python 直接运行
   python -m app.main
   ```

6. **访问 API 文档**
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

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
# 应用配置
APP_NAME=LingLearn Cloud API
APP_ENV=dev                          # dev, staging, production
DEBUG=true
API_V1_PREFIX=/api/v1
HOST=127.0.0.1
PORT=8000

# 日志和 CORS
LOG_LEVEL=INFO
CORS_ORIGINS=*                       # 生产环境请设置具体域名

# 数据库
DATABASE_URL=mysql+aiomysql://root:password@127.0.0.1:3306/linglearn_cloud
DB_ECHO=false
DB_POOL_RECYCLE=3600

# Redis (可选)
REDIS_ENABLED=false
REDIS_URL=redis://127.0.0.1:6379/0
REDIS_PREFIX=linglearn
REDIS_DEFAULT_TTL_SECONDS=300

# JWT 认证
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=30

# 大语言模型
LLM_PROVIDER=zhipu                   # 智谱 AI
LLM_API_KEY=your-api-key
LLM_MODEL=glm-4-flash
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions
LLM_TIMEOUT_SECONDS=60

# MinIO 对象存储
MINIO_ENDPOINT=127.0.0.1:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=linglearn-cloud
MINIO_SECURE=false
MINIO_PUBLIC_BASE_URL=
MINIO_PRESIGN_EXPIRE_SECONDS=3600
MINIO_AUTO_CREATE_BUCKET=true

# API 文档
DOCS_URL=/docs
REDOC_URL=/redoc
OPENAPI_URL=/openapi.json
```

### 前端环境变量 (.env)

```env
# API 配置
VITE_API_BASE_URL=/api/v1
VITE_API_PROXY_TARGET=http://127.0.0.1:8000
```

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
- `GET /api/v1/users/{user_id}/works` - 获取用户作品

#### 内容 (Contents)
- `GET /api/v1/feed/videos` - 获取视频流
- `POST /api/v1/contents` - 创建内容
- `GET /api/v1/contents/{content_id}` - 获取内容详情
- `PUT /api/v1/contents/{content_id}` - 更新内容
- `POST /api/v1/contents/{content_id}/like` - 点赞
- `DELETE /api/v1/contents/{content_id}/like` - 取消点赞
- `POST /api/v1/contents/{content_id}/favorite` - 收藏
- `DELETE /api/v1/contents/{content_id}/favorite` - 取消收藏
- `POST /api/v1/contents/{content_id}/share` - 分享
- `GET /api/v1/contents/{content_id}/comments` - 获取评论
- `POST /api/v1/contents/{content_id}/comments` - 发表评论
- `POST /api/v1/contents/{content_id}/watch-progress` - 上报观看进度

#### AI 聊天 (AI Chat)
- `POST /api/v1/ai-chat/completions` - AI 对话补全

#### 存储 (Storage)
- `POST /api/v1/storage/upload` - 上传文件
- `GET /api/v1/storage/{asset_id}` - 获取文件信息

#### 发现 (Discover)
- `GET /api/v1/discover` - 获取发现页内容

#### 健康检查 (Health)
- `GET /api/v1/health` - 服务健康检查

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

API 使用 JWT Bearer Token 认证：

```
Authorization: Bearer <access_token>
```

---

## 🚢 部署

### 后端部署

#### 使用 Docker (推荐)
```bash
# 构建镜像
docker build -t linglearn-cloud-server:latest ./Server

# 运行容器
docker run -d \
  --name linglearn-server \
  -p 8000:8000 \
  --env-file ./Server/.env \
  linglearn-cloud-server:latest
```

#### 使用 Systemd
```bash
# 创建服务文件 /etc/systemd/system/linglearn.service
[Unit]
Description=LingLearn Cloud API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/Server
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target

# 启动服务
sudo systemctl enable linglearn
sudo systemctl start linglearn
```

### 前端部署

#### 构建静态文件
```bash
cd fronted
npm run build
# 输出到 dist/ 目录
```

#### 使用 Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/fronted/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 生产环境注意事项

1. **安全配置**
   - 修改 `JWT_SECRET_KEY` 为强密码
   - 设置具体的 `CORS_ORIGINS`
   - 启用 HTTPS
   - 配置防火墙规则

2. **性能优化**
   - 启用 Redis 缓存
   - 配置数据库连接池
   - 使用 CDN 加速静态资源
   - 启用 Gzip 压缩

3. **监控和日志**
   - 配置日志收集
   - 设置性能监控
   - 配置错误追踪

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- **后端**: 遵循 PEP 8，使用 Ruff 进行代码检查
- **前端**: 遵循 ESLint 规则，使用 Prettier 格式化
- **提交信息**: 使用清晰的提交信息，遵循 Conventional Commits

### 问题反馈

如果您发现 bug 或有功能建议，请在 Issues 中提出。

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---

## 📞 联系方式

- **项目主页**: [GitHub Repository]
- **问题反馈**: [GitHub Issues]
- **文档**: [项目文档](./Server/docs/)

---

## 🙏 致谢

感谢所有为本项目做出贡献的开发者！

本项目使用了以下优秀的开源项目：
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Radix UI](https://www.radix-ui.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [MinIO](https://min.io/)

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个 Star！⭐**

Made with ❤️ by LingLearn Team

</div>
