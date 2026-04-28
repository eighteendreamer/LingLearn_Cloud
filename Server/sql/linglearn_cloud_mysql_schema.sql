SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS linglearn_cloud
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE linglearn_cloud;

DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS ai_workflow_runs;
DROP TABLE IF EXISTS ai_chat_messages;
DROP TABLE IF EXISTS ai_chat_sessions;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS report_achievements;
DROP TABLE IF EXISTS monthly_reports;
DROP TABLE IF EXISTS assessment_snapshots;
DROP TABLE IF EXISTS practice_answers;
DROP TABLE IF EXISTS practice_sessions;
DROP TABLE IF EXISTS user_learning_path_nodes;
DROP TABLE IF EXISTS user_learning_paths;
DROP TABLE IF EXISTS learning_path_node_dimension_links;
DROP TABLE IF EXISTS learning_path_nodes;
DROP TABLE IF EXISTS learning_paths;
DROP TABLE IF EXISTS user_skill_scores;
DROP TABLE IF EXISTS user_skill_snapshots;
DROP TABLE IF EXISTS skill_dimensions;
DROP TABLE IF EXISTS content_quiz_attempts;
DROP TABLE IF EXISTS content_quiz_options;
DROP TABLE IF EXISTS content_quizzes;
DROP TABLE IF EXISTS content_view_histories;
DROP TABLE IF EXISTS content_shares;
DROP TABLE IF EXISTS content_favorites;
DROP TABLE IF EXISTS content_likes;
DROP TABLE IF EXISTS content_comments;
DROP TABLE IF EXISTS user_lesson_progress;
DROP TABLE IF EXISTS user_course_enrollments;
DROP TABLE IF EXISTS course_lessons;
DROP TABLE IF EXISTS content_item_tags;
DROP TABLE IF EXISTS content_items;
DROP TABLE IF EXISTS question_options;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS question_banks;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS user_follow_relations;
DROP TABLE IF EXISTS user_badges;
DROP TABLE IF EXISTS badge_catalog;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS content_categories;
DROP TABLE IF EXISTS user_settings;
DROP TABLE IF EXISTS user_profiles;
DROP TABLE IF EXISTS media_assets;
DROP TABLE IF EXISTS user_refresh_tokens;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  username VARCHAR(64) NOT NULL COMMENT '登录用户名',
  email VARCHAR(128) NOT NULL COMMENT '邮箱地址',
  phone VARCHAR(32) NULL COMMENT '手机号',
  password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
  status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态：启用、禁用、锁定',
  register_source VARCHAR(32) NOT NULL DEFAULT 'password' COMMENT '注册来源：密码、后台创建、第三方登录',
  email_verified TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否完成邮箱验证',
  phone_verified TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否完成手机验证',
  last_login_at DATETIME NULL COMMENT '最后登录时间',
  last_login_ip VARCHAR(45) NULL COMMENT '最后登录IP',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  deleted_at DATETIME NULL COMMENT '删除时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_users_username (username),
  UNIQUE KEY uk_users_email (email),
  UNIQUE KEY uk_users_phone (phone),
  KEY idx_users_status_created_at (status, created_at),
  KEY idx_users_last_login_at (last_login_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统用户表';

CREATE TABLE user_refresh_tokens (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  device_id VARCHAR(64) NULL COMMENT '设备标识',
  refresh_token_hash VARCHAR(255) NOT NULL COMMENT '刷新令牌哈希',
  expired_at DATETIME NOT NULL COMMENT '过期时间',
  revoked_at DATETIME NULL COMMENT '撤销时间',
  last_used_at DATETIME NULL COMMENT '最后使用时间',
  ip_address VARCHAR(45) NULL COMMENT 'IP地址',
  user_agent VARCHAR(255) NULL COMMENT '用户代理',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_refresh_token_hash (refresh_token_hash),
  KEY idx_refresh_user_expire (user_id, revoked_at, expired_at),
  CONSTRAINT fk_refresh_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='刷新令牌表';

CREATE TABLE media_assets (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  bucket_name VARCHAR(64) NOT NULL COMMENT '对象存储桶名称',
  object_key VARCHAR(255) NOT NULL COMMENT '对象存储对象键',
  original_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
  mime_type VARCHAR(128) NOT NULL COMMENT 'MIME类型',
  extension VARCHAR(20) NULL COMMENT '文件扩展名',
  asset_type VARCHAR(32) NOT NULL COMMENT '资源类型：头像、视频、封面、图片、PDF、文档、报告',
  storage_provider VARCHAR(32) NOT NULL DEFAULT 'minio' COMMENT '存储提供方',
  file_size BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '文件大小（字节）',
  checksum_sha256 CHAR(64) NULL COMMENT 'SHA256校验值',
  public_url VARCHAR(500) NULL COMMENT '公开访问URL',
  width INT UNSIGNED NULL COMMENT '资源宽度',
  height INT UNSIGNED NULL COMMENT '资源高度',
  duration_seconds INT UNSIGNED NULL COMMENT '时长（秒）',
  uploaded_by BIGINT UNSIGNED NULL COMMENT '上传者用户ID',
  status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_media_bucket_object (bucket_name, object_key),
  KEY idx_media_asset_type_status (asset_type, status),
  KEY idx_media_uploaded_by_type (uploaded_by, asset_type, created_at),
  CONSTRAINT fk_media_uploaded_by FOREIGN KEY (uploaded_by) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='MinIO资源元数据表';

CREATE TABLE user_profiles (
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  display_name VARCHAR(64) NOT NULL COMMENT '显示昵称',
  avatar_asset_id BIGINT UNSIGNED NULL COMMENT '头像资源ID',
  bio VARCHAR(500) NULL COMMENT '个人简介',
  gender VARCHAR(16) NULL COMMENT '性别',
  birthday DATE NULL COMMENT '生日',
  location VARCHAR(128) NULL COMMENT '所在地',
  profession VARCHAR(64) NULL COMMENT '职业',
  learning_goal VARCHAR(500) NULL COMMENT '学习目标',
  timezone VARCHAR(64) NOT NULL DEFAULT 'Asia/Shanghai' COMMENT '时区',
  locale VARCHAR(16) NOT NULL DEFAULT 'zh-CN' COMMENT '地区语言',
  total_learning_minutes INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '累计学习分钟数',
  streak_days INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '连续学习天数',
  followers_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '粉丝数',
  following_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '关注数',
  likes_received_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '获得点赞数',
  extra_json JSON NULL COMMENT '扩展信息JSON',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (user_id),
  KEY idx_profiles_display_name (display_name),
  KEY idx_profiles_avatar_asset_id (avatar_asset_id),
  CONSTRAINT fk_profiles_user_id FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_profiles_avatar_asset_id FOREIGN KEY (avatar_asset_id) REFERENCES media_assets (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户资料表';

CREATE TABLE user_settings (
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  theme VARCHAR(20) NOT NULL DEFAULT 'light' COMMENT '主题模式',
  language VARCHAR(16) NOT NULL DEFAULT 'zh-CN' COMMENT '语言',
  daily_reminder_enabled TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否开启每日学习提醒',
  progress_notice_enabled TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否开启进度通知',
  badge_notice_enabled TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否开启徽章通知',
  weekly_report_enabled TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否开启周报通知',
  two_factor_enabled TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否开启双重认证',
  profile_public TINYINT(1) NOT NULL DEFAULT 1 COMMENT '个人资料是否公开',
  learning_data_public TINYINT(1) NOT NULL DEFAULT 0 COMMENT '学习数据是否公开',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (user_id),
  CONSTRAINT fk_settings_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户设置表';

CREATE TABLE content_categories (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  parent_id BIGINT UNSIGNED NULL COMMENT '父级记录ID',
  name VARCHAR(64) NOT NULL COMMENT '名称',
  slug VARCHAR(64) NOT NULL COMMENT '唯一标识Slug',
  description VARCHAR(255) NULL COMMENT '描述',
  icon VARCHAR(64) NULL COMMENT '图标',
  sort_order INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_categories_slug (slug),
  UNIQUE KEY uk_categories_name (name),
  KEY idx_categories_parent_sort (parent_id, sort_order),
  CONSTRAINT fk_categories_parent_id FOREIGN KEY (parent_id) REFERENCES content_categories (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='业务分类表';

CREATE TABLE tags (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  name VARCHAR(64) NOT NULL COMMENT '名称',
  slug VARCHAR(64) NOT NULL COMMENT '唯一标识Slug',
  tag_type VARCHAR(20) NOT NULL DEFAULT 'topic' COMMENT '标签类型',
  status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态',
  use_count BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '使用次数',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_tags_name (name),
  UNIQUE KEY uk_tags_slug (slug),
  KEY idx_tags_type_use_count (tag_type, use_count DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='话题标签表';

CREATE TABLE badge_catalog (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  code VARCHAR(64) NOT NULL COMMENT '业务编码',
  name VARCHAR(64) NOT NULL COMMENT '名称',
  description VARCHAR(255) NULL COMMENT '描述',
  icon VARCHAR(64) NULL COMMENT '图标',
  status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_badge_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='徽章字典表';

CREATE TABLE user_badges (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  badge_id BIGINT UNSIGNED NOT NULL COMMENT '徽章ID',
  source_type VARCHAR(32) NULL COMMENT '来源类型',
  source_id BIGINT UNSIGNED NULL COMMENT '来源记录ID',
  granted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '授予时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_user_badge (user_id, badge_id),
  KEY idx_user_badges_granted_at (user_id, granted_at DESC),
  CONSTRAINT fk_user_badges_user_id FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_user_badges_badge_id FOREIGN KEY (badge_id) REFERENCES badge_catalog (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户徽章记录表';

CREATE TABLE user_follow_relations (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  follower_user_id BIGINT UNSIGNED NOT NULL COMMENT '关注者用户ID',
  followee_user_id BIGINT UNSIGNED NOT NULL COMMENT '被关注用户ID',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_follow_relation (follower_user_id, followee_user_id),
  KEY idx_followee_created_at (followee_user_id, created_at DESC),
  CONSTRAINT fk_follow_follower_user_id FOREIGN KEY (follower_user_id) REFERENCES users (id),
  CONSTRAINT fk_follow_followee_user_id FOREIGN KEY (followee_user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户关注关系表';

CREATE TABLE resources (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  category_id BIGINT UNSIGNED NULL COMMENT '分类ID',
  title VARCHAR(120) NOT NULL COMMENT '标题',
  summary VARCHAR(500) NULL COMMENT '摘要',
  resource_type VARCHAR(32) NOT NULL COMMENT '资源类型：PDF、文档、图片、视频、文章、链接',
  source_mode VARCHAR(20) NOT NULL DEFAULT 'minio' COMMENT '资源来源：MinIO、外部链接',
  asset_id BIGINT UNSIGNED NULL COMMENT '资源ID',
  external_url VARCHAR(500) NULL COMMENT '外部链接URL',
  author_id BIGINT UNSIGNED NULL COMMENT '作者用户ID',
  status VARCHAR(20) NOT NULL DEFAULT 'published' COMMENT '状态',
  download_count BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '下载次数',
  view_count BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '查看次数',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  deleted_at DATETIME NULL COMMENT '删除时间',
  PRIMARY KEY (id),
  KEY idx_resources_category_type_status (category_id, resource_type, status),
  KEY idx_resources_author_status (author_id, status, created_at DESC),
  FULLTEXT KEY ft_resources_title_summary (title, summary),
  CONSTRAINT fk_resources_category_id FOREIGN KEY (category_id) REFERENCES content_categories (id),
  CONSTRAINT fk_resources_asset_id FOREIGN KEY (asset_id) REFERENCES media_assets (id),
  CONSTRAINT fk_resources_author_id FOREIGN KEY (author_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学习资源表';

CREATE TABLE courses (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  category_id BIGINT UNSIGNED NULL COMMENT '分类ID',
  title VARCHAR(120) NOT NULL COMMENT '标题',
  summary VARCHAR(500) NULL COMMENT '摘要',
  description TEXT NULL COMMENT '描述',
  course_type VARCHAR(32) NOT NULL DEFAULT 'recorded' COMMENT '课程类型',
  difficulty VARCHAR(20) NOT NULL DEFAULT 'beginner' COMMENT '难度等级',
  status VARCHAR(20) NOT NULL DEFAULT 'published' COMMENT '状态',
  cover_asset_id BIGINT UNSIGNED NULL COMMENT '封面资源ID',
  estimated_minutes INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '预估分钟数',
  lesson_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '课时数量',
  enrollment_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '报名人数',
  completion_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '完成人数',
  average_rating DECIMAL(3,2) NOT NULL DEFAULT 0.00 COMMENT '平均评分',
  published_at DATETIME NULL COMMENT '发布时间',
  created_by BIGINT UNSIGNED NULL COMMENT '创建者用户ID',
  updated_by BIGINT UNSIGNED NULL COMMENT '更新者用户ID',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  deleted_at DATETIME NULL COMMENT '删除时间',
  PRIMARY KEY (id),
  KEY idx_courses_category_status_publish (category_id, status, published_at DESC),
  KEY idx_courses_difficulty_status (difficulty, status),
  FULLTEXT KEY ft_courses_title_summary_description (title, summary, description),
  CONSTRAINT fk_courses_category_id FOREIGN KEY (category_id) REFERENCES content_categories (id),
  CONSTRAINT fk_courses_cover_asset_id FOREIGN KEY (cover_asset_id) REFERENCES media_assets (id),
  CONSTRAINT fk_courses_created_by FOREIGN KEY (created_by) REFERENCES users (id),
  CONSTRAINT fk_courses_updated_by FOREIGN KEY (updated_by) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='课程主表';

CREATE TABLE question_banks (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  category_id BIGINT UNSIGNED NULL COMMENT '分类ID',
  name VARCHAR(120) NOT NULL COMMENT '名称',
  description VARCHAR(500) NULL COMMENT '描述',
  bank_type VARCHAR(32) NOT NULL DEFAULT 'practice' COMMENT '题库类型',
  difficulty VARCHAR(20) NOT NULL DEFAULT 'mixed' COMMENT '难度等级',
  status VARCHAR(20) NOT NULL DEFAULT 'published' COMMENT '状态',
  question_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '题目数量',
  created_by BIGINT UNSIGNED NULL COMMENT '创建者用户ID',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_banks_category_type_status (category_id, bank_type, status),
  KEY idx_banks_created_by (created_by, created_at DESC),
  CONSTRAINT fk_banks_category_id FOREIGN KEY (category_id) REFERENCES content_categories (id),
  CONSTRAINT fk_banks_created_by FOREIGN KEY (created_by) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='练习题库表';

CREATE TABLE questions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  bank_id BIGINT UNSIGNED NOT NULL COMMENT '题库ID',
  category_id BIGINT UNSIGNED NULL COMMENT '分类ID',
  course_id BIGINT UNSIGNED NULL COMMENT '课程ID',
  lesson_id BIGINT UNSIGNED NULL COMMENT '课时ID',
  question_type VARCHAR(32) NOT NULL DEFAULT 'single_choice' COMMENT '题目类型',
  difficulty VARCHAR(20) NOT NULL DEFAULT 'medium' COMMENT '难度等级',
  stem TEXT NOT NULL COMMENT '题干',
  explanation TEXT NULL COMMENT '答案解析',
  correct_answer_text VARCHAR(255) NULL COMMENT '正确答案文本',
  status VARCHAR(20) NOT NULL DEFAULT 'published' COMMENT '状态',
  sort_order INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_questions_bank_status_difficulty (bank_id, status, difficulty),
  KEY idx_questions_course_lesson (course_id, lesson_id),
  KEY idx_questions_category_type (category_id, question_type),
  CONSTRAINT fk_questions_bank_id FOREIGN KEY (bank_id) REFERENCES question_banks (id),
  CONSTRAINT fk_questions_category_id FOREIGN KEY (category_id) REFERENCES content_categories (id),
  CONSTRAINT fk_questions_course_id FOREIGN KEY (course_id) REFERENCES courses (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='题库题目表';

CREATE TABLE question_options (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  question_id BIGINT UNSIGNED NOT NULL COMMENT '题目ID',
  option_key CHAR(1) NOT NULL COMMENT '选项标识',
  option_text VARCHAR(500) NOT NULL COMMENT '选项内容',
  is_correct TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否正确',
  sort_order INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_question_option_key (question_id, option_key),
  KEY idx_question_options_question_sort (question_id, sort_order),
  CONSTRAINT fk_question_options_question_id FOREIGN KEY (question_id) REFERENCES questions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='题目选项表';

CREATE TABLE content_items (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  author_id BIGINT UNSIGNED NOT NULL COMMENT '作者用户ID',
  category_id BIGINT UNSIGNED NULL COMMENT '分类ID',
  title VARCHAR(120) NOT NULL COMMENT '标题',
  summary VARCHAR(500) NULL COMMENT '摘要',
  content_type VARCHAR(32) NOT NULL DEFAULT 'short_video' COMMENT '内容类型',
  source_type VARCHAR(32) NOT NULL DEFAULT 'original' COMMENT '来源类型',
  visibility VARCHAR(20) NOT NULL DEFAULT 'public' COMMENT '可见范围',
  audit_status VARCHAR(20) NOT NULL DEFAULT 'approved' COMMENT '审核状态',
  publish_status VARCHAR(20) NOT NULL DEFAULT 'published' COMMENT '发布状态',
  cover_asset_id BIGINT UNSIGNED NULL COMMENT '封面资源ID',
  primary_media_asset_id BIGINT UNSIGNED NULL COMMENT '主媒体资源ID',
  external_video_url VARCHAR(500) NULL COMMENT '外部视频URL',
  bvid VARCHAR(64) NULL COMMENT '外部视频平台标识',
  duration_seconds INT UNSIGNED NULL COMMENT '时长（秒）',
  hashtags_json JSON NULL COMMENT '话题标签JSON',
  allow_comment TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否允许评论',
  allow_duet TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否允许合拍',
  has_quiz TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否启用答题互动',
  quiz_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '题目数量',
  views_count BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '浏览次数',
  likes_count BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '点赞次数',
  comments_count BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '评论次数',
  favorites_count BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '收藏次数',
  shares_count BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '分享次数',
  hot_score DECIMAL(12,4) NOT NULL DEFAULT 0.0000 COMMENT '推荐热度分数',
  published_at DATETIME NULL COMMENT '发布时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  deleted_at DATETIME NULL COMMENT '删除时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_content_items_bvid (bvid),
  KEY idx_content_author_status_publish (author_id, publish_status, published_at DESC),
  KEY idx_content_category_status_publish (category_id, publish_status, published_at DESC),
  KEY idx_content_type_status_publish (content_type, publish_status, published_at DESC),
  KEY idx_content_hot_score (publish_status, hot_score DESC, published_at DESC),
  KEY idx_content_audit_status (audit_status, publish_status),
  FULLTEXT KEY ft_content_title_summary (title, summary),
  CONSTRAINT fk_content_author_id FOREIGN KEY (author_id) REFERENCES users (id),
  CONSTRAINT fk_content_category_id FOREIGN KEY (category_id) REFERENCES content_categories (id),
  CONSTRAINT fk_content_cover_asset_id FOREIGN KEY (cover_asset_id) REFERENCES media_assets (id),
  CONSTRAINT fk_content_primary_media_asset_id FOREIGN KEY (primary_media_asset_id) REFERENCES media_assets (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='短视频与用户作品表';

CREATE TABLE content_item_tags (
  content_item_id BIGINT UNSIGNED NOT NULL COMMENT '内容ID',
  tag_id BIGINT UNSIGNED NOT NULL COMMENT '标签ID',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (content_item_id, tag_id),
  KEY idx_content_item_tags_tag_id (tag_id, content_item_id),
  CONSTRAINT fk_content_item_tags_content_item_id FOREIGN KEY (content_item_id) REFERENCES content_items (id),
  CONSTRAINT fk_content_item_tags_tag_id FOREIGN KEY (tag_id) REFERENCES tags (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='内容标签关联表';

CREATE TABLE course_lessons (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  course_id BIGINT UNSIGNED NOT NULL COMMENT '课程ID',
  title VARCHAR(120) NOT NULL COMMENT '标题',
  summary VARCHAR(500) NULL COMMENT '摘要',
  lesson_type VARCHAR(32) NOT NULL DEFAULT 'video' COMMENT '课时类型：视频、文章、测验、练习、直播',
  sort_order INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  estimated_minutes INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '预估分钟数',
  content_item_id BIGINT UNSIGNED NULL COMMENT '内容ID',
  resource_id BIGINT UNSIGNED NULL COMMENT '资源文件ID',
  question_bank_id BIGINT UNSIGNED NULL COMMENT '题库ID',
  unlock_type VARCHAR(20) NOT NULL DEFAULT 'free' COMMENT '解锁方式',
  status VARCHAR(20) NOT NULL DEFAULT 'published' COMMENT '状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_course_lesson_sort (course_id, sort_order),
  KEY idx_lessons_course_status_sort (course_id, status, sort_order),
  KEY idx_lessons_content_item_id (content_item_id),
  KEY idx_lessons_resource_id (resource_id),
  KEY idx_lessons_question_bank_id (question_bank_id),
  CONSTRAINT fk_lessons_course_id FOREIGN KEY (course_id) REFERENCES courses (id),
  CONSTRAINT fk_lessons_content_item_id FOREIGN KEY (content_item_id) REFERENCES content_items (id),
  CONSTRAINT fk_lessons_resource_id FOREIGN KEY (resource_id) REFERENCES resources (id),
  CONSTRAINT fk_lessons_question_bank_id FOREIGN KEY (question_bank_id) REFERENCES question_banks (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='课程课时表';

CREATE TABLE user_course_enrollments (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  course_id BIGINT UNSIGNED NOT NULL COMMENT '课程ID',
  status VARCHAR(20) NOT NULL DEFAULT 'learning' COMMENT '学习状态：学习中、暂停、已完成',
  enrolled_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
  started_at DATETIME NULL COMMENT '开始时间',
  completed_at DATETIME NULL COMMENT '完成时间',
  progress_percent DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '进度百分比',
  completed_lessons INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '已完成课时数',
  total_lessons INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '总课时数',
  total_learning_minutes INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '累计学习分钟数',
  last_lesson_id BIGINT UNSIGNED NULL COMMENT '最近学习课时ID',
  last_learned_at DATETIME NULL COMMENT '最近学习时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_user_course_enrollment (user_id, course_id),
  KEY idx_enrollment_user_status (user_id, status, last_learned_at DESC),
  KEY idx_enrollment_course_status (course_id, status),
  CONSTRAINT fk_enrollment_user_id FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_enrollment_course_id FOREIGN KEY (course_id) REFERENCES courses (id),
  CONSTRAINT fk_enrollment_last_lesson_id FOREIGN KEY (last_lesson_id) REFERENCES course_lessons (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户课程报名进度表';

CREATE TABLE user_lesson_progress (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  course_id BIGINT UNSIGNED NOT NULL COMMENT '课程ID',
  lesson_id BIGINT UNSIGNED NOT NULL COMMENT '课时ID',
  status VARCHAR(20) NOT NULL DEFAULT 'not_started' COMMENT '状态',
  progress_percent DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '进度百分比',
  watch_seconds INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '已观看秒数',
  last_position_seconds INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '最后播放位置（秒）',
  first_started_at DATETIME NULL COMMENT '首次开始时间',
  completed_at DATETIME NULL COMMENT '完成时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_user_lesson_progress (user_id, lesson_id),
  KEY idx_lesson_progress_user_course_status (user_id, course_id, status),
  KEY idx_lesson_progress_course_lesson (course_id, lesson_id),
  CONSTRAINT fk_lesson_progress_user_id FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_lesson_progress_course_id FOREIGN KEY (course_id) REFERENCES courses (id),
  CONSTRAINT fk_lesson_progress_lesson_id FOREIGN KEY (lesson_id) REFERENCES course_lessons (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户课时进度表';

CREATE TABLE content_comments (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  content_item_id BIGINT UNSIGNED NOT NULL COMMENT '内容ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  parent_id BIGINT UNSIGNED NULL COMMENT '父级记录ID',
  root_id BIGINT UNSIGNED NULL COMMENT '根评论ID',
  reply_to_user_id BIGINT UNSIGNED NULL COMMENT '回复目标用户ID',
  content VARCHAR(1000) NOT NULL COMMENT '内容正文',
  like_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '点赞数',
  status VARCHAR(20) NOT NULL DEFAULT 'normal' COMMENT '状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  deleted_at DATETIME NULL COMMENT '删除时间',
  PRIMARY KEY (id),
  KEY idx_comments_content_parent_created (content_item_id, parent_id, created_at DESC),
  KEY idx_comments_root_created (root_id, created_at DESC),
  KEY idx_comments_user_created (user_id, created_at DESC),
  CONSTRAINT fk_comments_content_item_id FOREIGN KEY (content_item_id) REFERENCES content_items (id),
  CONSTRAINT fk_comments_user_id FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_comments_parent_id FOREIGN KEY (parent_id) REFERENCES content_comments (id),
  CONSTRAINT fk_comments_root_id FOREIGN KEY (root_id) REFERENCES content_comments (id),
  CONSTRAINT fk_comments_reply_to_user_id FOREIGN KEY (reply_to_user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='内容评论表';

CREATE TABLE content_likes (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  content_item_id BIGINT UNSIGNED NOT NULL COMMENT '内容ID',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_content_like (user_id, content_item_id),
  KEY idx_likes_content_created (content_item_id, created_at DESC),
  CONSTRAINT fk_likes_user_id FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_likes_content_item_id FOREIGN KEY (content_item_id) REFERENCES content_items (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='内容点赞表';

CREATE TABLE content_favorites (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  content_item_id BIGINT UNSIGNED NOT NULL COMMENT '内容ID',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_content_favorite (user_id, content_item_id),
  KEY idx_favorites_content_created (content_item_id, created_at DESC),
  KEY idx_favorites_user_created (user_id, created_at DESC),
  CONSTRAINT fk_favorites_user_id FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_favorites_content_item_id FOREIGN KEY (content_item_id) REFERENCES content_items (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='内容收藏表';

CREATE TABLE content_shares (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  content_item_id BIGINT UNSIGNED NOT NULL COMMENT '内容ID',
  share_channel VARCHAR(32) NOT NULL DEFAULT 'internal' COMMENT '分享渠道',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_shares_content_created (content_item_id, created_at DESC),
  KEY idx_shares_user_created (user_id, created_at DESC),
  CONSTRAINT fk_shares_user_id FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_shares_content_item_id FOREIGN KEY (content_item_id) REFERENCES content_items (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='内容分享记录表';

CREATE TABLE content_view_histories (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  content_item_id BIGINT UNSIGNED NOT NULL COMMENT '内容ID',
  view_date DATE NOT NULL COMMENT '观看日期',
  view_count INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '查看次数',
  watch_seconds INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '已观看秒数',
  watch_progress DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '观看进度百分比',
  last_position_seconds INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '最后播放位置（秒）',
  completed TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否看完',
  liked TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否点赞',
  favorited TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否收藏',
  last_viewed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后观看时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_view_history_day (user_id, content_item_id, view_date),
  KEY idx_view_history_user_last (user_id, last_viewed_at DESC),
  KEY idx_view_history_content_date (content_item_id, view_date),
  CONSTRAINT fk_view_history_user_id FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_view_history_content_item_id FOREIGN KEY (content_item_id) REFERENCES content_items (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='按日观看历史表';

CREATE TABLE content_quizzes (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  content_item_id BIGINT UNSIGNED NOT NULL COMMENT '内容ID',
  title VARCHAR(200) NOT NULL COMMENT '标题',
  description VARCHAR(500) NULL COMMENT '描述',
  quiz_type VARCHAR(32) NOT NULL DEFAULT 'single_choice_poll' COMMENT '互动题类型',
  sort_order INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  status VARCHAR(20) NOT NULL DEFAULT 'published' COMMENT '状态',
  total_votes BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '总投票数',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_content_quiz_sort (content_item_id, sort_order),
  KEY idx_quizzes_content_status (content_item_id, status, sort_order),
  CONSTRAINT fk_quizzes_content_item_id FOREIGN KEY (content_item_id) REFERENCES content_items (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='内容互动题表';

CREATE TABLE content_quiz_options (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  quiz_id BIGINT UNSIGNED NOT NULL COMMENT '互动题ID',
  option_text VARCHAR(255) NOT NULL COMMENT '选项内容',
  option_order INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '选项顺序',
  vote_count BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '投票数',
  is_correct TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否正确',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_quiz_option_order (quiz_id, option_order),
  KEY idx_quiz_options_quiz_order (quiz_id, option_order),
  CONSTRAINT fk_quiz_options_quiz_id FOREIGN KEY (quiz_id) REFERENCES content_quizzes (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='互动题选项表';

CREATE TABLE content_quiz_attempts (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  quiz_id BIGINT UNSIGNED NOT NULL COMMENT '互动题ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  selected_option_id BIGINT UNSIGNED NOT NULL COMMENT '所选选项ID',
  is_correct TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否正确',
  submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
  client_ip VARCHAR(45) NULL COMMENT '客户端IP',
  PRIMARY KEY (id),
  UNIQUE KEY uk_quiz_attempt_user (quiz_id, user_id),
  KEY idx_quiz_attempts_user_submitted (user_id, submitted_at DESC),
  KEY idx_quiz_attempts_option_id (selected_option_id),
  CONSTRAINT fk_quiz_attempts_quiz_id FOREIGN KEY (quiz_id) REFERENCES content_quizzes (id),
  CONSTRAINT fk_quiz_attempts_user_id FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_quiz_attempts_selected_option_id FOREIGN KEY (selected_option_id) REFERENCES content_quiz_options (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='互动题作答记录表';

CREATE TABLE skill_dimensions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  code VARCHAR(64) NOT NULL COMMENT '业务编码',
  name VARCHAR(64) NOT NULL COMMENT '名称',
  description VARCHAR(255) NULL COMMENT '描述',
  sort_order INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_skill_dimensions_code (code),
  KEY idx_skill_dimensions_sort (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='能力维度字典表';

CREATE TABLE user_skill_snapshots (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  source_type VARCHAR(32) NOT NULL DEFAULT 'assessment' COMMENT '来源类型',
  source_ref_id BIGINT UNSIGNED NULL COMMENT '来源引用ID',
  snapshot_version INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '快照版本号',
  total_score DECIMAL(5,2) NULL COMMENT '总分',
  rank_percent DECIMAL(5,2) NULL COMMENT '排名百分位',
  generated_by VARCHAR(32) NOT NULL DEFAULT 'system' COMMENT '生成来源',
  generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_skill_snapshots_user_generated (user_id, generated_at DESC),
  KEY idx_skill_snapshots_source (source_type, source_ref_id),
  CONSTRAINT fk_skill_snapshots_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='能力画像快照表';

CREATE TABLE user_skill_scores (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  snapshot_id BIGINT UNSIGNED NOT NULL COMMENT '快照ID',
  dimension_id BIGINT UNSIGNED NOT NULL COMMENT '能力维度ID',
  score DECIMAL(5,2) NOT NULL COMMENT '得分',
  percentile DECIMAL(5,2) NULL COMMENT '百分位',
  level VARCHAR(32) NULL COMMENT '等级',
  insight VARCHAR(255) NULL COMMENT '分析洞察',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_skill_snapshot_dimension (snapshot_id, dimension_id),
  KEY idx_skill_scores_dimension_score (dimension_id, score DESC),
  CONSTRAINT fk_skill_scores_snapshot_id FOREIGN KEY (snapshot_id) REFERENCES user_skill_snapshots (id),
  CONSTRAINT fk_skill_scores_dimension_id FOREIGN KEY (dimension_id) REFERENCES skill_dimensions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='能力评分明细表';

CREATE TABLE learning_paths (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  path_type VARCHAR(20) NOT NULL DEFAULT 'template' COMMENT '路径类型：模板、个性化',
  name VARCHAR(120) NOT NULL COMMENT '名称',
  description VARCHAR(500) NULL COMMENT '描述',
  target_role VARCHAR(64) NULL COMMENT '目标岗位',
  based_on_snapshot_id BIGINT UNSIGNED NULL COMMENT '基于画像快照ID',
  created_by BIGINT UNSIGNED NULL COMMENT '创建者用户ID',
  status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态',
  is_default TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否默认模板',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_learning_paths_type_status (path_type, status, created_at DESC),
  KEY idx_learning_paths_snapshot (based_on_snapshot_id),
  CONSTRAINT fk_learning_paths_snapshot_id FOREIGN KEY (based_on_snapshot_id) REFERENCES user_skill_snapshots (id),
  CONSTRAINT fk_learning_paths_created_by FOREIGN KEY (created_by) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学习路径模板表';

CREATE TABLE learning_path_nodes (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  path_id BIGINT UNSIGNED NOT NULL COMMENT '学习路径ID',
  course_id BIGINT UNSIGNED NULL COMMENT '课程ID',
  node_type VARCHAR(32) NOT NULL DEFAULT 'course' COMMENT '节点类型',
  title VARCHAR(120) NOT NULL COMMENT '标题',
  description VARCHAR(500) NULL COMMENT '描述',
  sort_order INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  default_status VARCHAR(20) NOT NULL DEFAULT 'locked' COMMENT '默认节点状态',
  recommended_reason VARCHAR(500) NULL COMMENT '推荐理由',
  estimated_minutes INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '预估分钟数',
  prerequisite_node_id BIGINT UNSIGNED NULL COMMENT '前置节点ID',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_learning_path_node_sort (path_id, sort_order),
  KEY idx_learning_path_nodes_path_sort (path_id, sort_order),
  KEY idx_learning_path_nodes_prerequisite (prerequisite_node_id),
  CONSTRAINT fk_learning_path_nodes_path_id FOREIGN KEY (path_id) REFERENCES learning_paths (id),
  CONSTRAINT fk_learning_path_nodes_course_id FOREIGN KEY (course_id) REFERENCES courses (id),
  CONSTRAINT fk_learning_path_nodes_prerequisite_node_id FOREIGN KEY (prerequisite_node_id) REFERENCES learning_path_nodes (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学习路径节点表';

CREATE TABLE learning_path_node_dimension_links (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  node_id BIGINT UNSIGNED NOT NULL COMMENT '节点ID',
  dimension_id BIGINT UNSIGNED NOT NULL COMMENT '能力维度ID',
  match_score DECIMAL(5,2) NULL COMMENT '维度匹配分',
  note VARCHAR(255) NULL COMMENT '备注',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_path_node_dimension (node_id, dimension_id),
  KEY idx_path_dimension_links_dimension_id (dimension_id),
  CONSTRAINT fk_path_dimension_links_node_id FOREIGN KEY (node_id) REFERENCES learning_path_nodes (id),
  CONSTRAINT fk_path_dimension_links_dimension_id FOREIGN KEY (dimension_id) REFERENCES skill_dimensions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='路径节点能力维度关联表';

CREATE TABLE user_learning_paths (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  path_id BIGINT UNSIGNED NOT NULL COMMENT '学习路径ID',
  snapshot_id BIGINT UNSIGNED NULL COMMENT '快照ID',
  status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态：启用、归档、已完成',
  progress_percent DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '进度百分比',
  started_at DATETIME NULL COMMENT '开始时间',
  completed_at DATETIME NULL COMMENT '完成时间',
  current_node_id BIGINT UNSIGNED NULL COMMENT '当前节点ID',
  ai_summary VARCHAR(1000) NULL COMMENT 'AI总结',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_user_learning_paths_user_status (user_id, status, created_at DESC),
  KEY idx_user_learning_paths_snapshot (snapshot_id),
  CONSTRAINT fk_user_learning_paths_user_id FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_user_learning_paths_path_id FOREIGN KEY (path_id) REFERENCES learning_paths (id),
  CONSTRAINT fk_user_learning_paths_snapshot_id FOREIGN KEY (snapshot_id) REFERENCES user_skill_snapshots (id),
  CONSTRAINT fk_user_learning_paths_current_node_id FOREIGN KEY (current_node_id) REFERENCES learning_path_nodes (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户学习路径表';

CREATE TABLE user_learning_path_nodes (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_path_id BIGINT UNSIGNED NOT NULL COMMENT '用户学习路径ID',
  node_id BIGINT UNSIGNED NOT NULL COMMENT '节点ID',
  status VARCHAR(20) NOT NULL DEFAULT 'locked' COMMENT '状态',
  progress_percent DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '进度百分比',
  unlocked_at DATETIME NULL COMMENT '解锁时间',
  started_at DATETIME NULL COMMENT '开始时间',
  completed_at DATETIME NULL COMMENT '完成时间',
  ai_feedback VARCHAR(500) NULL COMMENT 'AI反馈',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_user_path_node (user_path_id, node_id),
  KEY idx_user_path_nodes_status (user_path_id, status, updated_at DESC),
  CONSTRAINT fk_user_path_nodes_user_path_id FOREIGN KEY (user_path_id) REFERENCES user_learning_paths (id),
  CONSTRAINT fk_user_path_nodes_node_id FOREIGN KEY (node_id) REFERENCES learning_path_nodes (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户学习路径节点进度表';

CREATE TABLE practice_sessions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  bank_id BIGINT UNSIGNED NULL COMMENT '题库ID',
  session_type VARCHAR(32) NOT NULL DEFAULT 'practice' COMMENT '会话类型',
  status VARCHAR(20) NOT NULL DEFAULT 'started' COMMENT '会话状态：已开始、已提交、已结束',
  started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
  submitted_at DATETIME NULL COMMENT '提交时间',
  finished_at DATETIME NULL COMMENT '结束时间',
  duration_seconds INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '时长（秒）',
  total_questions INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '总题数',
  answered_questions INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '已答题数',
  correct_questions INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '答对题数',
  score DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '得分',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_practice_sessions_user_status_started (user_id, status, started_at DESC),
  KEY idx_practice_sessions_bank_started (bank_id, started_at DESC),
  CONSTRAINT fk_practice_sessions_user_id FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_practice_sessions_bank_id FOREIGN KEY (bank_id) REFERENCES question_banks (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='练习会话表';

CREATE TABLE practice_answers (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  session_id BIGINT UNSIGNED NOT NULL COMMENT '会话ID',
  question_id BIGINT UNSIGNED NOT NULL COMMENT '题目ID',
  selected_option_id BIGINT UNSIGNED NULL COMMENT '所选选项ID',
  answer_text VARCHAR(500) NULL COMMENT '作答文本',
  is_correct TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否正确',
  score DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '得分',
  answered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '答题时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_practice_answer (session_id, question_id),
  KEY idx_practice_answers_question_answered (question_id, answered_at DESC),
  CONSTRAINT fk_practice_answers_session_id FOREIGN KEY (session_id) REFERENCES practice_sessions (id),
  CONSTRAINT fk_practice_answers_question_id FOREIGN KEY (question_id) REFERENCES questions (id),
  CONSTRAINT fk_practice_answers_selected_option_id FOREIGN KEY (selected_option_id) REFERENCES question_options (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='练习作答表';

CREATE TABLE assessment_snapshots (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  assessment_type VARCHAR(32) NOT NULL DEFAULT 'weekly' COMMENT '评估类型：日、周、月',
  period_start DATE NOT NULL COMMENT '周期开始日期',
  period_end DATE NOT NULL COMMENT '周期结束日期',
  total_learning_minutes INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '累计学习分钟数',
  completed_courses INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '完成课程数',
  average_score DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '平均分',
  rank_percent DECIMAL(5,2) NULL COMMENT '排名百分位',
  correct_rate DECIMAL(5,2) NULL COMMENT '正确率',
  focus_rate DECIMAL(5,2) NULL COMMENT '专注度',
  metrics_json JSON NULL COMMENT '指标汇总JSON',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_assessment_period (user_id, assessment_type, period_start, period_end),
  KEY idx_assessment_user_type_period (user_id, assessment_type, period_start DESC),
  CONSTRAINT fk_assessment_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学习评估快照表';

CREATE TABLE monthly_reports (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  report_month CHAR(7) NOT NULL COMMENT '报表月份（YYYY-MM）',
  assessment_snapshot_id BIGINT UNSIGNED NULL COMMENT '评估快照ID',
  report_status VARCHAR(20) NOT NULL DEFAULT 'generated' COMMENT '报告状态',
  total_learning_minutes INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '累计学习分钟数',
  completed_courses INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '完成课程数',
  average_score DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '平均分',
  site_rank INT UNSIGNED NULL COMMENT '全站排名',
  strengths_json JSON NULL COMMENT '优势项JSON',
  improvements_json JSON NULL COMMENT '改进项JSON',
  ai_summary TEXT NULL COMMENT 'AI总结',
  exported_pdf_asset_id BIGINT UNSIGNED NULL COMMENT '导出PDF资源ID',
  generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_monthly_report_user_month (user_id, report_month),
  KEY idx_monthly_reports_status (report_status, generated_at DESC),
  CONSTRAINT fk_monthly_reports_user_id FOREIGN KEY (user_id) REFERENCES users (id),
  CONSTRAINT fk_monthly_reports_assessment_snapshot_id FOREIGN KEY (assessment_snapshot_id) REFERENCES assessment_snapshots (id),
  CONSTRAINT fk_monthly_reports_exported_pdf_asset_id FOREIGN KEY (exported_pdf_asset_id) REFERENCES media_assets (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='月度学习报告表';

CREATE TABLE report_achievements (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  report_id BIGINT UNSIGNED NOT NULL COMMENT '报告ID',
  title VARCHAR(120) NOT NULL COMMENT '标题',
  description VARCHAR(255) NULL COMMENT '描述',
  icon VARCHAR(64) NULL COMMENT '图标',
  color_token VARCHAR(64) NULL COMMENT '颜色标识',
  sort_order INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序值',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_report_achievements_report_sort (report_id, sort_order),
  CONSTRAINT fk_report_achievements_report_id FOREIGN KEY (report_id) REFERENCES monthly_reports (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='报告成就表';

CREATE TABLE notifications (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  notification_type VARCHAR(32) NOT NULL COMMENT '通知类型',
  title VARCHAR(120) NOT NULL COMMENT '标题',
  body VARCHAR(1000) NOT NULL COMMENT '通知内容',
  biz_type VARCHAR(32) NULL COMMENT '业务类型',
  biz_id BIGINT UNSIGNED NULL COMMENT '业务ID',
  read_status TINYINT(1) NOT NULL DEFAULT 0 COMMENT '已读状态',
  read_at DATETIME NULL COMMENT '已读时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_notifications_user_read_created (user_id, read_status, created_at DESC),
  KEY idx_notifications_biz (biz_type, biz_id),
  CONSTRAINT fk_notifications_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='通知表';

CREATE TABLE ai_chat_sessions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  session_name VARCHAR(120) NULL COMMENT '会话名称',
  scene_code VARCHAR(32) NOT NULL DEFAULT 'study_assistant' COMMENT '场景编码',
  model_name VARCHAR(64) NOT NULL DEFAULT 'glm-4-flash' COMMENT '模型名称',
  status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态',
  summary VARCHAR(500) NULL COMMENT '摘要',
  last_message_at DATETIME NULL COMMENT '最后消息时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_ai_sessions_user_status_last (user_id, status, last_message_at DESC),
  CONSTRAINT fk_ai_sessions_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI对话会话表';

CREATE TABLE ai_chat_messages (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  session_id BIGINT UNSIGNED NOT NULL COMMENT '会话ID',
  role VARCHAR(16) NOT NULL COMMENT '消息角色：系统、用户、助手、工具',
  message_type VARCHAR(32) NOT NULL DEFAULT 'text' COMMENT '消息类型',
  content LONGTEXT NOT NULL COMMENT '内容正文',
  token_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Token数量',
  latency_ms INT UNSIGNED NULL COMMENT '耗时（毫秒）',
  error_code VARCHAR(64) NULL COMMENT '错误码',
  trace_id VARCHAR(64) NULL COMMENT '追踪ID',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_ai_messages_session_created (session_id, created_at),
  CONSTRAINT fk_ai_messages_session_id FOREIGN KEY (session_id) REFERENCES ai_chat_sessions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI对话消息表';

CREATE TABLE ai_workflow_runs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NULL COMMENT '用户ID',
  workflow_type VARCHAR(32) NOT NULL COMMENT '工作流类型：画像、路径、月报、导师回复',
  biz_type VARCHAR(32) NULL COMMENT '业务类型',
  biz_id BIGINT UNSIGNED NULL COMMENT '业务ID',
  status VARCHAR(20) NOT NULL DEFAULT 'running' COMMENT '状态',
  input_json JSON NULL COMMENT '工作流输入JSON',
  output_json JSON NULL COMMENT '工作流输出JSON',
  error_message VARCHAR(1000) NULL COMMENT '错误信息',
  started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
  finished_at DATETIME NULL COMMENT '结束时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_ai_workflow_type_status (workflow_type, status, created_at DESC),
  KEY idx_ai_workflow_biz (biz_type, biz_id),
  KEY idx_ai_workflow_user_type (user_id, workflow_type, created_at DESC),
  CONSTRAINT fk_ai_workflows_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='LangGraph工作流运行表';

CREATE TABLE audit_logs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id BIGINT UNSIGNED NULL COMMENT '用户ID',
  module_name VARCHAR(32) NOT NULL COMMENT '模块名称',
  action_name VARCHAR(32) NOT NULL COMMENT '动作名称',
  biz_type VARCHAR(32) NULL COMMENT '业务类型',
  biz_id BIGINT UNSIGNED NULL COMMENT '业务ID',
  request_id VARCHAR(64) NULL COMMENT '请求ID',
  ip_address VARCHAR(45) NULL COMMENT 'IP地址',
  user_agent VARCHAR(255) NULL COMMENT '用户代理',
  detail_json JSON NULL COMMENT '详情JSON',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_audit_module_action_created (module_name, action_name, created_at DESC),
  KEY idx_audit_biz (biz_type, biz_id),
  KEY idx_audit_user_created (user_id, created_at DESC),
  CONSTRAINT fk_audit_logs_user_id FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='审计日志表';

SET FOREIGN_KEY_CHECKS = 1;


