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
