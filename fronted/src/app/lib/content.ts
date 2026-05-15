import { apiRequest } from "./api";
import type {
  ContentInteractionBatchSyncPayload,
  ContentInteractionBatchSyncResponse,
  ContentCommentResponse,
  ContentCommentCreatePayload,
  ContentCategoryResponse,
  ContentCommentListResponse,
  ContentCreatePayload,
  DiscoverHotTagResponse,
  DiscoverHotTopicResponse,
  ContentInteractionMutationResponse,
  ContentQuizResponse,
  ContentSharePayload,
  ContentVideoResponse,
  ContentWatchProgressPayload,
  FeedVideosResponse,
  QuizSubmitResponse,
  SearchContentsResponse,
} from "./types";

type RequestOptions = {
  signal?: AbortSignal;
  cache?: boolean;
  cacheTtlMs?: number;
};

export async function createContent(payload: ContentCreatePayload) {
  return apiRequest<ContentVideoResponse>("/contents", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchContentDetail(contentId: number, options: RequestOptions = {}) {
  return apiRequest<ContentVideoResponse>(`/contents/${contentId}`, options);
}

export async function fetchContentCategories() {
  return apiRequest<ContentCategoryResponse[]>("/discover/categories");
}

export async function fetchDiscoverHotTopics() {
  return apiRequest<DiscoverHotTopicResponse[]>("/discover/hot-topics", { auth: false });
}

export async function fetchDiscoverHotTags() {
  return apiRequest<DiscoverHotTagResponse[]>("/discover/hot-tags", { auth: false });
}

export async function fetchFeedVideos(
  cursor?: string | null,
  recommendType = "for_you",
  categoryId?: number | null,
  options: RequestOptions = {},
) {
  const search = new URLSearchParams();
  search.set("limit", "10");
  search.set("recommend_type", recommendType);
  if (cursor) {
    search.set("cursor", cursor);
  }
  if (categoryId) {
    search.set("category_id", String(categoryId));
  }
  return apiRequest<FeedVideosResponse>(`/feed/videos?${search.toString()}`, options);
}

export async function fetchSearchContents(params: {
  keyword?: string | null;
  categoryId?: number | null;
  page?: number;
  pageSize?: number;
}, options: RequestOptions = {}) {
  const search = new URLSearchParams();
  search.set("page", String(params.page ?? 1));
  search.set("page_size", String(params.pageSize ?? 20));
  if (params.keyword?.trim()) {
    search.set("keyword", params.keyword.trim());
  }
  if (params.categoryId) {
    search.set("category_id", String(params.categoryId));
  }
  return apiRequest<SearchContentsResponse>(`/search/contents?${search.toString()}`, options);
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

export async function fetchContentQuizzes(contentId: number) {
  return apiRequest<ContentQuizResponse[]>(`/contents/${contentId}/quizzes`);
}

export async function submitQuizAnswer(quizId: number, selectedOptionId: number) {
  return apiRequest<QuizSubmitResponse>(`/quizzes/${quizId}/submit`, {
    method: "POST",
    body: JSON.stringify({ selected_option_id: selectedOptionId }),
  });
}

export async function syncContentInteractionsBatch(payload: ContentInteractionBatchSyncPayload) {
  return apiRequest<ContentInteractionBatchSyncResponse>("/contents/interactions/batch-sync", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
