import type { ContentVideoResponse } from "./types";

export const DISCOVER_STATE_STORAGE_KEY = "linglearn.cloud.discover.state";
export const VIDEO_FEED_MUTE_STORAGE_KEY = "linglearn.cloud.video-feed.muted";

export type ContentWatchSource = "discover" | "learning" | "profile";

export type DiscoverPersistedState = {
  searchQuery: string;
  selectedCategoryId: number | null;
  scrollTop: number;
};

export type DiscoverWatchNavigationState = {
  source: ContentWatchSource;
  videos: ContentVideoResponse[];
  currentIndex: number;
  persistedState?: DiscoverPersistedState;
};

export function readDiscoverPersistedState(): DiscoverPersistedState {
  if (typeof window === "undefined") {
    return {
      searchQuery: "",
      selectedCategoryId: null,
      scrollTop: 0,
    };
  }

  const raw = window.sessionStorage.getItem(DISCOVER_STATE_STORAGE_KEY);
  if (!raw) {
    return {
      searchQuery: "",
      selectedCategoryId: null,
      scrollTop: 0,
    };
  }

  try {
    const parsed = JSON.parse(raw) as Partial<DiscoverPersistedState>;
    return {
      searchQuery: typeof parsed.searchQuery === "string" ? parsed.searchQuery : "",
      selectedCategoryId: typeof parsed.selectedCategoryId === "number" ? parsed.selectedCategoryId : null,
      scrollTop: typeof parsed.scrollTop === "number" ? parsed.scrollTop : 0,
    };
  } catch {
    return {
      searchQuery: "",
      selectedCategoryId: null,
      scrollTop: 0,
    };
  }
}

export function writeDiscoverPersistedState(state: DiscoverPersistedState) {
  if (typeof window === "undefined") {
    return;
  }

  window.sessionStorage.setItem(DISCOVER_STATE_STORAGE_KEY, JSON.stringify(state));
}
