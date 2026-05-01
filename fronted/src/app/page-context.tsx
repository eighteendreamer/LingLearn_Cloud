import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useLocation } from "react-router";

import type { AIChatPageContext } from "./lib/types";

type PageContextValue = {
  pageContext: AIChatPageContext;
  updatePageContext: (patch: Partial<AIChatPageContext>) => void;
  resetPageContext: () => void;
};

const PageContextStore = createContext<PageContextValue | null>(null);

function inferPageContext(pathname: string): AIChatPageContext {
  if (pathname === "/") {
    return {
      route: pathname,
      page_type: "home_feed",
      page_title: "首页视频流",
      summary: "当前正在浏览推荐视频流，可以围绕当前视频继续做题、规划路径、提炼知识点。",
      current_video: null,
      available_actions: [
        {
          id: "analyze-current-video",
          label: "解析当前视频知识点",
          description: "提炼当前视频的核心知识点、术语和学习重点。",
          type: "analyze",
        },
        {
          id: "generate-video-practice",
          label: "生成视频同主题练习",
          description: "围绕当前视频主题生成在线练习、题库建议和错题巩固方向。",
          type: "generate",
          href: "/practice",
        },
        {
          id: "generate-video-path",
          label: "生成配套学习路径",
          description: "围绕当前视频主题生成分阶段学习路径和下一步计划。",
          type: "generate",
          href: "/learning-path",
        },
        {
          id: "evaluate-video-topic",
          label: "评估该主题掌握度",
          description: "基于当前视频主题快速诊断掌握程度并给出改进建议。",
          type: "analyze",
          href: "/assessment",
        },
      ],
      metadata: { section: "feed" },
    };
  }

  const pageMap: Record<string, Omit<AIChatPageContext, "route">> = {
    "/discover": {
      page_type: "discover",
      page_title: "发现页",
      summary: "当前正在浏览推荐内容和分类发现页，可以继续筛选、比较和推荐资源。",
      current_video: null,
      available_actions: [
        {
          id: "recommend-best-resources",
          label: "推荐最值得继续学的资源",
          description: "结合当前发现页内容筛选最适合继续学习的课程、视频和资料。",
          type: "recommend",
          href: "/resources",
        },
        {
          id: "build-discover-study-plan",
          label: "根据当前内容生成学习计划",
          description: "把当前发现页上的内容整理成可执行的学习顺序。",
          type: "generate",
          href: "/learning-path",
        },
      ],
      metadata: { section: "discover" },
    },
    "/my-learning": {
      page_type: "my_learning",
      page_title: "我的学习",
      summary: "当前正在查看学习记录、收藏和最近学习内容，可以做复盘和薄弱点诊断。",
      current_video: null,
      available_actions: [
        {
          id: "summarize-learning-progress",
          label: "总结当前学习进展",
          description: "根据当前学习记录输出阶段总结、学习进度和下一步重点。",
          type: "analyze",
        },
        {
          id: "find-learning-weak-points",
          label: "分析当前薄弱点",
          description: "识别最近学习中最该补强的知识点和练习方向。",
          type: "analyze",
          href: "/assessment",
        },
        {
          id: "build-review-plan",
          label: "生成复习计划",
          description: "把当前学习内容整理成接下来 7 天的复习节奏。",
          type: "generate",
          href: "/learning-path",
        },
      ],
      metadata: { section: "learning" },
    },
    "/profile": {
      page_type: "profile",
      page_title: "个人主页",
      summary: "当前正在查看当前账号的个人主页和学习工具入口，可以继续解释画像、报告和成长方向。",
      current_video: null,
      available_actions: [
        {
          id: "explain-profile-state",
          label: "解读当前学习状态",
          description: "结合主页信息解读当前学习状态和近期重点。",
          type: "analyze",
        },
        {
          id: "generate-profile-report",
          label: "生成学习报告",
          description: "结合当前账号信息输出阶段学习总结和下一步建议。",
          type: "generate",
          href: "/report",
        },
      ],
      metadata: { section: "profile" },
    },
    "/student-profile": {
      page_type: "student_profile",
      page_title: "学生画像",
      summary: "当前正在查看学生画像与能力特征，可以继续解释维度、定位短板和生成改进方案。",
      current_video: null,
      available_actions: [
        {
          id: "explain-portrait-dimensions",
          label: "解读画像维度",
          description: "解释当前画像各维度代表什么，以及它们对学习意味着什么。",
          type: "analyze",
        },
        {
          id: "build-improvement-plan",
          label: "生成画像改进方案",
          description: "根据当前画像短板生成阶段改进计划。",
          type: "generate",
          href: "/learning-path",
        },
      ],
      metadata: { section: "profile_tools" },
    },
    "/learning-path": {
      page_type: "learning_path",
      page_title: "学习路径",
      summary: "当前正在查看学习路径和阶段节点，可以继续优化路径、拆解周计划和安排下一步。",
      current_video: null,
      available_actions: [
        {
          id: "optimize-learning-path",
          label: "优化当前学习路径",
          description: "根据当前路径进展给出动态调整建议。",
          type: "recommend",
        },
        {
          id: "build-weekly-plan",
          label: "拆解成 7 天学习计划",
          description: "把当前路径拆解成一周可执行计划。",
          type: "generate",
        },
      ],
      metadata: { section: "path" },
    },
    "/practice": {
      page_type: "practice",
      page_title: "在线练习",
      summary: "当前正在查看在线练习题库与试卷入口，可以继续推荐题库、讲解错题和安排下一轮练习。",
      current_video: null,
      available_actions: [
        {
          id: "recommend-practice-bank",
          label: "推荐最适合的题库",
          description: "结合当前页面和学习目标推荐合适的练习题库。",
          type: "recommend",
        },
        {
          id: "generate-practice-round",
          label: "生成下一轮练习建议",
          description: "根据当前练习页面安排下一轮更合适的练习方向。",
          type: "generate",
        },
        {
          id: "explain-wrong-questions",
          label: "讲解当前错题方向",
          description: "围绕当前练习场景解释易错点和典型题型。",
          type: "analyze",
        },
      ],
      metadata: { section: "practice" },
    },
    "/assessment": {
      page_type: "assessment",
      page_title: "学习评估",
      summary: "当前正在查看学习评估结果与趋势，可以继续解读结果、识别薄弱点和转成训练计划。",
      current_video: null,
      available_actions: [
        {
          id: "summarize-assessment",
          label: "总结评估结果",
          description: "对当前评估页面生成诊断摘要和关键结论。",
          type: "analyze",
        },
        {
          id: "assessment-to-practice",
          label: "把评估转成练习计划",
          description: "把当前评估中的薄弱点转成下一轮练习安排。",
          type: "generate",
          href: "/practice",
        },
      ],
      metadata: { section: "assessment" },
    },
    "/report": {
      page_type: "report",
      page_title: "学习报告",
      summary: "当前正在查看阶段学习报告，可以继续做重点解读、阶段总结和下一周期计划。",
      current_video: null,
      available_actions: [
        {
          id: "explain-report",
          label: "解读学习报告",
          description: "解释当前报告中的重点信息和核心建议。",
          type: "analyze",
        },
        {
          id: "plan-next-cycle",
          label: "生成下一阶段计划",
          description: "把当前报告结论转成下一阶段的学习计划。",
          type: "generate",
          href: "/learning-path",
        },
      ],
      metadata: { section: "report" },
    },
    "/resources": {
      page_type: "resources",
      page_title: "资源中心",
      summary: "当前正在浏览课程、视频和学习资料，可以继续筛选资源、安排顺序和推荐下一步。",
      current_video: null,
      available_actions: [
        {
          id: "pick-best-resource",
          label: "筛选当前最值得学的资源",
          description: "从当前资源页中筛出最值得优先学习的内容。",
          type: "recommend",
        },
        {
          id: "build-resource-order",
          label: "生成资源学习顺序",
          description: "把当前资源整理成更合理的学习顺序。",
          type: "generate",
        },
      ],
      metadata: { section: "resources" },
    },
    "/create": {
      page_type: "create",
      page_title: "内容创作",
      summary: "当前正在上传或创建新的学习内容，可以继续优化内容结构、补充练习和增强可学性。",
      current_video: null,
      available_actions: [
        {
          id: "optimize-created-content",
          label: "优化当前创作内容",
          description: "根据当前创作页面上下文给出内容完善建议。",
          type: "recommend",
        },
        {
          id: "generate-quiz-from-content",
          label: "为内容生成配套练习",
          description: "围绕当前创作内容生成配套题目和练习建议。",
          type: "generate",
          href: "/practice",
        },
      ],
      metadata: { section: "create" },
    },
    "/ai-chat": {
      page_type: "ai_chat",
      page_title: "AI 学习助手",
      summary: "当前正在与 AI 学习助手对话。",
      current_video: null,
      available_actions: [],
      metadata: { section: "chat" },
    },
  };

  const matched = pageMap[pathname] ?? {
    page_type: "generic",
    page_title: "当前页面",
    summary: "当前正在浏览这个页面，可以继续提问、总结和规划下一步。",
    current_video: null,
    available_actions: [],
    metadata: { section: "generic" },
  };

  return {
    route: pathname,
    ...matched,
  };
}

export function PageContextProvider({ children }: { children: ReactNode }) {
  const location = useLocation();
  const [lastNonChatContext, setLastNonChatContext] = useState<AIChatPageContext | null>(null);
  const [pageContext, setPageContext] = useState<AIChatPageContext>(() =>
    inferPageContext(location.pathname),
  );

  useEffect(() => {
    const inferred = inferPageContext(location.pathname);
    if (location.pathname === "/ai-chat" && lastNonChatContext) {
      setPageContext({
        ...inferred,
        metadata: {
          ...(inferred.metadata ?? {}),
          related_page_context: lastNonChatContext,
        },
      });
      return;
    }
    setPageContext(inferred);
    if (location.pathname !== "/ai-chat") {
      setLastNonChatContext(inferred);
    }
  }, [location.pathname]);

  const updatePageContext = useCallback(
    (patch: Partial<AIChatPageContext>) => {
      setPageContext((previous) => ({
        ...previous,
        ...patch,
        route: location.pathname,
        current_video:
          patch.current_video === undefined ? previous.current_video ?? null : patch.current_video,
        available_actions: patch.available_actions ?? previous.available_actions,
        metadata: {
          ...(previous.metadata ?? {}),
          ...(patch.metadata ?? {}),
        },
      }));
      if (location.pathname !== "/ai-chat") {
        setLastNonChatContext((previous) => ({
          ...(previous ?? inferPageContext(location.pathname)),
          ...patch,
          route: location.pathname,
          current_video:
            patch.current_video === undefined
              ? (previous?.current_video ?? null)
              : patch.current_video,
          available_actions: patch.available_actions ?? previous?.available_actions ?? [],
          metadata: {
            ...(previous?.metadata ?? {}),
            ...(patch.metadata ?? {}),
          },
        }));
      }
    },
    [location.pathname],
  );

  const resetPageContext = useCallback(() => {
    setPageContext(inferPageContext(location.pathname));
  }, [location.pathname]);

  const value = useMemo<PageContextValue>(
    () => ({
      pageContext,
      updatePageContext,
      resetPageContext,
    }),
    [pageContext, resetPageContext, updatePageContext],
  );

  return <PageContextStore.Provider value={value}>{children}</PageContextStore.Provider>;
}

export function usePageContext() {
  const context = useContext(PageContextStore);
  if (!context) {
    throw new Error("usePageContext must be used within PageContextProvider.");
  }
  return context.pageContext;
}

export function usePageContextActions() {
  const context = useContext(PageContextStore);
  if (!context) {
    throw new Error("usePageContextActions must be used within PageContextProvider.");
  }
  return {
    updatePageContext: context.updatePageContext,
    resetPageContext: context.resetPageContext,
  };
}
