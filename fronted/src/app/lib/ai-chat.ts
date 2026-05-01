import { buildApiUrl } from "./api";
import { getAccessToken } from "./session";
import type { AIChatMessageResponse, AIChatMessageSendPayload } from "./types";

export type AIChatStreamEvent =
  | { type: "start" }
  | { type: "delta"; content: string }
  | { type: "done"; message: AIChatMessageResponse };

interface StreamOptions {
  onStart?: () => void;
  onDelta: (content: string) => void;
  onDone: (message: AIChatMessageResponse | null) => void;
}

export async function streamAIChatMessage(
  sessionId: number,
  payload: AIChatMessageSendPayload,
  options: StreamOptions
) {
  const headers = new Headers({ "Content-Type": "application/json" });
  const accessToken = getAccessToken();
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  const response = await fetch(buildApiUrl(`/ai/chat/sessions/${sessionId}/messages/stream`), {
    method: "POST",
    headers,
    body: JSON.stringify({ ...payload, stream: true }),
  });

  if (!response.ok || !response.body) {
    throw new Error("AI stream request failed.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const rawEvent of events) {
      const dataLine = rawEvent
        .split("\n")
        .find((line) => line.startsWith("data:"));
      if (!dataLine) {
        continue;
      }

      const event = JSON.parse(dataLine.slice(5).trim()) as AIChatStreamEvent;
      if (event.type === "start") {
        options.onStart?.();
      } else if (event.type === "delta") {
        options.onDelta(event.content);
      } else if (event.type === "done") {
        options.onDone(event.message);
      }
    }
  }
}
