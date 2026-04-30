import { apiRequest } from "./api";
import type {
  ContentCommentResponse,
  ContentCommentCreatePayload,
  ContentCategoryResponse,
  ContentCommentListResponse,
  ContentCreatePayload,
  ContentInteractionMutationResponse,
  ContentSharePayload,
  ContentVideoResponse,
  ContentWatchProgressPayload,
  FeedVideosResponse,
} from "./types";

export async function createContent(payload: ContentCreatePayload) {
  return apiRequest<ContentVideoResponse>("/contents", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchContentCategories() {
  return apiRequest<ContentCategoryResponse[]>("/discover/categories");
}

export async function fetchFeedVideos(cursor?: string | null, recommendType = "for_you") {
  const search = new URLSearchParams();
  search.set("limit", "10");
  search.set("recommend_type", recommendType);
  if (cursor) {
    search.set("cursor", cursor);
  }
  return apiRequest<FeedVideosResponse>(`/feed/videos?${search.toString()}`);
}

export async function likeContent(contentId: number) {
  return apiRequest<ContentInteractionMutationResponse>(`/contents/${contentId}/like`, {
    method: "POST",
  });
}

export async function unlikeContent(contentId: number) {
  return apiRequest<ContentInteractionMutationResponse>(`/contents/${contentId}/like`, {
    method: "DELETE",
  });
}

export async function favoriteContent(contentId: number) {
  return apiRequest<ContentInteractionMutationResponse>(`/contents/${contentId}/favorite`, {
    method: "POST",
  });
}

export async function unfavoriteContent(contentId: number) {
  return apiRequest<ContentInteractionMutationResponse>(`/contents/${contentId}/favorite`, {
    method: "DELETE",
  });
}

export async function shareContent(contentId: number, payload: ContentSharePayload = {}) {
  return apiRequest<ContentInteractionMutationResponse>(`/contents/${contentId}/share`, {
    method: "POST",
    body: JSON.stringify({
      share_channel: payload.share_channel || "internal",
    }),
  });
}

export async function fetchContentComments(contentId: number, page = 1, pageSize = 20) {
  const search = new URLSearchParams();
  search.set("page", String(page));
  search.set("page_size", String(pageSize));
  return apiRequest<ContentCommentListResponse>(
    `/contents/${contentId}/comments?${search.toString()}`,
    { auth: false },
  );
}

export async function createContentComment(contentId: number, payload: ContentCommentCreatePayload) {
  return apiRequest<ContentCommentResponse>(`/contents/${contentId}/comments`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function reportWatchProgress(contentId: number, payload: ContentWatchProgressPayload) {
  return apiRequest<ContentInteractionMutationResponse>(`/contents/${contentId}/watch-progress`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
