import { clearSession, getAccessToken } from "./session";

interface ApiEnvelope<T> {
  code: number;
  message: string;
  data: T;
  request_id?: string | null;
}

interface ApiRequestOptions extends RequestInit {
  auth?: boolean;
  cache?: boolean;
  cacheTtlMs?: number;
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "/api/v1").replace(/\/$/, "");
const DEFAULT_GET_CACHE_TTL_MS = 30_000;

type CacheEntry = {
  expiresAt: number;
  data: unknown;
};

const responseCache = new Map<string, CacheEntry>();
const inflightRequests = new Map<string, Promise<unknown>>();

function resolveMethod(options?: RequestInit) {
  return (options?.method || "GET").toUpperCase();
}

function buildCacheKey(path: string, scope: string) {
  return `${scope}:${path}`;
}

function readCachedResponse<T>(cacheKey: string): T | null {
  const cached = responseCache.get(cacheKey);
  if (!cached) {
    return null;
  }
  if (cached.expiresAt <= Date.now()) {
    responseCache.delete(cacheKey);
    return null;
  }
  return cached.data as T;
}

function writeCachedResponse(cacheKey: string, data: unknown, ttlMs: number) {
  responseCache.set(cacheKey, {
    data,
    expiresAt: Date.now() + ttlMs,
  });
}

function invalidateResponseCache(scopePrefix?: string) {
  if (!scopePrefix) {
    responseCache.clear();
    inflightRequests.clear();
    return;
  }

  for (const key of responseCache.keys()) {
    if (key.startsWith(scopePrefix)) {
      responseCache.delete(key);
    }
  }
}

export class ApiError extends Error {
  status: number;
  code: number;

  constructor(message: string, status: number, code = -1) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

export function buildApiUrl(path: string) {
  if (/^https?:\/\//.test(path)) {
    return path;
  }

  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}

async function parseEnvelope<T>(response: Response): Promise<ApiEnvelope<T> | null> {
  const raw = await response.text();
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as ApiEnvelope<T>;
  } catch {
    return null;
  }
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const {
    auth = true,
    cache = true,
    cacheTtlMs = DEFAULT_GET_CACHE_TTL_MS,
    headers,
    body,
    ...rest
  } = options;
  const requestHeaders = new Headers(headers);
  const method = resolveMethod(options);
  const accessToken = auth ? getAccessToken() : null;
  const scope = `user:${auth ? accessToken || "guest" : "anon"}`;
  const cacheKey = buildCacheKey(path, scope);
  const useCache = cache && method === "GET";

  if (auth) {
    if (accessToken) {
      requestHeaders.set("Authorization", `Bearer ${accessToken}`);
    }
  }

  if (body && !(body instanceof FormData) && !requestHeaders.has("Content-Type")) {
    requestHeaders.set("Content-Type", "application/json");
  }

  if (!useCache) {
    invalidateResponseCache(scope);
  } else {
    const cached = readCachedResponse<T>(cacheKey);
    if (cached !== null) {
      return cached;
    }

    const inflight = inflightRequests.get(cacheKey);
    if (inflight) {
      return inflight as Promise<T>;
    }
  }

  const requestPromise = (async () => {
    const response = await fetch(buildApiUrl(path), {
      ...rest,
      headers: requestHeaders,
      body,
    });

    const envelope = await parseEnvelope<T>(response);
    const message =
      envelope?.message || (response.ok ? "Request succeeded." : "Request failed.");

    if (response.status === 401) {
      clearSession();
      invalidateResponseCache(scope);
    }

    if (!response.ok) {
      throw new ApiError(message, response.status, envelope?.code ?? response.status);
    }

    if (!envelope) {
      throw new ApiError("Empty response from server.", response.status);
    }

    if (envelope.code !== 0) {
      throw new ApiError(envelope.message, response.status, envelope.code);
    }

    if (useCache) {
      writeCachedResponse(cacheKey, envelope.data, cacheTtlMs);
    }

    return envelope.data;
  })();

  if (useCache) {
    inflightRequests.set(cacheKey, requestPromise);
  }

  try {
    return await requestPromise;
  } finally {
    if (useCache) {
      inflightRequests.delete(cacheKey);
    }
  }
}

// 管理员专用的 API 请求函数
export async function adminApiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const {
    auth = true,
    cache = true,
    cacheTtlMs = DEFAULT_GET_CACHE_TTL_MS,
    headers,
    body,
    ...rest
  } = options;
  const requestHeaders = new Headers(headers);
  const method = resolveMethod(options);
  const adminToken = auth ? localStorage.getItem("admin_token") : null;
  const scope = `admin:${auth ? adminToken || "guest" : "anon"}`;
  const cacheKey = buildCacheKey(path, scope);
  const useCache = cache && method === "GET";

  if (auth) {
    if (adminToken) {
      requestHeaders.set("Authorization", `Bearer ${adminToken}`);
    }
  }

  if (body && !(body instanceof FormData) && !requestHeaders.has("Content-Type")) {
    requestHeaders.set("Content-Type", "application/json");
  }

  if (!useCache) {
    invalidateResponseCache(scope);
  } else {
    const cached = readCachedResponse<T>(cacheKey);
    if (cached !== null) {
      return cached;
    }

    const inflight = inflightRequests.get(cacheKey);
    if (inflight) {
      return inflight as Promise<T>;
    }
  }

  const requestPromise = (async () => {
    const response = await fetch(buildApiUrl(path), {
      ...rest,
      headers: requestHeaders,
      body,
    });

    const envelope = await parseEnvelope<T>(response);
    const message =
      envelope?.message || (response.ok ? "Request succeeded." : "Request failed.");

    if (response.status === 401) {
      invalidateResponseCache(scope);
      localStorage.removeItem("admin_token");
      localStorage.removeItem("admin_refresh_token");
      localStorage.removeItem("admin_user");
      window.location.href = "/admin/login";
    }

    if (!response.ok) {
      throw new ApiError(message, response.status, envelope?.code ?? response.status);
    }

    if (!envelope) {
      throw new ApiError("Empty response from server.", response.status);
    }

    if (envelope.code !== 0) {
      throw new ApiError(envelope.message, response.status, envelope.code);
    }

    if (useCache) {
      writeCachedResponse(cacheKey, envelope.data, cacheTtlMs);
    }

    return envelope.data;
  })();

  if (useCache) {
    inflightRequests.set(cacheKey, requestPromise);
  }

  try {
    return await requestPromise;
  } finally {
    if (useCache) {
      inflightRequests.delete(cacheKey);
    }
  }
}
