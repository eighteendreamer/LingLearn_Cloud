"""
AI Agent Manager - six agents unified orchestration entry.
"""
from __future__ import annotations

import logging
from datetime import date
from typing import Any

from langchain_core.messages import AIMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import utc_now_naive
from app.db.session import get_session_factory
from app.infra.ai.agent_data_context import AgentDatabaseContextBuilder
from app.infra.ai.agent_skills import (
    FEATURE_EXTRACTION_SKILL,
    LEARNING_EVALUATION_SKILL,
    RESOURCE_GENERATION_SKILL,
    STUDY_PLAN_SKILL,
    TUTOR_QA_SKILL,
    USER_INTERACTION_SKILL,
)
from app.infra.ai.agent_tools import default_tool_keys_for_skill
from app.infra.ai.context_builder import UserLearningContextBuilder
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

logger = logging.getLogger(__name__)


def _safe_transcript(messages: list[Any]) -> list[dict[str, str]]:
    transcript: list[dict[str, str]] = []
    for message in messages[-10:]:
        if isinstance(message, dict):
            role = str(message.get("role") or message.get("type") or "message")
            content = str(message.get("content", ""))
        else:
            role = str(getattr(message, "role", None) or getattr(message, "type", None) or "message")
            content = str(getattr(message, "content", message))
        transcript.append({"role": role, "content": content})
    return transcript


class AgentManager:
    """Coordinates the six LingLearn agents."""

    def __init__(self) -> None:
        self.runtime = LangGraphRuntime()
        self.llm = self.runtime.get_llm()
        self.context_builder = UserLearningContextBuilder()
        self.agent_data_builder = AgentDatabaseContextBuilder()
        self.session_factory = get_session_factory()

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
        account_snapshot: dict[str, Any] | None = None,
    ) -> UserInteractionState:
        state: UserInteractionState = {
            "user_id": user_id,
            "session_id": session_id,
            "scene_code": scene_code,
            "messages": messages,
            "context": context,
            "account_snapshot": account_snapshot or {},
            "intent": {},
            "routing_plan": {},
            "selected_skills": [],
            "tool_plan": {},
            "resource_actions": [],
            "delegated_results": {},
            "delegate_runner": lambda skill_code, interaction_state: self._run_delegated_skill(
                db_session,
                skill_code=skill_code,
                interaction_state=interaction_state,
            ),
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
                "routing_plan": result["routing_plan"],
                "selected_skills": result["selected_skills"],
                "tool_plan": result["tool_plan"],
                "resource_actions": result["resource_actions"],
                "delegated_results": result["delegated_results"],
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
        tool_context: dict[str, Any] | None = None,
    ) -> FeatureExtractionState:
        state: FeatureExtractionState = {
            "user_id": user_id,
            "source_type": source_type,
            "source_ref_id": source_ref_id,
            "conversations": conversations or [],
            "assessment_data": assessment_data or {},
            "tool_context": tool_context or {},
            "dialogue_analysis": {},
            "six_dimension_profile": {},
            "quality_report": {},
            "status": "init",
        }
        db_tool_context = await self.agent_data_builder.build_for_skill(
            db_session,
            skill_code=FEATURE_EXTRACTION_SKILL.code,
            user_id=user_id,
            tool_keys=default_tool_keys_for_skill(FEATURE_EXTRACTION_SKILL.code),
            source_type=source_type,
            source_ref_id=source_ref_id,
            latest_user_text=self._latest_text_from_conversations(conversations),
            recent_transcript=_safe_transcript(conversations or []),
        )
        state["tool_context"] = {**db_tool_context, **(tool_context or {})}
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
        tool_context: dict[str, Any] | None = None,
    ) -> ResourceGenerationState:
        state: ResourceGenerationState = {
            "user_id": user_id,
            "learning_goal": learning_goal,
            "current_level": current_level,
            "learning_history": learning_history or {},
            "profile": profile or {},
            "tool_context": tool_context or {},
            "goal_analysis": {},
            "path_plan": {},
            "generated_content": {},
            "adjustments": {},
            "quality_score": 0,
            "status": "init",
        }
        db_tool_context = await self.agent_data_builder.build_for_skill(
            db_session,
            skill_code=RESOURCE_GENERATION_SKILL.code,
            user_id=user_id,
            tool_keys=default_tool_keys_for_skill(RESOURCE_GENERATION_SKILL.code),
            latest_user_text=learning_goal,
        )
        state["tool_context"] = {**db_tool_context, **(tool_context or {})}
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
        tool_context: dict[str, Any] | None = None,
    ) -> StudyPlanState:
        state: StudyPlanState = {
            "user_id": user_id,
            "evaluation_type": evaluation_type,
            "data": data,
            "tool_context": tool_context or {},
            "grading": {},
            "mastery": {},
            "report": {},
            "status": "init",
        }
        db_tool_context = await self.agent_data_builder.build_for_skill(
            db_session,
            skill_code=STUDY_PLAN_SKILL.code,
            user_id=user_id,
            tool_keys=default_tool_keys_for_skill(STUDY_PLAN_SKILL.code),
            latest_user_text=str(data.get("latest_message") or ""),
            evaluation_type=evaluation_type,
        )
        state["tool_context"] = {**db_tool_context, **(tool_context or {})}
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
        tool_context: dict[str, Any] | None = None,
    ) -> TutorQAState:
        state: TutorQAState = {
            "user_id": user_id,
            "question_id": question_id,
            "question_content": question_content,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "conversation_history": conversation_history or [],
            "tool_context": tool_context or {},
            "intent": {},
            "guidance": "",
            "wrong_question_analysis": {},
            "answer": "",
            "status": "init",
        }
        db_tool_context = await self.agent_data_builder.build_for_skill(
            db_session,
            skill_code=TUTOR_QA_SKILL.code,
            user_id=user_id,
            tool_keys=default_tool_keys_for_skill(TUTOR_QA_SKILL.code),
            latest_user_text=question_content,
            recent_transcript=_safe_transcript(conversation_history or []),
            session_id=None,
            user_answer=user_answer,
            correct_answer=correct_answer,
        )
        state["tool_context"] = {**db_tool_context, **(tool_context or {})}
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
        tool_context: dict[str, Any] | None = None,
    ) -> LearningEvaluationState:
        state: LearningEvaluationState = {
            "user_id": user_id,
            "month": month,
            "learning_data": learning_data,
            "path_progress": path_progress or {},
            "tool_context": tool_context or {},
            "diagnosis": {},
            "learner_portrait": {},
            "optimization": {},
            "report_content": {},
            "recommendations": [],
            "status": "init",
        }
        db_tool_context = await self.agent_data_builder.build_for_skill(
            db_session,
            skill_code=LEARNING_EVALUATION_SKILL.code,
            user_id=user_id,
            tool_keys=default_tool_keys_for_skill(LEARNING_EVALUATION_SKILL.code),
            latest_user_text=str(learning_data.get("latest_message") or ""),
            month=month,
        )
        state["tool_context"] = {**db_tool_context, **(tool_context or {})}
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
        try:
            account_snapshot = await self.context_builder.build(db_session, user_id)
        except Exception:
            account_snapshot = {}
        frontend_page_context = self._extract_page_context(context)
        interaction_tool_context = await self.agent_data_builder.build_for_skill(
            db_session,
            skill_code=USER_INTERACTION_SKILL.code,
            user_id=user_id,
            tool_keys=default_tool_keys_for_skill(USER_INTERACTION_SKILL.code),
            session_id=session_id,
            latest_user_text=self._latest_user_text(messages),
            recent_transcript=_safe_transcript(messages),
        )
        interaction_tool_context.update(self._build_page_tool_context(frontend_page_context))

        merged_context = {
            **account_snapshot,
            **context,
            "page_context": frontend_page_context,
            "user_interaction_context": interaction_tool_context,
        }
        result = await self.run_user_interaction(
            db_session,
            user_id=user_id,
            session_id=session_id,
            scene_code=scene_code,
            messages=messages,
            context=merged_context,
            account_snapshot=account_snapshot,
        )
        return {
            **result,
            "account_snapshot": account_snapshot,
            "messages": [*messages, AIMessage(content=result["response"])],
        }

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
            result = await self.run_feature_extraction(
                db_session,
                user_id=user_id,
                source_type=evaluation_type,
                source_ref_id=data.get("snapshot_id"),
                assessment_data=data,
            )
            return {
                "scores": result["six_dimension_profile"],
                "report": result["quality_report"],
                **result,
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

    async def _run_delegated_skill(
        self,
        db_session: AsyncSession,
        *,
        skill_code: str,
        interaction_state: UserInteractionState,
    ) -> dict[str, Any] | None:
        latest_user_text = self._latest_user_text(interaction_state["messages"])
        account_snapshot = interaction_state.get("account_snapshot") or {}
        requested_tool_keys = (
            interaction_state.get("tool_plan", {}).get(skill_code)
            or default_tool_keys_for_skill(skill_code)
        )
        tool_context = await self._build_database_tool_context(
            db_session,
            skill_code=skill_code,
            tool_keys=requested_tool_keys,
            interaction_state=interaction_state,
        )

        if skill_code == RESOURCE_GENERATION_SKILL.code:
            learning_goal = self._augment_learning_goal_with_page_context(
                latest_user_text or self._fallback_learning_goal(account_snapshot),
                interaction_state.get("context"),
            )
            result = await self.run_resource_generation_agent(
                db_session,
                user_id=interaction_state["user_id"],
                learning_goal=learning_goal,
                current_level=self._infer_current_level(account_snapshot),
                learning_history={
                    "recent_courses": account_snapshot.get("recent_courses"),
                    "practice_summary": account_snapshot.get("practice_summary"),
                    "latest_assessment": account_snapshot.get("latest_assessment"),
                },
                profile=account_snapshot.get("profile") or {},
                tool_context=tool_context,
            )
            return {
                "tool_context": tool_context,
                "goal_analysis": result["goal_analysis"],
                "path_plan": result["path_plan"],
                "generated_content": result["generated_content"],
                "adjustments": result["adjustments"],
            }

        if skill_code == STUDY_PLAN_SKILL.code:
            result = await self.run_study_plan_agent(
                db_session,
                user_id=interaction_state["user_id"],
                evaluation_type="chat_assessment",
                data={
                    "latest_message": latest_user_text,
                    "scene_code": interaction_state["scene_code"],
                    "account_snapshot": account_snapshot,
                },
                tool_context=tool_context,
            )
            return {
                "tool_context": tool_context,
                "grading": result["grading"],
                "mastery": result["mastery"],
                "report": result["report"],
            }

        if skill_code == TUTOR_QA_SKILL.code:
            result = await self.run_tutor_qa_agent(
                db_session,
                user_id=interaction_state["user_id"],
                question_content=latest_user_text,
                conversation_history=interaction_state["messages"],
                tool_context=tool_context,
            )
            return {
                "tool_context": tool_context,
                "intent": result["intent"],
                "guidance": result["guidance"],
                "answer": result["answer"],
            }

        if skill_code == LEARNING_EVALUATION_SKILL.code:
            result = await self.run_learning_evaluation_agent(
                db_session,
                user_id=interaction_state["user_id"],
                month=date.today().strftime("%Y-%m"),
                learning_data={
                    "latest_message": latest_user_text,
                    "account_snapshot": account_snapshot,
                },
                path_progress=account_snapshot.get("active_learning_path") or {},
                tool_context=tool_context,
            )
            return {
                "tool_context": tool_context,
                "diagnosis": result["diagnosis"],
                "learner_portrait": result["learner_portrait"],
                "optimization": result["optimization"],
                "report_content": result["report_content"],
                "recommendations": result["recommendations"],
            }

        return None

    async def _build_database_tool_context(
        self,
        db_session: AsyncSession,
        *,
        skill_code: str,
        tool_keys: list[str],
        interaction_state: UserInteractionState,
    ) -> dict[str, Any]:
        latest_user_text = self._latest_user_text(interaction_state["messages"])
        recent_transcript = _safe_transcript(interaction_state["messages"])
        return await self.agent_data_builder.build_for_skill(
            db_session,
            skill_code=skill_code,
            user_id=interaction_state["user_id"],
            tool_keys=tool_keys,
            session_id=interaction_state.get("session_id"),
            latest_user_text=latest_user_text,
            recent_transcript=recent_transcript,
            evaluation_type="chat_assessment" if skill_code == STUDY_PLAN_SKILL.code else None,
            month=date.today().strftime("%Y-%m") if skill_code == LEARNING_EVALUATION_SKILL.code else None,
        ) | self._build_page_tool_context(interaction_state.get("context", {}).get("page_context"))

    def _build_tool_context(
        self,
        *,
        skill_code: str,
        tool_keys: list[str],
        interaction_state: UserInteractionState,
    ) -> dict[str, Any]:
        account_snapshot = interaction_state.get("account_snapshot") or {}
        latest_user_text = self._latest_user_text(interaction_state["messages"])
        recent_transcript = _safe_transcript(interaction_state["messages"])

        return {
            tool_key: self._execute_virtual_tool(
                tool_key=tool_key,
                skill_code=skill_code,
                latest_user_text=latest_user_text,
                account_snapshot=account_snapshot,
                interaction_state=interaction_state,
                recent_transcript=recent_transcript,
            )
            for tool_key in tool_keys
        }

    def _execute_virtual_tool(
        self,
        *,
        tool_key: str,
        skill_code: str,
        latest_user_text: str,
        account_snapshot: dict[str, Any],
        interaction_state: UserInteractionState,
        recent_transcript: list[dict[str, str]],
    ) -> dict[str, Any]:
        profile = account_snapshot.get("profile") or {}
        latest_assessment = account_snapshot.get("latest_assessment") or {}
        latest_report = account_snapshot.get("latest_report") or {}
        recent_courses = account_snapshot.get("recent_courses") or []
        practice_summary = account_snapshot.get("practice_summary") or {}
        active_learning_path = account_snapshot.get("active_learning_path") or {}
        latest_skill_profile = account_snapshot.get("latest_skill_profile") or {}

        if tool_key == "workflow-router":
            return {
                "scene_code": interaction_state["scene_code"],
                "latest_user_text": latest_user_text,
                "skill_code": skill_code,
            }
        if tool_key == "learning-context-reader":
            return {
                "display_name": profile.get("display_name"),
                "learning_goal": profile.get("learning_goal"),
                "profession": profile.get("profession"),
                "streak_days": profile.get("streak_days"),
                "total_learning_minutes": profile.get("total_learning_minutes"),
            }
        if tool_key == "session-memory-reader":
            return {"recent_transcript": recent_transcript[-6:]}
        if tool_key == "favorite-resource-manager":
            return {"supports_favorite_action": True, "latest_user_text": latest_user_text}
        if tool_key == "dialogue-evidence-reader":
            return {"dialogue_evidence": recent_transcript[-8:], "latest_question": latest_user_text}
        if tool_key == "six-dimension-profile-generator":
            return {
                "dimensions": ["knowledge", "logic", "expression", "habit", "motivation", "reflection"],
                "latest_assessment": latest_assessment,
                "practice_summary": practice_summary,
            }
        if tool_key == "image-quality-validator":
            return {"supported": True, "notes": "Image validation context available."}
        if tool_key == "assessment-snapshot-reader":
            return latest_assessment
        if tool_key == "course-progress-reader":
            return {"recent_courses": recent_courses}
        if tool_key == "practice-history-reader":
            return practice_summary
        if tool_key == "learning-path-reader":
            return active_learning_path
        if tool_key == "resource-candidate-reader":
            return {
                "course_topics": [item.get("title") for item in recent_courses[:3]],
                "goal": profile.get("learning_goal"),
                "weak_signals": latest_assessment,
            }
        if tool_key == "learning-goal-analyzer":
            return {
                "goal": latest_user_text or profile.get("learning_goal"),
                "current_level": self._infer_current_level(account_snapshot),
                "active_learning_path": active_learning_path,
            }
        if tool_key == "mastery-scorer":
            return {
                "estimated_level": self._infer_current_level(account_snapshot),
                "average_score": latest_assessment.get("average_score") or practice_summary.get("average_score"),
                "correct_rate": latest_assessment.get("correct_rate"),
            }
        if tool_key == "study-report-writer":
            return {"latest_report_summary": latest_report.get("ai_summary"), "latest_message": latest_user_text}
        if tool_key == "question-intent-parser":
            return {"question": latest_user_text, "scene_code": interaction_state["scene_code"]}
        if tool_key == "socratic-hint-builder":
            return {"strategy": "先追问思路，再分步提示，最后总结关键点。"}
        if tool_key == "wrong-question-reader":
            return {"latest_question": latest_user_text, "known_wrong_question_context": None}
        if tool_key == "concept-example-builder":
            return {"example_style": "使用贴近编程学习场景的短例子。"}
        if tool_key == "assessment-trend-reader":
            return {"latest_assessment": latest_assessment, "latest_report": latest_report}
        if tool_key == "monthly-report-reader":
            return latest_report
        if tool_key == "learner-portrait-writer":
            return {
                "profile": profile,
                "latest_skill_profile": latest_skill_profile,
                "latest_report": latest_report,
            }
        if tool_key == "optimization-suggester":
            return {
                "path_progress": active_learning_path.get("progress_percent"),
                "latest_score": latest_assessment.get("average_score"),
                "streak_days": profile.get("streak_days"),
            }
        if tool_key == "response-style-planner":
            return {
                "style": "markdown",
                "tone": "friendly_direct",
                "reply_granularity": "actionable",
            }
        return {}

    @staticmethod
    def _extract_page_context(context: dict[str, Any] | None) -> dict[str, Any]:
        if not isinstance(context, dict):
            return {}
        page_context = context.get("page_context")
        return page_context if isinstance(page_context, dict) else {}

    @staticmethod
    def _build_page_tool_context(page_context: dict[str, Any] | None) -> dict[str, Any]:
        if not isinstance(page_context, dict) or not page_context:
            return {}

        route = str(page_context.get("route") or "")
        actions = page_context.get("available_actions")
        if not isinstance(actions, list):
            actions = []

        current_video = page_context.get("current_video")
        if not isinstance(current_video, dict):
            current_video = None

        return {
            "page-context-reader": {
                "route": route,
                "page_type": page_context.get("page_type"),
                "page_title": page_context.get("page_title"),
                "summary": page_context.get("summary"),
                "current_video": current_video,
                "available_actions": actions,
                "metadata": page_context.get("metadata") if isinstance(page_context.get("metadata"), dict) else {},
            },
            "page-action-planner": {
                "route": route,
                "available_actions": actions,
                "current_video_title": current_video.get("title") if current_video else None,
            },
        }

    @staticmethod
    def _latest_user_text(messages: list[Any]) -> str:
        for message in reversed(messages):
            role = getattr(message, "type", None) or getattr(message, "role", None) or ""
            if role in {"human", "user"}:
                return str(getattr(message, "content", message))
            if isinstance(message, dict) and (message.get("role") == "user" or message.get("type") == "user"):
                return str(message.get("content", ""))
        return ""

    @staticmethod
    def _infer_current_level(account_snapshot: dict[str, Any]) -> str:
        skill_profile = account_snapshot.get("latest_skill_profile") or {}
        total_score = float(skill_profile.get("total_score") or 0)
        if total_score >= 85:
            return "advanced"
        if total_score >= 68:
            return "intermediate"
        return "beginner"

    @staticmethod
    def _fallback_learning_goal(account_snapshot: dict[str, Any]) -> str:
        profile = account_snapshot.get("profile") or {}
        return str(profile.get("learning_goal") or "??????????????")

    @classmethod
    def _augment_learning_goal_with_page_context(
        cls,
        learning_goal: str,
        context: dict[str, Any] | None,
    ) -> str:
        goal = (learning_goal or "").strip()
        page_context = cls._extract_page_context(context)
        current_video = page_context.get("current_video")
        if not isinstance(current_video, dict) or not current_video.get("title"):
            return goal

        title = str(current_video.get("title") or "").strip()
        category = str(current_video.get("category_name") or "").strip()
        summary = str(current_video.get("summary") or "").strip()
        details = [f"Current video: {title}"]
        if category:
            details.append(f"Category: {category}")
        if summary:
            details.append(f"Summary: {summary}")
        details.append("Please prioritize same-topic practice generation, study path suggestions, and next-page actions.")
        return f"{goal}\n\n" + "\n".join(details)

    @staticmethod
    def _latest_text_from_conversations(conversations: list[Any] | None) -> str:
        transcript = _safe_transcript(conversations or [])
        for item in reversed(transcript):
            if item["role"] in {"user", "human"}:
                return item["content"]
        return transcript[-1]["content"] if transcript else ""

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
        workflow_run_id = await self._create_workflow_run(
            workflow_type=workflow_type,
            user_id=user_id,
            biz_type=biz_type,
            biz_id=biz_id,
            input_json=input_json,
        )
        try:
            result = await agent_run()
            if workflow_run_id is not None:
                await self._update_workflow_run(
                    workflow_run_id,
                    status="success",
                    output_json=output_builder(result),
                )
            return result
        except Exception as exc:
            if workflow_run_id is not None:
                await self._update_workflow_run(
                    workflow_run_id,
                    status="failed",
                    error_message=str(exc),
                )
            raise

    async def _create_workflow_run(
        self,
        workflow_type: str,
        user_id: int,
        biz_type: str | None,
        biz_id: int | None,
        input_json: dict[str, Any],
    ) -> int | None:
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
        try:
            async with self.session_factory() as session:
                session.add(workflow_run)
                await session.flush()
                workflow_run_id = workflow_run.id
                await session.commit()
                return workflow_run_id
        except Exception:
            logger.exception("Failed to create AI workflow run: workflow_type=%s user_id=%s", workflow_type, user_id)
            return None

    async def _update_workflow_run(
        self,
        workflow_run_id: int,
        status: str,
        output_json: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        try:
            async with self.session_factory() as session:
                workflow_run = await session.get(AIWorkflowRun, workflow_run_id)
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
                await session.flush()
                await session.commit()
        except Exception:
            logger.exception("Failed to update AI workflow run: workflow_run_id=%s status=%s", workflow_run_id, status)
            return
