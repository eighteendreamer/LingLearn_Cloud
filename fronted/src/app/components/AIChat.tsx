import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, ArrowLeft, Lightbulb } from "lucide-react";
import { Link } from "react-router";

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

export function AIChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "你好！我是你的AI学习助手 🤖\n\n我可以帮你：\n• 解答编程问题\n• 讲解算法原理\n• 推荐学习路径\n• 代码审查建议\n\n有什么想问的吗？",
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
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

  const simulateResponse = async (userInput: string) => {
    const responses: Record<string, string> = {
      数据结构: "学习数据结构建议按这个顺序：\n\n1️⃣ 数组和字符串（基础）\n2️⃣ 链表（指针操作）\n3️⃣ 栈和队列（后进先出/先进先出）\n4️⃣ 树和二叉树（递归思想）\n5️⃣ 图（复杂关系）\n\n每学一个都要配合LeetCode练习哦！",
      Python: "Python vs JavaScript：\n\n🐍 Python:\n• 语法简洁，适合初学者\n• 强大的数据分析库\n• 后端开发、AI/ML首选\n\n⚡ JavaScript:\n• 前端开发必备\n• Node.js做后端\n• 生态系统庞大\n\n建议：先学Python打基础，再学JS做全栈！",
      前端: "前端学习路线推荐：\n\n📌 第一阶段（基础）\nHTML + CSS + JavaScript\n\n📌 第二阶段（框架）\nReact / Vue / Angular\n\n📌 第三阶段（工程化）\nWebpack、Vite、TypeScript\n\n📌 第四阶段（进阶）\n性能优化、设计模式、微前端\n\n每天坚持2小时，3个月见效！",
      算法: "算法入门建议：\n\n✅ 从简单题开始\n• LeetCode Easy 题目\n• 每天1-2道题\n\n✅ 掌握基本套路\n• 双指针\n• 滑动窗口\n• 二分查找\n\n✅ 理解时间复杂度\nO(n), O(logn), O(n²)\n\n不要急，慢慢来！刷题贵在坚持！",
      default: "这是个好问题！让我想想...\n\n基于你的问题，我建议：\n\n1. 先打好基础知识\n2. 多动手实践\n3. 看官方文档\n4. 参与开源项目\n\n有具体的困惑可以再问我！",
    };

    let response = responses.default;
    for (const [key, value] of Object.entries(responses)) {
      if (userInput.includes(key)) {
        response = value;
        break;
      }
    }

    const words = response.split("");
    let currentText = "";
    const messageId = Date.now().toString();

    setMessages((prev) => [
      ...prev,
      {
        id: messageId,
        content: "",
        isUser: false,
        timestamp: new Date(),
      },
    ]);

    for (let i = 0; i < words.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 20));
      currentText += words[i];
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId ? { ...msg, content: currentText } : msg
        )
      );
    }

    setIsTyping(false);
  };

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const question = input;
    setInput("");
    setIsTyping(true);

    await simulateResponse(question);
  };

  const handleQuickQuestion = (question: string) => {
    setInput(question);
  };

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
            className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}
          >
            {!message.isUser && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center mr-2 flex-shrink-0">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
            )}
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-3 shadow-md ${
                message.isUser
                  ? "bg-emerald-500 text-white rounded-br-sm"
                  : "bg-white text-gray-900 rounded-bl-sm border border-gray-200"
              }`}
            >
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
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
