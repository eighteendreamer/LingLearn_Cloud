import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser, DBSession
from app.core.response import success
from app.modules.ai_chat.schemas import (
    AIChatMessageSendRequest,
    AIChatSessionCreateRequest,
    LearningPathWorkflowRequest,
    LearningEvaluationWorkflowRequest,
    MonthlyReportWorkflowRequest,
    ResourceGenerationWorkflowRequest,
    StudyPlanWorkflowRequest,
    StudentProfileWorkflowRequest,
    TutorQAWorkflowRequest,
)
from app.infra.ai.agent_manager import AgentManager
from app.modules.ai_chat.service import AIChatService
from app.modules.learning_path.schemas import LearningPathGenerateRequest, SkillProfileGenerateRequest
from app.modules.learning_path.service import LearningPathService
from app.modules.report.service import ReportService

router = APIRouter()


@router.get("/ai/agents")
async def list_ai_agents():
    return success(
        data=[
            {
                "code": "user_interaction",
                "name": "用户交互智能体",
                "responsibilities": ["多轮对话交互", "流式输出展示", "资源收藏管理"],
            },
            {
                "code": "feature_extraction",
                "name": "特征抽取智能体",
                "responsibilities": ["对话内容分析", "六维态内容生成", "画像质量校验"],
            },
            {
                "code": "resource_generation",
                "name": "资源生成智能体",
                "responsibilities": ["学习目标分析", "路径智能规划", "动态调整优化"],
            },
            {
                "code": "study_plan",
                "name": "学习计划智能体",
                "responsibilities": ["自动批改评分", "掌握度判定", "学习报告生成"],
            },
            {
                "code": "tutor_qa",
                "name": "智能答疑智能体",
                "responsibilities": ["多轮对话答疑", "思维引导辅导", "错题讲题分析"],
            },
            {
                "code": "learning_evaluation",
                "name": "学习评估智能体",
                "responsibilities": ["学习效果诊断", "学情画像生成", "迭代优化建议"],
            },
        ]
    )


@router.get("/ai/chat/sessions")
async def list_chat_sessions(
    current_user: CurrentUser,
    session: DBSession,
):
    """List user's AI chat sessions"""
    service = AIChatService()
    result = await service.list_user_sessions(session, int(current_user.sub))
    return success(data=result)


@router.post("/ai/chat/sessions")
async def create_chat_session(
    payload: AIChatSessionCreateRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    """Create a new AI chat session"""
    service = AIChatService()
    result = await service.create_session(session, int(current_user.sub), payload)
    return success(data=result, message="Chat session created.")


@router.get("/ai/chat/sessions/{session_id}/messages")
async def list_session_messages(
    session_id: int,
    current_user: CurrentUser,
    session: DBSession,
):
    """Get all messages in a chat session"""
    service = AIChatService()
    result = await service.list_session_messages(session, int(current_user.sub), session_id)
    return success(data=result)


@router.post("/ai/chat/sessions/{session_id}/messages")
async def send_message(
    session_id: int,
    payload: AIChatMessageSendRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    """Send a message to AI assistant and get response"""
    service = AIChatService()
    result = await service.send_message(session, int(current_user.sub), session_id, payload)
    return success(data=result)


@router.post("/ai/chat/sessions/{session_id}/messages/stream")
async def stream_message(
    session_id: int,
    payload: AIChatMessageSendRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    """Send a message and stream assistant tokens as Server-Sent Events."""
    service = AIChatService()

    async def event_stream():
        async for event in service.stream_message_events(session, int(current_user.sub), session_id, payload):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/ai/workflows/student-profile")
async def run_student_profile_workflow(
    payload: StudentProfileWorkflowRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    service = LearningPathService()
    result = await service.generate_skill_profile(
        session,
        int(current_user.sub),
        SkillProfileGenerateRequest(
            source_type=payload.source_type,
            source_ref_id=payload.source_ref_id,
        ),
    )
    return success(data=result, message="Student profile workflow completed.")


@router.post("/ai/workflows/learning-path")
async def run_learning_path_workflow(
    payload: LearningPathWorkflowRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    service = LearningPathService()
    result = await service.generate_learning_path(
        session,
        int(current_user.sub),
        LearningPathGenerateRequest(
            target_role=payload.target_role,
            current_level=payload.current_level,
        ),
    )
    return success(data=result, message="Learning path workflow completed.")


@router.post("/ai/workflows/monthly-report")
async def run_monthly_report_workflow(
    payload: MonthlyReportWorkflowRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    service = ReportService()
    result = await service.generate_report(session, int(current_user.sub), payload.report_month)
    return success(data=result, message="Monthly report workflow completed.")


@router.post("/ai/workflows/resource-generation")
async def run_resource_generation_workflow(
    payload: ResourceGenerationWorkflowRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    manager = AgentManager()
    result = await manager.run_resource_generation_agent(
        session,
        user_id=int(current_user.sub),
        learning_goal=payload.learning_goal,
        current_level=payload.current_level,
        learning_history=payload.learning_history,
        profile=payload.profile,
    )
    return success(data=result, message="Resource generation agent completed.")


@router.post("/ai/workflows/study-plan")
async def run_study_plan_workflow(
    payload: StudyPlanWorkflowRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    manager = AgentManager()
    result = await manager.run_study_plan_agent(
        session,
        user_id=int(current_user.sub),
        evaluation_type=payload.evaluation_type,
        data=payload.data,
    )
    return success(data=result, message="Study plan agent completed.")


@router.post("/ai/workflows/tutor-qa")
async def run_tutor_qa_workflow(
    payload: TutorQAWorkflowRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    manager = AgentManager()
    result = await manager.run_tutor_qa_agent(
        session,
        user_id=int(current_user.sub),
        question_id=payload.question_id,
        question_content=payload.question_content,
        user_answer=payload.user_answer,
        correct_answer=payload.correct_answer,
    )
    return success(data=result, message="Tutor QA agent completed.")


@router.post("/ai/workflows/learning-evaluation")
async def run_learning_evaluation_workflow(
    payload: LearningEvaluationWorkflowRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    manager = AgentManager()
    result = await manager.run_learning_evaluation_agent(
        session,
        user_id=int(current_user.sub),
        month=payload.month,
        learning_data=payload.learning_data,
        path_progress=payload.path_progress,
    )
    return success(data=result, message="Learning evaluation agent completed.")
