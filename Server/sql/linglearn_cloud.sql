/*
 Navicat Premium Dump SQL

 Source Server         : Aliyun_MySQL
 Source Server Type    : MySQL
 Source Server Version : 90001 (9.0.1)
 Source Host           : 47.109.194.175:3306
 Source Schema         : linglearn_cloud

 Target Server Type    : MySQL
 Target Server Version : 90001 (9.0.1)
 File Encoding         : 65001

 Date: 01/05/2026 15:00:20
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for ai_chat_messages
-- ----------------------------
DROP TABLE IF EXISTS `ai_chat_messages`;
CREATE TABLE `ai_chat_messages`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `session_id` bigint UNSIGNED NOT NULL COMMENT '会话ID',
  `role` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '消息角色：系统、用户、助手、工具',
  `message_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'text' COMMENT '消息类型',
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '内容正文',
  `token_count` int UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Token数量',
  `latency_ms` int UNSIGNED NULL DEFAULT NULL COMMENT '耗时（毫秒）',
  `error_code` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '错误码',
  `trace_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '追踪ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_ai_messages_session_created`(`session_id` ASC, `created_at` ASC) USING BTREE,
  CONSTRAINT `fk_ai_messages_session_id` FOREIGN KEY (`session_id`) REFERENCES `ai_chat_sessions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = 'AI对话消息表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for ai_chat_sessions
-- ----------------------------
DROP TABLE IF EXISTS `ai_chat_sessions`;
CREATE TABLE `ai_chat_sessions`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `session_name` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '会话名称',
  `scene_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'study_assistant' COMMENT '场景编码',
  `model_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'glm-4-flash' COMMENT '模型名称',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'active' COMMENT '状态',
  `summary` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '摘要',
  `last_message_at` datetime NULL DEFAULT NULL COMMENT '最后消息时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_ai_sessions_user_status_last`(`user_id` ASC, `status` ASC, `last_message_at` DESC) USING BTREE,
  CONSTRAINT `fk_ai_sessions_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = 'AI对话会话表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for ai_workflow_runs
-- ----------------------------
DROP TABLE IF EXISTS `ai_workflow_runs`;
CREATE TABLE `ai_workflow_runs`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '用户ID',
  `workflow_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '工作流类型：画像、路径、月报、导师回复',
  `biz_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '业务类型',
  `biz_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '业务ID',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'running' COMMENT '状态',
  `input_json` json NULL COMMENT '工作流输入JSON',
  `output_json` json NULL COMMENT '工作流输出JSON',
  `error_message` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '错误信息',
  `started_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
  `finished_at` datetime NULL DEFAULT NULL COMMENT '结束时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_ai_workflow_type_status`(`workflow_type` ASC, `status` ASC, `created_at` DESC) USING BTREE,
  INDEX `idx_ai_workflow_biz`(`biz_type` ASC, `biz_id` ASC) USING BTREE,
  INDEX `idx_ai_workflow_user_type`(`user_id` ASC, `workflow_type` ASC, `created_at` DESC) USING BTREE,
  CONSTRAINT `fk_ai_workflows_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = 'LangGraph工作流运行表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for assessment_snapshots
-- ----------------------------
DROP TABLE IF EXISTS `assessment_snapshots`;
CREATE TABLE `assessment_snapshots`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `assessment_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'weekly' COMMENT '评估类型：日、周、月',
  `period_start` date NOT NULL COMMENT '周期开始日期',
  `period_end` date NOT NULL COMMENT '周期结束日期',
  `total_learning_minutes` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '累计学习分钟数',
  `completed_courses` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '完成课程数',
  `average_score` decimal(5, 2) NOT NULL DEFAULT 0.00 COMMENT '平均分',
  `rank_percent` decimal(5, 2) NULL DEFAULT NULL COMMENT '排名百分位',
  `correct_rate` decimal(5, 2) NULL DEFAULT NULL COMMENT '正确率',
  `focus_rate` decimal(5, 2) NULL DEFAULT NULL COMMENT '专注度',
  `metrics_json` json NULL COMMENT '指标汇总JSON',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_assessment_period`(`user_id` ASC, `assessment_type` ASC, `period_start` ASC, `period_end` ASC) USING BTREE,
  INDEX `idx_assessment_user_type_period`(`user_id` ASC, `assessment_type` ASC, `period_start` DESC) USING BTREE,
  CONSTRAINT `fk_assessment_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '学习评估快照表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for audit_logs
-- ----------------------------
DROP TABLE IF EXISTS `audit_logs`;
CREATE TABLE `audit_logs`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '用户ID',
  `module_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模块名称',
  `action_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '动作名称',
  `biz_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '业务类型',
  `biz_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '业务ID',
  `request_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '请求ID',
  `ip_address` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'IP地址',
  `user_agent` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户代理',
  `detail_json` json NULL COMMENT '详情JSON',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_audit_module_action_created`(`module_name` ASC, `action_name` ASC, `created_at` DESC) USING BTREE,
  INDEX `idx_audit_biz`(`biz_type` ASC, `biz_id` ASC) USING BTREE,
  INDEX `idx_audit_user_created`(`user_id` ASC, `created_at` DESC) USING BTREE,
  CONSTRAINT `fk_audit_logs_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '审计日志表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for badge_catalog
-- ----------------------------
DROP TABLE IF EXISTS `badge_catalog`;
CREATE TABLE `badge_catalog`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `code` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '业务编码',
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '名称',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '描述',
  `icon` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '图标',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'active' COMMENT '状态',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_badge_code`(`code` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '徽章字典表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for content_categories
-- ----------------------------
DROP TABLE IF EXISTS `content_categories`;
CREATE TABLE `content_categories`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `parent_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '父级记录ID',
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '名称',
  `slug` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '唯一标识Slug',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '描述',
  `icon` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '图标',
  `sort_order` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'active' COMMENT '状态',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_categories_slug`(`slug` ASC) USING BTREE,
  UNIQUE INDEX `uk_categories_name`(`name` ASC) USING BTREE,
  INDEX `idx_categories_parent_sort`(`parent_id` ASC, `sort_order` ASC) USING BTREE,
  CONSTRAINT `fk_categories_parent_id` FOREIGN KEY (`parent_id`) REFERENCES `content_categories` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '业务分类表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for content_comments
-- ----------------------------
DROP TABLE IF EXISTS `content_comments`;
CREATE TABLE `content_comments`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `content_item_id` bigint UNSIGNED NOT NULL COMMENT '内容ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `parent_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '父级记录ID',
  `root_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '根评论ID',
  `reply_to_user_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '回复目标用户ID',
  `content` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '内容正文',
  `like_count` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '点赞数',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'normal' COMMENT '状态',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime NULL DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_comments_content_parent_created`(`content_item_id` ASC, `parent_id` ASC, `created_at` DESC) USING BTREE,
  INDEX `idx_comments_root_created`(`root_id` ASC, `created_at` DESC) USING BTREE,
  INDEX `idx_comments_user_created`(`user_id` ASC, `created_at` DESC) USING BTREE,
  INDEX `fk_comments_parent_id`(`parent_id` ASC) USING BTREE,
  INDEX `fk_comments_reply_to_user_id`(`reply_to_user_id` ASC) USING BTREE,
  CONSTRAINT `fk_comments_content_item_id` FOREIGN KEY (`content_item_id`) REFERENCES `content_items` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_comments_parent_id` FOREIGN KEY (`parent_id`) REFERENCES `content_comments` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_comments_reply_to_user_id` FOREIGN KEY (`reply_to_user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_comments_root_id` FOREIGN KEY (`root_id`) REFERENCES `content_comments` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_comments_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 19 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '内容评论表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for content_favorites
-- ----------------------------
DROP TABLE IF EXISTS `content_favorites`;
CREATE TABLE `content_favorites`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `content_item_id` bigint UNSIGNED NOT NULL COMMENT '内容ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_content_favorite`(`user_id` ASC, `content_item_id` ASC) USING BTREE,
  INDEX `idx_favorites_content_created`(`content_item_id` ASC, `created_at` DESC) USING BTREE,
  INDEX `idx_favorites_user_created`(`user_id` ASC, `created_at` DESC) USING BTREE,
  CONSTRAINT `fk_favorites_content_item_id` FOREIGN KEY (`content_item_id`) REFERENCES `content_items` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_favorites_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '内容收藏表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for content_item_tags
-- ----------------------------
DROP TABLE IF EXISTS `content_item_tags`;
CREATE TABLE `content_item_tags`  (
  `content_item_id` bigint UNSIGNED NOT NULL COMMENT '内容ID',
  `tag_id` bigint UNSIGNED NOT NULL COMMENT '标签ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`content_item_id`, `tag_id`) USING BTREE,
  INDEX `idx_content_item_tags_tag_id`(`tag_id` ASC, `content_item_id` ASC) USING BTREE,
  CONSTRAINT `fk_content_item_tags_content_item_id` FOREIGN KEY (`content_item_id`) REFERENCES `content_items` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_content_item_tags_tag_id` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '内容标签关联表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for content_items
-- ----------------------------
DROP TABLE IF EXISTS `content_items`;
CREATE TABLE `content_items`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `author_id` bigint UNSIGNED NOT NULL COMMENT '作者用户ID',
  `category_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '分类ID',
  `title` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '标题',
  `summary` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '摘要',
  `content_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'short_video' COMMENT '内容类型',
  `source_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'original' COMMENT '来源类型',
  `visibility` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'public' COMMENT '可见范围',
  `audit_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'approved' COMMENT '审核状态',
  `publish_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'published' COMMENT '发布状态',
  `cover_asset_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '封面资源ID',
  `primary_media_asset_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '主媒体资源ID',
  `external_video_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '外部视频URL',
  `bvid` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '外部视频平台标识',
  `duration_seconds` int UNSIGNED NULL DEFAULT NULL COMMENT '时长（秒）',
  `hashtags_json` json NULL COMMENT '话题标签JSON',
  `allow_comment` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否允许评论',
  `allow_duet` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否允许合拍',
  `has_quiz` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否启用答题互动',
  `quiz_count` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '题目数量',
  `views_count` bigint UNSIGNED NOT NULL DEFAULT 0 COMMENT '浏览次数',
  `likes_count` bigint UNSIGNED NOT NULL DEFAULT 0 COMMENT '点赞次数',
  `comments_count` bigint UNSIGNED NOT NULL DEFAULT 0 COMMENT '评论次数',
  `favorites_count` bigint UNSIGNED NOT NULL DEFAULT 0 COMMENT '收藏次数',
  `shares_count` bigint UNSIGNED NOT NULL DEFAULT 0 COMMENT '分享次数',
  `hot_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '推荐热度分数',
  `published_at` datetime NULL DEFAULT NULL COMMENT '发布时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime NULL DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_content_items_bvid`(`bvid` ASC) USING BTREE,
  INDEX `idx_content_author_status_publish`(`author_id` ASC, `publish_status` ASC, `published_at` DESC) USING BTREE,
  INDEX `idx_content_category_status_publish`(`category_id` ASC, `publish_status` ASC, `published_at` DESC) USING BTREE,
  INDEX `idx_content_type_status_publish`(`content_type` ASC, `publish_status` ASC, `published_at` DESC) USING BTREE,
  INDEX `idx_content_hot_score`(`publish_status` ASC, `hot_score` DESC, `published_at` DESC) USING BTREE,
  INDEX `idx_content_audit_status`(`audit_status` ASC, `publish_status` ASC) USING BTREE,
  INDEX `fk_content_cover_asset_id`(`cover_asset_id` ASC) USING BTREE,
  INDEX `fk_content_primary_media_asset_id`(`primary_media_asset_id` ASC) USING BTREE,
  FULLTEXT INDEX `ft_content_title_summary`(`title`, `summary`),
  CONSTRAINT `fk_content_author_id` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_content_category_id` FOREIGN KEY (`category_id`) REFERENCES `content_categories` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_content_cover_asset_id` FOREIGN KEY (`cover_asset_id`) REFERENCES `media_assets` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_content_primary_media_asset_id` FOREIGN KEY (`primary_media_asset_id`) REFERENCES `media_assets` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 15 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '短视频与用户作品表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for content_likes
-- ----------------------------
DROP TABLE IF EXISTS `content_likes`;
CREATE TABLE `content_likes`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `content_item_id` bigint UNSIGNED NOT NULL COMMENT '内容ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_content_like`(`user_id` ASC, `content_item_id` ASC) USING BTREE,
  INDEX `idx_likes_content_created`(`content_item_id` ASC, `created_at` DESC) USING BTREE,
  CONSTRAINT `fk_likes_content_item_id` FOREIGN KEY (`content_item_id`) REFERENCES `content_items` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_likes_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 15 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '内容点赞表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for content_quiz_attempts
-- ----------------------------
DROP TABLE IF EXISTS `content_quiz_attempts`;
CREATE TABLE `content_quiz_attempts`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `quiz_id` bigint UNSIGNED NOT NULL COMMENT '互动题ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `selected_option_id` bigint UNSIGNED NOT NULL COMMENT '所选选项ID',
  `is_correct` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否正确',
  `submitted_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
  `client_ip` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '客户端IP',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_quiz_attempt_user`(`quiz_id` ASC, `user_id` ASC) USING BTREE,
  INDEX `idx_quiz_attempts_user_submitted`(`user_id` ASC, `submitted_at` DESC) USING BTREE,
  INDEX `idx_quiz_attempts_option_id`(`selected_option_id` ASC) USING BTREE,
  CONSTRAINT `fk_quiz_attempts_quiz_id` FOREIGN KEY (`quiz_id`) REFERENCES `content_quizzes` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_quiz_attempts_selected_option_id` FOREIGN KEY (`selected_option_id`) REFERENCES `content_quiz_options` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_quiz_attempts_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '互动题作答记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for content_quiz_options
-- ----------------------------
DROP TABLE IF EXISTS `content_quiz_options`;
CREATE TABLE `content_quiz_options`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `quiz_id` bigint UNSIGNED NOT NULL COMMENT '互动题ID',
  `option_text` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '选项内容',
  `option_order` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '选项顺序',
  `vote_count` bigint UNSIGNED NOT NULL DEFAULT 0 COMMENT '投票数',
  `is_correct` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否正确',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_quiz_option_order`(`quiz_id` ASC, `option_order` ASC) USING BTREE,
  INDEX `idx_quiz_options_quiz_order`(`quiz_id` ASC, `option_order` ASC) USING BTREE,
  CONSTRAINT `fk_quiz_options_quiz_id` FOREIGN KEY (`quiz_id`) REFERENCES `content_quizzes` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '互动题选项表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for content_quizzes
-- ----------------------------
DROP TABLE IF EXISTS `content_quizzes`;
CREATE TABLE `content_quizzes`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `content_item_id` bigint UNSIGNED NOT NULL COMMENT '内容ID',
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '标题',
  `description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '描述',
  `quiz_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'single_choice_poll' COMMENT '互动题类型',
  `sort_order` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'published' COMMENT '状态',
  `total_votes` bigint UNSIGNED NOT NULL DEFAULT 0 COMMENT '总投票数',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_content_quiz_sort`(`content_item_id` ASC, `sort_order` ASC) USING BTREE,
  INDEX `idx_quizzes_content_status`(`content_item_id` ASC, `status` ASC, `sort_order` ASC) USING BTREE,
  CONSTRAINT `fk_quizzes_content_item_id` FOREIGN KEY (`content_item_id`) REFERENCES `content_items` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '内容互动题表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for content_recommendation_impressions
-- ----------------------------
DROP TABLE IF EXISTS `content_recommendation_impressions`;
CREATE TABLE `content_recommendation_impressions`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `content_item_id` bigint UNSIGNED NOT NULL COMMENT '内容ID',
  `scene_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'for_you' COMMENT '推荐场景编码',
  `recommend_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'for_you' COMMENT '推荐类型',
  `recall_source` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '召回来源：hot、category、tag、author、explore、cold_start',
  `session_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '一次下发列表的会话ID',
  `position_no` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '在列表中的位置',
  `rank_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '排序分',
  `shown_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '曝光时间',
  `clicked_at` datetime NULL DEFAULT NULL COMMENT '点击时间',
  `watch_seconds` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '曝光后的观看秒数',
  `watch_progress` decimal(5, 2) NOT NULL DEFAULT 0.00 COMMENT '曝光后的观看进度',
  `completed` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否完播',
  `liked` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否点赞',
  `favorited` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否收藏',
  `commented` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否评论',
  `shared` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否分享',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_reco_impression_user_scene_time`(`user_id` ASC, `scene_code` ASC, `shown_at` DESC) USING BTREE,
  INDEX `idx_reco_impression_content_time`(`content_item_id` ASC, `shown_at` DESC) USING BTREE,
  INDEX `idx_reco_impression_session_pos`(`session_id` ASC, `position_no` ASC) USING BTREE,
  INDEX `idx_reco_impression_recall_source`(`recall_source` ASC, `shown_at` DESC) USING BTREE,
  CONSTRAINT `fk_reco_impression_content_item_id` FOREIGN KEY (`content_item_id`) REFERENCES `content_items` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_reco_impression_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 196 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '推荐曝光与反馈日志表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for content_shares
-- ----------------------------
DROP TABLE IF EXISTS `content_shares`;
CREATE TABLE `content_shares`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `content_item_id` bigint UNSIGNED NOT NULL COMMENT '内容ID',
  `share_channel` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'internal' COMMENT '分享渠道',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_shares_content_created`(`content_item_id` ASC, `created_at` DESC) USING BTREE,
  INDEX `idx_shares_user_created`(`user_id` ASC, `created_at` DESC) USING BTREE,
  CONSTRAINT `fk_shares_content_item_id` FOREIGN KEY (`content_item_id`) REFERENCES `content_items` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_shares_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '内容分享记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for content_view_histories
-- ----------------------------
DROP TABLE IF EXISTS `content_view_histories`;
CREATE TABLE `content_view_histories`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `content_item_id` bigint UNSIGNED NOT NULL COMMENT '内容ID',
  `view_date` date NOT NULL COMMENT '观看日期',
  `view_count` int UNSIGNED NOT NULL DEFAULT 1 COMMENT '查看次数',
  `watch_seconds` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '已观看秒数',
  `watch_progress` decimal(5, 2) NOT NULL DEFAULT 0.00 COMMENT '观看进度百分比',
  `last_position_seconds` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '最后播放位置（秒）',
  `completed` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否看完',
  `liked` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否点赞',
  `favorited` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否收藏',
  `last_viewed_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后观看时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_view_history_day`(`user_id` ASC, `content_item_id` ASC, `view_date` ASC) USING BTREE,
  INDEX `idx_view_history_user_last`(`user_id` ASC, `last_viewed_at` DESC) USING BTREE,
  INDEX `idx_view_history_content_date`(`content_item_id` ASC, `view_date` ASC) USING BTREE,
  CONSTRAINT `fk_view_history_content_item_id` FOREIGN KEY (`content_item_id`) REFERENCES `content_items` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_view_history_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 41 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '按日观看历史表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for course_lessons
-- ----------------------------
DROP TABLE IF EXISTS `course_lessons`;
CREATE TABLE `course_lessons`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `course_id` bigint UNSIGNED NOT NULL COMMENT '课程ID',
  `title` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '标题',
  `summary` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '摘要',
  `lesson_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'video' COMMENT '课时类型：视频、文章、测验、练习、直播',
  `sort_order` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  `estimated_minutes` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '预估分钟数',
  `content_item_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '内容ID',
  `resource_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '资源文件ID',
  `question_bank_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '题库ID',
  `unlock_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'free' COMMENT '解锁方式',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'published' COMMENT '状态',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_course_lesson_sort`(`course_id` ASC, `sort_order` ASC) USING BTREE,
  INDEX `idx_lessons_course_status_sort`(`course_id` ASC, `status` ASC, `sort_order` ASC) USING BTREE,
  INDEX `idx_lessons_content_item_id`(`content_item_id` ASC) USING BTREE,
  INDEX `idx_lessons_resource_id`(`resource_id` ASC) USING BTREE,
  INDEX `idx_lessons_question_bank_id`(`question_bank_id` ASC) USING BTREE,
  CONSTRAINT `fk_lessons_content_item_id` FOREIGN KEY (`content_item_id`) REFERENCES `content_items` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_lessons_course_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_lessons_question_bank_id` FOREIGN KEY (`question_bank_id`) REFERENCES `question_banks` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_lessons_resource_id` FOREIGN KEY (`resource_id`) REFERENCES `resources` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '课程课时表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for courses
-- ----------------------------
DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `category_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '分类ID',
  `title` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '标题',
  `summary` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '摘要',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '描述',
  `course_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'recorded' COMMENT '课程类型',
  `difficulty` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'beginner' COMMENT '难度等级',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'published' COMMENT '状态',
  `cover_asset_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '封面资源ID',
  `estimated_minutes` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '预估分钟数',
  `lesson_count` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '课时数量',
  `enrollment_count` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '报名人数',
  `completion_count` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '完成人数',
  `average_rating` decimal(3, 2) NOT NULL DEFAULT 0.00 COMMENT '平均评分',
  `published_at` datetime NULL DEFAULT NULL COMMENT '发布时间',
  `created_by` bigint UNSIGNED NULL DEFAULT NULL COMMENT '创建者用户ID',
  `updated_by` bigint UNSIGNED NULL DEFAULT NULL COMMENT '更新者用户ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime NULL DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_courses_category_status_publish`(`category_id` ASC, `status` ASC, `published_at` DESC) USING BTREE,
  INDEX `idx_courses_difficulty_status`(`difficulty` ASC, `status` ASC) USING BTREE,
  INDEX `fk_courses_cover_asset_id`(`cover_asset_id` ASC) USING BTREE,
  INDEX `fk_courses_created_by`(`created_by` ASC) USING BTREE,
  INDEX `fk_courses_updated_by`(`updated_by` ASC) USING BTREE,
  FULLTEXT INDEX `ft_courses_title_summary_description`(`title`, `summary`, `description`),
  CONSTRAINT `fk_courses_category_id` FOREIGN KEY (`category_id`) REFERENCES `content_categories` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_courses_cover_asset_id` FOREIGN KEY (`cover_asset_id`) REFERENCES `media_assets` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_courses_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_courses_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '课程主表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for learning_path_node_dimension_links
-- ----------------------------
DROP TABLE IF EXISTS `learning_path_node_dimension_links`;
CREATE TABLE `learning_path_node_dimension_links`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `node_id` bigint UNSIGNED NOT NULL COMMENT '节点ID',
  `dimension_id` bigint UNSIGNED NOT NULL COMMENT '能力维度ID',
  `match_score` decimal(5, 2) NULL DEFAULT NULL COMMENT '维度匹配分',
  `note` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_path_node_dimension`(`node_id` ASC, `dimension_id` ASC) USING BTREE,
  INDEX `idx_path_dimension_links_dimension_id`(`dimension_id` ASC) USING BTREE,
  CONSTRAINT `fk_path_dimension_links_dimension_id` FOREIGN KEY (`dimension_id`) REFERENCES `skill_dimensions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_path_dimension_links_node_id` FOREIGN KEY (`node_id`) REFERENCES `learning_path_nodes` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '路径节点能力维度关联表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for learning_path_nodes
-- ----------------------------
DROP TABLE IF EXISTS `learning_path_nodes`;
CREATE TABLE `learning_path_nodes`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `path_id` bigint UNSIGNED NOT NULL COMMENT '学习路径ID',
  `course_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '课程ID',
  `node_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'course' COMMENT '节点类型',
  `title` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '标题',
  `description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '描述',
  `sort_order` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  `default_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'locked' COMMENT '默认节点状态',
  `recommended_reason` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '推荐理由',
  `estimated_minutes` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '预估分钟数',
  `prerequisite_node_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '前置节点ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_learning_path_node_sort`(`path_id` ASC, `sort_order` ASC) USING BTREE,
  INDEX `idx_learning_path_nodes_path_sort`(`path_id` ASC, `sort_order` ASC) USING BTREE,
  INDEX `idx_learning_path_nodes_prerequisite`(`prerequisite_node_id` ASC) USING BTREE,
  INDEX `fk_learning_path_nodes_course_id`(`course_id` ASC) USING BTREE,
  CONSTRAINT `fk_learning_path_nodes_course_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_learning_path_nodes_path_id` FOREIGN KEY (`path_id`) REFERENCES `learning_paths` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_learning_path_nodes_prerequisite_node_id` FOREIGN KEY (`prerequisite_node_id`) REFERENCES `learning_path_nodes` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '学习路径节点表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for learning_paths
-- ----------------------------
DROP TABLE IF EXISTS `learning_paths`;
CREATE TABLE `learning_paths`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `path_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'template' COMMENT '路径类型：模板、个性化',
  `name` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '名称',
  `description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '描述',
  `target_role` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '目标岗位',
  `based_on_snapshot_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '基于画像快照ID',
  `created_by` bigint UNSIGNED NULL DEFAULT NULL COMMENT '创建者用户ID',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'active' COMMENT '状态',
  `is_default` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否默认模板',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_learning_paths_type_status`(`path_type` ASC, `status` ASC, `created_at` DESC) USING BTREE,
  INDEX `idx_learning_paths_snapshot`(`based_on_snapshot_id` ASC) USING BTREE,
  INDEX `fk_learning_paths_created_by`(`created_by` ASC) USING BTREE,
  CONSTRAINT `fk_learning_paths_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_learning_paths_snapshot_id` FOREIGN KEY (`based_on_snapshot_id`) REFERENCES `user_skill_snapshots` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '学习路径模板表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for media_assets
-- ----------------------------
DROP TABLE IF EXISTS `media_assets`;
CREATE TABLE `media_assets`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `bucket_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '对象存储桶名称',
  `object_key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '对象存储对象键',
  `original_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '原始文件名',
  `mime_type` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'MIME类型',
  `extension` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '文件扩展名',
  `asset_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '资源类型：头像、视频、封面、图片、PDF、文档、报告',
  `storage_provider` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'minio' COMMENT '存储提供方',
  `file_size` bigint UNSIGNED NOT NULL DEFAULT 0 COMMENT '文件大小（字节）',
  `checksum_sha256` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'SHA256校验值',
  `public_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '公开访问URL',
  `width` int UNSIGNED NULL DEFAULT NULL COMMENT '资源宽度',
  `height` int UNSIGNED NULL DEFAULT NULL COMMENT '资源高度',
  `duration_seconds` int UNSIGNED NULL DEFAULT NULL COMMENT '时长（秒）',
  `uploaded_by` bigint UNSIGNED NULL DEFAULT NULL COMMENT '上传者用户ID',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'active' COMMENT '状态',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_media_bucket_object`(`bucket_name` ASC, `object_key` ASC) USING BTREE,
  INDEX `idx_media_asset_type_status`(`asset_type` ASC, `status` ASC) USING BTREE,
  INDEX `idx_media_uploaded_by_type`(`uploaded_by` ASC, `asset_type` ASC, `created_at` ASC) USING BTREE,
  CONSTRAINT `fk_media_uploaded_by` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 26 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = 'MinIO资源元数据表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for monthly_reports
-- ----------------------------
DROP TABLE IF EXISTS `monthly_reports`;
CREATE TABLE `monthly_reports`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `report_month` char(7) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '报表月份（YYYY-MM）',
  `assessment_snapshot_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '评估快照ID',
  `report_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'generated' COMMENT '报告状态',
  `total_learning_minutes` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '累计学习分钟数',
  `completed_courses` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '完成课程数',
  `average_score` decimal(5, 2) NOT NULL DEFAULT 0.00 COMMENT '平均分',
  `site_rank` int UNSIGNED NULL DEFAULT NULL COMMENT '全站排名',
  `strengths_json` json NULL COMMENT '优势项JSON',
  `improvements_json` json NULL COMMENT '改进项JSON',
  `ai_summary` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT 'AI总结',
  `exported_pdf_asset_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '导出PDF资源ID',
  `generated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_monthly_report_user_month`(`user_id` ASC, `report_month` ASC) USING BTREE,
  INDEX `idx_monthly_reports_status`(`report_status` ASC, `generated_at` DESC) USING BTREE,
  INDEX `fk_monthly_reports_assessment_snapshot_id`(`assessment_snapshot_id` ASC) USING BTREE,
  INDEX `fk_monthly_reports_exported_pdf_asset_id`(`exported_pdf_asset_id` ASC) USING BTREE,
  CONSTRAINT `fk_monthly_reports_assessment_snapshot_id` FOREIGN KEY (`assessment_snapshot_id`) REFERENCES `assessment_snapshots` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_monthly_reports_exported_pdf_asset_id` FOREIGN KEY (`exported_pdf_asset_id`) REFERENCES `media_assets` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_monthly_reports_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '月度学习报告表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for notifications
-- ----------------------------
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE `notifications`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `notification_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '通知类型',
  `title` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '标题',
  `body` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '通知内容',
  `biz_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '业务类型',
  `biz_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '业务ID',
  `read_status` tinyint(1) NOT NULL DEFAULT 0 COMMENT '已读状态',
  `read_at` datetime NULL DEFAULT NULL COMMENT '已读时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_notifications_user_read_created`(`user_id` ASC, `read_status` ASC, `created_at` DESC) USING BTREE,
  INDEX `idx_notifications_biz`(`biz_type` ASC, `biz_id` ASC) USING BTREE,
  CONSTRAINT `fk_notifications_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '通知表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for practice_answers
-- ----------------------------
DROP TABLE IF EXISTS `practice_answers`;
CREATE TABLE `practice_answers`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `session_id` bigint UNSIGNED NOT NULL COMMENT '会话ID',
  `question_id` bigint UNSIGNED NOT NULL COMMENT '题目ID',
  `selected_option_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '所选选项ID',
  `answer_text` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '作答文本',
  `is_correct` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否正确',
  `score` decimal(5, 2) NOT NULL DEFAULT 0.00 COMMENT '得分',
  `answered_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '答题时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_practice_answer`(`session_id` ASC, `question_id` ASC) USING BTREE,
  INDEX `idx_practice_answers_question_answered`(`question_id` ASC, `answered_at` DESC) USING BTREE,
  INDEX `fk_practice_answers_selected_option_id`(`selected_option_id` ASC) USING BTREE,
  CONSTRAINT `fk_practice_answers_question_id` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_practice_answers_selected_option_id` FOREIGN KEY (`selected_option_id`) REFERENCES `question_options` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_practice_answers_session_id` FOREIGN KEY (`session_id`) REFERENCES `practice_sessions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '练习作答表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for practice_sessions
-- ----------------------------
DROP TABLE IF EXISTS `practice_sessions`;
CREATE TABLE `practice_sessions`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `bank_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '题库ID',
  `session_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'practice' COMMENT '会话类型',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'started' COMMENT '会话状态：已开始、已提交、已结束',
  `started_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
  `submitted_at` datetime NULL DEFAULT NULL COMMENT '提交时间',
  `finished_at` datetime NULL DEFAULT NULL COMMENT '结束时间',
  `duration_seconds` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '时长（秒）',
  `total_questions` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '总题数',
  `answered_questions` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '已答题数',
  `correct_questions` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '答对题数',
  `score` decimal(5, 2) NOT NULL DEFAULT 0.00 COMMENT '得分',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_practice_sessions_user_status_started`(`user_id` ASC, `status` ASC, `started_at` DESC) USING BTREE,
  INDEX `idx_practice_sessions_bank_started`(`bank_id` ASC, `started_at` DESC) USING BTREE,
  CONSTRAINT `fk_practice_sessions_bank_id` FOREIGN KEY (`bank_id`) REFERENCES `question_banks` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_practice_sessions_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '练习会话表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for question_banks
-- ----------------------------
DROP TABLE IF EXISTS `question_banks`;
CREATE TABLE `question_banks`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `category_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '分类ID',
  `name` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '名称',
  `description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '描述',
  `bank_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'practice' COMMENT '题库类型',
  `difficulty` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'mixed' COMMENT '难度等级',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'published' COMMENT '状态',
  `question_count` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '题目数量',
  `created_by` bigint UNSIGNED NULL DEFAULT NULL COMMENT '创建者用户ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_banks_category_type_status`(`category_id` ASC, `bank_type` ASC, `status` ASC) USING BTREE,
  INDEX `idx_banks_created_by`(`created_by` ASC, `created_at` DESC) USING BTREE,
  CONSTRAINT `fk_banks_category_id` FOREIGN KEY (`category_id`) REFERENCES `content_categories` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_banks_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '练习题库表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for question_options
-- ----------------------------
DROP TABLE IF EXISTS `question_options`;
CREATE TABLE `question_options`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `question_id` bigint UNSIGNED NOT NULL COMMENT '题目ID',
  `option_key` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '选项标识',
  `option_text` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '选项内容',
  `is_correct` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否正确',
  `sort_order` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_question_option_key`(`question_id` ASC, `option_key` ASC) USING BTREE,
  INDEX `idx_question_options_question_sort`(`question_id` ASC, `sort_order` ASC) USING BTREE,
  CONSTRAINT `fk_question_options_question_id` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '题目选项表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for questions
-- ----------------------------
DROP TABLE IF EXISTS `questions`;
CREATE TABLE `questions`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `bank_id` bigint UNSIGNED NOT NULL COMMENT '题库ID',
  `category_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '分类ID',
  `course_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '课程ID',
  `lesson_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '课时ID',
  `question_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'single_choice' COMMENT '题目类型',
  `difficulty` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'medium' COMMENT '难度等级',
  `stem` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '题干',
  `explanation` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '答案解析',
  `correct_answer_text` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '正确答案文本',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'published' COMMENT '状态',
  `sort_order` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_questions_bank_status_difficulty`(`bank_id` ASC, `status` ASC, `difficulty` ASC) USING BTREE,
  INDEX `idx_questions_course_lesson`(`course_id` ASC, `lesson_id` ASC) USING BTREE,
  INDEX `idx_questions_category_type`(`category_id` ASC, `question_type` ASC) USING BTREE,
  CONSTRAINT `fk_questions_bank_id` FOREIGN KEY (`bank_id`) REFERENCES `question_banks` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_questions_category_id` FOREIGN KEY (`category_id`) REFERENCES `content_categories` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_questions_course_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '题库题目表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for report_achievements
-- ----------------------------
DROP TABLE IF EXISTS `report_achievements`;
CREATE TABLE `report_achievements`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `report_id` bigint UNSIGNED NOT NULL COMMENT '报告ID',
  `title` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '标题',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '描述',
  `icon` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '图标',
  `color_token` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '颜色标识',
  `sort_order` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_report_achievements_report_sort`(`report_id` ASC, `sort_order` ASC) USING BTREE,
  CONSTRAINT `fk_report_achievements_report_id` FOREIGN KEY (`report_id`) REFERENCES `monthly_reports` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '报告成就表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for resources
-- ----------------------------
DROP TABLE IF EXISTS `resources`;
CREATE TABLE `resources`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `category_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '分类ID',
  `title` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '标题',
  `summary` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '摘要',
  `resource_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '资源类型：PDF、文档、图片、视频、文章、链接',
  `source_mode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'minio' COMMENT '资源来源：MinIO、外部链接',
  `asset_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '资源ID',
  `external_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '外部链接URL',
  `author_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '作者用户ID',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'published' COMMENT '状态',
  `download_count` bigint UNSIGNED NOT NULL DEFAULT 0 COMMENT '下载次数',
  `view_count` bigint UNSIGNED NOT NULL DEFAULT 0 COMMENT '查看次数',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime NULL DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_resources_category_type_status`(`category_id` ASC, `resource_type` ASC, `status` ASC) USING BTREE,
  INDEX `idx_resources_author_status`(`author_id` ASC, `status` ASC, `created_at` DESC) USING BTREE,
  INDEX `fk_resources_asset_id`(`asset_id` ASC) USING BTREE,
  FULLTEXT INDEX `ft_resources_title_summary`(`title`, `summary`),
  CONSTRAINT `fk_resources_asset_id` FOREIGN KEY (`asset_id`) REFERENCES `media_assets` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_resources_author_id` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_resources_category_id` FOREIGN KEY (`category_id`) REFERENCES `content_categories` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '学习资源表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for skill_dimensions
-- ----------------------------
DROP TABLE IF EXISTS `skill_dimensions`;
CREATE TABLE `skill_dimensions`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `code` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '业务编码',
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '名称',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '描述',
  `sort_order` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'active' COMMENT '状态',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_skill_dimensions_code`(`code` ASC) USING BTREE,
  INDEX `idx_skill_dimensions_sort`(`sort_order` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '能力维度字典表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for tags
-- ----------------------------
DROP TABLE IF EXISTS `tags`;
CREATE TABLE `tags`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '名称',
  `slug` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '唯一标识Slug',
  `tag_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'topic' COMMENT '标签类型',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'active' COMMENT '状态',
  `use_count` bigint UNSIGNED NOT NULL DEFAULT 0 COMMENT '使用次数',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_tags_name`(`name` ASC) USING BTREE,
  UNIQUE INDEX `uk_tags_slug`(`slug` ASC) USING BTREE,
  INDEX `idx_tags_type_use_count`(`tag_type` ASC, `use_count` DESC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 24 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '话题标签表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_author_interest_profiles
-- ----------------------------
DROP TABLE IF EXISTS `user_author_interest_profiles`;
CREATE TABLE `user_author_interest_profiles`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `author_id` bigint UNSIGNED NOT NULL COMMENT '作者用户ID',
  `interest_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '作者总兴趣分',
  `watch_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '观看贡献分',
  `like_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '点赞贡献分',
  `favorite_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '收藏贡献分',
  `comment_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '评论贡献分',
  `share_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '分享贡献分',
  `complete_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '完播贡献分',
  `negative_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '负反馈分',
  `last_interaction_at` datetime NULL DEFAULT NULL COMMENT '最近一次产生该作者行为的时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_author_interest`(`user_id` ASC, `author_id` ASC) USING BTREE,
  INDEX `idx_user_author_interest_score`(`user_id` ASC, `interest_score` DESC, `updated_at` DESC) USING BTREE,
  INDEX `idx_author_interest_author_score`(`author_id` ASC, `interest_score` DESC) USING BTREE,
  CONSTRAINT `fk_user_author_interest_author_id` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_user_author_interest_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户作者兴趣画像表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_badges
-- ----------------------------
DROP TABLE IF EXISTS `user_badges`;
CREATE TABLE `user_badges`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `badge_id` bigint UNSIGNED NOT NULL COMMENT '徽章ID',
  `source_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '来源类型',
  `source_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '来源记录ID',
  `granted_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '授予时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_badge`(`user_id` ASC, `badge_id` ASC) USING BTREE,
  INDEX `idx_user_badges_granted_at`(`user_id` ASC, `granted_at` DESC) USING BTREE,
  INDEX `fk_user_badges_badge_id`(`badge_id` ASC) USING BTREE,
  CONSTRAINT `fk_user_badges_badge_id` FOREIGN KEY (`badge_id`) REFERENCES `badge_catalog` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_user_badges_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户徽章记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_category_interest_profiles
-- ----------------------------
DROP TABLE IF EXISTS `user_category_interest_profiles`;
CREATE TABLE `user_category_interest_profiles`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `category_id` bigint UNSIGNED NOT NULL COMMENT '分类ID',
  `interest_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '分类总兴趣分',
  `watch_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '观看贡献分',
  `like_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '点赞贡献分',
  `favorite_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '收藏贡献分',
  `comment_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '评论贡献分',
  `share_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '分享贡献分',
  `complete_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '完播贡献分',
  `negative_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '负反馈分',
  `last_interaction_at` datetime NULL DEFAULT NULL COMMENT '最近一次产生该分类行为的时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_category_interest`(`user_id` ASC, `category_id` ASC) USING BTREE,
  INDEX `idx_user_category_interest_score`(`user_id` ASC, `interest_score` DESC, `updated_at` DESC) USING BTREE,
  INDEX `idx_category_interest_category_score`(`category_id` ASC, `interest_score` DESC) USING BTREE,
  CONSTRAINT `fk_user_category_interest_category_id` FOREIGN KEY (`category_id`) REFERENCES `content_categories` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_user_category_interest_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户分类兴趣画像表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_course_enrollments
-- ----------------------------
DROP TABLE IF EXISTS `user_course_enrollments`;
CREATE TABLE `user_course_enrollments`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `course_id` bigint UNSIGNED NOT NULL COMMENT '课程ID',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'learning' COMMENT '学习状态：学习中、暂停、已完成',
  `enrolled_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
  `started_at` datetime NULL DEFAULT NULL COMMENT '开始时间',
  `completed_at` datetime NULL DEFAULT NULL COMMENT '完成时间',
  `progress_percent` decimal(5, 2) NOT NULL DEFAULT 0.00 COMMENT '进度百分比',
  `completed_lessons` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '已完成课时数',
  `total_lessons` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '总课时数',
  `total_learning_minutes` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '累计学习分钟数',
  `last_lesson_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '最近学习课时ID',
  `last_learned_at` datetime NULL DEFAULT NULL COMMENT '最近学习时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_course_enrollment`(`user_id` ASC, `course_id` ASC) USING BTREE,
  INDEX `idx_enrollment_user_status`(`user_id` ASC, `status` ASC, `last_learned_at` DESC) USING BTREE,
  INDEX `idx_enrollment_course_status`(`course_id` ASC, `status` ASC) USING BTREE,
  INDEX `fk_enrollment_last_lesson_id`(`last_lesson_id` ASC) USING BTREE,
  CONSTRAINT `fk_enrollment_course_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_enrollment_last_lesson_id` FOREIGN KEY (`last_lesson_id`) REFERENCES `course_lessons` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_enrollment_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户课程报名进度表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_follow_relations
-- ----------------------------
DROP TABLE IF EXISTS `user_follow_relations`;
CREATE TABLE `user_follow_relations`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `follower_user_id` bigint UNSIGNED NOT NULL COMMENT '关注者用户ID',
  `followee_user_id` bigint UNSIGNED NOT NULL COMMENT '被关注用户ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_follow_relation`(`follower_user_id` ASC, `followee_user_id` ASC) USING BTREE,
  INDEX `idx_followee_created_at`(`followee_user_id` ASC, `created_at` DESC) USING BTREE,
  CONSTRAINT `fk_follow_followee_user_id` FOREIGN KEY (`followee_user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_follow_follower_user_id` FOREIGN KEY (`follower_user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户关注关系表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_learning_path_nodes
-- ----------------------------
DROP TABLE IF EXISTS `user_learning_path_nodes`;
CREATE TABLE `user_learning_path_nodes`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_path_id` bigint UNSIGNED NOT NULL COMMENT '用户学习路径ID',
  `node_id` bigint UNSIGNED NOT NULL COMMENT '节点ID',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'locked' COMMENT '状态',
  `progress_percent` decimal(5, 2) NOT NULL DEFAULT 0.00 COMMENT '进度百分比',
  `unlocked_at` datetime NULL DEFAULT NULL COMMENT '解锁时间',
  `started_at` datetime NULL DEFAULT NULL COMMENT '开始时间',
  `completed_at` datetime NULL DEFAULT NULL COMMENT '完成时间',
  `ai_feedback` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'AI反馈',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_path_node`(`user_path_id` ASC, `node_id` ASC) USING BTREE,
  INDEX `idx_user_path_nodes_status`(`user_path_id` ASC, `status` ASC, `updated_at` DESC) USING BTREE,
  INDEX `fk_user_path_nodes_node_id`(`node_id` ASC) USING BTREE,
  CONSTRAINT `fk_user_path_nodes_node_id` FOREIGN KEY (`node_id`) REFERENCES `learning_path_nodes` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_user_path_nodes_user_path_id` FOREIGN KEY (`user_path_id`) REFERENCES `user_learning_paths` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户学习路径节点进度表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_learning_paths
-- ----------------------------
DROP TABLE IF EXISTS `user_learning_paths`;
CREATE TABLE `user_learning_paths`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `path_id` bigint UNSIGNED NOT NULL COMMENT '学习路径ID',
  `snapshot_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '快照ID',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'active' COMMENT '状态：启用、归档、已完成',
  `progress_percent` decimal(5, 2) NOT NULL DEFAULT 0.00 COMMENT '进度百分比',
  `started_at` datetime NULL DEFAULT NULL COMMENT '开始时间',
  `completed_at` datetime NULL DEFAULT NULL COMMENT '完成时间',
  `current_node_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '当前节点ID',
  `ai_summary` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'AI总结',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_learning_paths_user_status`(`user_id` ASC, `status` ASC, `created_at` DESC) USING BTREE,
  INDEX `idx_user_learning_paths_snapshot`(`snapshot_id` ASC) USING BTREE,
  INDEX `fk_user_learning_paths_path_id`(`path_id` ASC) USING BTREE,
  INDEX `fk_user_learning_paths_current_node_id`(`current_node_id` ASC) USING BTREE,
  CONSTRAINT `fk_user_learning_paths_current_node_id` FOREIGN KEY (`current_node_id`) REFERENCES `learning_path_nodes` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_user_learning_paths_path_id` FOREIGN KEY (`path_id`) REFERENCES `learning_paths` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_user_learning_paths_snapshot_id` FOREIGN KEY (`snapshot_id`) REFERENCES `user_skill_snapshots` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_user_learning_paths_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户学习路径表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_lesson_progress
-- ----------------------------
DROP TABLE IF EXISTS `user_lesson_progress`;
CREATE TABLE `user_lesson_progress`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `course_id` bigint UNSIGNED NOT NULL COMMENT '课程ID',
  `lesson_id` bigint UNSIGNED NOT NULL COMMENT '课时ID',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'not_started' COMMENT '状态',
  `progress_percent` decimal(5, 2) NOT NULL DEFAULT 0.00 COMMENT '进度百分比',
  `watch_seconds` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '已观看秒数',
  `last_position_seconds` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '最后播放位置（秒）',
  `first_started_at` datetime NULL DEFAULT NULL COMMENT '首次开始时间',
  `completed_at` datetime NULL DEFAULT NULL COMMENT '完成时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_lesson_progress`(`user_id` ASC, `lesson_id` ASC) USING BTREE,
  INDEX `idx_lesson_progress_user_course_status`(`user_id` ASC, `course_id` ASC, `status` ASC) USING BTREE,
  INDEX `idx_lesson_progress_course_lesson`(`course_id` ASC, `lesson_id` ASC) USING BTREE,
  INDEX `fk_lesson_progress_lesson_id`(`lesson_id` ASC) USING BTREE,
  CONSTRAINT `fk_lesson_progress_course_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_lesson_progress_lesson_id` FOREIGN KEY (`lesson_id`) REFERENCES `course_lessons` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_lesson_progress_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户课时进度表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_profiles
-- ----------------------------
DROP TABLE IF EXISTS `user_profiles`;
CREATE TABLE `user_profiles`  (
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `display_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '显示昵称',
  `avatar_asset_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '头像资源ID',
  `bio` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '个人简介',
  `gender` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '性别',
  `birthday` date NULL DEFAULT NULL COMMENT '生日',
  `location` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '所在地',
  `profession` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '职业',
  `learning_goal` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '学习目标',
  `timezone` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'Asia/Shanghai' COMMENT '时区',
  `locale` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'zh-CN' COMMENT '地区语言',
  `total_learning_minutes` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '累计学习分钟数',
  `streak_days` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '连续学习天数',
  `followers_count` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '粉丝数',
  `following_count` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '关注数',
  `likes_received_count` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '获得点赞数',
  `extra_json` json NULL COMMENT '扩展信息JSON',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`user_id`) USING BTREE,
  INDEX `idx_profiles_display_name`(`display_name` ASC) USING BTREE,
  INDEX `idx_profiles_avatar_asset_id`(`avatar_asset_id` ASC) USING BTREE,
  CONSTRAINT `fk_profiles_avatar_asset_id` FOREIGN KEY (`avatar_asset_id`) REFERENCES `media_assets` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_profiles_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户资料表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_refresh_tokens
-- ----------------------------
DROP TABLE IF EXISTS `user_refresh_tokens`;
CREATE TABLE `user_refresh_tokens`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `device_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '设备标识',
  `refresh_token_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '刷新令牌哈希',
  `expired_at` datetime NOT NULL COMMENT '过期时间',
  `revoked_at` datetime NULL DEFAULT NULL COMMENT '撤销时间',
  `last_used_at` datetime NULL DEFAULT NULL COMMENT '最后使用时间',
  `ip_address` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'IP地址',
  `user_agent` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户代理',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_refresh_token_hash`(`refresh_token_hash` ASC) USING BTREE,
  INDEX `idx_refresh_user_expire`(`user_id` ASC, `revoked_at` ASC, `expired_at` ASC) USING BTREE,
  CONSTRAINT `fk_refresh_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 17 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '刷新令牌表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_settings
-- ----------------------------
DROP TABLE IF EXISTS `user_settings`;
CREATE TABLE `user_settings`  (
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `theme` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'light' COMMENT '主题模式',
  `language` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'zh-CN' COMMENT '语言',
  `daily_reminder_enabled` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否开启每日学习提醒',
  `progress_notice_enabled` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否开启进度通知',
  `badge_notice_enabled` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否开启徽章通知',
  `weekly_report_enabled` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否开启周报通知',
  `two_factor_enabled` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否开启双重认证',
  `profile_public` tinyint(1) NOT NULL DEFAULT 1 COMMENT '个人资料是否公开',
  `learning_data_public` tinyint(1) NOT NULL DEFAULT 0 COMMENT '学习数据是否公开',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`user_id`) USING BTREE,
  CONSTRAINT `fk_settings_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户设置表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_skill_scores
-- ----------------------------
DROP TABLE IF EXISTS `user_skill_scores`;
CREATE TABLE `user_skill_scores`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `snapshot_id` bigint UNSIGNED NOT NULL COMMENT '快照ID',
  `dimension_id` bigint UNSIGNED NOT NULL COMMENT '能力维度ID',
  `score` decimal(5, 2) NOT NULL COMMENT '得分',
  `percentile` decimal(5, 2) NULL DEFAULT NULL COMMENT '百分位',
  `level` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '等级',
  `insight` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '分析洞察',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_skill_snapshot_dimension`(`snapshot_id` ASC, `dimension_id` ASC) USING BTREE,
  INDEX `idx_skill_scores_dimension_score`(`dimension_id` ASC, `score` DESC) USING BTREE,
  CONSTRAINT `fk_skill_scores_dimension_id` FOREIGN KEY (`dimension_id`) REFERENCES `skill_dimensions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_skill_scores_snapshot_id` FOREIGN KEY (`snapshot_id`) REFERENCES `user_skill_snapshots` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '能力评分明细表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_skill_snapshots
-- ----------------------------
DROP TABLE IF EXISTS `user_skill_snapshots`;
CREATE TABLE `user_skill_snapshots`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `source_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'assessment' COMMENT '来源类型',
  `source_ref_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '来源引用ID',
  `snapshot_version` int UNSIGNED NOT NULL DEFAULT 1 COMMENT '快照版本号',
  `total_score` decimal(5, 2) NULL DEFAULT NULL COMMENT '总分',
  `rank_percent` decimal(5, 2) NULL DEFAULT NULL COMMENT '排名百分位',
  `generated_by` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'system' COMMENT '生成来源',
  `generated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_skill_snapshots_user_generated`(`user_id` ASC, `generated_at` DESC) USING BTREE,
  INDEX `idx_skill_snapshots_source`(`source_type` ASC, `source_ref_id` ASC) USING BTREE,
  CONSTRAINT `fk_skill_snapshots_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '能力画像快照表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_tag_interest_profiles
-- ----------------------------
DROP TABLE IF EXISTS `user_tag_interest_profiles`;
CREATE TABLE `user_tag_interest_profiles`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint UNSIGNED NOT NULL COMMENT '用户ID',
  `tag_id` bigint UNSIGNED NOT NULL COMMENT '标签ID',
  `interest_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '标签总兴趣分',
  `watch_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '观看贡献分',
  `like_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '点赞贡献分',
  `favorite_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '收藏贡献分',
  `comment_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '评论贡献分',
  `share_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '分享贡献分',
  `complete_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '完播贡献分',
  `negative_score` decimal(12, 4) NOT NULL DEFAULT 0.0000 COMMENT '负反馈分',
  `last_interaction_at` datetime NULL DEFAULT NULL COMMENT '最近一次产生该标签行为的时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_tag_interest`(`user_id` ASC, `tag_id` ASC) USING BTREE,
  INDEX `idx_user_tag_interest_score`(`user_id` ASC, `interest_score` DESC, `updated_at` DESC) USING BTREE,
  INDEX `idx_tag_interest_tag_score`(`tag_id` ASC, `interest_score` DESC) USING BTREE,
  CONSTRAINT `fk_user_tag_interest_tag_id` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_user_tag_interest_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 28 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户标签兴趣画像表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '登录用户名',
  `email` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '邮箱地址',
  `phone` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '手机号',
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '密码哈希',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'active' COMMENT '状态：启用、禁用、锁定',
  `register_source` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'password' COMMENT '注册来源：密码、后台创建、第三方登录',
  `email_verified` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否完成邮箱验证',
  `phone_verified` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否完成手机验证',
  `last_login_at` datetime NULL DEFAULT NULL COMMENT '最后登录时间',
  `last_login_ip` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '最后登录IP',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime NULL DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_users_username`(`username` ASC) USING BTREE,
  UNIQUE INDEX `uk_users_email`(`email` ASC) USING BTREE,
  UNIQUE INDEX `uk_users_phone`(`phone` ASC) USING BTREE,
  INDEX `idx_users_status_created_at`(`status` ASC, `created_at` ASC) USING BTREE,
  INDEX `idx_users_last_login_at`(`last_login_at` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '系统用户表' ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
