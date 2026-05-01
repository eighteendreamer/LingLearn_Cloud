"""
AI Agent Manager - 六大 LangGraph 智能体统一编排入口。
"""
from typing import Any

from langchain_core.messages import AIMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import utc_now_naive
from app.infra.ai.graphs.six_agents import (
    FeatureExtractionAgent,
    FeatureExtractionState,
    LearningEvaluationAgent,
    LearningEvaluationState,
    ResourceGenerationAgent,
    ResourceGenerationState,
    StudyPlanAgent,
    StudyPlanState,
    TutorQAAgent,
    TutorQAState,
    UserInteractionAgent,
    UserInteractionState,
)
from app.infra.ai.langgraph_runtime import LangGraphRuntime
from app.modules.ai_chat.workflow_models import AIWorkflowRun


class AgentManager:
    """Coordinates the six learning-domain LangGraph agents."""

    def __init__(self) -> None:
        self.runtime = LangGraphRuntime()
        self.llm = self.runtime.get_llm()

        self.user_interaction_agent = UserInteractionAgent(self.llm)
        self.feature_extraction_agent = FeatureExtractionAgent(self.llm)
        self.resource_generation_agent = ResourceGenerationAgent(self.llm)
        self.study_plan_agent = StudyPlanAgent(self.llm)
        self.tutor_qa_agent = TutorQAAgent(self.llm)
        self.learning_evaluation_agent = LearningEvaluationAgent(self.llm)

    async def run_user_interaction(
        self,
        db_session: AsyncSession,
        *,
        user_id: int,
        session_id: int | None,
        scene_code: str,
        messages: list[Any],
        context: dict[str, Any],
    ) -> UserInteractionState:
        state: UserInteractionState = {
            "user_id": user_id,
            "session_id": session_id,
            "scene_code": scene_code,
            "messages": messages,
            "context": context,
            "intent": {},
            "resource_actions": [],
            "response": "",
            "status": "init",
        }
        return await self._execute_agent(
            db_session,
            workflow_type="agent_user_interaction",
            user_id=user_id,
            biz_type="chat_session",
            biz_id=session_id,
            input_json={"scene_code": scene_code, "message_count": len(messages)},
            agent_run=lambda: self.user_interaction_agent.run(state),
            output_builder=lambda result: {
                "intent": result["intent"],
                "resource_actions": result["resource_actions"],
                "response": result["response"],
            },
        )

    async def run_feature_extraction(
        self,
        db_session: AsyncSession,
        *,
        user_id: int,
        source_type: str,
        source_ref_id: int | None,
        conversations: list[Any] | None = None,
        assessment_data: dict[str, Any] | None = None,
    ) -> FeatureExtractionState:
        state: FeatureExtractionState = {
            "user_id": user_id,
            "source_type": source_type,
            "source_ref_id": source_ref_id,
            "conversations": conversations or [],
            "assessment_data": assessment_data or {},
            "dialogue_analysis": {},
            "six_dimension_profile": {},
            "quality_report": {},
            "status": "init",
        }
        return await self._execute_agent(
            db_session,
            workflow_type="agent_feature_extraction",
            user_id=user_id,
            biz_type=source_type,
            biz_id=source_ref_id,
            input_json={"source_type": source_type, "source_ref_id": source_ref_id},
            agent_run=lambda: self.feature_extraction_agent.run(state),
            output_builder=lambda result: {
                "dialogue_analysis": result["dialogue_analysis"],
                "six_dimension_profile": result["six_dimension_profile"],
                "quality_report": result["quality_report"],
            },
        )

    async def run_resource_generation_agent(
        self,
        db_session: AsyncSession,
        *,
        user_id: int,
        learning_goal: str,
        current_level: str = "beginner",
        learning_history: dict[str, Any] | None = None,
        profile: dict[str, Any] | None = None,
    ) -> ResourceGenerationState:
        state: ResourceGenerationState = {
            "user_id": user_id,
            "learning_goal": learning_goal,
            "current_level": current_level,
            "learning_history": learning_history or {},
            "profile": profile or {},
            "goal_analysis": {},
            "path_plan": {},
            "generated_content": {},
            "adjustments": {},
            "quality_score": 0,
            "status": "init",
        }
        return await self._execute_agent(
            db_session,
            workflow_type="agent_resource_generation",
            user_id=user_id,
            biz_type="learning_goal",
            biz_id=None,
            input_json={"learning_goal": learning_goal, "current_level": current_level},
            agent_run=lambda: self.resource_generation_agent.run(state),
            output_builder=lambda result: {
                "goal_analysis": result["goal_analysis"],
                "path_plan": result["path_plan"],
                "generated_content": result["generated_content"],
                "adjustments": result["adjustments"],
                "quality_score": result["quality_score"],
            },
        )

    async def run_study_plan_agent(
        self,
        db_session: AsyncSession,
        *,
        user_id: int,
        evaluation_type: str,
        data: dict[str, Any],
    ) -> StudyPlanState:
        state: StudyPlanState = {
            "user_id": user_id,
            "evaluation_type": evaluation_type,
            "data": data,
            "grading": {},
            "mastery": {},
            "report": {},
            "status": "init",
        }
        return await self._execute_agent(
            db_session,
            workflow_type="agent_study_plan",
            user_id=user_id,
            biz_type=evaluation_type,
            biz_id=None,
            input_json={"evaluation_type": evaluation_type},
            agent_run=lambda: self.study_plan_agent.run(state),
            output_builder=lambda result: {
                "grading": result["grading"],
                "mastery": result["mastery"],
                "report": result["report"],
            },
        )

    async def run_tutor_qa_agent(
        self,
        db_session: AsyncSession,
        *,
        user_id: int,
        question_content: str,
        question_id: int | None = None,
        user_answer: str | None = None,
        correct_answer: str | None = None,
        conversation_history: list[Any] | None = None,
    ) -> TutorQAState:
        state: TutorQAState = {
            "user_id": user_id,
            "question_id": question_id,
            "question_content": question_content,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "conversation_history": conversation_history or [],
            "intent": {},
            "guidance": "",
            "wrong_question_analysis": {},
            "answer": "",
            "status": "init",
        }
        return await self._execute_agent(
            db_session,
            workflow_type="agent_tutor_qa",
            user_id=user_id,
            biz_type="question",
            biz_id=question_id,
            input_json={"question_id": question_id, "has_answer": bool(user_answer)},
            agent_run=lambda: self.tutor_qa_agent.run(state),
            output_builder=lambda result: {
                "intent": result["intent"],
                "guidance": result["guidance"],
                "wrong_question_analysis": result["wrong_question_analysis"],
                "answer": result["answer"],
            },
        )

    async def run_learning_evaluation_agent(
        self,
        db_session: AsyncSession,
        *,
        user_id: int,
        month: str | None,
        learning_data: dict[str, Any],
        path_progress: dict[str, Any] | None = None,
    ) -> LearningEvaluationState:
        state: LearningEvaluationState = {
            "user_id": user_id,
            "month": month,
            "learning_data": learning_data,
            "path_progress": path_progress or {},
            "diagnosis": {},
            "learner_portrait": {},
            "optimization": {},
            "report_content": {},
            "recommendations": [],
            "status": "init",
        }
        return await self._execute_agent(
            db_session,
            workflow_type="agent_learning_evaluation",
            user_id=user_id,
            biz_type="monthly_report" if month else "learning_evaluation",
            biz_id=None,
            input_json={"month": month},
            agent_run=lambda: self.learning_evaluation_agent.run(state),
            output_builder=lambda result: {
                "diagnosis": result["diagnosis"],
                "learner_portrait": result["learner_portrait"],
                "optimization": result["optimization"],
                "report_content": result["report_content"],
                "recommendations": result["recommendations"],
            },
        )

    async def run_tutor_chat(
        self,
        db_session: AsyncSession,
        user_id: int,
        session_id: int,
        scene_code: str,
        messages: list[Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        result = await self.run_user_interaction(
            db_session,
            user_id=user_id,
            session_id=session_id,
            scene_code=scene_code,
            messages=messages,
            context=context,
        )
        return {**result, "messages": [*messages, AIMessage(content=result["response"])]}

    async def run_resource_generation(
        self,
        db_session: AsyncSession,
        user_id: int,
        learning_goal: str,
    ) -> dict[str, Any]:
        return await self.run_resource_generation_agent(
            db_session,
            user_id=user_id,
            learning_goal=learning_goal,
        )

    async def run_learning_evaluation(
        self,
        db_session: AsyncSession,
        user_id: int,
        evaluation_type: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        if evaluation_type == "skill_profile":
            profile = await self.run_feature_extraction(
                db_session,
                user_id=user_id,
                source_type=evaluation_type,
                source_ref_id=data.get("snapshot_id"),
                assessment_data=data,
            )
            return {
                "scores": profile["six_dimension_profile"],
                "report": profile["quality_report"],
                **profile,
            }
        result = await self.run_study_plan_agent(
            db_session,
            user_id=user_id,
            evaluation_type=evaluation_type,
            data=data,
        )
        return {"scores": result["grading"], "report": result["report"], **result}

    async def run_supervision(
        self,
        db_session: AsyncSession,
        user_id: int,
        question_id: int,
        question_content: str,
        user_answer: str,
        correct_answer: str,
    ) -> dict[str, Any]:
        result = await self.run_tutor_qa_agent(
            db_session,
            user_id=user_id,
            question_id=question_id,
            question_content=question_content,
            user_answer=user_answer,
            correct_answer=correct_answer,
        )
        return {
            "analysis": result["wrong_question_analysis"],
            "guidance": result["guidance"],
            "answer": result["answer"],
            **result,
        }

    async def run_learning_path(
        self,
        db_session: AsyncSession,
        user_id: int,
        current_level: str,
        learning_history: dict[str, Any],
    ) -> dict[str, Any]:
        result = await self.run_resource_generation_agent(
            db_session,
            user_id=user_id,
            learning_goal="生成个性化学习路径",
            current_level=current_level,
            learning_history=learning_history,
        )
        return {
            "profile": result["goal_analysis"],
            "path": result["path_plan"],
            "optimization": result["adjustments"],
            **result,
        }

    async def run_monthly_report(
        self,
        db_session: AsyncSession,
        user_id: int,
        month: str,
        learning_data: dict[str, Any],
    ) -> dict[str, Any]:
        return await self.run_learning_evaluation_agent(
            db_session,
            user_id=user_id,
            month=month,
            learning_data=learning_data,
        )

    async def _execute_agent(
        self,
        db_session: AsyncSession,
        *,
        workflow_type: str,
        user_id: int,
        biz_type: str | None,
        biz_id: int | None,
        input_json: dict[str, Any],
        agent_run,
        output_builder,
    ):
        workflow_run = await self._create_workflow_run(
            db_session,
            workflow_type=workflow_type,
            user_id=user_id,
            biz_type=biz_type,
            biz_id=biz_id,
            input_json=input_json,
        )
        try:
            result = await agent_run()
            await self._update_workflow_run(
                db_session,
                workflow_run.id,
                status="success",
                output_json=output_builder(result),
            )
            return result
        except Exception as exc:
            await self._update_workflow_run(
                db_session,
                workflow_run.id,
                status="failed",
                error_message=str(exc),
            )
            raise

    async def _create_workflow_run(
        self,
        db_session: AsyncSession,
        workflow_type: str,
        user_id: int,
        biz_type: str | None,
        biz_id: int | None,
        input_json: dict[str, Any],
    ) -> AIWorkflowRun:
        now = utc_now_naive()
        workflow_run = AIWorkflowRun(
            workflow_type=workflow_type,
            biz_type=biz_type,
            biz_id=biz_id,
            user_id=user_id,
            input_json=input_json,
            status="running",
            started_at=now,
            created_at=now,
            updated_at=now,
        )
        db_session.add(workflow_run)
        await db_session.flush()
        return workflow_run

    async def _update_workflow_run(
        self,
        db_session: AsyncSession,
        workflow_run_id: int,
        status: str,
        output_json: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        workflow_run = await db_session.get(AIWorkflowRun, workflow_run_id)
        if not workflow_run:
            return
        workflow_run.status = status
        if output_json is not None:
            workflow_run.output_json = output_json
        if error_message:
            workflow_run.error_message = error_message
        now = utc_now_naive()
        workflow_run.finished_at = now
        workflow_run.updated_at = now
        await db_session.flush()
