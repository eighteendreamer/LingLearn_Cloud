import { apiRequest } from "./api";
import type {
  ContentCreatePayload,
  ContentVideoResponse,
  FeedVideosResponse,
} from "./types";

export async function createContent(payload: ContentCreatePayload) {
  return apiRequest<ContentVideoResponse>("/contents", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchFeedVideos(cursor?: string | null) {
  const search = new URLSearchParams();
  search.set("limit", "10");
  if (cursor) {
    search.set("cursor", cursor);
  }
  return apiRequest<FeedVideosResponse>(`/feed/videos?${search.toString()}`);
}
