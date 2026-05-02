import { useEffect, useRef, useState } from "react";
import { AlertCircle, Lightbulb, MessageCircle, Send, Sparkles, X } from "lucide-react";
import { useNavigate } from "react-router";

import { ApiError, apiRequest } from "../lib/api";
import { streamAIChatMessage } from "../lib/ai-chat";
import { resolveAssistantPageContext } from "../lib/assistant-context";
import { generateVideoPractice } from "../lib/learning-api";
import { hasSession } from "../lib/session";
import type {
  AIChatPageContext,
  AIChatMessageResponse,
  AIChatSessionCreatePayload,
  AIChatSessionResponse,
} from "../lib/types";
import { usePageContext } from "../page-context";
import { MarkdownMessage } from "./MarkdownMessage";
import { VideoAssistantActions } from "./VideoAssistantActions";

interface Message {
  id: number;
  content: string;
  role: string;
}

function normalizeMessageRole(role: string | null | undefined) {
  return role === "user" ? "user" : "assistant";
}

const DEFAULT_MESSAGE =
  "我是你的 AI 学习助手，可以围绕编程、学习规划和当前页面内容继续提问。";

export function FloatingAIChat() {
  const pageContext = usePageContext();
  const navigate = useNavigate();
  const effectivePageContext = resolveAssistantPageContext(pageContext);
  const currentVideo = effectivePageContext.current_video ?? null;
  const isAuthenticated = hasSession();

  const [isOpen, setIsOpen] = useState(false);
  const [currentSession, setCurrentSession] = useState<AIChatSessionResponse | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      content: DEFAULT_MESSAGE,
      role: "assistant",
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState("");
  const [isGeneratingPractice, setIsGeneratingPractice] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const localMessageIdRef = useRef(-1);

  const quickQuestions = [
    "帮我制定 Python 学习计划",
    "解释 Python 和 JavaScript 的区别",
    "推荐一条前端学习路线",
    "算法应该怎么入门",
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (isOpen && isAuthenticated && !currentSession) {
      void initSession();
    }
  }, [isAuthenticated, isOpen, currentSession]);

  const createLocalMessageId = () => {
    localMessageIdRef.current -= 1;
    return localMessageIdRef.current;
  };

  const appendAssistantMessage = (content: string) => {
    setMessages((previous) => [
      ...previous,
      {
        id: createLocalMessageId(),
        content,
        role: "assistant",
      },
    ]);
  };

  const initSession = async () => {
    if (!hasSession()) {
      setError("登录后才可以使用 AI 助手。");
      return;
    }

    try {
      const sessions = await apiRequest<AIChatSessionResponse[]>("/ai/chat/sessions");

      if (sessions.length > 0) {
        setCurrentSession(sessions[0]);
        const messagesData = await apiRequest<AIChatMessageResponse[]>(
          `/ai/chat/sessions/${sessions[0].id}/messages`,
        );
        if (messagesData.length > 0) {
          setMessages(
            messagesData.map((message) => ({
              id: message.id,
              content: message.content,
              role: normalizeMessageRole(message.role),
            })),
          );
        }
        return;
      }

      const payload: AIChatSessionCreatePayload = {
        session_name: "悬浮助手",
        scene_code: "study_assistant",
        model_name: "glm-4-flash",
      };
      const session = await apiRequest<AIChatSessionResponse>("/ai/chat/sessions", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setCurrentSession(session);
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        setError("登录状态已失效，请重新登录后再使用 AI 助手。");
        return;
      }
      console.error("Failed to init session:", requestError);
      setError("无法初始化 AI 助手会话。");
    }
  };

  const handleAsk = async (userInput: string, contextOverride?: AIChatPageContext) => {
    if (!hasSession()) {
      setError("登录后才可以发送消息。");
      return;
    }

    if (!currentSession || !userInput.trim()) {
      setError("助手会话尚未准备好。");
      return;
    }

    const question = userInput.trim();
    const userMessageId = createLocalMessageId();
    const assistantMessageId = createLocalMessageId();
    setMessages((previous) => [
      ...previous,
      { id: userMessageId, content: question, role: "user" },
      { id: assistantMessageId, content: "", role: "assistant" },
    ]);
    setInput("");
    setIsTyping(true);
    setError("");

    try {
      await streamAIChatMessage(
        currentSession.id,
        {
          content: question,
          stream: true,
          page_context: contextOverride ?? effectivePageContext,
        },
        {
          onDelta: (content) => {
            setMessages((previous) =>
              previous.map((message) =>
                message.id === assistantMessageId
                  ? { ...message, content: message.content + content }
                  : message,
              ),
            );
          },
          onDone: (message) => {
            if (!message) {
              return;
            }
            setMessages((previous) =>
              previous.map((item) =>
                item.id === assistantMessageId
                  ? {
                      id: message.id,
                      content: message.content,
                      role: normalizeMessageRole(message.role),
                    }
                  : item,
              ),
            );
          },
        },
      );
    } catch (requestError) {
      const message =
        requestError instanceof ApiError
          ? requestError.message
          : "助手暂时不可用，请稍后再试。";
      setError(message);
      setMessages((previous) =>
        previous.map((item) =>
          item.id === assistantMessageId
            ? { ...item, content: "发送失败，请重试。" }
            : item,
        ),
      );
    } finally {
      setIsTyping(false);
    }
  };

  const handleGenerateVideoPractice = async () => {
    if (!currentVideo?.video_url || isGeneratingPractice) {
      return;
    }

    setIsGeneratingPractice(true);
    setError("");
    try {
      const result = await generateVideoPractice({
        page_context: effectivePageContext,
        request_text:
          "请基于当前视频生成同主题练习题库，并创建一个可以直接作答的练习 session。",
        question_count: 6,
        session_type: "practice",
      });
      appendAssistantMessage(
        `已生成《${result.bank.title}》练习，正在为你打开。`,
      );
      setIsOpen(false);
      navigate(`/practice?bank_id=${result.bank.id}&session_id=${result.session.id}`);
    } catch (requestError) {
      const message =
        requestError instanceof ApiError
          ? requestError.message
          : "根据当前视频生成练习失败了。";
      setError(message);
      appendAssistantMessage(message);
    } finally {
      setIsGeneratingPractice(false);
    }
  };

  return (
    <>
      {!isOpen ? (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-24 right-3 z-50 flex h-14 w-14 items-center justify-center rounded-full border border-white/20 bg-gradient-to-br from-emerald-500 to-teal-500 shadow-2xl transition-all hover:scale-110 hover:shadow-2xl"
          aria-label={"打开 AI 助手"}
        >
          <MessageCircle className="h-6 w-6 text-white" />
        </button>
      ) : null}

      {isOpen ? (
        <div
          data-floating-ai-chat="true"
          className="fixed bottom-24 right-3 z-50 flex h-[min(520px,calc(100vh-8rem))] min-h-0 w-[min(360px,calc(100vw-1.5rem))] flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl"
          onWheel={(event) => event.stopPropagation()}
        >
          <div className="flex flex-shrink-0 items-center justify-between bg-gradient-to-r from-emerald-500 to-teal-500 px-4 py-3">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/20">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">智能学习助手</h3>
                <p className="text-xs text-white/80">结合当前场景的对话帮手</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="flex h-8 w-8 items-center justify-center rounded-full bg-white/20 transition-colors hover:bg-white/30"
              aria-label={"关闭 AI 助手"}
            >
              <X className="h-4 w-4 text-white" />
            </button>
          </div>

          <div
            className="min-h-0 flex-1 space-y-3 overflow-y-auto overscroll-contain bg-gradient-to-b from-gray-50 to-white px-4 py-3 [touch-action:pan-y]"
            onWheel={(event) => event.stopPropagation()}
            style={{ WebkitOverflowScrolling: "touch" }}
          >
            {!isAuthenticated ? (
              <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-4 text-sm text-amber-800">
                <p className="font-medium">登录后可使用 AI 助手</p>
                <p className="mt-1 text-xs text-amber-700">
                  你可以在登录后继续解析视频、生成练习和发起对话。
                </p>
                <button
                  onClick={() => navigate("/login")}
                  className="mt-3 rounded-full bg-emerald-500 px-4 py-2 text-xs font-medium text-white transition-colors hover:bg-emerald-600"
                >
                  去登录
                </button>
              </div>
            ) : null}

            {currentVideo ? (
              <VideoAssistantActions
                disabled={!isAuthenticated || !currentSession || isTyping}
                practiceLoading={isGeneratingPractice}
                onAnalyze={() =>
                  void handleAsk(
                    "请解析当前视频，提炼核心知识点、关键步骤和学习建议。",
                    effectivePageContext,
                  )
                }
                onGeneratePractice={() => void handleGenerateVideoPractice()}
                onGenerateSummary={() =>
                  void handleAsk(
                    "请生成当前视频的结构化总结，覆盖开头、中间和结尾内容。",
                    effectivePageContext,
                  )
                }
              />
            ) : null}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {message.role !== "user" ? (
                  <div className="mr-1.5 mt-1 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-teal-500">
                    <Sparkles className="h-3 w-3 text-white" />
                  </div>
                ) : null}
                <div
                  className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm leading-relaxed shadow-sm ${
                    message.role === "user"
                      ? "rounded-br-sm bg-emerald-500 text-white"
                      : "rounded-bl-sm border border-gray-200 bg-white text-gray-900"
                  }`}
                >
                  {message.role === "user" ? (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  ) : (
                    <MarkdownMessage content={message.content || "正在思考..."} />
                  )}
                </div>
              </div>
            ))}

            {isTyping ? (
              <div className="flex items-start gap-1.5">
                <div className="mt-1 flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-teal-500">
                  <Sparkles className="h-3 w-3 text-white" />
                </div>
                <div className="rounded-2xl rounded-bl-sm border border-gray-200 bg-white px-3 py-2 shadow-sm">
                  <div className="flex gap-1">
                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-bounce" />
                    <div
                      className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    />
                    <div
                      className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-bounce"
                      style={{ animationDelay: "0.4s" }}
                    />
                  </div>
                </div>
              </div>
            ) : null}

            {error ? (
              <div className="flex items-center gap-1.5 rounded-lg border border-red-100 bg-red-50 px-3 py-2 text-xs text-red-600">
                <AlertCircle className="h-3.5 w-3.5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            ) : null}

            <div ref={messagesEndRef} />
          </div>

          {messages.length <= 1 ? (
            <div className="flex-shrink-0 border-t border-gray-100 bg-white px-4 py-2">
              <div className="mb-1.5 flex items-center gap-1 text-xs text-gray-500">
                <Lightbulb className="h-3 w-3" />
                <span>可以试试这些提问</span>
              </div>
              <div className="grid grid-cols-2 gap-1.5">
                {quickQuestions.map((question) => (
                  <button
                    key={question}
                    onClick={() => setInput(question)}
                    className="rounded-lg border border-gray-100 bg-gray-50 px-2 py-1.5 text-left text-xs text-gray-700 transition-colors hover:bg-emerald-50 hover:text-emerald-700"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          <div className="flex-shrink-0 border-t border-gray-100 bg-white px-3 py-3">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => event.key === "Enter" && void handleAsk(input)}
                placeholder={"输入你想问的问题..."}
                className="flex-1 rounded-full border border-gray-200 bg-gray-100 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                disabled={!isAuthenticated || isTyping}
              />
              <button
                onClick={() => void handleAsk(input)}
                disabled={!isAuthenticated || !input.trim() || isTyping}
                className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-emerald-500 shadow-md transition-colors hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Send className="h-4 w-4 text-white" />
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
