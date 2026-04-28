import { useState, useEffect } from "react";
import { CheckCircle, XCircle, Clock, Award } from "lucide-react";

interface Question {
  id: string;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
}

export function OnlinePractice() {
  const questions: Question[] = [
    {
      id: "1",
      question: "以下哪种数据结构使用先进先出(FIFO)的原则？",
      options: ["栈(Stack)", "队列(Queue)", "树(Tree)", "图(Graph)"],
      correctAnswer: 1,
      explanation: "队列使用先进先出(FIFO)原则，最先进入的元素最先被处理。",
    },
    {
      id: "2",
      question: "时间复杂度 O(n log n) 通常对应哪种排序算法？",
      options: ["冒泡排序", "选择排序", "快速排序", "插入排序"],
      correctAnswer: 2,
      explanation: "快速排序的平均时间复杂度为 O(n log n)。",
    },
    {
      id: "3",
      question: "二叉搜索树的中序遍历结果是什么？",
      options: ["随机顺序", "从大到小", "从小到大", "层序遍历"],
      correctAnswer: 2,
      explanation: "二叉搜索树的中序遍历会按照从小到大的顺序输出节点值。",
    },
    {
      id: "4",
      question: "在Python中，哪个关键字用于定义函数？",
      options: ["function", "def", "func", "define"],
      correctAnswer: 1,
      explanation: "Python使用def关键字来定义函数。",
    },
    {
      id: "5",
      question: "HTTP协议默认使用的端口号是？",
      options: ["21", "22", "80", "443"],
      correctAnswer: 2,
      explanation: "HTTP协议默认使用80端口，HTTPS使用443端口。",
    },
  ];

  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<(number | null)[]>(
    new Array(questions.length).fill(null)
  );
  const [showResults, setShowResults] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(600);

  useEffect(() => {
    if (showResults) return;
    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          setShowResults(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [showResults]);

  const handleSelectAnswer = (answerIndex: number) => {
    if (showResults) return;
    const newAnswers = [...selectedAnswers];
    newAnswers[currentQuestion] = answerIndex;
    setSelectedAnswers(newAnswers);
  };

  const handleSubmit = () => {
    setShowResults(true);
  };

  const calculateScore = () => {
    let correct = 0;
    selectedAnswers.forEach((answer, index) => {
      if (answer === questions[index].correctAnswer) {
        correct++;
      }
    });
    return Math.round((correct / questions.length) * 100);
  };

  const getCorrectCount = () => {
    let correct = 0;
    selectedAnswers.forEach((answer, index) => {
      if (answer === questions[index].correctAnswer) {
        correct++;
      }
    });
    return correct;
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-800 mb-2">在线练习</h1>
        <p className="text-gray-600">完成测评题目，检验你的学习成果</p>
      </div>

      {showResults ? (
        <div className="bg-white rounded-xl shadow-sm p-8 text-center">
          <div className="w-20 h-20 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Award className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">测试完成！</h2>
          <div className="text-6xl font-bold text-emerald-500 my-6">{calculateScore()}分</div>
          <p className="text-gray-600 mb-8">
            你答对了 {getCorrectCount()} / {questions.length} 道题
          </p>

          <div className="space-y-4 text-left max-w-2xl mx-auto">
            {questions.map((question, index) => {
              const userAnswer = selectedAnswers[index];
              const isCorrect = userAnswer === question.correctAnswer;
              return (
                <div
                  key={question.id}
                  className={`p-4 rounded-lg border-2 ${
                    isCorrect ? "border-emerald-200 bg-emerald-50" : "border-red-200 bg-red-50"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {isCorrect ? (
                      <CheckCircle className="w-5 h-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 mb-2">
                        {index + 1}. {question.question}
                      </p>
                      <p className="text-sm text-gray-600">
                        你的答案: {userAnswer !== null ? question.options[userAnswer] : "未作答"}
                      </p>
                      {!isCorrect && (
                        <p className="text-sm text-emerald-600 mt-1">
                          正确答案: {question.options[question.correctAnswer]}
                        </p>
                      )}
                      <p className="text-sm text-gray-500 mt-2 italic">{question.explanation}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex gap-4 justify-center mt-8">
            <button
              onClick={() => {
                setShowResults(false);
                setSelectedAnswers(new Array(questions.length).fill(null));
                setCurrentQuestion(0);
                setTimeRemaining(600);
              }}
              className="px-6 py-3 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
            >
              重新测试
            </button>
            <button className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
              返回首页
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
              <div className="flex items-center gap-6">
                <div className="text-sm text-gray-600">
                  题目 <span className="font-bold text-gray-900">{currentQuestion + 1}</span> / {questions.length}
                </div>
                <div className="flex gap-2">
                  {questions.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentQuestion(index)}
                      className={`w-8 h-8 rounded-lg text-sm font-medium transition-all ${
                        index === currentQuestion
                          ? "bg-emerald-500 text-white shadow-md"
                          : selectedAnswers[index] !== null
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                      }`}
                    >
                      {index + 1}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg">
                <Clock className="w-5 h-5 text-gray-600" />
                <span className="font-mono font-semibold text-gray-800">
                  {Math.floor(timeRemaining / 60)}:{(timeRemaining % 60).toString().padStart(2, "0")}
                </span>
              </div>
            </div>

            <div className="mb-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-6">
                {questions[currentQuestion].question}
              </h3>
              <div className="space-y-3">
                {questions[currentQuestion].options.map((option, index) => {
                  const isSelected = selectedAnswers[currentQuestion] === index;
                  const letter = String.fromCharCode(65 + index);

                  return (
                    <button
                      key={index}
                      onClick={() => handleSelectAnswer(index)}
                      className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                        isSelected
                          ? "border-emerald-500 bg-emerald-50"
                          : "border-gray-200 hover:border-gray-300 bg-white hover:bg-gray-50"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-8 h-8 rounded-lg flex items-center justify-center font-semibold ${
                            isSelected
                              ? "bg-emerald-500 text-white"
                              : "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {letter}
                        </div>
                        <span className="text-gray-900">{option}</span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="flex justify-between items-center pt-4 border-t border-gray-200">
              <button
                onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                disabled={currentQuestion === 0}
                className="px-6 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                上一题
              </button>

              <div className="text-sm text-gray-600">
                已完成 {selectedAnswers.filter((a) => a !== null).length} / {questions.length} 题
              </div>

              {currentQuestion === questions.length - 1 ? (
                <button
                  onClick={handleSubmit}
                  disabled={selectedAnswers.some((answer) => answer === null)}
                  className="px-6 py-2.5 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
                >
                  提交答案
                </button>
              ) : (
                <button
                  onClick={() => setCurrentQuestion(Math.min(questions.length - 1, currentQuestion + 1))}
                  className="px-6 py-2.5 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors font-medium"
                >
                  下一题
                </button>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
