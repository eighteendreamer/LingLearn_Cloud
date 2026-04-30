import type {
  ContentCommentResponse,
  ContentInteractionBatchCommentItemPayload,
  ContentInteractionBatchFavoriteItemPayload,
  ContentInteractionBatchItemPayload,
  ContentInteractionBatchLikeItemPayload,
  ContentInteractionBatchSyncPayload,
} from "./types";

const INTERACTION_QUEUE_STORAGE_KEY = "linglearn.cloud.interaction-sync-queue";

export type PendingCommentDraft = {
  client_id: string;
  temp_comment_id: number;
  content_id: number;
  content: string;
  parent_id: number | null;
  created_at: string;
  display_name: string;
  avatar_url: string | null;
  reply_to_display_name: string | null;
};

export type InteractionSyncQueue = {
  likes: Record<number, ContentInteractionBatchLikeItemPayload>;
  favorites: Record<number, ContentInteractionBatchFavoriteItemPayload>;
  comments: PendingCommentDraft[];
};

const EMPTY_QUEUE: InteractionSyncQueue = {
  likes: {},
  favorites: {},
  comments: [],
};

function buildClientId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

export function createPendingCommentDraft(input: {
  contentId: number;
  content: string;
  parentId: number | null;
  displayName: string;
  avatarUrl: string | null;
  replyToDisplayName: string | null;
}): PendingCommentDraft {
  return {
    client_id: buildClientId("comment"),
    temp_comment_id: -Date.now(),
    content_id: input.contentId,
    content: input.content,
    parent_id: input.parentId,
    created_at: new Date().toISOString(),
    display_name: input.displayName,
    avatar_url: input.avatarUrl,
    reply_to_display_name: input.replyToDisplayName,
  };
}

export function buildPendingCommentResponse(
  draft: PendingCommentDraft,
  userId: number,
): ContentCommentResponse {
  return {
    id: draft.temp_comment_id,
    content_item_id: draft.content_id,
    user_id: userId,
    display_name: draft.display_name,
    avatar_url: draft.avatar_url,
    content: draft.content,
    like_count: 0,
    parent_id: draft.parent_id,
    root_id: draft.parent_id,
    reply_to_user_id: null,
    reply_to_display_name: draft.reply_to_display_name,
    created_at: draft.created_at,
  };
}

export function readInteractionSyncQueue(): InteractionSyncQueue {
  if (typeof window === "undefined") {
    return EMPTY_QUEUE;
  }
  const raw = window.localStorage.getItem(INTERACTION_QUEUE_STORAGE_KEY);
  if (!raw) {
    return EMPTY_QUEUE;
  }
  try {
    const parsed = JSON.parse(raw) as Partial<InteractionSyncQueue>;
    return {
      likes: parsed.likes ?? {},
      favorites: parsed.favorites ?? {},
      comments: parsed.comments ?? [],
    };
  } catch {
    return EMPTY_QUEUE;
  }
}

export function persistInteractionSyncQueue(queue: InteractionSyncQueue) {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(INTERACTION_QUEUE_STORAGE_KEY, JSON.stringify(queue));
}

export function enqueueLikeAction(queue: InteractionSyncQueue, contentId: number, liked: boolean): InteractionSyncQueue {
  return {
    ...queue,
    likes: {
      ...queue.likes,
      [contentId]: {
        client_id: buildClientId("like"),
        action: "set_like",
        content_id: contentId,
        liked,
      },
    },
  };
}

export function enqueueFavoriteAction(
  queue: InteractionSyncQueue,
  contentId: number,
  favorited: boolean,
): InteractionSyncQueue {
  return {
    ...queue,
    favorites: {
      ...queue.favorites,
      [contentId]: {
        client_id: buildClientId("favorite"),
        action: "set_favorite",
        content_id: contentId,
        favorited,
      },
    },
  };
}

export function enqueueCommentAction(queue: InteractionSyncQueue, draft: PendingCommentDraft): InteractionSyncQueue {
  return {
    ...queue,
    comments: [...queue.comments, draft],
  };
}

export function buildInteractionSyncPayload(queue: InteractionSyncQueue): ContentInteractionBatchSyncPayload {
  const items: ContentInteractionBatchItemPayload[] = [
    ...Object.values(queue.likes),
    ...Object.values(queue.favorites),
    ...queue.comments.map<ContentInteractionBatchCommentItemPayload>((comment) => ({
      client_id: comment.client_id,
      action: "create_comment",
      content_id: comment.content_id,
      content: comment.content,
      parent_id: comment.parent_id,
    })),
  ];
  return { items };
}

export function removeSyncedQueueItems(
  currentQueue: InteractionSyncQueue,
  syncedQueue: InteractionSyncQueue,
): InteractionSyncQueue {
  const nextLikes = { ...currentQueue.likes };
  const nextFavorites = { ...currentQueue.favorites };

  Object.entries(syncedQueue.likes).forEach(([contentId, item]) => {
    if (nextLikes[Number(contentId)]?.client_id === item.client_id) {
      delete nextLikes[Number(contentId)];
    }
  });

  Object.entries(syncedQueue.favorites).forEach(([contentId, item]) => {
    if (nextFavorites[Number(contentId)]?.client_id === item.client_id) {
      delete nextFavorites[Number(contentId)];
    }
  });

  const syncedCommentIds = new Set(syncedQueue.comments.map((item) => item.client_id));

  return {
    likes: nextLikes,
    favorites: nextFavorites,
    comments: currentQueue.comments.filter((item) => !syncedCommentIds.has(item.client_id)),
  };
}
