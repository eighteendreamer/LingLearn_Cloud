import { useEffect, useRef, useState } from "react";
import { ArrowLeft, Lightbulb, Send, Sparkles } from "lucide-react";
import { Link, useNavigate } from "react-router";

import { apiRequest } from "../lib/api";
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
  timestamp: Date;
}

function normalizeMessageRole(role: string | null | undefined) {
  return role === "user" ? "user" : "assistant";
}

const DEFAULT_ASSISTANT_MESSAGE =
  "我是你的 AI 学习助手。\n\n我可以帮你制定学习计划、解释知识点、整理复习笔记，也能结合当前视频触发学习动作。";

export function AIChat() {
  const pageContext = usePageContext();
  const navigate = useNavigate();
  const effectivePageContext = resolveAssistantPageContext(pageContext);
  const currentVideo = effectivePageContext.current_video ?? null;
  const isAuthenticated = hasSession();

  const [sessions, setSessions] = useState<AIChatSessionResponse[]>([]);
  const [currentSession, setCurrentSession] = useState<AIChatSessionResponse | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isGeneratingPractice, setIsGeneratingPractice] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const localMessageIdRef = useRef(-1);

  const quickQuestions = [
    "帮我制定 Python 学习计划",
    "解释 Python 和 JavaScript 的区别",
    "推荐一条前端学习路线",
    "我应该如何开始算法练习",
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    void loadSessions();
  }, [isAuthenticated]);

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
        timestamp: new Date(),
      },
    ]);
  };

  const loadSessions = async () => {
    try {
      setLoading(true);
      const sessionsData = await apiRequest<AIChatSessionResponse[]>("/ai/chat/sessions");
      setSessions(sessionsData);

      if (sessionsData.length > 0) {
        await loadSession(sessionsData[0]);
      } else {
        await createNewSession();
      }
    } catch (error) {
      if (error instanceof Error && "status" in error && (error as { status?: number }).status === 401) {
        setLoading(false);
        return;
      }
      console.error("Failed to load sessions:", error);
      await createNewSession();
    } finally {
      setLoading(false);
    }
  };

  const createNewSession = async () => {
    try {
      const payload: AIChatSessionCreatePayload = {
        session_name: "新对话",
        scene_code: "study_assistant",
        model_name: "glm-4-flash",
      };
      const session = await apiRequest<AIChatSessionResponse>("/ai/chat/sessions", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setCurrentSession(session);
      setSessions((previous) => [session, ...previous]);
      setMessages([
        {
          id: 0,
          content: DEFAULT_ASSISTANT_MESSAGE,
          role: "assistant",
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      console.error("Failed to create session:", error);
    }
  };

  const loadSession = async (session: AIChatSessionResponse) => {
    try {
      setCurrentSession(session);
      const messagesData = await apiRequest<AIChatMessageResponse[]>(
        `/ai/chat/sessions/${session.id}/messages`,
      );
      const formattedMessages: Message[] = messagesData.map((message) => ({
        id: message.id,
        content: message.content,
        role: normalizeMessageRole(message.role),
        timestamp: new Date(message.created_at),
      }));

      setMessages(
        formattedMessages.length > 0
          ? formattedMessages
          : [
              {
                id: 0,
                content: DEFAULT_ASSISTANT_MESSAGE,
                role: "assistant",
                timestamp: new Date(),
              },
            ],
      );
    } catch (error) {
      console.error("Failed to load messages:", error);
    }
  };

  const sendPrompt = async (rawInput: string, contextOverride?: AIChatPageContext) => {
    if (!isAuthenticated || !rawInput.trim() || isTyping || !currentSession) {
      return;
    }

    const question = rawInput.trim();
    const userMessageId = createLocalMessageId();
    const assistantMessageId = createLocalMessageId();

    setMessages((previous) => [
      ...previous,
      {
        id: userMessageId,
        content: question,
        role: "user",
        timestamp: new Date(),
      },
      {
        id: assistantMessageId,
        content: "",
        role: "assistant",
        timestamp: new Date(),
      },
    ]);
    setInput("");
    setIsTyping(true);

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
                      timestamp: new Date(message.created_at),
                    }
                  : item,
              ),
            );
          },
        },
      );
    } catch (error) {
      console.error("Failed to send message:", error);
      setMessages((previous) =>
        previous.map((message) =>
          message.id === assistantMessageId
            ? { ...message, content: "发送失败，请重试。" }
            : message,
        ),
      );
    } finally {
      setIsTyping(false);
    }
  };

  const handleGenerateVideoPractice = async () => {
    if (!isAuthenticated || !currentVideo?.video_url || isGeneratingPractice) {
      return;
    }

    setIsGeneratingPractice(true);
    try {
      const result = await generateVideoPractice({
        page_context: effectivePageContext,
        request_text:
          "请基于当前视频生成同主题练习题库，并创建一个可以直接作答的练习 session。",
        question_count: 6,
        session_type: "practice",
      });
      appendAssistantMessage(
        `已基于《${currentVideo.title}》生成《${result.bank.title}》练习，正在为你打开。`,
      );
      navigate(`/practice?bank_id=${result.bank.id}&session_id=${result.session.id}`);
    } catch (error) {
      console.error("Failed to generate video practice:", error);
      appendAssistantMessage(
        "根据当前视频生成练习失败了，请稍后再试。",
      );
    } finally {
      setIsGeneratingPractice(false);
    }
  };

  if (loading) {
    return (
      <div className="h-full min-h-0 flex flex-col overflow-hidden bg-gradient-to-br from-blue-50 via-white to-emerald-50">
        <div className="flex-1 flex items-center justify-center">
          <div className="text-gray-500">加载中...</div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="h-full min-h-0 flex flex-col overflow-hidden bg-gradient-to-br from-blue-50 via-white to-emerald-50">
        <div className="flex-1 flex items-center justify-center px-6">
          <div className="w-full max-w-md rounded-[2rem] border border-white/70 bg-white/90 p-8 text-center shadow-sm backdrop-blur">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 shadow-md shadow-emerald-500/20">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <h1 className="mt-5 text-2xl font-bold text-gray-900">登录后使用 AI 助手</h1>
            <p className="mt-2 text-sm leading-6 text-gray-600">
              登录后你可以继续发起学习对话、解析当前视频、生成同主题练习和整理视频总结。
            </p>
            <Link
              to="/login"
              className="mt-6 inline-flex rounded-full bg-emerald-500 px-5 py-3 text-sm font-medium text-white transition-colors hover:bg-emerald-600"
            >
              去登录
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full min-h-0 flex flex-col overflow-hidden bg-gradient-to-br from-blue-50 via-white to-emerald-50">
      <div className="relative z-10 shrink-0 border-b border-gray-200 bg-white/92 px-4 py-4 shadow-sm backdrop-blur-xl">
        <div className="mx-auto flex w-full max-w-6xl items-center gap-3">
          <Link to="/profile" className="rounded-full p-1 transition-colors hover:bg-gray-100">
            <ArrowLeft className="h-6 w-6 text-gray-700" />
          </Link>
          <div className="flex min-w-0 flex-1 items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 shadow-md shadow-emerald-500/20">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="truncate text-[1.75rem] font-bold leading-none text-gray-900">智能学习助手</h1>
              <div className="mt-1 flex items-center gap-2 text-xs">
                <span className="text-emerald-600">在线</span>
                <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-emerald-700">
                  {currentSession?.scene_code === "study_assistant" ? "学习对话" : "AI 对话"}
                </span>
                {sessions.length > 1 ? (
                  <span className="text-gray-500">{`已加载 ${sessions.length} 个会话`}</span>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-5 px-4 py-6 md:px-6">
          {currentVideo ? (
            <VideoAssistantActions
              disabled={!currentSession || isTyping}
              practiceLoading={isGeneratingPractice}
              onAnalyze={() =>
                void sendPrompt(
                  "请解析当前视频，提炼核心知识点、关键步骤和学习建议。",
                  effectivePageContext,
                )
              }
              onGeneratePractice={() => void handleGenerateVideoPractice()}
              onGenerateSummary={() =>
                void sendPrompt(
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
                <div className="mr-3 mt-1 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 shadow-md shadow-emerald-500/15">
                  <Sparkles className="h-4 w-4 text-white" />
                </div>
              ) : null}
              <div
                className={`max-w-[min(80%,44rem)] rounded-[1.6rem] px-4 py-3 shadow-md ${
                  message.role === "user"
                    ? "rounded-br-md bg-emerald-500 text-white shadow-emerald-500/20"
                    : "rounded-bl-md border border-gray-200 bg-white text-gray-900"
                }`}
              >
                {message.role === "user" ? (
                  <p className="whitespace-pre-wrap text-sm leading-7">{message.content}</p>
                ) : (
                  <MarkdownMessage
                    content={message.content || "正在思考..."}
                    className="text-sm leading-7"
                  />
                )}
              </div>
            </div>
          ))}

          {isTyping ? (
            <div className="flex items-start gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 shadow-md shadow-emerald-500/15">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <div className="rounded-[1.6rem] rounded-bl-md border border-gray-200 bg-white px-4 py-3 shadow-md">
                <div className="flex gap-1">
                  <div className="h-2 w-2 rounded-full bg-emerald-500 animate-bounce" />
                  <div
                    className="h-2 w-2 rounded-full bg-emerald-500 animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  />
                  <div
                    className="h-2 w-2 rounded-full bg-emerald-500 animate-bounce"
                    style={{ animationDelay: "0.4s" }}
                  />
                </div>
              </div>
            </div>
          ) : null}

          {messages.length <= 1 ? (
            <div className="mt-2 rounded-[1.8rem] border border-white/70 bg-white/85 p-4 shadow-sm backdrop-blur">
              <div className="mb-3 flex items-center gap-2 text-xs text-gray-600">
                <Lightbulb className="h-3 w-3" />
                <span>可以先从这些问题开始</span>
              </div>
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {quickQuestions.map((question) => (
                  <button
                    key={question}
                    onClick={() => setInput(question)}
                    className="rounded-2xl border border-gray-200 bg-white px-3 py-3 text-left text-sm text-gray-700 shadow-sm transition-colors hover:bg-emerald-50 hover:text-emerald-700"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="shrink-0 border-t border-gray-200 bg-white/95 px-4 pb-[calc(env(safe-area-inset-bottom,0px)+1rem)] pt-3 shadow-[0_-8px_30px_rgba(15,23,42,0.04)] backdrop-blur-xl">
        <div className="mx-auto w-full max-w-6xl">
          <div className="flex items-end gap-3 rounded-[1.75rem] border border-gray-200 bg-white px-3 py-3 shadow-sm">
            <input
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => event.key === "Enter" && void sendPrompt(input)}
              placeholder={"你可以输入任何学习相关问题..."}
              className="flex-1 bg-transparent px-2 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none"
              disabled={isTyping}
            />
            <button
              onClick={() => void sendPrompt(input)}
              disabled={!input.trim() || isTyping}
              className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-2xl bg-emerald-500 shadow-md shadow-emerald-500/20 transition-colors hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Send className="h-5 w-5 text-white" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
