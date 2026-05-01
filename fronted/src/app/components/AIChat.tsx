import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, ArrowLeft, Lightbulb } from "lucide-react";
import { Link } from "react-router";
import { apiRequest } from "../lib/api";
import { streamAIChatMessage } from "../lib/ai-chat";
import { MarkdownMessage } from "./MarkdownMessage";
import { usePageContext } from "../page-context";
import type {
  AIChatSessionResponse,
  AIChatMessageResponse,
  AIChatSessionCreatePayload,
} from "../lib/types";

interface Message {
  id: number;
  content: string;
  role: string;
  timestamp: Date;
}

export function AIChat() {
  const pageContext = usePageContext();
  const [sessions, setSessions] = useState<AIChatSessionResponse[]>([]);
  const [currentSession, setCurrentSession] = useState<AIChatSessionResponse | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickQuestions = [
    "如何学习数据结构？",
    "Python和JavaScript的区别",
    "推荐前端学习路线",
    "算法题如何入门",
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadSessions();
  }, []);

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
      setSessions([session, ...sessions]);
      setMessages([
        {
          id: 0,
          content: "你好！我是你的AI学习助手 🤖\n\n我可以帮你：\n• 解答编程问题\n• 讲解算法原理\n• 推荐学习路径\n• 代码审查建议\n\n有什么想问的吗？",
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
        `/ai/chat/sessions/${session.id}/messages`
      );
      
      const formattedMessages: Message[] = messagesData.map((msg) => ({
        id: msg.id,
        content: msg.content,
        role: msg.role,
        timestamp: new Date(msg.created_at),
      }));

      if (formattedMessages.length === 0) {
        formattedMessages.push({
          id: 0,
          content: "你好！我是你的AI学习助手 🤖\n\n我可以帮你：\n• 解答编程问题\n• 讲解算法原理\n• 推荐学习路径\n• 代码审查建议\n\n有什么想问的吗？",
          role: "assistant",
          timestamp: new Date(),
        });
      }

      setMessages(formattedMessages);
    } catch (error) {
      console.error("Failed to load messages:", error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isTyping || !currentSession) return;

    const userMessage: Message = {
      id: Date.now(),
      content: input,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const question = input;
    setInput("");
    setIsTyping(true);
    const assistantMessageId = Date.now() + 1;
    setMessages((prev) => [
      ...prev,
      {
        id: assistantMessageId,
        content: "",
        role: "assistant",
        timestamp: new Date(),
      },
    ]);

    try {
      await streamAIChatMessage(currentSession.id, {
        content: question,
        stream: true,
        page_context: pageContext,
      }, {
        onDelta: (content) => {
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantMessageId
                ? { ...message, content: message.content + content }
                : message
            )
          );
        },
        onDone: (message) => {
          if (!message) {
            return;
          }
          setMessages((prev) =>
            prev.map((item) =>
              item.id === assistantMessageId
                ? {
                    id: message.id,
                    content: message.content,
                    role: message.role,
                    timestamp: new Date(message.created_at),
                  }
                : item
            )
          );
        },
      });
    } catch (error) {
      console.error("Failed to send message:", error);
      setMessages((prev) =>
        prev.map((message) =>
          message.id === assistantMessageId
            ? { ...message, content: "抱歉，发送消息失败，请稍后重试。" }
            : message
        )
      );
    } finally {
      setIsTyping(false);
    }
  };

  const handleQuickQuestion = (question: string) => {
    setInput(question);
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

  return (
    <div className="h-full min-h-0 flex flex-col overflow-hidden bg-gradient-to-br from-blue-50 via-white to-emerald-50">
      <div className="relative z-10 shrink-0 border-b border-gray-200 bg-white/92 px-4 py-4 shadow-sm backdrop-blur-xl">
        <div className="mx-auto flex w-full max-w-6xl items-center gap-3">
          <Link to="/profile" className="rounded-full p-1 transition-colors hover:bg-gray-100">
          <ArrowLeft className="w-6 h-6 text-gray-700" />
        </Link>
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-md shadow-emerald-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
            <div className="min-w-0">
              <h1 className="truncate text-gray-900 text-[1.75rem] font-bold leading-none">AI学习助手</h1>
              <div className="mt-1 flex items-center gap-2 text-xs">
                <span className="text-emerald-600">● 在线</span>
                <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-emerald-700">
                  {currentSession?.scene_code === "study_assistant" ? "学习对话" : "智能会话"}
                </span>
                {sessions.length > 1 && (
                  <span className="text-gray-500">已加载 {sessions.length} 个会话</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-5 px-4 py-6 md:px-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {message.role !== "user" && (
                <div className="mr-3 mt-1 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 shadow-md shadow-emerald-500/15">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
              )}
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
                  <MarkdownMessage content={message.content || "正在思考..."} className="text-sm leading-7" />
                )}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex items-start gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 shadow-md shadow-emerald-500/15">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div className="rounded-[1.6rem] rounded-bl-md border border-gray-200 bg-white px-4 py-3 shadow-md">
                <div className="flex gap-1">
                  <div className="h-2 w-2 rounded-full bg-emerald-500 animate-bounce"></div>
                  <div className="h-2 w-2 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                  <div className="h-2 w-2 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                </div>
              </div>
            </div>
          )}

          {messages.length <= 1 && (
            <div className="mt-2 rounded-[1.8rem] border border-white/70 bg-white/85 p-4 shadow-sm backdrop-blur">
              <div className="mb-3 flex items-center gap-2 text-gray-600 text-xs">
                <Lightbulb className="w-3 h-3" />
                <span>试试这些问题</span>
              </div>
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {quickQuestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => handleQuickQuestion(q)}
                    className="rounded-2xl border border-gray-200 bg-white px-3 py-3 text-left text-sm text-gray-700 shadow-sm transition-colors hover:bg-emerald-50 hover:text-emerald-700"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="shrink-0 border-t border-gray-200 bg-white/95 px-4 pb-[calc(env(safe-area-inset-bottom,0px)+1rem)] pt-3 shadow-[0_-8px_30px_rgba(15,23,42,0.04)] backdrop-blur-xl">
        <div className="mx-auto w-full max-w-6xl">
          <div className="flex items-end gap-3 rounded-[1.75rem] border border-gray-200 bg-white px-3 py-3 shadow-sm">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="问我任何学习问题..."
              className="flex-1 bg-transparent px-2 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none"
              disabled={isTyping}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isTyping}
              className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-2xl bg-emerald-500 shadow-md shadow-emerald-500/20 transition-colors hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Send className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
