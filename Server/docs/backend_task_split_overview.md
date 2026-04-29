# LingLearn Cloud 双后端开发任务拆分总览

## 1. 目的

本文档用于把 LingLearn Cloud 后端工作拆分给 2 位后端开发同学，并尽量满足以下目标：

- 模块边界清晰
- 并行开发冲突少
- 数据表与接口责任明确
- 推荐算法、学习模块、AI 模块都有人负责
- 后续联调路径清楚

本文档基于以下文件拆分：

- [backend_development_spec.md](./backend_development_spec.md)
- [api_development_manual.md](./api_development_manual.md)
- [recommendation_algorithm_spec.md](./recommendation_algorithm_spec.md)

## 2. 拆分原则

本项目不适合按“页面”平均拆，因为很多页面背后共享数据表和服务层逻辑。更合理的方式是按领域拆分：

- 后端 A：底座能力 + 内容流主链路 + 推荐系统
- 后端 B：学习域 + AI 域 + 报告域

这样拆的原因：

- 首页视频流、互动、推荐、上传发布是一个强耦合链路，交给同一个人更稳
- 学习路径、练习、评估、报告、AI 助手天然属于学习域，交给同一个人更完整
- 认证、用户、公共基础设施由 A 先搭底座，B 在统一骨架上接模块，避免风格分裂

## 3. 人员分工

### 3.1 后端开发 A 负责

- FastAPI 项目骨架
- 公共基础设施
- 鉴权与用户体系
- 文件上传与 MinIO
- 内容发布与首页视频流
- 点赞、收藏、评论、分享、观看记录
- 发现页与搜索基础能力
- 推荐系统与推荐画像

对应任务文档：

- [backend_developer_a_tasks.md](./backend_developer_a_tasks.md)

### 3.2 后端开发 B 负责

- 课程与资源中心
- 我的学习
- 在线练习
- 学习评估
- 学习路径
- 学习报告
- AI 学习助手
- 通知中心

对应任务文档：

- [backend_developer_b_tasks.md](./backend_developer_b_tasks.md)

## 4. 公共协作边界

以下内容由后端 A 先提供，后端 B 基于这些公共能力开发：

- `app/main.py`
- `app/api/router.py`
- `app/api/deps.py`
- `app/core/config.py`
- `app/core/security.py`
- `app/core/exceptions.py`
- `app/core/response.py`
- `app/core/logging.py`
- `app/db/base.py`
- `app/db/session.py`
- `app/db/models.py` 或统一模型注册入口
- 基础用户鉴权依赖
- 通用分页结构
- 统一响应结构

以下内容由 A、B 共同遵守：

- 接口统一走 `/api/v1`
- Schema 命名规则一致
- Repository 不写业务判断
- Service 负责事务边界
- 所有接口都返回统一响应结构

## 5. 目录所有权建议

建议在正式建后端目录后，按下面方式划分主要写入归属：

### 5.1 后端开发 A 写入归属

- `app/main.py`
- `app/api/`
- `app/core/`
- `app/db/`
- `app/infra/storage/`
- `app/common/`
- `app/modules/auth/`
- `app/modules/user/`
- `app/modules/content/`
- `app/modules/social/`
- `app/modules/discover/`
- `app/modules/search/`
- `app/modules/recommendation/`

### 5.2 后端开发 B 写入归属

- `app/infra/ai/`
- `app/modules/course/`
- `app/modules/resource/`
- `app/modules/practice/`
- `app/modules/assessment/`
- `app/modules/report/`
- `app/modules/ai_chat/`
- `app/modules/learning_path/`
- `app/modules/notification/`

### 5.3 共同可读、尽量少同时改

- `app/api/router.py`
- `app/db/models.py`
- `app/core/enums.py`

建议做法：

- A 先提交初版骨架和模块占位
- B 在占位基础上填自己的模块
- 公共文件由 A 主持整合，B 提前约定要注册的 router 和 model

## 6. 开发阶段建议

## 6.1 第一阶段：底座搭建

目标：

- 让项目能启动
- 能连数据库
- 能跑健康检查
- 能完成 JWT 鉴权

负责人：

- A 主负责
- B 参与 review 和接口约定

## 6.2 第二阶段：核心主链路并行

A 负责：

- 登录注册
- 用户资料
- 上传
- 视频发布
- 首页 feed
- 点赞收藏评论分享
- 推荐冷启动与基础排序

B 负责：

- 课程
- 资源
- 练习
- 学习面板

## 6.3 第三阶段：AI 与学习闭环

A 负责：

- 推荐画像聚合
- 推荐曝光日志
- 推荐分数任务

B 负责：

- 学习路径
- 学习评估
- 月报
- AI Chat
- 通知

## 6.4 第四阶段：联调与测试

共同完成：

- 前端联调
- 接口补字段
- 统一错误码
- 单元测试与集成测试
- 数据初始化脚本

## 7. 联调依赖顺序

建议按照下面顺序联调：

1. 健康检查、配置、数据库连接
2. `auth`
3. `users`
4. `storage`
5. `contents` 与 `feed`
6. `social`
7. `courses` / `resources`
8. `practice`
9. `learning_path`
10. `assessment`
11. `report`
12. `ai_chat`
13. `recommendation` 优化版

## 8. 风险点

当前最容易产生冲突的地方有 4 个：

- `app/api/router.py` 的统一注册
- `db/models.py` 的模型导入汇总
- 用户信息结构是否被多个模块重复定义
- 推荐和学习画像是否混用表结构

建议：

- 每新增一个模块，先确定 API 前缀、表名、Service 名称
- 不要在不同模块重复定义“用户统计”逻辑
- 推荐画像和学习画像分开维护，不共用一张表

## 9. 交付标准

每个模块至少交付以下内容：

- ORM 模型
- Pydantic Schema
- Repository
- Service
- API Router
- 单元测试
- 接口文档补充

## 10. 结论

本项目最适合的 2 人拆法不是平均拆接口数，而是：

- A 负责“底座 + 内容流 + 推荐”
- B 负责“学习域 + AI 域”

这样既符合当前数据库结构，也能把首页主链路和学习闭环分别做完整。
