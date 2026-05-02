import type { AIChatPageContext } from "./types";

export function resolveAssistantPageContext(pageContext: AIChatPageContext): AIChatPageContext {
  const related = pageContext.metadata?.related_page_context;
  if (
    pageContext.current_video?.video_url ||
    !related ||
    typeof related !== "object"
  ) {
    return pageContext;
  }

  return related as AIChatPageContext;
}
