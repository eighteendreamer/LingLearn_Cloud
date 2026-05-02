import { apiRequest } from "./api";
import type {
  LearningPathGeneratePayload,
  MonthlyReportResponse,
  PracticeAnswerResponse,
  PracticeQuestionResponse,
  PracticeSessionResponse,
  PracticeSessionResultResponse,
  PracticeSessionSubmitResponse,
  QuestionBankResponse,
  SkillSnapshotResponse,
  UserLearningPathResponse,
  VideoPracticeGeneratePayload,
  VideoPracticeGenerateResponse,
} from "./types";

export async function fetchQuestionBanks() {
  const page = await apiRequest<{ list: QuestionBankResponse[] }>("/practice/banks?page=1&page_size=20");
  return page.list;
}

export async function fetchPracticeQuestions(bankId: number) {
  return apiRequest<PracticeQuestionResponse[]>(`/practice/banks/${bankId}/questions`);
}

export async function submitPracticeSession(sessionId: number) {
  return apiRequest<PracticeSessionSubmitResponse>(`/practice/sessions/${sessionId}/submit`, {
    method: "POST",
  });
}

export async function fetchPracticeSession(sessionId: number) {
  return apiRequest<PracticeSessionResponse>(`/practice/sessions/${sessionId}`);
}

export async function fetchPracticeResult(sessionId: number) {
  return apiRequest<PracticeSessionResultResponse>(`/practice/sessions/${sessionId}/result`);
}

export async function generateVideoPractice(payload: VideoPracticeGeneratePayload) {
  return apiRequest<VideoPracticeGenerateResponse>("/practice/video-generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function normalizePracticeAnswer(response: PracticeAnswerResponse): PracticeAnswerResponse {
  return {
    ...response,
    score: response.score ?? response.earned_score ?? 0,
    earned_score: response.earned_score ?? response.score ?? 0,
    correct_option_ids: response.correct_option_ids ?? [],
  };
}

export async function fetchLatestSkillProfile() {
  return apiRequest<SkillSnapshotResponse | null>("/users/me/skill-profile/latest");
}

export async function generateSkillProfile() {
  return apiRequest<SkillSnapshotResponse>("/users/me/skill-profile/generate", {
    method: "POST",
    body: JSON.stringify({ source_type: "assessment" }),
  });
}

export async function fetchOrGenerateSkillProfile() {
  const profile = await fetchLatestSkillProfile();
  return profile ?? generateSkillProfile();
}

export async function fetchActiveLearningPath() {
  return apiRequest<UserLearningPathResponse | null>("/users/me/learning-paths/active");
}

export async function generateLearningPath(payload: LearningPathGeneratePayload = {}) {
  return apiRequest<UserLearningPathResponse>("/users/me/learning-paths/generate", {
    method: "POST",
    body: JSON.stringify({ current_level: "beginner", ...payload }),
  });
}

export async function fetchOrGenerateLearningPath() {
  const path = await fetchActiveLearningPath();
  return path ?? generateLearningPath();
}

export async function updateLearningPathNode(
  userPathId: number,
  nodeId: number,
  status: string,
  progressPercent: number
) {
  return apiRequest<UserLearningPathResponse>(`/users/me/learning-paths/${userPathId}/nodes/${nodeId}`, {
    method: "PATCH",
    body: JSON.stringify({ status, progress_percent: progressPercent }),
  });
}

export async function fetchMonthlyReports() {
  return apiRequest<MonthlyReportResponse[]>("/users/me/reports");
}

export async function fetchMonthlyReport(reportMonth: string) {
  return apiRequest<MonthlyReportResponse>(`/users/me/reports/${reportMonth}`);
}

export async function generateMonthlyReport(reportMonth: string) {
  return apiRequest<MonthlyReportResponse>(`/users/me/reports/${reportMonth}/generate`, {
    method: "POST",
  });
}

export async function exportMonthlyReport(reportMonth: string) {
  return apiRequest(`/users/me/reports/${reportMonth}/export`, {
    method: "POST",
  });
}
