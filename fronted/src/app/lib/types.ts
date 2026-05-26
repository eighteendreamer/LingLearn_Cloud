export interface AuthTokenResponse {
  user_id: number;
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

export interface PasswordResetRequestResponse {
  message: string;
  expires_in_seconds: number;
  masked_email: string | null;
  sent: boolean;
}

export interface PasswordResetConfirmResponse {
  message: string;
}

export interface UserStatsResponse {
  total_learning_minutes: number;
  streak_days: number;
  followers_count: number;
  following_count: number;
  likes_received_count: number;
}

export interface UserProfileResponse {
  user_id: number;
  username: string;
  email: string;
  phone: string | null;
  display_name: string;
  avatar_asset_id: number | null;
  avatar_url: string | null;
  bio: string | null;
  gender: string | null;
  birthday: string | null;
  location: string | null;
  profession: string | null;
  learning_goal: string | null;
  timezone: string;
  locale: string;
  stats: UserStatsResponse;
  created_at: string;
  updated_at: string;
}

export interface UserSettingsResponse {
  theme: string;
  language: string;
  daily_reminder_enabled: boolean;
  progress_notice_enabled: boolean;
  badge_notice_enabled: boolean;
  weekly_report_enabled: boolean;
  two_factor_enabled: boolean;
  profile_public: boolean;
  learning_data_public: boolean;
}

export interface CurrentUserResponse {
  profile: UserProfileResponse;
  settings: UserSettingsResponse;
}

export interface UserWorkListItemResponse {
  id: number;
  title: string;
  summary: string | null;
  cover_url: string | null;
  published_at: string | null;
}

export interface UserPreferenceFacetResponse {
  key: string;
  name: string;
  score: number;
  likes_count: number;
  favorites_count: number;
  content_count: number;
}

export interface UserPreferenceAuthorFacetResponse {
  user_id: number;
  display_name: string;
  score: number;
  likes_count: number;
  favorites_count: number;
  content_count: number;
}

export interface UserPreferenceRecentActionResponse {
  content_id: number;
  title: string;
  cover_url: string | null;
  category_name: string | null;
  author_name: string;
  action_type: string;
  acted_at: string;
}

export interface UserPreferenceContentItemResponse {
  content_id: number;
  title: string;
  cover_url: string | null;
  category_key: string;
  category_name: string;
  author_name: string;
  liked: boolean;
  favorited: boolean;
  latest_acted_at: string;
}

export interface UserPreferenceCategoryGroupResponse {
  key: string;
  name: string;
  item_count: number;
  items: UserPreferenceContentItemResponse[];
}

export interface UserLearningPreferenceInsightResponse {
  summary: string;
  total_likes: number;
  total_favorites: number;
  total_interactions: number;
  top_categories: UserPreferenceFacetResponse[];
  top_tags: UserPreferenceFacetResponse[];
  top_authors: UserPreferenceAuthorFacetResponse[];
  recent_actions: UserPreferenceRecentActionResponse[];
  grouped_works: UserPreferenceCategoryGroupResponse[];
}

export interface PageResponse<T> {
  list: T[];
  page: number;
  page_size: number;
  total: number;
  has_more: boolean;
}

export interface StoredSession {
  userId: number;
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  currentUser: CurrentUserResponse | null;
}

export interface UserProfileUpdatePayload {
  display_name?: string;
  avatar_asset_id?: number | null;
  bio?: string | null;
  email?: string;
  phone?: string | null;
  location?: string | null;
  profession?: string | null;
  birthday?: string | null;
  learning_goal?: string | null;
}

export interface UserSettingsUpdatePayload {
  theme?: string;
  language?: string;
  daily_reminder_enabled?: boolean;
  progress_notice_enabled?: boolean;
  badge_notice_enabled?: boolean;
  weekly_report_enabled?: boolean;
  two_factor_enabled?: boolean;
  profile_public?: boolean;
  learning_data_public?: boolean;
}

export interface ContentAuthorResponse {
  user_id: number;
  display_name: string;
  avatar_url: string | null;
  is_following: boolean;
}

export interface ContentCategoryResponse {
  id: number;
  name: string;
}

export interface DiscoverHotTopicResponse {
  id: number;
  name: string;
  content_count: number;
  views_count: number;
  likes_count: number;
  trend_score: number;
}

export interface DiscoverHotTagResponse {
  id: number;
  name: string;
  content_count: number;
  views_count: number;
  likes_count: number;
  trend_score: number;
}

export interface ContentInteractionResponse {
  views_count: number;
  likes_count: number;
  comments_count: number;
  favorites_count: number;
  shares_count: number;
  liked: boolean;
  favorited: boolean;
}

export interface ContentInteractionMutationResponse {
  content_id: number;
  interaction: ContentInteractionResponse;
}

export interface ContentCommentResponse {
  id: number;
  content_item_id: number;
  user_id: number;
  display_name: string;
  avatar_url: string | null;
  content: string;
  like_count: number;
  parent_id: number | null;
  root_id: number | null;
  reply_to_user_id: number | null;
  reply_to_display_name: string | null;
  created_at: string;
}

export interface ContentCommentListResponse {
  list: ContentCommentResponse[];
  page: number;
  page_size: number;
  total: number;
  has_more: boolean;
}

export interface ContentVideoResponse {
  id: number;
  title: string;
  summary: string | null;
  hashtags: string[];
  author: ContentAuthorResponse;
  category: ContentCategoryResponse | null;
  cover_url: string | null;
  video_url: string | null;
  hls_manifest_url: string | null;
  duration_seconds: number | null;
  bvid: string | null;
  interaction: ContentInteractionResponse;
  has_quiz: boolean;
  quiz_count: number;
  published_at: string | null;
}

export interface FeedVideosResponse {
  list: ContentVideoResponse[];
  next_cursor: string | null;
  has_more: boolean;
}

export type SearchContentsResponse = PageResponse<ContentVideoResponse>;

export interface ContentFavoriteItemResponse {
  content: ContentVideoResponse;
  favorited_at: string;
}

export interface ContentWatchHistoryItemResponse {
  content: ContentVideoResponse;
  watch_seconds: number;
  watch_progress: number;
  last_position_seconds: number;
  completed: boolean;
  last_viewed_at: string;
}

export interface QuizOptionResponse {
  option_id: number;
  option_text: string;
  vote_count: number;
  percent: number;
  is_correct: boolean | null;
}

export interface ContentQuizResponse {
  quiz_id: number;
  content_id: number;
  title: string;
  description: string | null;
  quiz_type: string;
  total_votes: number;
  has_submitted: boolean;
  selected_option_id: number | null;
  options: QuizOptionResponse[];
}

export interface QuizSubmitResponse {
  quiz_id: number;
  selected_option_id: number;
  is_correct: boolean;
  total_votes: number;
  options: QuizOptionResponse[];
}

export interface ContentCreatePayload {
  title: string;
  summary?: string | null;
  category_id?: number | null;
  cover_asset_id: number;
  primary_media_asset_id: number;
  content_type?: string;
  hashtags?: string[];
  duration_seconds?: number | null;
  allow_comment?: boolean;
  allow_duet?: boolean;
}

export interface ContentSharePayload {
  share_channel?: string;
}

export interface ContentCommentCreatePayload {
  content: string;
  parent_id?: number | null;
}

export interface ContentWatchProgressPayload {
  watch_seconds: number;
  watch_progress: number;
  last_position_seconds: number;
  completed: boolean;
}

export interface ContentInteractionBatchLikeItemPayload {
  client_id: string;
  action: "set_like";
  content_id: number;
  liked: boolean;
}

export interface ContentInteractionBatchFavoriteItemPayload {
  client_id: string;
  action: "set_favorite";
  content_id: number;
  favorited: boolean;
}

export interface ContentInteractionBatchCommentItemPayload {
  client_id: string;
  action: "create_comment";
  content_id: number;
  content: string;
  parent_id?: number | null;
}

export type ContentInteractionBatchItemPayload =
  | ContentInteractionBatchLikeItemPayload
  | ContentInteractionBatchFavoriteItemPayload
  | ContentInteractionBatchCommentItemPayload;

export interface ContentInteractionBatchSyncPayload {
  items: ContentInteractionBatchItemPayload[];
}

export interface ContentInteractionBatchItemResponse {
  client_id: string;
  action: string;
  content_id: number;
  interaction: ContentInteractionResponse;
  comment: ContentCommentResponse | null;
}

export interface ContentInteractionBatchSyncResponse {
  items: ContentInteractionBatchItemResponse[];
}

// ============ Backend B Types ============

// Learning Dashboard
export interface LearningDashboardResponse {
  total_learning_minutes: number;
  favorites_count: number;
  streak_days: number;
  completed_goals: number;
}

export interface CourseEnrollmentResponse {
  id: number;
  course_id: number;
  course_title: string;
  course_cover_url: string | null;
  instructor_name: string;
  total_lessons: number;
  completed_lessons: number;
  progress_percent: number;
  last_learned_at: string | null;
  enrolled_at: string;
}

export interface CourseInstructorResponse {
  user_id: number;
  display_name: string;
  avatar_url: string | null;
}

export interface CourseCategoryResponse {
  id: number;
  name: string;
}

export interface CourseLessonResponse {
  id: number;
  title: string;
  description: string | null;
  content_item_id: number | null;
  duration_minutes: number;
  sort_order: number;
  is_free: boolean;
  is_completed: boolean;
  progress_percent: number;
}

export interface CourseDetailResponse {
  id: number;
  title: string;
  description: string | null;
  instructor: CourseInstructorResponse;
  category: CourseCategoryResponse | null;
  cover_url: string | null;
  level: string;
  duration_minutes: number;
  lesson_count: number;
  enrollment_count: number;
  rating: number;
  is_enrolled: boolean;
  lessons: CourseLessonResponse[];
  created_at: string;
}

export interface CourseListItemResponse {
  id: number;
  title: string;
  description: string | null;
  instructor: CourseInstructorResponse;
  category: CourseCategoryResponse | null;
  cover_url: string | null;
  level: string;
  duration_minutes: number;
  lesson_count: number;
  enrollment_count: number;
  rating: number;
  is_enrolled: boolean;
}

// Practice
export interface QuestionBankResponse {
  id: number;
  title: string;
  description: string | null;
  category?: string;
  difficulty: string;
  question_count: number;
  total_score?: number;
}

export interface PracticeQuestionResponse {
  id: number;
  question_text?: string;
  content?: string;
  question_type: string;
  difficulty?: string;
  score: number;
  options: PracticeQuestionOptionResponse[];
}

export interface PracticeQuestionOptionResponse {
  id: number;
  option_text?: string;
  content?: string;
  option_order?: number;
  sort_order?: number;
}

export interface PracticeSessionResponse {
  id: number;
  bank_id: number;
  session_type: string;
  status: string;
  total_score?: number;
  earned_score?: number;
  total_questions: number;
  answered_questions: number;
  started_at?: string;
  created_at?: string;
  completed_at?: string | null;
}

export interface PracticeSessionCreatePayload {
  bank_id: number;
  session_type: string;
}

export interface VideoPracticeGeneratePayload {
  page_context: AIChatPageContext;
  request_text?: string;
  question_count?: number;
  session_type?: string;
}

export interface VideoPracticeGenerateResponse {
  bank: QuestionBankResponse;
  session: PracticeSessionResponse;
}

export interface PracticeAnswerSubmitPayload {
  question_id: number;
  selected_option_ids: number[];
}

export interface PracticeAnswerResponse {
  question_id: number;
  is_correct: boolean;
  score?: number;
  earned_score?: number;
  correct_option_ids?: number[];
}

export interface PracticeSessionSubmitResponse {
  session_id: number;
  total_questions: number;
  correct_answers: number;
  total_score: number;
  earned_score: number;
  accuracy: number;
}

export interface PracticeSessionResultAnswer {
  question_id: number;
  is_correct: boolean;
  earned_score: number;
}

export interface PracticeSessionResultResponse extends PracticeSessionSubmitResponse {
  bank_title: string;
  submitted_at: string;
  answers: PracticeSessionResultAnswer[];
}

// Assessment
export interface AssessmentSnapshotResponse {
  id: number;
  user_id: number;
  assessment_type: string;
  period_start: string;
  period_end: string;
  total_learning_minutes: number;
  completed_courses: number;
  average_score: number;
  rank_percent: number | null;
  correct_rate: number | null;
  focus_rate: number | null;
  metrics_json: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface AssessmentTrendDataPoint {
  date: string;
  learning_minutes: number;
  average_score: number;
  correct_rate: number | null;
}

export interface AssessmentTrendResponse {
  assessment_type: string;
  data_points: AssessmentTrendDataPoint[];
}

export interface AssessmentGeneratePayload {
  assessment_type: string;
  force_regenerate?: boolean;
}

// Student profile and learning path
export interface SkillScoreResponse {
  dimension_id: number;
  code: string;
  name: string;
  score: number;
  percentile: number | null;
  level: string | null;
  insight: string | null;
}

export interface SkillSnapshotResponse {
  id: number;
  user_id: number;
  source_type: string;
  source_ref_id: number | null;
  snapshot_version: number;
  total_score: number | null;
  rank_percent: number | null;
  generated_by: string;
  generated_at: string;
  scores: SkillScoreResponse[];
}

export interface LearningPathNodeResponse {
  id: number;
  node_id: number;
  title: string;
  description: string | null;
  node_type: string;
  course_id: number | null;
  status: string;
  progress_percent: number;
  sort_order: number;
  recommended_reason: string | null;
  estimated_minutes: number;
  stage_code?: string | null;
  stage_goal?: string | null;
  resources: LearningPathStageResourceResponse[];
  assessment?: LearningPathStageAssessmentResponse | null;
}

export interface UserLearningPathResponse {
  id: number;
  path_id: number;
  name: string;
  description: string | null;
  target_role: string | null;
  status: string;
  progress_percent: number;
  current_node_id: number | null;
  ai_summary: string | null;
  nodes: LearningPathNodeResponse[];
}

export interface LearningPathStageResourceResponse {
  resource_type: string;
  source: string;
  title: string;
  description?: string | null;
  content_id?: number | null;
  category_name?: string | null;
  cover_url?: string | null;
  video_url?: string | null;
  external_url?: string | null;
}

export interface LearningPathStageAssessmentResponse {
  mode: string;
  question_count: number;
  pass_score: number;
  generated_bank_id?: number | null;
  generated_session_id?: number | null;
}

export interface LearningPathPlanStageResponse {
  stage_code: string;
  title: string;
  goal: string;
  description?: string | null;
  estimated_hours: number;
  recommended_reason?: string | null;
  resources: LearningPathStageResourceResponse[];
  assessment?: LearningPathStageAssessmentResponse | null;
}

export interface LearningPathPlanRouteResponse {
  route_code: string;
  title: string;
  summary: string;
  fit_reason: string;
  difficulty: string;
  estimated_weeks: number;
  stages: LearningPathPlanStageResponse[];
}

export interface LearningPathPlanResponse {
  planning_summary: string;
  route_options: LearningPathPlanRouteResponse[];
}

export interface LearningPathActivatePayload {
  selected_route: LearningPathPlanRouteResponse;
}

export interface LearningPathNodePracticeGenerateResponse {
  bank_id: number;
  bank_title: string;
  session_id: number;
}

export interface LearningPathGeneratePayload {
  target_role?: string | null;
  current_level?: string;
  weekly_hours?: number;
  route_count?: number;
  preferred_resource_mode?: string;
}

// Reports
export interface ReportAchievementResponse {
  id: number;
  title: string;
  description: string | null;
  icon: string | null;
  color_token: string | null;
  sort_order: number;
}

export interface MonthlyReportResponse {
  id: number;
  user_id: number;
  report_month: string;
  assessment_snapshot_id: number | null;
  report_status: string;
  total_learning_minutes: number;
  completed_courses: number;
  average_score: number;
  site_rank: number | null;
  strengths: string[];
  improvements: string[];
  ai_summary: string | null;
  exported_pdf_asset_id: number | null;
  generated_at: string;
  achievements: ReportAchievementResponse[];
}

// Notification
export interface NotificationResponse {
  id: number;
  notification_type: string;
  title: string;
  body: string;
  biz_type: string | null;
  biz_id: number | null;
  read_status: boolean;
  read_at: string | null;
  created_at: string;
}

export interface NotificationUnreadCountResponse {
  unread_count: number;
}

// AI Chat
export interface AIChatSessionResponse {
  id: number;
  session_name: string | null;
  scene_code: string;
  model_name: string;
  status: string;
  summary: string | null;
  last_message_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AIChatMessageResponse {
  id: number;
  session_id: number;
  role: string;
  message_type: string;
  content: string;
  token_count: number;
  latency_ms: number | null;
  error_code: string | null;
  trace_id: string | null;
  created_at: string;
}

export interface AIChatSessionCreatePayload {
  session_name?: string | null;
  scene_code?: string;
  model_name?: string;
}

export interface AIChatMessageSendPayload {
  content: string;
  stream?: boolean;
  page_context?: AIChatPageContext;
}

export interface AIChatPageAction {
  id: string;
  label: string;
  description?: string | null;
  type: "navigate" | "generate" | "analyze" | "recommend";
  href?: string | null;
}

export interface AIChatCurrentVideoContext {
  content_id: number;
  title: string;
  summary?: string | null;
  category_name?: string | null;
  author_name?: string | null;
  hashtags?: string[];
  has_quiz?: boolean;
  quiz_count?: number;
  duration_seconds?: number | null;
  video_url?: string | null;
}

export interface AIChatPageContext {
  route: string;
  page_type: string;
  page_title: string;
  summary?: string | null;
  current_video?: AIChatCurrentVideoContext | null;
  available_actions: AIChatPageAction[];
  metadata?: Record<string, any>;
}
