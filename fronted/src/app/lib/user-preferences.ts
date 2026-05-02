import { getStoredCurrentUser } from "./session";
import { applyRuntimeLanguage } from "./runtime-i18n";
import type { CurrentUserResponse } from "./types";

const DEFAULT_LANGUAGE = "zh-CN";
const THEME_MEDIA_QUERY = "(prefers-color-scheme: dark)";

function canUseDom() {
  return typeof window !== "undefined" && typeof document !== "undefined";
}

function resolveTheme(theme: string) {
  if (!canUseDom()) {
    return "light";
  }

  if (theme === "dark") {
    return "dark";
  }

  if (theme === "system") {
    return window.matchMedia(THEME_MEDIA_QUERY).matches ? "dark" : "light";
  }

  return "light";
}

export function applyThemePreference(theme: string) {
  if (!canUseDom()) {
    return;
  }

  const root = document.documentElement;
  const resolvedTheme = resolveTheme(theme);

  root.classList.toggle("dark", resolvedTheme === "dark");
  root.dataset.theme = theme;
  root.style.colorScheme = resolvedTheme;
}

export function applyLanguagePreference(language: string) {
  if (!canUseDom()) {
    return;
  }

  const resolvedLanguage = language || DEFAULT_LANGUAGE;
  document.documentElement.lang = resolvedLanguage;
  applyRuntimeLanguage(resolvedLanguage);
}

export function applyCurrentUserPreferences(currentUser?: CurrentUserResponse | null) {
  const source = currentUser ?? getStoredCurrentUser();
  const theme = source?.settings.theme ?? "system";
  const language = source?.settings.language ?? source?.profile.locale ?? DEFAULT_LANGUAGE;

  applyThemePreference(theme);
  applyLanguagePreference(language);
}

export function watchSystemThemeChanges(onChange: () => void) {
  if (!canUseDom()) {
    return () => undefined;
  }

  const mediaQuery = window.matchMedia(THEME_MEDIA_QUERY);
  const handleChange = () => onChange();

  if ("addEventListener" in mediaQuery) {
    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }

  mediaQuery.addListener(handleChange);
  return () => mediaQuery.removeListener(handleChange);
}
