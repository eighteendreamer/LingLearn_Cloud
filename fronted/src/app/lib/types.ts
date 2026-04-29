export interface AuthTokenResponse {
  user_id: number;
  access_token: string;
  refresh_token: string;
  expires_in: number;
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
}

export interface ContentCategoryResponse {
  id: number;
  name: string;
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

export interface ContentVideoResponse {
  id: number;
  title: string;
  summary: string | null;
  hashtags: string[];
  author: ContentAuthorResponse;
  category: ContentCategoryResponse | null;
  cover_url: string | null;
  video_url: string | null;
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
