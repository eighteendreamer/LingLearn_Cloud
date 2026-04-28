import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, X, MessageCircle, Lightbulb, AlertCircle } from "lucide-react";

interface Message {
  id: string;
  content: string;
  isUser: boolean;
}

const API_KEY = import.meta.env.VITE_ZHIPU_API_KEY;
const API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions";

const SYSTEM_PROMPT = `你是一个专业的编程学习AI助手，名叫"智慧学习助手"。你的职责是：
1. 解答编程相关问题（Python、前端、算法、数据库等）
2. 用简洁易懂的方式讲解技术概念
3. 提供学习路径建议
4. 给出代码示例时要标注语言
请用中文回答，回答要简洁实用。`;

export function FloatingAIChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "你好！我是你的AI学习助手 🤖\n我可以帮你解答编程问题、讲解算法、推荐学习路径。\n有什么想问的吗？",
      isUser: false,
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatHistoryRef = useRef<{ role: string; content: string }[]>([]);

  const quickQuestions = [
    "如何学习数据结构？",
    "Python和JavaScript的区别",
    "推荐前端学习路线",
    "算法题如何入门",
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const streamResponse = async (userInput: string) => {
    chatHistoryRef.current.push({ role: "user", content: userInput });

    const messageId = Date.now().toString();
    setMessages((prev) => [...prev, { id: messageId, content: "", isUser: false }]);
    setError("");

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${API_KEY}`,
        },
        body: JSON.stringify({
          model: "glm-4-flash",
          messages: [
            { role: "system", content: SYSTEM_PROMPT },
            ...chatHistoryRef.current.slice(-20),
          ],
          stream: true,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error?.message || `请求失败 (${response.status})`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("无法读取响应流");

      const decoder = new TextDecoder();
      let fullText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n").filter((l) => l.startsWith("data:"));

        for (const line of lines) {
          const data = line.replace("data:", "").trim();
          if (data === "[DONE]") break;
          try {
            const json = JSON.parse(data);
            const delta = json.choices?.[0]?.delta?.content;
            if (delta) {
              fullText += delta;
              setMessages((prev) =>
                prev.map((msg) => (msg.id === messageId ? { ...msg, content: fullText } : msg))
              );
            }
          } catch {
            // 跳过解析失败的行
          }
        }
      }

      chatHistoryRef.current.push({ role: "assistant", content: fullText });
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : "请求出错";
      setError(errMsg);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId
            ? { ...msg, content: "抱歉，请求出了点问题，请稍后再试。" }
            : msg
        )
      );
    }

    setIsTyping(false);
  };

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;
    const question = input;
    setMessages((prev) => [...prev, { id: Date.now().toString(), content: question, isUser: true }]);
    setInput("");
    setIsTyping(true);
    await streamResponse(question);
  };

  return (
    <>
      {/* 悬浮按钮 */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-24 right-5 z-50 w-14 h-14 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-xl hover:shadow-2xl hover:scale-110 transition-all"
        >
          <MessageCircle className="w-6 h-6 text-white" />
        </button>
      )}

      {/* 聊天窗口 */}
      {isOpen && (
        <div className="fixed bottom-24 right-5 z-50 w-[360px] h-[520px] flex flex-col rounded-2xl shadow-2xl border border-gray-200 overflow-hidden bg-white">
          {/* 头部 */}
          <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 flex-shrink-0">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="text-white font-semibold text-sm">AI学习助手</h3>
                <p className="text-white/80 text-xs">● 在线</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center hover:bg-white/30 transition-colors"
            >
              <X className="w-4 h-4 text-white" />
            </button>
          </div>

          {/* 消息区域 */}
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

          {/* 快捷问题 */}
          {messages.length <= 1 && (
            <div className="px-4 py-2 border-t border-gray-100 flex-shrink-0 bg-white">
              <div className="flex items-center gap-1 mb-1.5 text-gray-500 text-xs">
                <Lightbulb className="w-3 h-3" />
                <span>试试问我</span>
              </div>
              <div className="grid grid-cols-2 gap-1.5">
                {quickQuestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => { setInput(q); }}
                    className="text-left px-2 py-1.5 bg-gray-50 text-gray-700 text-xs rounded-lg hover:bg-emerald-50 hover:text-emerald-700 transition-colors border border-gray-100"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 输入框 */}
          <div className="px-3 py-3 border-t border-gray-100 flex-shrink-0 bg-white">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder="问我任何学习问题..."
                className="flex-1 px-3 py-2 bg-gray-100 text-gray-900 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 placeholder-gray-400 border border-gray-200"
                disabled={isTyping}
              />
              <button
                onClick={handleSend}
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
