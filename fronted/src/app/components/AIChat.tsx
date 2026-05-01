import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, ArrowLeft, Lightbulb } from "lucide-react";
import { Link } from "react-router";
import { apiRequest } from "../lib/api";
import { streamAIChatMessage } from "../lib/ai-chat";
import { MarkdownMessage } from "./MarkdownMessage";
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
      <div className="h-screen flex flex-col bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-16">
        <div className="flex-1 flex items-center justify-center">
          <div className="text-gray-500">加载中...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-16">
      <div className="flex items-center gap-3 p-4 bg-white border-b border-gray-200 shadow-sm">
        <Link to="/profile">
          <ArrowLeft className="w-6 h-6 text-gray-700" />
        </Link>
        <div className="flex items-center gap-2 flex-1">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-md">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-gray-900 font-semibold">AI学习助手</h1>
            <p className="text-xs text-emerald-600">● 在线</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {message.role !== "user" && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center mr-2 flex-shrink-0">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
            )}
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-3 shadow-md ${
                message.role === "user"
                  ? "bg-emerald-500 text-white rounded-br-sm"
                  : "bg-white text-gray-900 rounded-bl-sm border border-gray-200"
              }`}
            >
              {message.role === "user" ? (
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
              ) : (
                <MarkdownMessage content={message.content || "正在思考..."} className="text-sm leading-relaxed" />
              )}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex items-start gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-md">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-md">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {messages.length <= 1 && (
        <div className="px-4 pb-4">
          <div className="flex items-center gap-2 mb-2 text-gray-600 text-xs">
            <Lightbulb className="w-3 h-3" />
            <span>试试问我这些</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {quickQuestions.map((q) => (
              <button
                key={q}
                onClick={() => handleQuickQuestion(q)}
                className="text-left px-3 py-2 bg-white text-gray-700 text-xs rounded-lg hover:bg-gray-50 transition-colors border border-gray-200 shadow-sm"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="p-4 bg-white border-t border-gray-200">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="问我任何学习问题..."
            className="flex-1 px-4 py-3 bg-gray-100 text-gray-900 rounded-full focus:outline-none focus:ring-2 focus:ring-emerald-500 placeholder-gray-500 border border-gray-200"
            disabled={isTyping}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isTyping}
            className="w-11 h-11 bg-emerald-500 rounded-full flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed hover:bg-emerald-600 transition-colors shadow-md"
          >
            <Send className="w-5 h-5 text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}
