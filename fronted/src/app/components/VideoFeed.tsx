import { useState, useEffect, useRef } from "react";
import { Heart, MessageCircle, Share2, Bookmark, Play, Volume2, VolumeX, MoreHorizontal, Vote, X, Search, Check, ChevronRight } from "lucide-react";
import { Link } from "react-router";

interface Video {
  id: string;
  title: string;
  description: string;
  author: string;
  avatar: string;
  category: string;
  likes: number;
  comments: number;
  shares: number;
  isLiked: boolean;
  isSaved: boolean;
  thumbnail: string;
  duration: string;
  videoUrl?: string;
  bvid?: string;
  hasQuiz?: boolean;
  quizCount?: number;
}

interface QuizOption {
  text: string;
  votes: number;
}

interface QuizQuestion {
  question: string;
  options: QuizOption[];
  correctAnswer: number;
  totalVotes: number;
}

export function VideoFeed() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);
  const videoRefs = useRef<(HTMLVideoElement | null)[]>([]);
  const touchStartY = useRef(0);
  const [isLoading, setIsLoading] = useState(true);

  const [showQuiz, setShowQuiz] = useState(false);
  const [quizIdx, setQuizIdx] = useState(0);
  const [quizAnswered, setQuizAnswered] = useState<Record<string, number | null>>({});
  const [animatedPercents, setAnimatedPercents] = useState<Record<string, number[]>>({});

  const videoQuizzes: Record<string, QuizQuestion[]> = {
    "1": [
      {
        question: "列表推导式的基本语法是什么？",
        options: [
          { text: "[x for x in range(10)]", votes: 891 },
          { text: "{x for x in range(10)}", votes: 234 },
          { text: "(x for x in range(10))", votes: 312 },
          { text: "x for x in range(10)", votes: 156 },
        ],
        correctAnswer: 0,
        totalVotes: 1593,
      },
      {
        question: "以下哪个可以生成偶数列表？",
        options: [
          { text: "[x for x in range(10) if x%2==0]", votes: 756 },
          { text: "[x for x in range(10) if x%2]", votes: 189 },
          { text: "[x if x%2==0 for x in range(10)]", votes: 98 },
          { text: "[x%2==0 for x in range(10)]", votes: 67 },
        ],
        correctAnswer: 0,
        totalVotes: 1110,
      },
    ],
    "2": [
      {
        question: "justify-content: center 的作用是？",
        options: [
          { text: "主轴居中对齐", votes: 1245 },
          { text: "交叉轴居中对齐", votes: 321 },
          { text: "两端对齐", votes: 156 },
          { text: "平均分布", votes: 87 },
        ],
        correctAnswer: 0,
        totalVotes: 1809,
      },
      {
        question: "align-items 的默认值是？",
        options: [
          { text: "flex-start", votes: 432 },
          { text: "center", votes: 287 },
          { text: "stretch", votes: 876 },
          { text: "baseline", votes: 123 },
        ],
        correctAnswer: 2,
        totalVotes: 1718,
      },
      {
        question: "哪个属性让Flex项目换行？",
        options: [
          { text: "flex-direction: column", votes: 156 },
          { text: "flex-wrap: wrap", votes: 1087 },
          { text: "justify-content: space-between", votes: 234 },
          { text: "align-items: flex-start", votes: 98 },
        ],
        correctAnswer: 1,
        totalVotes: 1575,
      },
    ],
    "3": [
      {
        question: "快速排序的平均时间复杂度是？",
        options: [
          { text: "O(n)", votes: 234 },
          { text: "O(n log n)", votes: 1567 },
          { text: "O(n²)", votes: 321 },
          { text: "O(log n)", votes: 156 },
        ],
        correctAnswer: 1,
        totalVotes: 2278,
      },
    ],
  };

  const videos: Video[] = [
    {
      id: "1",
      title: "Python入门：5分钟学会列表推导式",
      description: "超实用的Python技巧，让你的代码更简洁优雅！#Python #编程 #数据分析",
      author: "编程导师小李",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=1",
      category: "Python",
      likes: 12500,
      comments: 342,
      shares: 156,
      isLiked: false,
      isSaved: false,
      thumbnail: "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=400",
      duration: "5:23",
      videoUrl: "https://videos.pexels.com/video-files/5748225/5748225-uhd_2732_1440_25fps.mp4",
      bvid: "BV1ZB4y1Z7o8",
      hasQuiz: true,
      quizCount: 2,
    },
    {
      id: "2",
      title: "前端必学：Flex布局3分钟速通",
      description: "从零开始掌握Flex布局，再也不怕CSS布局问题！#前端开发 #CSS #Web开发",
      author: "前端大神王老师",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=2",
      category: "前端",
      likes: 18900,
      comments: 567,
      shares: 289,
      isLiked: true,
      isSaved: false,
      thumbnail: "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=400",
      duration: "3:15",
      videoUrl: "https://videos.pexels.com/video-files/3129671/3129671-hd_1920_1080_30fps.mp4",
      bvid: "BV1y4421Z7hK",
      hasQuiz: true,
      quizCount: 3,
    },
    {
      id: "3",
      title: "算法可视化：快速排序原理动画演示",
      description: "动画演示快速排序全过程，秒懂算法原理！#算法 #数据结构 #面试",
      author: "算法讲解达人",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=3",
      category: "算法",
      likes: 25600,
      comments: 891,
      shares: 432,
      isLiked: false,
      isSaved: true,
      thumbnail: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400",
      duration: "4:42",
      videoUrl: "https://videos.pexels.com/video-files/5750642/5750642-hd_1920_1080_30fps.mp4",
      bvid: "BV13CBTY3E6U",
      hasQuiz: true,
      quizCount: 1,
    },
    {
      id: "4",
      title: "React Hooks实战：useState深度解析",
      description: "React Hooks核心概念，带你深入理解useState的使用场景！#React #前端",
      author: "React专家张老师",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=4",
      category: "React",
      likes: 15200,
      comments: 423,
      shares: 198,
      isLiked: false,
      isSaved: false,
      thumbnail: "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=400",
      duration: "6:18",
      videoUrl: "https://videos.pexels.com/video-files/7767903/7767903-hd_1920_1080_25fps.mp4",
      bvid: "BV1ye4y1g784",
    },
    {
      id: "5",
      title: "数据库优化技巧：索引的正确使用方式",
      description: "MySQL索引优化实战，查询速度提升10倍！#数据库 #MySQL #性能优化",
      author: "数据库专家刘老师",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=5",
      category: "数据库",
      likes: 9800,
      comments: 234,
      shares: 145,
      isLiked: false,
      isSaved: true,
      thumbnail: "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=400",
      duration: "7:05",
      videoUrl: "https://videos.pexels.com/video-files/855162/855162-hd_1920_1080_30fps.mp4",
      bvid: "BV1ZB4y1Z7o8",
    },
  ];

  const [videoStates, setVideoStates] = useState(
    videos.map((v) => ({ isLiked: v.isLiked, isSaved: v.isSaved, likes: v.likes }))
  );

  const handleScroll = (direction: "up" | "down") => {
    setCurrentIndex((prev) => {
      if (direction === "down" && prev < videos.length - 1) {
        return prev + 1;
      } else if (direction === "up" && prev > 0) {
        return prev - 1;
      }
      return prev;
    });
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartY.current = e.touches[0].clientY;
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    const touchEndY = e.changedTouches[0].clientY;
    const diff = touchStartY.current - touchEndY;

    if (Math.abs(diff) > 50) {
      if (diff > 0) {
        handleScroll("down");
      } else {
        handleScroll("up");
      }
    }
  };

  useEffect(() => {
    setIsLoading(false);
  }, []);

  useEffect(() => {
    videoRefs.current.forEach((video, index) => {
      if (video) {
        if (index === currentIndex && isPlaying) {
          video.play().catch(() => {});
        } else {
          video.pause();
        }
      }
    });
  }, [currentIndex, isPlaying]);

  useEffect(() => {
    videoRefs.current.forEach((video) => {
      if (video) {
        video.muted = isMuted;
      }
    });
  }, [isMuted]);

  const handleVideoClick = () => {
    setIsPlaying(!isPlaying);
  };

  useEffect(() => {
    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      if (e.deltaY > 0) {
        handleScroll("down");
      } else {
        handleScroll("up");
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown" || e.key === "ArrowRight") {
        e.preventDefault();
        handleScroll("down");
      } else if (e.key === "ArrowUp" || e.key === "ArrowLeft") {
        e.preventDefault();
        handleScroll("up");
      }
    };

    window.addEventListener("wheel", handleWheel, { passive: false });
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("wheel", handleWheel);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  const handleLike = () => {
    setVideoStates((prev) =>
      prev.map((state, idx) =>
        idx === currentIndex
          ? {
              ...state,
              isLiked: !state.isLiked,
              likes: state.isLiked ? state.likes - 1 : state.likes + 1,
            }
          : state
      )
    );
  };

  const handleSave = () => {
    setVideoStates((prev) =>
      prev.map((state, idx) =>
        idx === currentIndex ? { ...state, isSaved: !state.isSaved } : state
      )
    );
  };

  const handleAnswer = (optionIndex: number) => {
    const key = `${currentVideo.id}-${quizIdx}`;
    setQuizAnswered((prev) => ({ ...prev, [key]: optionIndex }));

    const quiz = currentQuizList?.[quizIdx];
    if (!quiz) return;
    const newTotal = quiz.totalVotes + 1;
    const newOptions = quiz.options.map((opt, idx) =>
      idx === optionIndex ? { ...opt, votes: opt.votes + 1 } : opt
    );
    const percents = newOptions.map((opt) => Math.round((opt.votes / newTotal) * 100));
    setAnimatedPercents((prev) => ({ ...prev, [key]: percents }));
  };

  const handleOpenQuiz = () => {
    setQuizIdx(0);
    setShowQuiz(true);
  };

  const currentVideo = videos[currentIndex];
  const currentState = videoStates[currentIndex];
  const currentQuizList = videoQuizzes[currentVideo.id];
  const currentQuizItem = currentQuizList?.[quizIdx];

  if (isLoading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50">
        <div className="text-gray-900">加载中...</div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="h-screen w-screen relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-emerald-50"
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      {/* 顶部导航 */}
      <div className="absolute top-0 left-0 right-0 z-30 flex items-center justify-between px-4 pt-3 pb-8 bg-gradient-to-b from-black/40 to-transparent">
        <div className="flex items-center gap-6">
          {["关注", "推荐"].map((tab, i) => (
            <span
              key={tab}
              className={`text-base font-bold ${i === 1 ? "text-white" : "text-white/60"}`}
            >
              {tab}
              {i === 1 && <div className="h-0.5 bg-white rounded-full mt-1 mx-auto w-6"></div>}
            </span>
          ))}
        </div>
        <div className="flex items-center gap-4">
          <Link to="/discover">
            <Search className="w-6 h-6 text-white" />
          </Link>
          <Link
            to="/login"
            className="w-9 h-9 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center border border-white/30 hover:bg-white/30 transition-all"
          >
            <span className="text-white text-xs font-bold">登录</span>
          </Link>
        </div>
      </div>

      <div
        className="absolute inset-0 transition-transform duration-500 ease-out"
        style={{ transform: `translateY(-${currentIndex * 100}vh)` }}
      >
        {videos.map((video, index) => (
          <div
            key={video.id}
            className="h-screen w-screen relative flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-emerald-50"
            onClick={video.bvid ? undefined : handleVideoClick}
          >
            {video.bvid ? (
              <>
                <iframe
                  className="absolute inset-0 w-full h-full"
                  src={`https://player.bilibili.com/player.html?bvid=${video.bvid}&autoplay=0&muted=1&high_quality=1&danmaku=0`}
                  allowFullScreen
                  allow="autoplay; encrypted-media"
                  style={{ border: "none" }}
                />
                {index === currentIndex && (
                  <div className="absolute inset-0" style={{ zIndex: 5 }}></div>
                )}
              </>
            ) : (
              <video
                ref={(el) => { videoRefs.current[index] = el; }}
                className="absolute inset-0 w-full h-full object-cover"
                src={video.videoUrl}
                loop
                playsInline
                poster={video.thumbnail}
              />
            )}

            {!isPlaying && index === currentIndex && !video.bvid && (
              <div className="absolute inset-0 flex items-center justify-center z-15">
                <div className="w-20 h-20 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center shadow-lg">
                  <Play className="w-10 h-10 text-emerald-600 ml-1" />
                </div>
              </div>
            )}

            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/30 z-10 pointer-events-none"></div>

            {/* 视频信息 */}
            <div className="absolute bottom-0 left-0 right-0 z-20 p-4 pb-24 pointer-events-none">
              <div className="flex items-center gap-3 mb-3 pointer-events-auto">
                <img
                  src={video.avatar}
                  alt={video.author}
                  className="w-12 h-12 rounded-full border-2 border-white/80 shadow-lg"
                />
                <div className="flex-1">
                  <h3 className="text-white font-bold drop-shadow-lg">{video.author}</h3>
                  <p className="text-white/80 text-sm drop-shadow">{video.category}</p>
                </div>
                <button className="px-5 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-full text-sm font-bold hover:shadow-lg hover:scale-105 transition-all pointer-events-auto">
                  关注
                </button>
              </div>
              <h2 className="text-white font-bold text-lg mb-2 drop-shadow-lg">{video.title}</h2>
              <p className="text-white/90 text-sm leading-relaxed mb-3 drop-shadow">{video.description}</p>
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white/20 backdrop-blur-sm rounded-lg">
                  <Play className="w-3.5 h-3.5 text-white" />
                  <span className="text-white text-xs font-medium">{video.duration}</span>
                </div>
                <div className="px-3 py-1.5 bg-white/20 backdrop-blur-sm rounded-lg">
                  <span className="text-white text-xs font-medium"># {video.category}</span>
                </div>
              </div>
            </div>

            {/* 右侧操作栏 */}
            <div className="absolute right-4 bottom-32 flex flex-col items-center gap-5 z-20">
              {video.hasQuiz && (
                <button
                  onClick={handleOpenQuiz}
                  className="flex flex-col items-center gap-1.5 group"
                >
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shadow-lg group-hover:scale-110 transition-all">
                    <Vote className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-gray-900 text-xs font-medium bg-white/80 px-2 py-0.5 rounded-lg shadow-sm">{video.quizCount}题</span>
                </button>
              )}

              <button onClick={handleLike} className="flex flex-col items-center gap-1.5 group">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-all ${
                  currentState.isLiked ? "bg-gradient-to-br from-red-500 to-pink-500" : "bg-white"
                }`}>
                  <Heart className={`w-6 h-6 ${currentState.isLiked ? "fill-white text-white" : "text-gray-700"}`} />
                </div>
                <span className="text-gray-900 text-xs font-medium bg-white/80 px-2 py-0.5 rounded-lg shadow-sm">
                  {currentState.likes > 10000 ? `${(currentState.likes / 1000).toFixed(1)}w` : currentState.likes}
                </span>
              </button>

              <button className="flex flex-col items-center gap-1.5 group">
                <div className="w-12 h-12 rounded-xl bg-white shadow-lg flex items-center justify-center group-hover:scale-110 transition-all">
                  <MessageCircle className="w-6 h-6 text-gray-700" />
                </div>
                <span className="text-gray-900 text-xs font-medium bg-white/80 px-2 py-0.5 rounded-lg shadow-sm">{video.comments}</span>
              </button>

              <button onClick={handleSave} className="flex flex-col items-center gap-1.5 group">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-all ${
                  currentState.isSaved ? "bg-gradient-to-br from-yellow-500 to-orange-500" : "bg-white"
                }`}>
                  <Bookmark className={`w-6 h-6 ${currentState.isSaved ? "fill-white text-white" : "text-gray-700"}`} />
                </div>
                <span className="text-gray-900 text-xs font-medium bg-white/80 px-2 py-0.5 rounded-lg shadow-sm">收藏</span>
              </button>

              <button className="flex flex-col items-center gap-1.5 group">
                <div className="w-12 h-12 rounded-xl bg-white shadow-lg flex items-center justify-center group-hover:scale-110 transition-all">
                  <Share2 className="w-6 h-6 text-gray-700" />
                </div>
                <span className="text-gray-900 text-xs font-medium bg-white/80 px-2 py-0.5 rounded-lg shadow-sm">{video.shares}</span>
              </button>

              <button onClick={() => setIsMuted(!isMuted)} className="flex flex-col items-center gap-1.5 group">
                <div className="w-12 h-12 rounded-xl bg-white shadow-lg flex items-center justify-center group-hover:scale-110 transition-all">
                  {isMuted ? <VolumeX className="w-6 h-6 text-gray-700" /> : <Volume2 className="w-6 h-6 text-gray-700" />}
                </div>
              </button>
            </div>

            <div className="absolute top-4 right-4 z-20">
              <button className="w-10 h-10 rounded-xl bg-white shadow-lg flex items-center justify-center hover:scale-105 transition-all">
                <MoreHorizontal className="w-5 h-5 text-gray-700" />
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="absolute left-1/2 transform -translate-x-1/2 top-6 flex gap-1 z-30">
        {videos.map((_, index) => (
          <div
            key={index}
            className={`h-1 rounded-full transition-all ${
              index === currentIndex ? "w-8 bg-emerald-500" : "w-1 bg-gray-400"
            }`}
          ></div>
        ))}
      </div>

      {/* 做题卡片 - 抖音投票风格 */}
      {showQuiz && currentQuizItem && (
        <div className="absolute bottom-24 left-4 right-16 z-40">
          <div className="bg-black/65 backdrop-blur-xl rounded-2xl p-5 border border-white/10">
            {/* 头部 */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Vote className="w-4 h-4 text-violet-400" />
                <span className="text-white/90 text-sm font-medium">
                  {quizIdx + 1}/{currentQuizList!.length}
                </span>
              </div>
              <button
                onClick={() => setShowQuiz(false)}
                className="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center hover:bg-white/30 transition-colors"
              >
                <X className="w-4 h-4 text-white" />
              </button>
            </div>

            {/* 题目 */}
            <p className="text-white font-bold text-base mb-4 leading-relaxed">
              {currentQuizItem.question}
            </p>

            {/* 选项 */}
            <div className="space-y-2.5">
              {currentQuizItem.options.map((option, idx) => {
                const key = `${currentVideo.id}-${quizIdx}`;
                const hasAnswered = quizAnswered[key] !== undefined && quizAnswered[key] !== null;
                const isSelected = quizAnswered[key] === idx;
                const isCorrect = idx === currentQuizItem.correctAnswer;
                const percent = animatedPercents[key]?.[idx] ?? 0;

                return (
                  <button
                    key={idx}
                    onClick={() => !hasAnswered && handleAnswer(idx)}
                    className={`w-full text-left px-4 py-3 rounded-xl transition-all relative overflow-hidden ${
                      hasAnswered && isCorrect
                        ? "border-2 border-emerald-400"
                        : hasAnswered && isSelected && !isCorrect
                        ? "border-2 border-red-400"
                        : hasAnswered
                        ? "border border-white/10"
                        : "border border-white/15 hover:bg-white/20 cursor-pointer"
                    }`}
                  >
                    {/* 抖音投票进度条 */}
                    {hasAnswered && (
                      <div
                        className={`absolute top-0 left-0 bottom-0 rounded-xl transition-all duration-700 ease-out ${
                          isCorrect
                            ? "bg-emerald-500/40"
                            : isSelected
                            ? "bg-red-500/30"
                            : "bg-white/8"
                        }`}
                        style={{ width: `${percent}%` }}
                      />
                    )}
                    <div className="flex items-center justify-between relative z-10">
                      <div className="flex items-center gap-3">
                        <span className={`w-6 h-6 rounded-md flex items-center justify-center text-xs font-bold ${
                          hasAnswered && isCorrect
                            ? "bg-emerald-400 text-white"
                            : hasAnswered && isSelected && !isCorrect
                            ? "bg-red-400 text-white"
                            : "bg-white/20 text-white"
                        }`}>
                          {hasAnswered && isCorrect ? (
                            <Check className="w-4 h-4" />
                          ) : hasAnswered && isSelected ? (
                            <X className="w-4 h-4" />
                          ) : (
                            String.fromCharCode(65 + idx)
                          )}
                        </span>
                        <span className={`text-sm font-medium ${
                          hasAnswered && isCorrect ? "text-emerald-300" :
                          hasAnswered && isSelected ? "text-red-300" : "text-white/90"
                        }`}>
                          {option.text}
                        </span>
                      </div>
                      {hasAnswered && (
                        <span className={`text-sm font-bold ml-2 ${
                          isCorrect ? "text-emerald-300" : isSelected ? "text-red-300" : "text-white/50"
                        }`}>
                          {percent}%
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* 底部：答题结果 + 下一题 */}
            <div className="flex items-center justify-between mt-4">
              <div className="flex items-center gap-3">
                {/* 进度点 */}
                <div className="flex gap-1.5">
                  {currentQuizList!.map((_, idx) => {
                    const qKey = `${currentVideo.id}-${idx}`;
                    return (
                      <div
                        key={idx}
                        className={`h-1.5 rounded-full transition-all ${
                          idx === quizIdx
                            ? "w-6 bg-violet-400"
                            : quizAnswered[qKey] !== undefined && quizAnswered[qKey] !== null
                            ? "w-1.5 bg-emerald-400"
                            : "w-1.5 bg-white/30"
                        }`}
                      />
                    );
                  })}
                </div>
                {/* 参与人数 */}
                <span className="text-white/40 text-xs">
                  {currentQuizItem.totalVotes.toLocaleString()}人参与
                </span>
              </div>

              {/* 下一题按钮 */}
              {quizIdx < currentQuizList!.length - 1 && (
                <button
                  onClick={() => setQuizIdx(quizIdx + 1)}
                  className="flex items-center gap-1 px-4 py-2 bg-violet-500/80 text-white rounded-lg text-sm font-bold hover:bg-violet-500 transition-colors"
                >
                  下一题
                  <ChevronRight className="w-4 h-4" />
                </button>
              )}
              {quizIdx === currentQuizList!.length - 1 && quizAnswered[`${currentVideo.id}-${quizIdx}`] !== undefined && quizAnswered[`${currentVideo.id}-${quizIdx}`] !== null && (
                <button
                  onClick={() => setShowQuiz(false)}
                  className="px-4 py-2 bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white rounded-lg text-sm font-bold hover:opacity-90 transition-all"
                >
                  完成
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
