# LingLearn Cloud 推荐算法测试文档

## 1. 文档目标

本文档用于验证 LingLearn Cloud 首页 `for_you` 推荐算法是否已经真正执行，并且验证以下 4 条核心链路是否成立：

1. 首页推荐请求已经走推荐服务，而不是仅按固定顺序返回内容。
2. 推荐曝光日志能够正确写入数据库。
3. 用户行为能够驱动分类、标签、作者 3 类兴趣画像更新。
4. 推荐结果会随着用户行为变化而发生偏移。

本文档覆盖：

1. 接口层测试
2. 数据库层测试
3. 行为驱动测试
4. 冷启动测试
5. 个性化推荐测试
6. 故障排查

---

## 2. 适用范围

适用于当前第一期推荐实现，代码依据：

1. [recommendation_algorithm_spec.md](/G:/Code_Warehouse/LingLearn_Cloud/Server/docs/recommendation_algorithm_spec.md)
2. [backend_developer_a_tasks.md](/G:/Code_Warehouse/LingLearn_Cloud/Server/docs/backend_developer_a_tasks.md)
3. [recommendation/service.py](/G:/Code_Warehouse/LingLearn_Cloud/Server/app/modules/recommendation/service.py)
4. [content/service.py](/G:/Code_Warehouse/LingLearn_Cloud/Server/app/modules/content/service.py)
5. [recommendation/models.py](/G:/Code_Warehouse/LingLearn_Cloud/Server/app/modules/recommendation/models.py)

---

## 3. 当前实现说明

### 3.1 当前首页推荐入口

首页推荐流走：

```text
GET /api/v1/feed/videos?recommend_type=for_you
```

该接口在：

1. [content/api.py](/G:/Code_Warehouse/LingLearn_Cloud/Server/app/modules/content/api.py)
2. [content/service.py](/G:/Code_Warehouse/LingLearn_Cloud/Server/app/modules/content/service.py)

当 `recommend_type=for_you` 时，会进入：

1. [RecommendationService.list_for_you_rows(...)](/G:/Code_Warehouse/LingLearn_Cloud/Server/app/modules/recommendation/service.py)

### 3.2 当前算法已支持的能力

当前版本已经实现：

1. 新用户冷启动推荐
2. 热门召回
3. 分类兴趣召回
4. 标签兴趣召回
5. 作者兴趣召回
6. 探索召回
7. 推荐曝光日志写入
8. 点赞、收藏、评论、分享、观看进度驱动兴趣画像更新

### 3.3 当前行为权重

当前代码中的行为更新规则来自 [recommendation/service.py](/G:/Code_Warehouse/LingLearn_Cloud/Server/app/modules/recommendation/service.py)：

1. `watch`
   - 有效观看：`interest +2`
   - 观看进度 >= 50%：`interest +3`
   - 完播或进度 >= 95%：`interest +5`
   - 低停留：`interest -1`，`negative +1`
2. `like`
   - `interest +6`
3. `unlike`
   - `interest -3`
4. `favorite`
   - `interest +10`
5. `unfavorite`
   - `interest -5`
6. `comment`
   - `interest +12`
7. `share`
   - `interest +8`

### 3.4 当前推荐相关数据表

推荐算法测试重点看这 4 张表：

1. `user_category_interest_profiles`
2. `user_tag_interest_profiles`
3. `user_author_interest_profiles`
4. `content_recommendation_impressions`

表结构定义在：

1. [recommendation/models.py](/G:/Code_Warehouse/LingLearn_Cloud/Server/app/modules/recommendation/models.py)

---

## 4. 测试前置条件

### 4.1 服务要求

测试前请确认：

1. 后端已经启动
2. 数据库可以正常连接
3. 首页 feed 可以正常返回数据
4. 已经有一批公开视频可供推荐

推荐启动命令：

```powershell
cd G:\Code_Warehouse\LingLearn_Cloud\Server
E:\Interpreter\Python_Conda\envs\ai-service\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4.2 内容前置要求

为了让推荐算法可测，推荐库里的内容必须满足：

1. `visibility = public`
2. `audit_status = approved`
3. `publish_status = published`
4. `published_at` 不为空
5. `category_id` 最好不为空

特别注意：

1. 如果 `category_id` 为 `NULL`，则 `user_category_interest_profiles` 不会写入。
2. 如果视频没有标签，则 `user_tag_interest_profiles` 的信号会偏弱。

### 4.3 分类前置要求

当前发布页已接入真实分类接口：

```text
GET /api/v1/discover/categories
```

默认分类会在首次访问时自动初始化为：

1. 编程
2. 算法
3. 前端
4. 后端
5. 数据库
6. AI/ML

### 4.4 测试账号建议

建议准备 3 类账号：

1. 冷启动账号
   - 没有任何观看、点赞、收藏、评论、分享行为
2. 轻度活跃账号
   - 有少量观看和点赞
3. 强偏好账号
   - 明显偏向某一分类或某一作者

如果你使用批量脚本生成的数据，可以优先使用：

1. `seeduser_01`
2. `seeduser_02`
3. `seeduser_03`
4. `seeduser_04`

默认密码：

```text
SeedUser123
```

---

## 5. 测试目标与验收标准

### 5.1 最小验收标准

算法执行最小验收标准：

1. 调用 `for_you` 后，`content_recommendation_impressions` 有新增记录。
2. 用户做行为后，至少有一张兴趣画像表发生更新。
3. 同一账号行为变化后，再次请求 `for_you`，结果顺序发生变化。

### 5.2 完整验收标准

完整推荐验收标准：

1. 冷启动用户能拿到推荐内容。
2. 冷启动用户曝光日志写入成功。
3. 老用户的分类、标签、作者画像能被实时更新。
4. 用户偏好的分类在推荐中占比提升。
5. 用户偏好的作者在推荐中更容易出现。
6. 最近看过的内容不会反复刷屏。
7. `recall_source` 能反映不同召回来源。

---

## 6. 测试总流程

推荐按下面顺序测试：

1. 测接口是否可访问
2. 测冷启动是否生效
3. 测曝光日志是否写入
4. 测用户行为是否写画像
5. 测推荐结果是否偏移
6. 测关注流与推荐流是否隔离
7. 测异常和边界情况

---

## 7. 第一步：获取登录 Token

### 7.1 登录接口

当前登录接口：

```text
POST /api/v1/auth/login
```

请求结构：

```json
{
  "account": "seeduser_01",
  "password": "SeedUser123",
  "device_id": "algo-test-device-01"
}
```

### 7.2 curl 示例

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"account\":\"seeduser_01\",\"password\":\"SeedUser123\",\"device_id\":\"algo-test-device-01\"}"
```

### 7.3 预期结果

预期返回：

1. `code = 0`
2. `data.access_token` 非空
3. `data.user_id` 正确

后续所有推荐测试都使用这个 `access_token`。

---

## 8. 第二步：验证首页推荐接口是否执行

### 8.1 请求接口

```powershell
curl "http://127.0.0.1:8000/api/v1/feed/videos?recommend_type=for_you&limit=10" ^
  -H "Authorization: Bearer 你的token"
```

### 8.2 预期结果

预期：

1. 返回 `200`
2. `code = 0`
3. `data.list` 长度大于 0
4. 每条内容都有 `id`
5. 作者信息、互动信息、分类信息可正常返回

### 8.3 失败排查

如果这里失败，优先检查：

1. 后端是否正常启动
2. token 是否有效
3. 数据库是否可连接
4. 是否存在可推荐内容

---

## 9. 第三步：验证曝光日志是否写入

### 9.1 关键表

```text
content_recommendation_impressions
```

### 9.2 SQL

```sql
SELECT
  id,
  user_id,
  content_item_id,
  scene_code,
  recommend_type,
  recall_source,
  session_id,
  position_no,
  rank_score,
  shown_at,
  clicked_at,
  watch_seconds,
  watch_progress,
  completed,
  liked,
  favorited,
  commented,
  shared
FROM content_recommendation_impressions
WHERE user_id = 你的用户ID
ORDER BY id DESC
LIMIT 20;
```

### 9.3 预期结果

只要执行过一次 `for_you`，这里就应该有新增记录。

重点看：

1. `recommend_type = 'for_you'`
2. `scene_code = 'for_you'`
3. `position_no` 从 1 开始递增
4. `recall_source` 有值
5. `rank_score` 有值

### 9.4 结论判断

如果该表没有新增数据，说明：

1. 推荐服务没有真正执行到曝光写入
2. 或者事务没有提交成功

如果该表有新增，则说明算法已经实际执行过。

---

## 10. 第四步：验证冷启动推荐

### 10.1 冷启动定义

当前实现里，如果用户没有兴趣画像，则 `for_you` 自动走冷启动。

实现判断位于：

1. [RecommendationService.list_for_you_rows(...)](/G:/Code_Warehouse/LingLearn_Cloud/Server/app/modules/recommendation/service.py)

判断逻辑：

1. 查询用户是否已有画像
2. 如果没有，则走 `_build_cold_start_rows(...)`

### 10.2 测试步骤

1. 使用一个新注册账号登录
2. 不进行任何点赞、收藏、评论、观看上报
3. 直接请求：

```powershell
curl "http://127.0.0.1:8000/api/v1/feed/videos?recommend_type=for_you&limit=10" ^
  -H "Authorization: Bearer 新用户token"
```

### 10.3 预期结果

预期：

1. 有推荐内容返回
2. 不报错
3. 曝光日志写入成功
4. `recall_source` 主要是 `cold_start`

### 10.4 SQL

```sql
SELECT
  id,
  content_item_id,
  recall_source,
  rank_score,
  shown_at
FROM content_recommendation_impressions
WHERE user_id = 新用户ID
ORDER BY id DESC
LIMIT 20;
```

---

## 11. 第五步：验证行为驱动兴趣画像更新

### 11.1 要测的行为

推荐至少测 5 类正向行为：

1. 观看进度上报
2. 点赞
3. 收藏
4. 评论
5. 分享

### 11.2 推荐测试顺序

建议按这个顺序触发：

1. 先请求一次 `for_you`
2. 记下列表中的一个内容 ID
3. 对这个内容做观看上报
4. 然后点赞
5. 然后收藏
6. 然后评论
7. 然后分享

### 11.3 测试接口

#### 观看进度

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/contents/内容ID/watch-progress" ^
  -H "Authorization: Bearer 你的token" ^
  -H "Content-Type: application/json" ^
  -d "{\"watch_seconds\":20,\"watch_progress\":80,\"last_position_seconds\":20,\"completed\":false}"
```

#### 点赞

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/contents/内容ID/like" ^
  -H "Authorization: Bearer 你的token"
```

#### 收藏

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/contents/内容ID/favorite" ^
  -H "Authorization: Bearer 你的token"
```

#### 评论

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/contents/内容ID/comments" ^
  -H "Authorization: Bearer 你的token" ^
  -H "Content-Type: application/json" ^
  -d "{\"content\":\"推荐算法测试评论\"}"
```

#### 分享

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/contents/内容ID/share" ^
  -H "Authorization: Bearer 你的token" ^
  -H "Content-Type: application/json" ^
  -d "{\"share_channel\":\"internal\"}"
```

### 11.4 预期结果

预期：

1. 所有接口返回 `200`
2. `code = 0`
3. 对应互动计数发生变化
4. 推荐画像表发生变化

---

## 12. 第六步：验证分类画像是否更新

### 12.1 关键前提

要让分类画像写入，目标内容必须有 `category_id`。

如果 `content_items.category_id` 为空，那么：

1. `user_category_interest_profiles` 不会新增
2. 这是正常现象，不代表推荐没执行

### 12.2 先查目标内容分类

```sql
SELECT id, title, category_id, author_id
FROM content_items
WHERE id = 目标内容ID;
```

### 12.3 查分类画像

```sql
SELECT
  id,
  user_id,
  category_id,
  interest_score,
  watch_score,
  like_score,
  favorite_score,
  comment_score,
  share_score,
  complete_score,
  negative_score,
  last_interaction_at,
  created_at,
  updated_at
FROM user_category_interest_profiles
WHERE user_id = 你的用户ID
ORDER BY interest_score DESC, updated_at DESC;
```

### 12.4 预期结果

如果目标内容有分类，那么：

1. 第一次行为后，应新增一条分类画像记录
2. 后续点赞、收藏、评论、分享会继续累加分数
3. `last_interaction_at` 会更新

### 12.5 推荐验收方法

建议连续做：

1. 一次观看进度上报
2. 一次点赞
3. 一次收藏
4. 一次评论

然后再查分数变化。

---

## 13. 第七步：验证标签画像是否更新

### 13.1 SQL

```sql
SELECT
  id,
  user_id,
  tag_id,
  interest_score,
  watch_score,
  like_score,
  favorite_score,
  comment_score,
  share_score,
  complete_score,
  negative_score,
  last_interaction_at,
  created_at,
  updated_at
FROM user_tag_interest_profiles
WHERE user_id = 你的用户ID
ORDER BY interest_score DESC, updated_at DESC;
```

### 13.2 预期结果

预期：

1. 只要内容有标签，标签画像就应写入
2. 同一行为会按内容标签均摊分值
3. 标签分数比分类更细粒度

### 13.3 重点说明

如果分类画像为空、标签画像有值，通常代表：

1. 内容带了 `hashtags`
2. 但内容没有 `category_id`

---

## 14. 第八步：验证作者画像是否更新

### 14.1 SQL

```sql
SELECT
  id,
  user_id,
  author_id,
  interest_score,
  watch_score,
  like_score,
  favorite_score,
  comment_score,
  share_score,
  complete_score,
  negative_score,
  last_interaction_at,
  created_at,
  updated_at
FROM user_author_interest_profiles
WHERE user_id = 你的用户ID
ORDER BY interest_score DESC, updated_at DESC;
```

### 14.2 预期结果

预期：

1. 只要用户和某作者内容发生有效行为，就会产生作者画像
2. 多次互动同一作者，分数持续增长
3. 后续推荐中，该作者内容更容易进入前列

---

## 15. 第九步：验证曝光反馈字段是否被回写

### 15.1 背景

推荐算法不只是写曝光，还会随着用户行为反向更新最新曝光记录的反馈字段。

写入逻辑位于：

1. [RecommendationService.update_impression_feedback(...)](/G:/Code_Warehouse/LingLearn_Cloud/Server/app/modules/recommendation/service.py)

### 15.2 SQL

```sql
SELECT
  id,
  user_id,
  content_item_id,
  clicked_at,
  watch_seconds,
  watch_progress,
  completed,
  liked,
  favorited,
  commented,
  shared,
  shown_at
FROM content_recommendation_impressions
WHERE user_id = 你的用户ID
  AND content_item_id = 目标内容ID
ORDER BY id DESC
LIMIT 10;
```

### 15.3 预期结果

当你做完行为后，最新那条曝光记录应该被更新：

1. 点赞后 `liked = true`
2. 收藏后 `favorited = true`
3. 评论后 `commented = true`
4. 分享后 `shared = true`
5. 观看上报后 `watch_seconds`、`watch_progress`、`completed` 变化
6. 发生点击或互动后 `clicked_at` 不为空

---

## 16. 第十步：验证推荐结果是否真的发生偏移

这是最重要的一步。

### 16.1 测试目标

验证推荐算法不是“只记数据不影响结果”，而是会让推荐排序真正发生变化。

### 16.2 测试步骤

#### 第一次请求

先请求一次：

```powershell
curl "http://127.0.0.1:8000/api/v1/feed/videos?recommend_type=for_you&limit=10" ^
  -H "Authorization: Bearer 你的token"
```

记下前 10 条：

1. 内容 ID
2. 分类
3. 作者
4. 标题

#### 制造兴趣偏好

选择同一个分类下的 3 到 5 个视频，做这些行为：

1. 每个视频上报一次观看进度
2. 对其中 2 个视频点赞
3. 对其中 1 到 2 个视频收藏
4. 对其中 1 个视频评论

#### 第二次请求

再次请求：

```powershell
curl "http://127.0.0.1:8000/api/v1/feed/videos?recommend_type=for_you&limit=10" ^
  -H "Authorization: Bearer 你的token"
```

### 16.3 预期结果

预期变化：

1. 你重点互动过的分类出现频率更高
2. 你重点互动过的作者更容易进入前列
3. 你完全没兴趣的内容占比下降
4. 已经完整看过的内容不应频繁重复出现

### 16.4 建议记录表

建议手工整理成对比表：

| 次数 | 排名 | 内容ID | 分类 | 作者 | 标题 |
| --- | --- | --- | --- | --- | --- |
| 第一次 | 1 |  |  |  |  |
| 第一次 | 2 |  |  |  |  |
| 第二次 | 1 |  |  |  |  |
| 第二次 | 2 |  |  |  |  |

---

## 17. 第十一步：验证召回来源是否变化

### 17.1 SQL

```sql
SELECT
  id,
  content_item_id,
  recall_source,
  rank_score,
  shown_at
FROM content_recommendation_impressions
WHERE user_id = 你的用户ID
ORDER BY id DESC
LIMIT 30;
```

### 17.2 预期结果

#### 冷启动用户

以 `cold_start`、`hot` 为主。

#### 已有偏好用户

应逐步出现更多：

1. `category`
2. `tag`
3. `author`
4. `explore`

### 17.3 判断逻辑

如果一个用户已经有明显兴趣画像，但 `recall_source` 长期只有 `cold_start` 或 `hot`，则说明：

1. 个性化召回没有生效
2. 或者用户画像为空
3. 或者内容侧缺少分类/标签/作者可匹配特征

---

## 18. 第十二步：验证最近看过内容是否被过滤或降权

### 18.1 背景

当前个性化推荐会读取用户最近看过的内容并尽量避免重复推荐。

### 18.2 SQL

```sql
SELECT
  id,
  user_id,
  content_item_id,
  view_date,
  view_count,
  watch_seconds,
  watch_progress,
  completed,
  last_viewed_at
FROM content_view_histories
WHERE user_id = 你的用户ID
ORDER BY last_viewed_at DESC
LIMIT 20;
```

### 18.3 验证方式

1. 连续完整看完一个视频
2. 再多次刷新首页 `for_you`
3. 观察该视频是否还频繁出现

### 18.4 预期结果

预期：

1. 最近已看且完成度高的视频应减少重复曝光
2. 不应连续多次刷到同一条内容

---

## 19. 第十三步：验证关注流与推荐流隔离

虽然这不是推荐核心本身，但需要确认没有串流。

### 19.1 请求关注流

```powershell
curl "http://127.0.0.1:8000/api/v1/feed/videos?recommend_type=following&limit=10" ^
  -H "Authorization: Bearer 你的token"
```

### 19.2 请求推荐流

```powershell
curl "http://127.0.0.1:8000/api/v1/feed/videos?recommend_type=for_you&limit=10" ^
  -H "Authorization: Bearer 你的token"
```

### 19.3 预期结果

预期：

1. `following` 只看关注作者内容
2. `for_you` 走推荐算法
3. 两者结果明显不同

---

## 20. 第十四步：异常与边界测试

### 20.1 无分类内容

准备一个 `category_id = NULL` 的内容，执行行为后检查：

1. 分类画像不写入
2. 标签画像、作者画像仍可能写入

这是正常行为。

### 20.2 无标签内容

准备一个没有标签的内容，执行行为后检查：

1. 标签画像不写入
2. 分类画像、作者画像仍可能写入

### 20.3 匿名用户请求 `for_you`

不带 token 请求：

```powershell
curl "http://127.0.0.1:8000/api/v1/feed/videos?recommend_type=for_you&limit=10"
```

预期：

1. 仍可拿到内容
2. 但不会为匿名用户写用户级画像

### 20.4 重复点赞

连续多次点赞同一个内容：

预期：

1. 点赞接口具备幂等性
2. 不应无限重复累加兴趣分

### 20.5 收藏后取消收藏

先收藏，再取消收藏：

预期：

1. `favorite_score` 先增加
2. `unfavorite` 后兴趣分出现回调

### 20.6 点赞后取消点赞

先点赞，再取消点赞：

预期：

1. `like_score` 先增加
2. `unlike` 后兴趣分出现回调

---

## 21. 常用 SQL 清单

### 21.1 查用户

```sql
SELECT id, username, email
FROM users
ORDER BY id;
```

### 21.2 查内容及分类

```sql
SELECT id, title, author_id, category_id, hashtags_json, published_at
FROM content_items
ORDER BY id DESC
LIMIT 30;
```

### 21.3 查分类表

```sql
SELECT id, name, slug, status
FROM content_categories
ORDER BY id;
```

### 21.4 查分类画像

```sql
SELECT *
FROM user_category_interest_profiles
WHERE user_id = 你的用户ID
ORDER BY interest_score DESC, updated_at DESC;
```

### 21.5 查标签画像

```sql
SELECT *
FROM user_tag_interest_profiles
WHERE user_id = 你的用户ID
ORDER BY interest_score DESC, updated_at DESC;
```

### 21.6 查作者画像

```sql
SELECT *
FROM user_author_interest_profiles
WHERE user_id = 你的用户ID
ORDER BY interest_score DESC, updated_at DESC;
```

### 21.7 查曝光日志

```sql
SELECT *
FROM content_recommendation_impressions
WHERE user_id = 你的用户ID
ORDER BY id DESC
LIMIT 50;
```

### 21.8 查观看历史

```sql
SELECT *
FROM content_view_histories
WHERE user_id = 你的用户ID
ORDER BY last_viewed_at DESC
LIMIT 50;
```

---

## 22. 常见问题与排查

### 22.1 `user_category_interest_profiles` 一直为空

优先检查：

1. `content_items.category_id` 是否为空
2. 发布页是否正确提交了 `category_id`
3. 当前测试内容是否真的有分类

### 22.2 `content_recommendation_impressions` 没有新增

优先检查：

1. 首页请求是否真的走 `recommend_type=for_you`
2. 后端事务是否提交
3. 推荐服务是否在 `list_feed_videos(...)` 中被调用

### 22.3 行为后标签画像更新了，但分类画像没更新

通常是：

1. 内容有标签
2. 内容没有 `category_id`

### 22.4 推荐结果一直没变化

优先检查：

1. 行为是否真的成功写入
2. 画像表分数是否变化
3. 推荐内容池是否足够丰富
4. 测试账号是否总在重复刷很少几条内容

### 22.5 冷启动用户也出现很多 `category/tag/author`

说明：

1. 该用户其实已经有画像
2. 不是冷启动账号

需要先查三张画像表是否已有数据。

---

## 23. 建议测试节奏

推荐按这个节奏跑：

### 第一轮

1. 登录
2. 调一次 `for_you`
3. 查曝光日志

目标：

1. 证明算法有执行

### 第二轮

1. 对一个内容做观看、点赞、收藏、评论
2. 查三张画像表

目标：

1. 证明行为能更新画像

### 第三轮

1. 对某一分类集中做 5 到 10 次行为
2. 再调 `for_you`
3. 对比结果排序

目标：

1. 证明推荐结果会偏移

### 第四轮

1. 用全新账号测冷启动
2. 用老账号测个性化
3. 对比 `recall_source`

目标：

1. 证明冷启动与个性化两套路径都工作正常

---

## 24. 最终结论判定模板

测试结束后，可以按下面格式记录结果：

### 24.1 算法执行判定

1. `for_you` 接口是否成功：是 / 否
2. 曝光日志是否写入：是 / 否
3. 分类画像是否更新：是 / 否
4. 标签画像是否更新：是 / 否
5. 作者画像是否更新：是 / 否
6. 推荐排序是否发生偏移：是 / 否
7. 冷启动是否生效：是 / 否
8. 关注流与推荐流是否隔离：是 / 否

### 24.2 结论示例

可用示例：

```text
推荐算法第一期已执行。
for_you 请求可写入曝光日志，观看/点赞/收藏/评论可更新画像表，
并且用户偏好行为会影响后续推荐结果排序。
当前功能满足冷启动、基础个性化推荐和行为反馈闭环测试要求。
```

---

## 25. 后续建议

完成本文档测试后，建议继续补两类能力：

1. 定时任务测试
   - 热度重算
   - 兴趣衰减
2. 推荐效果监控
   - CTR
   - 完播率
   - 收藏率
   - 评论率

这样就能从“算法已执行”进一步走到“算法效果可评估”。
