import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser, DBSession
from app.core.response import success
from app.infra.ai.agent_manager import AgentManager
from app.infra.ai.agent_skills import list_skills
from app.modules.ai_chat.schemas import (
    AIChatMessageSendRequest,
    AIChatSessionCreateRequest,
    LearningEvaluationWorkflowRequest,
    LearningPathWorkflowRequest,
    MonthlyReportWorkflowRequest,
    ResourceGenerationWorkflowRequest,
    StudyPlanWorkflowRequest,
    StudentProfileWorkflowRequest,
    TutorQAWorkflowRequest,
)
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
                "code": skill.code,
                "name": skill.name,
                "summary": skill.summary,
                "responsibilities": list(skill.responsibilities),
                "supported_tools": list(skill.supported_tools),
                "chat_enabled": skill.chat_enabled,
                "standalone_enabled": skill.standalone_enabled,
            }
            for skill in list_skills()
        ]
    )


@router.get("/ai/chat/sessions")
async def list_chat_sessions(
    current_user: CurrentUser,
    session: DBSession,
):
    service = AIChatService()
    result = await service.list_user_sessions(session, int(current_user.sub))
    return success(data=result)


@router.post("/ai/chat/sessions")
async def create_chat_session(
    payload: AIChatSessionCreateRequest,
    current_user: CurrentUser,
    session: DBSession,
):
    service = AIChatService()
    result = await service.create_session(session, int(current_user.sub), payload)
    return success(data=result, message="Chat session created.")


@router.get("/ai/chat/sessions/{session_id}/messages")
async def list_session_messages(
    session_id: int,
    current_user: CurrentUser,
    session: DBSession,
):
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
