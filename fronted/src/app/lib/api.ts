import { clearSession, getAccessToken } from "./session";

interface ApiEnvelope<T> {
  code: number;
  message: string;
  data: T;
  request_id?: string | null;
}

interface ApiRequestOptions extends RequestInit {
  auth?: boolean;
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "/api/v1").replace(/\/$/, "");

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

function buildUrl(path: string) {
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
  const { auth = true, headers, body, ...rest } = options;
  const requestHeaders = new Headers(headers);

  if (auth) {
    const accessToken = getAccessToken();
    if (accessToken) {
      requestHeaders.set("Authorization", `Bearer ${accessToken}`);
    }
  }

  if (body && !(body instanceof FormData) && !requestHeaders.has("Content-Type")) {
    requestHeaders.set("Content-Type", "application/json");
  }

  const response = await fetch(buildUrl(path), {
    ...rest,
    headers: requestHeaders,
    body,
  });

  const envelope = await parseEnvelope<T>(response);
  const message =
    envelope?.message || (response.ok ? "Request succeeded." : "Request failed.");

  if (response.status === 401) {
    clearSession();
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

  return envelope.data;
}
