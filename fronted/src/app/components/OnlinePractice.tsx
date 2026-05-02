import { useEffect, useState } from "react";
import { useSearchParams } from "react-router";
import { Award, CheckCircle, Clock, XCircle } from "lucide-react";

import { apiRequest } from "../lib/api";
import {
  fetchPracticeQuestions,
  fetchPracticeResult,
  fetchPracticeSession,
  fetchQuestionBanks,
  normalizePracticeAnswer,
  submitPracticeSession,
} from "../lib/learning-api";
import type {
  PracticeAnswerResponse,
  PracticeAnswerSubmitPayload,
  PracticeQuestionResponse,
  PracticeSessionCreatePayload,
  PracticeSessionResponse,
  QuestionBankResponse,
} from "../lib/types";

export function OnlinePractice() {
  const [searchParams] = useSearchParams();
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
    void loadBanks();
  }, []);

  useEffect(() => {
    const sessionIdParam = searchParams.get("session_id");
    const bankIdParam = searchParams.get("bank_id");
    if (!sessionIdParam || !bankIdParam || session) {
      return;
    }

    const sessionId = Number(sessionIdParam);
    const bankId = Number(bankIdParam);
    if (!Number.isFinite(sessionId) || !Number.isFinite(bankId)) {
      return;
    }

    void openExistingPracticeSession(sessionId, bankId);
  }, [searchParams, session]);

  useEffect(() => {
    if (showResults || !session) {
      return;
    }
    const timer = setInterval(() => {
      setTimeRemaining((previous) => {
        if (previous <= 1) {
          clearInterval(timer);
          void handleSubmit();
          return 0;
        }
        return previous - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [session, showResults]);

  const loadBanks = async () => {
    try {
      setLoading(true);
      setBanks(await fetchQuestionBanks());
    } catch (error) {
      console.error("Failed to load question banks:", error);
    } finally {
      setLoading(false);
    }
  };

  const resetPracticeState = (questionsData: PracticeQuestionResponse[]) => {
    setQuestions(questionsData);
    setSelectedAnswers(new Array(questionsData.length).fill(null));
    setAnswerResults(new Array(questionsData.length).fill(null));
    setCurrentQuestion(0);
    setShowResults(false);
    setTimeRemaining(600);
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
      const questionsData = await fetchPracticeQuestions(bank.id);
      setSession(sessionData);
      resetPracticeState(questionsData);
    } catch (error) {
      console.error("Failed to start practice:", error);
    } finally {
      setGeneratingPaper(false);
    }
  };

  const openExistingPracticeSession = async (sessionId: number, bankId: number) => {
    try {
      setGeneratingPaper(true);
      const [sessionData, questionsData] = await Promise.all([
        fetchPracticeSession(sessionId),
        fetchPracticeQuestions(bankId),
      ]);
      const matchedBank = banks.find((item) => item.id === bankId) ?? {
        id: bankId,
        title: `视频练习 #${bankId}`,
        description: "基于当前视频生成的 AI 练习题库。",
        difficulty: "mixed",
        question_count: questionsData.length,
      };
      setSelectedBank(matchedBank);
      setSession(sessionData);
      resetPracticeState(questionsData);
    } catch (error) {
      console.error("Failed to open generated practice session:", error);
    } finally {
      setGeneratingPaper(false);
      setLoading(false);
    }
  };

  const handleSelectAnswer = (optionId: number) => {
    if (showResults || !session) {
      return;
    }

    const question = questions[currentQuestion];
    const nextAnswers = [...selectedAnswers];
    if (question.question_type === "single_choice") {
      nextAnswers[currentQuestion] = [optionId];
    } else {
      const current = nextAnswers[currentQuestion] || [];
      nextAnswers[currentQuestion] = current.includes(optionId)
        ? current.filter((id) => id !== optionId)
        : [...current, optionId];
    }
    setSelectedAnswers(nextAnswers);
  };

  const submitAnswer = async (questionIndex: number) => {
    if (!session || !selectedAnswers[questionIndex]) {
      return null;
    }

    try {
      const payload: PracticeAnswerSubmitPayload = {
        question_id: questions[questionIndex].id,
        selected_option_ids: selectedAnswers[questionIndex] ?? [],
      };
      const result = await apiRequest<PracticeAnswerResponse>(
        `/practice/sessions/${session.id}/answers`,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );
      const normalized = normalizePracticeAnswer(result);
      setAnswerResults((previous) => {
        const next = [...previous];
        next[questionIndex] = normalized;
        return next;
      });
      return normalized;
    } catch (error) {
      console.error("Failed to submit answer:", error);
      return null;
    }
  };

  const handleSubmit = async () => {
    if (!session) {
      return;
    }

    const submittedResults = [...answerResults];
    for (let index = 0; index < questions.length; index += 1) {
      if (selectedAnswers[index] && !answerResults[index]) {
        submittedResults[index] = await submitAnswer(index);
      }
    }

    try {
      await submitPracticeSession(session.id);
      const result = await fetchPracticeResult(session.id);
      const resultMap = new Map(result.answers.map((answer) => [answer.question_id, answer]));
      setAnswerResults(
        questions.map((question, index) => {
          const answer = resultMap.get(question.id);
          return (
            submittedResults[index] ??
            (answer
              ? {
                  question_id: answer.question_id,
                  is_correct: answer.is_correct,
                  earned_score: answer.earned_score,
                  score: answer.earned_score,
                  correct_option_ids: [],
                }
              : null)
          );
        }),
      );
    } catch (error) {
      console.error("Failed to complete session:", error);
    } finally {
      setShowResults(true);
    }
  };

  const calculateScore = () => {
    const totalScore = answerResults.reduce(
      (sum, result) => sum + (result?.score ?? result?.earned_score ?? 0),
      0,
    );
    const maxScore = questions.reduce((sum, question) => sum + question.score, 0);
    return maxScore > 0 ? Math.round((totalScore / maxScore) * 100) : 0;
  };

  const correctCount = answerResults.filter((result) => result?.is_correct).length;

  if (loading) {
    return (
      <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-24">
        <div className="mx-auto flex h-64 max-w-5xl items-center justify-center p-8">
          <div className="text-gray-500">练习加载中...</div>
        </div>
      </div>
    );
  }

  if (!session || questions.length === 0) {
    return (
      <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-24">
        <div className="mx-auto max-w-5xl p-8">
          <div className="mb-6">
            <h1 className="mb-2 text-2xl font-semibold text-gray-800">在线练习</h1>
            <p className="text-gray-600">选择一个题库，开始本次练习。</p>
          </div>
          {selectedBank && generatingPaper ? (
            <div className="mb-4 rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
              正在为你生成练习试卷...
            </div>
          ) : null}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {banks.map((bank) => (
              <div
                key={bank.id}
                className={`rounded-xl border bg-white p-6 shadow-sm transition-all ${
                  selectedBank?.id === bank.id
                    ? "border-emerald-500"
                    : "border-gray-200 hover:border-emerald-500"
                }`}
              >
                <h3 className="mb-2 text-lg font-semibold text-gray-900">{bank.title}</h3>
                <p className="mb-4 text-sm text-gray-600">{bank.description}</p>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span>{`题目数：${bank.question_count}`}</span>
                  <span>{`难度：${bank.difficulty}`}</span>
                  <span>{`分类：${bank.category || "通用"}`}</span>
                </div>
                <div className="mt-5 flex gap-3">
                  <button
                    onClick={() => setSelectedBank(bank)}
                    className="rounded-lg bg-gray-100 px-4 py-2 text-gray-700 transition-colors hover:bg-gray-200"
                  >
                    选中
                  </button>
                  <button
                    onClick={() => void startPractice(bank)}
                    disabled={generatingPaper}
                    className="rounded-lg bg-emerald-500 px-4 py-2 text-white transition-colors hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {generatingPaper && selectedBank?.id === bank.id ? "生成中..." : "开始练习"}
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
      <div className="mx-auto max-w-5xl p-8">
        <div className="mb-6">
          <h1 className="mb-2 text-2xl font-semibold text-gray-800">在线练习</h1>
          <p className="text-gray-600">完成下面的题目，检查你的掌握情况。</p>
        </div>

        {showResults ? (
          <div className="rounded-xl bg-white p-8 text-center shadow-sm">
            <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-teal-500">
              <Award className="h-10 w-10 text-white" />
            </div>
            <h2 className="mb-2 text-3xl font-bold text-gray-900">练习完成</h2>
            <div className="my-6 text-6xl font-bold text-emerald-500">{calculateScore()}</div>
            <p className="mb-8 text-gray-600">{`你答对了 ${correctCount} / ${questions.length} 题。`}</p>

            <div className="mx-auto max-w-2xl space-y-4 text-left">
              {questions.map((question, index) => {
                const result = answerResults[index];
                const userAnswer = selectedAnswers[index];
                const isCorrect = result?.is_correct || false;
                return (
                  <div
                    key={question.id}
                    className={`rounded-lg border-2 p-4 ${
                      isCorrect ? "border-emerald-200 bg-emerald-50" : "border-red-200 bg-red-50"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {isCorrect ? (
                        <CheckCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-emerald-500" />
                      ) : (
                        <XCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-500" />
                      )}
                      <div className="flex-1">
                        <p className="mb-2 font-medium text-gray-900">
                          {index + 1}. {question.question_text || question.content}
                        </p>
                        <p className="text-sm text-gray-600">
                          你的答案：
                          {userAnswer
                            ? question.options
                                .filter((option) => userAnswer.includes(option.id))
                                .map((option) => option.option_text || option.content)
                                .join(", ")
                            : "未作答"}
                        </p>
                        <p className="mt-2 text-sm text-gray-500">
                          {`得分：${result?.score ?? result?.earned_score ?? 0} / ${question.score}`}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-8 flex justify-center gap-4">
              <button
                onClick={() => selectedBank && void startPractice(selectedBank)}
                className="rounded-lg bg-emerald-500 px-6 py-3 text-white transition-colors hover:bg-emerald-600"
              >
                再来一次
              </button>
              <button
                onClick={() => {
                  setSession(null);
                  setQuestions([]);
                  setShowResults(false);
                }}
                className="rounded-lg bg-gray-100 px-6 py-3 text-gray-700 transition-colors hover:bg-gray-200"
              >
                返回题库
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="mb-6 rounded-xl bg-white p-6 shadow-sm">
              <div className="mb-6 flex items-center justify-between border-b border-gray-200 pb-4">
                <div className="flex items-center gap-6">
                  <div className="text-sm text-gray-600">
                    第
                    <span className="font-bold text-gray-900">{currentQuestion + 1}</span>
                    {` / ${questions.length} 题`}
                  </div>
                  <div className="flex gap-2">
                    {questions.map((_, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentQuestion(index)}
                        className={`h-8 w-8 rounded-lg text-sm font-medium transition-all ${
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
                <div className="flex items-center gap-2 rounded-lg bg-gray-100 px-4 py-2">
                  <Clock className="h-5 w-5 text-gray-600" />
                  <span className="font-mono font-semibold text-gray-800">
                    {Math.floor(timeRemaining / 60)}:{(timeRemaining % 60).toString().padStart(2, "0")}
                  </span>
                </div>
              </div>

              <div className="mb-8">
                <h3 className="mb-6 text-xl font-semibold text-gray-900">
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
                        className={`w-full rounded-xl border-2 p-4 text-left transition-all ${
                          isSelected
                            ? "border-emerald-500 bg-emerald-50"
                            : "border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`flex h-8 w-8 items-center justify-center rounded-lg font-semibold ${
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

              <div className="flex items-center justify-between border-t border-gray-200 pt-4">
                <button
                  onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                  disabled={currentQuestion === 0}
                  className="rounded-lg bg-gray-100 px-6 py-2.5 text-gray-700 transition-colors hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  上一题
                </button>

                <div className="text-sm text-gray-600">
                  {`已完成 ${selectedAnswers.filter((answer) => answer !== null).length} / ${questions.length}`}
                </div>

                {currentQuestion === questions.length - 1 ? (
                  <button
                    onClick={() => void handleSubmit()}
                    className="rounded-lg bg-emerald-500 px-6 py-2.5 text-white transition-colors hover:bg-emerald-600"
                  >
                    提交答卷
                  </button>
                ) : (
                  <button
                    onClick={() => setCurrentQuestion(Math.min(questions.length - 1, currentQuestion + 1))}
                    className="rounded-lg bg-emerald-500 px-6 py-2.5 text-white transition-colors hover:bg-emerald-600"
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
