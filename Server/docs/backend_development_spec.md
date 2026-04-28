# LingLearn Cloud 后端开发规范

## 1. 目标

本规范用于指导基于 `FastAPI + SQLAlchemy + MySQL + MinIO + LangGraph` 的模块化后端开发，强调：

- 模块边界清晰
- 数据访问统一
- 事务边界可控
- AI 工作流可观测
- 代码结构长期可维护

## 2. 总体架构

推荐采用“模块化单体”架构，而不是一开始拆微服务。

### 2.1 分层原则

- `API 层`：接收请求、参数校验、鉴权、序列化响应
- `Service 层`：业务编排、事务边界、调用仓储 / AI / MinIO
- `Repository 层`：数据库读写，禁止写业务判断
- `Domain / Model 层`：ORM 模型、领域常量、枚举
- `Schema 层`：Pydantic 请求 / 响应模型
- `Infra 层`：MySQL、Redis、MinIO、LangGraph、消息、日志

## 3. 推荐目录结构

```text
Server/
  app/
    main.py
    api/
      router.py
      deps.py
    core/
      config.py
      security.py
      exceptions.py
      response.py
      logging.py
      enums.py
    db/
      base.py
      session.py
      models.py
      migrations/
    infra/
      storage/
        minio_client.py
        service.py
      ai/
        llm_client.py
        langgraph_runtime.py
      cache/
      tasks/
    common/
      pagination.py
      utils.py
      constants.py
    modules/
      auth/
        api.py
        schemas.py
        models.py
        repository.py
        service.py
      user/
        api.py
        schemas.py
        models.py
        repository.py
        service.py
      content/
        api.py
        schemas.py
        models.py
        repository.py
        service.py
      social/
        api.py
        schemas.py
        models.py
        repository.py
        service.py
      course/
      resource/
      practice/
      assessment/
      report/
      ai_chat/
      learning_path/
      notification/
    tests/
      unit/
      integration/
      e2e/
```

## 4. 模块拆分要求

### 4.1 模块粒度

每个模块必须满足以下约束：

- 有自己的 `api.py`
- 有自己的 `service.py`
- 有自己的 `repository.py`
- 有自己的 `schemas.py`
- ORM 可分布在模块内，也可统一收口到 `db/models.py`

### 4.2 模块职责示例

#### `auth`

- 注册
- 登录
- token 刷新
- 登出
- 密码加密 / 校验

#### `user`

- 个人资料
- 设置
- 关注关系
- 用户主页

#### `content`

- 视频流
- 作品发布
- 内容详情
- 搜索基础聚合

#### `social`

- 点赞
- 收藏
- 评论
- 分享
- 观看记录

#### `course`

- 课程目录
- 课时结构
- 学习进度

#### `resource`

- 文档 / 附件 / 链接资源
- 资源检索
- 最近文件

#### `practice`

- 题库
- 会话
- 作答
- 判分

#### `assessment`

- 指标聚合
- 周 / 月评估快照

#### `report`

- 学习月报生成
- PDF 导出

#### `ai_chat`

- AI 对话
- 消息上下文管理

#### `learning_path`

- 学习路径模板
- 用户个性化路径
- 节点状态管理

## 5. 编码规范

## 5.1 命名

- 文件名：小写下划线，如 `user_profile_service.py`
- 类名：大驼峰，如 `UserProfileService`
- 函数名：小写下划线，如 `create_content_item`
- 常量：全大写下划线，如 `DEFAULT_PAGE_SIZE`
- 接口路径：复数名词，如 `/users/me/notifications`

## 5.2 类型标注

所有函数都必须写类型标注，尤其是：

- API 入参 / 出参
- Service 返回值
- Repository 查询结果

## 5.3 Schema 约定

- `schemas.py` 中区分：
  - `XXXCreateRequest`
  - `XXXUpdateRequest`
  - `XXXQueryRequest`
  - `XXXResponse`
  - `XXXListItemResponse`

## 5.4 禁止事项

- 禁止在 `api.py` 里直接写 SQL
- 禁止在 `repository.py` 写复杂业务分支
- 禁止在 `service.py` 返回 ORM 对象给前端
- 禁止跨模块直接操作别的模块表，必须走对方 service 或 repository facade

## 6. FastAPI 规范

## 6.1 路由组织

聚合路由统一在 `app/api/router.py` 注册：

```python
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(content_router, prefix="/contents", tags=["contents"])
```

## 6.2 依赖注入

统一通过 `Depends` 注入：

- 数据库 Session
- 当前用户
- 分页对象
- 权限校验器

示例：

```python
@router.get("/me")
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return success(service.get_me(current_user.user_id))
```

## 6.3 响应统一

禁止裸返回字典，统一使用响应封装器：

```python
def success(data=None, message: str = "ok"):
    return {"code": 0, "message": message, "data": data}
```

## 7. SQLAlchemy 规范

## 7.1 版本

- 使用 SQLAlchemy 2.0 风格
- 推荐异步驱动：`mysql+asyncmy://` 或 `mysql+aiomysql://`

## 7.2 Session 生命周期

- 一次请求一个 Session
- Service 层负责事务提交
- Repository 不主动提交事务，除非特别说明

## 7.3 Repository 职责

Repository 只做三类事情：

1. 基础 CRUD
2. 条件查询 / 聚合查询
3. 行级锁 / 批量更新

示例：

```python
class ContentRepository:
    async def get_by_id(self, session: AsyncSession, content_id: int) -> ContentItem | None:
        ...

    async def list_feed(self, session: AsyncSession, query: FeedQuery) -> list[ContentItem]:
        ...
```

## 7.4 ORM 模型要求

每张表至少包含：

- `id`
- `created_at`
- `updated_at`

业务表按需补充：

- `deleted_at`
- `status`
- 统计字段

## 7.5 索引规范

以下字段必须优先加索引：

- 所有外键
- 所有唯一查询字段
- 列表页排序字段
- 联表过滤字段
- 时间范围查询字段

严禁：

- 为低区分度布尔字段单独建索引
- 为 rarely-used 的长文本字段建普通索引

## 8. MinIO 规范

## 8.1 上传策略

统一采用“后端签名、前端直传”：

1. 申请上传票据
2. 客户端上传到 MinIO
3. 回调确认
4. 激活资产记录

## 8.2 对象路径规范

```text
avatars/{user_id}/{yyyy}/{mm}/{file}
content/covers/{content_id}/{file}
content/videos/{content_id}/{file}
reports/{user_id}/{yyyy-mm}/{file}
resources/{resource_id}/{file}
```

## 8.3 Asset 元数据

所有文件都必须写入 `media_assets`，至少记录：

- `bucket_name`
- `object_key`
- `mime_type`
- `asset_type`
- `file_size`
- `checksum_sha256`

## 9. LangGraph 规范

## 9.1 适用场景

建议仅在“多步推理 / 编排”场景使用 LangGraph：

- 学生画像生成
- 个性化学习路径生成
- 学习月报总结
- AI 学习助手工具编排

普通单次 LLM 问答不强制走 LangGraph。

## 9.2 Graph 拆分

推荐目录：

```text
app/infra/ai/graphs/
  student_profile_graph.py
  learning_path_graph.py
  monthly_report_graph.py
  tutor_chat_graph.py
```

## 9.3 工作流记录

每次执行图都必须落 `ai_workflow_runs`：

- `workflow_type`
- `biz_type`
- `biz_id`
- `input_json`
- `output_json`
- `status`
- `error_message`

这样后续查错会轻松很多。

## 10. Service 层规范

## 10.1 事务边界

事务以 Service 方法为边界。

示例：

```python
class ContentService:
    async def create_content(self, req: ContentCreateRequest, user_id: int) -> int:
        async with self.uow.transaction():
            ...
            return content_id
```

## 10.2 Service 允许做的事

- 参数补全
- 权限判断
- 状态机流转
- 聚合多个 repository
- 调用 MinIO / LangGraph / 通知

## 10.3 Service 不应该做的事

- 拼原始 SQL
- 直接依赖 HTTP Request 对象
- 直接返回 ORM Entity 给 API 层

## 11. 鉴权与权限

## 11.1 登录态

- Access Token：2 小时
- Refresh Token：30 天
- 支持多设备登录

## 11.2 权限分层

- `anonymous`
- `user`
- `creator`
- `admin`

## 11.3 典型权限判断

- 只有作者本人或管理员可以编辑作品
- 只有本人可以修改自己的设置
- 评论删除支持评论本人、作品作者、管理员

## 12. 日志与可观测性

## 12.1 日志要求

每个请求必须记录：

- `request_id`
- `user_id`
- `path`
- `method`
- `latency_ms`
- `status_code`

## 12.2 审计日志

以下动作必须落 `audit_logs`：

- 登录成功 / 失败
- 发布 / 删除作品
- 修改资料
- 导出报告
- 管理员审核

## 12.3 AI 观测

AI 相关还必须记录：

- `model_name`
- `prompt_tokens`
- `completion_tokens`
- `latency_ms`
- `workflow_run_id`

## 13. 测试规范

## 13.1 测试分层

- 单元测试：Service、工具函数、规则判断
- 集成测试：Repository、数据库事务、MinIO 适配
- 接口测试：FastAPI 路由

## 13.2 必测模块

第一阶段至少覆盖：

- `auth`
- `content`
- `social`
- `practice`
- `learning_path`

## 13.3 测试命名

```text
test_auth_login_success.py
test_content_create_reject_large_video.py
test_practice_submit_should_score_correctly.py
```

## 14. 数据迁移规范

- 使用 Alembic 管理 DDL
- 禁止人工直接改线上表结构
- 每个迁移文件必须说明：
  - 变更目的
  - 影响表
  - 回滚方案

## 15. 开发顺序建议

建议按下面顺序推进，这样能尽快把前端页面真正跑起来：

1. `auth`
2. `user`
3. `storage`
4. `content`
5. `social`
6. `course` / `resource`
7. `practice`
8. `assessment`
9. `learning_path`
10. `report`
11. `ai_chat`

## 16. 交付标准

一个模块达到“可交付”至少需要：

- ORM 模型
- Pydantic Schema
- Repository
- Service
- API Router
- 单元测试
- 接口文档
- 错误码

如果你们后面准备正式开始后端搭建，下一步最自然的是直接按这个规范把 `FastAPI` 项目骨架一并搭出来，包括模块目录、数据库会话、JWT、MinIO 客户端和基础路由。  
