import { apiRequest } from "./api";
import {
  clearSession,
  getRefreshToken,
  saveAuthSession,
  saveCurrentUser,
} from "./session";
import type {
  AuthTokenResponse,
  CurrentUserResponse,
  PageResponse,
  UserProfileUpdatePayload,
  UserSettingsUpdatePayload,
  UserWorkListItemResponse,
} from "./types";

interface LoginPayload {
  account: string;
  password: string;
}

interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  display_name: string;
}

export async function loginWithPassword(payload: LoginPayload) {
  const tokens = await apiRequest<AuthTokenResponse>("/auth/login", {
    method: "POST",
    auth: false,
    body: JSON.stringify(payload),
  });
  saveAuthSession(tokens);
  return fetchCurrentUser();
}

export async function registerWithPassword(payload: RegisterPayload) {
  const tokens = await apiRequest<AuthTokenResponse>("/auth/register", {
    method: "POST",
    auth: false,
    body: JSON.stringify(payload),
  });
  saveAuthSession(tokens);
  return fetchCurrentUser();
}

export async function fetchCurrentUser() {
  const currentUser = await apiRequest<CurrentUserResponse>("/users/me");
  saveCurrentUser(currentUser);
  return currentUser;
}

export async function updateMyProfile(payload: UserProfileUpdatePayload) {
  const currentUser = await apiRequest<CurrentUserResponse>("/users/me/profile", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  saveCurrentUser(currentUser);
  return currentUser;
}

export async function updateMySettings(payload: UserSettingsUpdatePayload) {
  const currentUser = await apiRequest<CurrentUserResponse>("/users/me/settings", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  saveCurrentUser(currentUser);
  return currentUser;
}

export async function fetchMyWorks(userId: number) {
  return apiRequest<PageResponse<UserWorkListItemResponse>>(
    `/users/${userId}/works?page=1&page_size=6`,
  );
}

export async function logoutCurrentUser() {
  const refreshToken = getRefreshToken();

  try {
    if (refreshToken) {
      await apiRequest("/auth/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    }
  } finally {
    clearSession();
  }
}

export async function followUser(userId: number) {
  return apiRequest<{ target_user_id: number; is_following: boolean }>(`/users/${userId}/follow`, {
    method: "POST",
  });
}

export async function unfollowUser(userId: number) {
  return apiRequest<{ target_user_id: number; is_following: boolean }>(`/users/${userId}/follow`, {
    method: "DELETE",
  });
}
