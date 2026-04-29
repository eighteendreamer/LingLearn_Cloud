# LingLearn Cloud 后端开发 A 任务书

## 1. 角色定位

你负责本项目后端的“平台底座”和“内容主链路”，范围包括：

- FastAPI 项目骨架
- 公共基础设施
- 鉴权与用户体系
- MinIO 上传
- 视频内容发布与首页 feed
- 社交互动
- 发现 / 搜索基础能力
- 推荐系统

你的工作会直接决定整个项目是否能启动、能联调、能完成首页推荐。

## 2. 你的模块边界

你负责以下模块：

- `auth`
- `user`
- `storage`
  - `content`
- `social`
- `discover`
- `search`
- `recommendation`

你负责以下基础目录：

- `app/main.py`
- `app/api/`
- `app/core/`
- `app/db/`
- `app/common/`
- `app/infra/storage/`

## 3. 你负责的数据表

### 3.1 基础与用户

- `users`
- `user_refresh_tokens`
- `user_profiles`
- `user_settings`
- `user_follow_relations`
- `media_assets`

### 3.2 内容与互动

- `content_categories`
- `tags`
- `content_items`
- `content_item_tags`
- `content_comments`
- `content_likes`
- `content_favorites`
- `content_shares`
- `content_view_histories`
- `content_quizzes`
- `content_quiz_options`
- `content_quiz_attempts`

### 3.3 推荐

- `user_category_interest_profiles`
- `user_tag_interest_profiles`
- `user_author_interest_profiles`
- `content_recommendation_impressions`

## 4. 你负责的接口

## 4.1 基础能力

- `GET /health` 或等价健康检查接口

## 4.2 Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`

## 4.3 User

- `GET /users/me`
- `PUT /users/me/profile`
- `PUT /users/me/settings`
- `GET /users/{user_id}`
- `POST /users/{user_id}/follow`
- `DELETE /users/{user_id}/follow`
- `GET /users/{user_id}/works`

## 4.4 Storage

- `POST /storage/presign-upload`
- `POST /storage/complete-upload`

## 4.5 Content / Feed

- `GET /feed/videos`
- `POST /contents`
- `GET /contents/{content_id}`
- `PUT /contents/{content_id}`
- `GET /discover/categories`
- `GET /discover/hot-topics`
- `GET /discover/hot-tags`
- `GET /search/contents`

## 4.6 Social

- `POST /contents/{content_id}/like`
- `DELETE /contents/{content_id}/like`
- `POST /contents/{content_id}/favorite`
- `DELETE /contents/{content_id}/favorite`
- `POST /contents/{content_id}/share`
- `POST /contents/{content_id}/watch-progress`
- `GET /contents/{content_id}/comments`
- `POST /contents/{content_id}/comments`
- `GET /users/me/favorites`
- `GET /users/me/watch-history`

## 4.7 Quiz

- `GET /contents/{content_id}/quizzes`
- `POST /quizzes/{quiz_id}/submit`

## 5. 你要先交付的基础骨架

这是你第一优先级，必须先做：

1. 建立 `Server/app` 目录结构
2. 配置 FastAPI 启动入口
3. 配置环境变量读取
4. 配置数据库 Session
5. 配置统一响应结构
6. 配置统一异常处理
7. 配置 JWT 鉴权
8. 配置全局 Router 注册
9. 提供 `get_current_user` 等依赖

交付后，后端 B 才能在相同骨架下继续开发自己的模块。

## 6. 推荐系统职责

你额外负责首页推荐系统第一期落地，基于：

- [recommendation_algorithm_spec.md](./recommendation_algorithm_spec.md)

第一期必须完成：

1. 新用户冷启动推荐
2. 热门召回
3. 分类兴趣召回
4. 基础标签兴趣召回
5. 推荐曝光日志写入
6. 点赞、收藏、评论、观看进度驱动兴趣画像更新

第一期可以暂缓：

- 协同过滤
- 学习排序模型
- A/B 实验平台

## 7. 推荐系统实现任务

### 7.1 数据侧

- 完成推荐相关表的迁移或落库
- 建立兴趣画像更新逻辑
- 建立 `hot_score` 计算任务
- 建立曝光日志写入逻辑

### 7.2 服务侧

- 实现 `recommendation` 模块或 `content service` 内推荐服务
- 支持 `recommend_type=for_you`
- 支持无画像自动走 `cold_start`
- 支持已看内容降权
- 支持同作者 / 同分类打散

### 7.3 任务侧

- 定时更新内容热度
- 定时做兴趣分衰减
- 定时清理旧曝光日志

## 8. 分阶段任务

## 8.1 第一阶段

- 项目骨架
- 数据库连接
- JWT
- `auth`
- `user`

完成标志：

- 可以注册、登录、获取当前用户信息

## 8.2 第二阶段

- `storage`
- `content`
- `social`
- `quiz`

完成标志：

- 可以上传资源、发布视频、观看 feed、点赞收藏评论

## 8.3 第三阶段

- `discover`
- `search`
- `recommendation`

完成标志：

- 首页 `for_you` 能根据默认算法和初步兴趣画像出结果

## 9. 与后端 B 的协作约定

你需要先给 B 明确以下约定：

- 用户鉴权方式
- 当前用户对象结构
- 统一错误码
- 统一分页结构
- 文件上传资产表结构
- 公共枚举命名

你需要预留给 B 的公共接口或能力：

- `get_current_user`
- `success(...)` 响应封装
- 公共分页 schema
- `media_assets` 查询能力
- `users/me` 基础资料结构

## 10. 你的测试任务

至少补这些测试：

- `auth` 登录注册成功 / 失败
- token 刷新与登出
- 内容创建校验
- 观看进度写入
- 点赞 / 收藏幂等
- 推荐冷启动列表
- 推荐兴趣画像更新

## 11. 你的交付标准

每个模块交付：

- `api.py`
- `schemas.py`
- `models.py`
- `repository.py`
- `service.py`
- 单元测试

基础设施交付：

- 项目可启动
- 数据库可连通
- Swagger 可访问
- JWT 可用
- MinIO 预签名上传可用

## 12. 你当前最优开发顺序

建议严格按下面顺序做：

1. 项目骨架
2. `auth`
3. `user`
4. `storage`
5. `content`
6. `social`
7. `discover/search`
8. `recommendation`

## 13. 完成后的结果

你完成后，项目会具备一条完整的首页主链路：

- 用户登录
- 用户上传素材
- 用户发布视频
- 首页拉取视频流
- 用户观看、点赞、收藏、评论
- 系统根据行为逐渐做定向推荐

这是整个项目最关键的业务闭环。
