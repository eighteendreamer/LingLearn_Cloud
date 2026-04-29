import type { AuthTokenResponse, CurrentUserResponse, StoredSession } from "./types";

const SESSION_STORAGE_KEY = "linglearn.cloud.session";

function canUseStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function readSession(): StoredSession | null {
  if (!canUseStorage()) {
    return null;
  }

  const raw = window.localStorage.getItem(SESSION_STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as StoredSession;
  } catch {
    window.localStorage.removeItem(SESSION_STORAGE_KEY);
    return null;
  }
}

function writeSession(session: StoredSession) {
  if (!canUseStorage()) {
    return;
  }

  window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
}

export function getStoredSession() {
  return readSession();
}

export function getAccessToken() {
  return readSession()?.accessToken ?? null;
}

export function getRefreshToken() {
  return readSession()?.refreshToken ?? null;
}

export function getStoredCurrentUser() {
  return readSession()?.currentUser ?? null;
}

export function hasSession() {
  return Boolean(getAccessToken());
}

export function clearSession() {
  if (!canUseStorage()) {
    return;
  }

  window.localStorage.removeItem(SESSION_STORAGE_KEY);
}

export function saveAuthSession(tokens: AuthTokenResponse) {
  const previous = readSession();
  const next: StoredSession = {
    userId: tokens.user_id,
    accessToken: tokens.access_token,
    refreshToken: tokens.refresh_token,
    expiresAt: Date.now() + tokens.expires_in * 1000,
    currentUser: previous?.currentUser ?? null,
  };
  writeSession(next);
}

export function saveCurrentUser(currentUser: CurrentUserResponse) {
  const existing = readSession();
  if (!existing) {
    return;
  }

  writeSession({
    ...existing,
    currentUser,
  });
}
