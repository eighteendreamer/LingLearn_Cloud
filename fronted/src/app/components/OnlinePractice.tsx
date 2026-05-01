import { useState, useEffect } from "react";
import { CheckCircle, XCircle, Clock, Award } from "lucide-react";
import { apiRequest } from "../lib/api";
import {
  fetchPracticeQuestions,
  fetchPracticeResult,
  fetchQuestionBanks,
  normalizePracticeAnswer,
  submitPracticeSession,
} from "../lib/learning-api";
import type {
  QuestionBankResponse,
  PracticeQuestionResponse,
  PracticeSessionResponse,
  PracticeAnswerResponse,
  PracticeSessionCreatePayload,
  PracticeAnswerSubmitPayload,
} from "../lib/types";

export function OnlinePractice() {
  const [banks, setBanks] = useState<QuestionBankResponse[]>([]);
  const [selectedBank, setSelectedBank] = useState<QuestionBankResponse | null>(null);
  const [questions, setQuestions] = useState<PracticeQuestionResponse[]>([]);
  const [session, setSession] = useState<PracticeSessionResponse | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<(number[] | null)[]>([]);
  const [answerResults, setAnswerResults] = useState<(PracticeAnswerResponse | null)[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(600);
  const [loading, setLoading] = useState(true);
  const [generatingPaper, setGeneratingPaper] = useState(false);

  useEffect(() => {
    loadBanks();
  }, []);

  useEffect(() => {
    if (showResults || !session) return;
    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [showResults, session]);

  const loadBanks = async () => {
    try {
      setLoading(true);
      const data = await fetchQuestionBanks();
      setBanks(data);
    } catch (error) {
      console.error("Failed to load question banks:", error);
    } finally {
      setLoading(false);
    }
  };

  const startPractice = async (bank: QuestionBankResponse) => {
    try {
      setGeneratingPaper(true);
      setSelectedBank(bank);
      const payload: PracticeSessionCreatePayload = {
        bank_id: bank.id,
        session_type: "practice",
      };
      const sessionData = await apiRequest<PracticeSessionResponse>("/practice/sessions", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setSession(sessionData);

      const questionsData = await fetchPracticeQuestions(bank.id);
      setQuestions(questionsData);
      setSelectedAnswers(new Array(questionsData.length).fill(null));
      setAnswerResults(new Array(questionsData.length).fill(null));
      setCurrentQuestion(0);
      setShowResults(false);
      setTimeRemaining(600);
    } catch (error) {
      console.error("Failed to start practice:", error);
    } finally {
      setGeneratingPaper(false);
    }
  };

  const handleSelectAnswer = (optionId: number) => {
    if (showResults || !session) return;
    const question = questions[currentQuestion];
    const newAnswers = [...selectedAnswers];

    if (question.question_type === "single_choice") {
      newAnswers[currentQuestion] = [optionId];
    } else {
      const current = newAnswers[currentQuestion] || [];
      if (current.includes(optionId)) {
        newAnswers[currentQuestion] = current.filter((id) => id !== optionId);
      } else {
        newAnswers[currentQuestion] = [...current, optionId];
      }
    }
    setSelectedAnswers(newAnswers);
  };

  const submitAnswer = async (questionIndex: number) => {
    if (!session || !selectedAnswers[questionIndex]) return null;

    try {
      const payload: PracticeAnswerSubmitPayload = {
        question_id: questions[questionIndex].id,
        selected_option_ids: selectedAnswers[questionIndex]!,
      };
      const result = await apiRequest<PracticeAnswerResponse>(
        `/practice/sessions/${session.id}/answers`,
        {
          method: "POST",
          body: JSON.stringify(payload),
        }
      );
      const normalized = normalizePracticeAnswer(result);
      const newResults = [...answerResults];
      newResults[questionIndex] = normalized;
      setAnswerResults(newResults);
      return normalized;
    } catch (error) {
      console.error("Failed to submit answer:", error);
      return null;
    }
  };

  const handleSubmit = async () => {
    if (!session) return;

    const submittedResults = [...answerResults];
    for (let i = 0; i < questions.length; i++) {
      if (selectedAnswers[i] && !answerResults[i]) {
        submittedResults[i] = await submitAnswer(i);
      }
    }

    try {
      await submitPracticeSession(session.id);
      const result = await fetchPracticeResult(session.id);
      const resultMap = new Map(result.answers.map((answer) => [answer.question_id, answer]));
      setAnswerResults(
        questions.map((question, index) => {
          const answer = resultMap.get(question.id);
          return submittedResults[index] ?? (answer
            ? {
                question_id: answer.question_id,
                is_correct: answer.is_correct,
                earned_score: answer.earned_score,
                score: answer.earned_score,
                correct_option_ids: [],
              }
            : null);
        })
      );
      setShowResults(true);
    } catch (error) {
      console.error("Failed to complete session:", error);
      setShowResults(true);
    }
  };

  const calculateScore = () => {
    const totalScore = answerResults.reduce((sum, result) => sum + (result?.score ?? result?.earned_score ?? 0), 0);
    const maxScore = questions.reduce((sum, q) => sum + q.score, 0);
    return maxScore > 0 ? Math.round((totalScore / maxScore) * 100) : 0;
  };

  const getCorrectCount = () => {
    return answerResults.filter((result) => result?.is_correct).length;
  };

  if (loading) {
    return (
      <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-24">
        <div className="p-8 max-w-5xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">加载中...</div>
          </div>
        </div>
      </div>
    );
  }

  if (!session || questions.length === 0) {
    return (
      <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-24">
        <div className="p-8 max-w-5xl mx-auto">
          <div className="mb-6">
            <h1 className="text-2xl font-semibold text-gray-800 mb-2">在线练习</h1>
            <p className="text-gray-600">先选择题库，再生成对应试卷开始练习</p>
          </div>
          {selectedBank && generatingPaper && (
            <div className="mb-4 rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
              正在根据题库生成练习试卷...
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {banks.map((bank) => (
              <div
                key={bank.id}
                className={`bg-white rounded-xl p-6 shadow-sm border transition-all ${
                  selectedBank?.id === bank.id
                    ? "border-emerald-500"
                    : "border-gray-200 hover:border-emerald-500"
                }`}
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{bank.title}</h3>
                <p className="text-sm text-gray-600 mb-4">{bank.description}</p>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span>题目: {bank.question_count}</span>
                  <span>难度: {bank.difficulty}</span>
                  <span>分类: {bank.category || "综合"}</span>
                </div>
                <div className="mt-5 flex gap-3">
                  <button
                    onClick={() => setSelectedBank(bank)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    选择题库
                  </button>
                  <button
                    onClick={() => startPractice(bank)}
                    disabled={generatingPaper}
                    className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {generatingPaper && selectedBank?.id === bank.id ? "生成中..." : "生成试卷"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-24">
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
                const result = answerResults[index];
                const userAnswer = selectedAnswers[index];
                const isCorrect = result?.is_correct || false;
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
                          {index + 1}. {question.question_text || question.content}
                        </p>
                        <p className="text-sm text-gray-600">
                          你的答案:{" "}
                          {userAnswer
                            ? question.options
                                .filter((opt) => userAnswer.includes(opt.id))
                                .map((opt) => opt.option_text || opt.content)
                                .join(", ")
                            : "未作答"}
                        </p>
                        {!isCorrect && result?.correct_option_ids && result.correct_option_ids.length > 0 && (
                          <p className="text-sm text-emerald-600 mt-1">
                            正确答案:{" "}
                            {question.options
                              .filter((opt) => result.correct_option_ids?.includes(opt.id))
                              .map((opt) => opt.option_text || opt.content)
                              .join(", ")}
                          </p>
                        )}
                        <p className="text-sm text-gray-500 mt-2">
                          得分: {result?.score ?? result?.earned_score ?? 0} / {question.score}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="flex gap-4 justify-center mt-8">
              <button
                onClick={() => {
                  if (selectedBank) {
                    startPractice(selectedBank);
                  }
                }}
                className="px-6 py-3 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
              >
                重新测试
              </button>
              <button
                onClick={() => {
                  setSession(null);
                  setQuestions([]);
                  setShowResults(false);
                }}
                className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                返回题库
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
                <div className="flex items-center gap-6">
                  <div className="text-sm text-gray-600">
                    题目 <span className="font-bold text-gray-900">{currentQuestion + 1}</span> /{" "}
                    {questions.length}
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
                  {questions[currentQuestion].question_text || questions[currentQuestion].content}
                </h3>
                <div className="space-y-3">
                  {questions[currentQuestion].options.map((option) => {
                    const isSelected = selectedAnswers[currentQuestion]?.includes(option.id) || false;
                    const order = option.option_order ?? option.sort_order ?? 1;
                    const letter = String.fromCharCode(65 + order - 1);

                    return (
                      <button
                        key={option.id}
                        onClick={() => handleSelectAnswer(option.id)}
                        className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                          isSelected
                            ? "border-emerald-500 bg-emerald-50"
                            : "border-gray-200 hover:border-gray-300 bg-white hover:bg-gray-50"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`w-8 h-8 rounded-lg flex items-center justify-center font-semibold ${
                              isSelected ? "bg-emerald-500 text-white" : "bg-gray-100 text-gray-600"
                            }`}
                          >
                            {letter}
                          </div>
                          <span className="text-gray-900">{option.option_text || option.content}</span>
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
    </div>
  );
}
