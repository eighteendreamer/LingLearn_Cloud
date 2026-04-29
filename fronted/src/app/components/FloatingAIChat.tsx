import { useEffect, useRef, useState } from "react";
import {
  AlertCircle,
  Lightbulb,
  MessageCircle,
  Send,
  Sparkles,
  X,
} from "lucide-react";

import { ApiError, apiRequest } from "../lib/api";

interface Message {
  id: string;
  content: string;
  isUser: boolean;
}

interface AIChatCompletionResponse {
  reply: string;
  model: string;
}

export function FloatingAIChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "你好，我是你的 AI 学习助手。你可以直接问我编程、学习路径或算法问题。",
      isUser: false,
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickQuestions = [
    "如何学习数据结构？",
    "Python 和 JavaScript 的区别是什么？",
    "推荐一条前端学习路线",
    "算法题应该怎么入门？",
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleAsk = async (userInput: string) => {
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content: userInput,
      isUser: true,
    };
    const nextMessages = [...messages, userMessage];
    const replyId = `assistant-${Date.now()}`;

    setMessages([...nextMessages, { id: replyId, content: "", isUser: false }]);
    setInput("");
    setIsTyping(true);
    setError("");

    try {
      const history = nextMessages
        .slice(-12)
        .map((message) => ({
          role: message.isUser ? "user" : "assistant",
          content: message.content,
        }));

      const data = await apiRequest<AIChatCompletionResponse>("/ai-chat/completions", {
        method: "POST",
        auth: false,
        body: JSON.stringify({ messages: history }),
      });

      setMessages((previous) =>
        previous.map((message) =>
          message.id === replyId ? { ...message, content: data.reply } : message,
        ),
      );
    } catch (requestError) {
      const message =
        requestError instanceof ApiError
          ? requestError.message
          : "AI 助手暂时不可用，请稍后重试。";
      setError(message);
      setMessages((previous) =>
        previous.map((item) =>
          item.id === replyId
            ? { ...item, content: "抱歉，当前无法获取回答，请稍后再试。" }
            : item,
        ),
      );
    } finally {
      setIsTyping(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isTyping) {
      return;
    }

    await handleAsk(input.trim());
  };

  return (
    <>
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-24 right-3 z-50 flex h-14 w-14 items-center justify-center rounded-full border border-white/20 bg-gradient-to-br from-emerald-500 to-teal-500 shadow-2xl transition-all hover:scale-110 hover:shadow-2xl"
        >
          <MessageCircle className="w-6 h-6 text-white" />
        </button>
      )}

      {isOpen && (
        <div className="fixed bottom-24 right-3 z-50 flex h-[min(520px,calc(100vh-8rem))] w-[min(360px,calc(100vw-1.5rem))] flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl">
          <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 flex-shrink-0">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="text-white font-semibold text-sm">AI 学习助手</h3>
                <p className="text-white/80 text-xs">由后端统一接入模型</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center hover:bg-white/30 transition-colors"
            >
              <X className="w-4 h-4 text-white" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 bg-gradient-to-b from-gray-50 to-white">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.isUser ? "justify-end" : "justify-start"}`}>
                {!msg.isUser && (
                  <div className="w-6 h-6 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center mr-1.5 flex-shrink-0 mt-1">
                    <Sparkles className="w-3 h-3 text-white" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-2xl px-3 py-2 shadow-sm text-sm leading-relaxed ${
                    msg.isUser
                      ? "bg-emerald-500 text-white rounded-br-sm"
                      : "bg-white text-gray-900 rounded-bl-sm border border-gray-200"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {isTyping && !messages[messages.length - 1]?.content && (
              <div className="flex items-start gap-1.5">
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center mt-1">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
                <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-3 py-2 shadow-sm">
                  <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" />
                    <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                    <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }} />
                  </div>
                </div>
              </div>
            )}
            {error && (
              <div className="flex items-center gap-1.5 px-3 py-2 bg-red-50 text-red-600 text-xs rounded-lg border border-red-100">
                <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {messages.length <= 1 && (
            <div className="px-4 py-2 border-t border-gray-100 flex-shrink-0 bg-white">
              <div className="flex items-center gap-1 mb-1.5 text-gray-500 text-xs">
                <Lightbulb className="w-3 h-3" />
                <span>试试这些问题</span>
              </div>
              <div className="grid grid-cols-2 gap-1.5">
                {quickQuestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => setInput(q)}
                    className="text-left px-2 py-1.5 bg-gray-50 text-gray-700 text-xs rounded-lg hover:bg-emerald-50 hover:text-emerald-700 transition-colors border border-gray-100"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="px-3 py-3 border-t border-gray-100 flex-shrink-0 bg-white">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && void handleSend()}
                placeholder="问我任何学习问题..."
                className="flex-1 px-3 py-2 bg-gray-100 text-gray-900 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 placeholder-gray-400 border border-gray-200"
                disabled={isTyping}
              />
              <button
                onClick={() => void handleSend()}
                disabled={!input.trim() || isTyping}
                className="w-9 h-9 bg-emerald-500 rounded-full flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed hover:bg-emerald-600 transition-colors shadow-md flex-shrink-0"
              >
                <Send className="w-4 h-4 text-white" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
