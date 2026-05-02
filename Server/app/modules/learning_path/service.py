import asyncio
import json
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, InfrastructureError, NotFoundError
from app.infra.ai.agent_manager import AgentManager
from app.modules.content.repository import ContentRepository
from app.modules.learning_path.repository import LearningPathRepository
from app.modules.learning_path.schemas import (
    LearningPathActivateRequest,
    LearningPathGenerateRequest,
    LearningPathNodePracticeGenerateResponse,
    LearningPathNodeResponse,
    LearningPathNodeUpdateRequest,
    LearningPathPlanResponse,
    LearningPathPlanRouteResponse,
    LearningPathPlanStageResponse,
    LearningPathStageAssessmentResponse,
    LearningPathStageResourceResponse,
    SkillProfileGenerateRequest,
    SkillScoreResponse,
    SkillSnapshotResponse,
    UserLearningPathResponse,
)
from app.modules.practice.repository import PracticeRepository


class LearningPathService:
    def __init__(
        self,
        *,
        repository: LearningPathRepository | None = None,
        content_repository: ContentRepository | None = None,
        practice_repository: PracticeRepository | None = None,
    ) -> None:
        self.repository = repository or LearningPathRepository()
        self.content_repository = content_repository or ContentRepository()
        self.practice_repository = practice_repository or PracticeRepository()
        self.agent_manager = AgentManager()

    async def get_latest_skill_profile(self, session: AsyncSession, user_id: int):
        snapshot = await self.repository.get_latest_snapshot(session, user_id)
        return await self._build_snapshot_response(session, snapshot) if snapshot else None

    async def list_skill_profile_history(self, session: AsyncSession, user_id: int):
        snapshots = await self.repository.list_snapshots(session, user_id, limit=20)
        return [await self._build_snapshot_response(session, item) for item in snapshots]

    async def generate_skill_profile(
        self,
        session: AsyncSession,
        user_id: int,
        payload: SkillProfileGenerateRequest,
    ):
        dimensions = await self.repository.ensure_default_dimensions(session)
        scores = []
        for index, dimension in enumerate(dimensions):
            score = max(55, min(92, 72 + (index % 3) * 6 - index))
            scores.append(
                {
                    "dimension_id": dimension.id,
                    "score": float(score),
                    "percentile": min(95.0, float(score + 5)),
                    "level": "advanced" if score >= 85 else "intermediate" if score >= 70 else "foundation",
                    "insight": f"{dimension.name}表现较稳定，建议结合项目练习持续巩固。",
                }
            )
        snapshot = await self.repository.create_snapshot(
            session,
            user_id=user_id,
            source_type=payload.source_type,
            source_ref_id=payload.source_ref_id,
            scores=scores,
        )
        try:
            await self.agent_manager.run_learning_evaluation(
                session,
                user_id=user_id,
                evaluation_type="skill_profile",
                data={"snapshot_id": snapshot.id, "scores": scores},
            )
        except Exception:
            pass
        await session.commit()
        return await self._build_snapshot_response(session, snapshot)

    async def get_active_learning_path(self, session: AsyncSession, user_id: int):
        user_path = await self.repository.get_active_user_path(session, user_id)
        return await self._build_path_response(session, user_id, user_path) if user_path else None

    async def list_learning_path_history(self, session: AsyncSession, user_id: int) -> list[UserLearningPathResponse]:
        user_paths = await self.repository.list_user_paths(session, user_id, limit=12)
        return [await self._build_path_response(session, user_id, item) for item in user_paths]

    async def get_learning_path(self, session: AsyncSession, user_id: int, user_path_id: int):
        user_path = await self.repository.get_user_path(session, user_id, user_path_id)
        if not user_path:
            raise NotFoundError(message="Learning path not found.")
        return await self._build_path_response(session, user_id, user_path)

    async def generate_learning_path_plan(
        self,
        session: AsyncSession,
        user_id: int,
        payload: LearningPathGenerateRequest,
    ) -> LearningPathPlanResponse:
        snapshot = await self.repository.get_latest_snapshot(session, user_id)
        score_rows = await self.repository.list_scores(session, snapshot.id) if snapshot else []
        weak_dimensions = self._extract_weak_dimensions(score_rows)

        raw_routes: list[dict[str, Any]] = []
        raw_summary = ""
        try:
            agent_result = await self.agent_manager.run_resource_generation_agent(
                session,
                user_id=user_id,
                learning_goal=self._build_route_generation_goal(payload, weak_dimensions),
                current_level=payload.current_level,
                learning_history={
                    "snapshot_id": snapshot.id if snapshot else None,
                    "weekly_hours": payload.weekly_hours,
                },
                profile={
                    "weak_dimensions": weak_dimensions,
                    "target_role": payload.target_role,
                },
            )
            raw_summary = self._unwrap_text(agent_result.get("goal_analysis")) or self._unwrap_text(
                agent_result.get("adjustments")
            )
            parsed = self._extract_json_object(self._unwrap_text(agent_result.get("path_plan")))
            if isinstance(parsed, dict) and isinstance(parsed.get("route_options"), list):
                raw_routes = [item for item in parsed["route_options"] if isinstance(item, dict)]
        except Exception:
            raw_routes = []

        if not raw_routes:
            raw_routes = self._build_default_route_blueprints(payload, weak_dimensions)

        route_options: list[LearningPathPlanRouteResponse] = []
        for index, raw_route in enumerate(raw_routes[: payload.route_count], start=1):
            route_options.append(
                await self._normalize_route_option(
                    session,
                    user_id,
                    payload,
                    raw_route=raw_route,
                    route_index=index,
                    weak_dimensions=weak_dimensions,
                )
            )

        if not route_options:
            raise InfrastructureError(message="Failed to generate learning path options.")

        return LearningPathPlanResponse(
            planning_summary=self._normalize_planning_summary(raw_summary, payload, len(route_options)),
            route_options=route_options,
        )

    async def activate_learning_path(
        self,
        session: AsyncSession,
        user_id: int,
        payload: LearningPathActivateRequest,
    ) -> UserLearningPathResponse:
        snapshot = await self.repository.get_latest_snapshot(session, user_id)
        route = payload.selected_route
        await self.repository.deactivate_active_paths(session, user_id)
        user_path = await self.repository.create_path_with_nodes(
            session,
            user_id=user_id,
            snapshot_id=snapshot.id if snapshot else None,
            target_role=(route.title or "").strip()[:64],
            path_name=route.title[:120],
            path_description=(route.summary or "")[:500] or None,
            nodes=[
                {
                    "title": stage.title,
                    "description": stage.description,
                    "recommended_reason": stage.recommended_reason or route.fit_reason,
                    "estimated_minutes": stage.estimated_hours * 60,
                    "node_type": "stage",
                    "ai_feedback": self._encode_stage_metadata(stage),
                }
                for stage in route.stages
            ],
            ai_summary=route.fit_reason[:1000],
        )
        await session.commit()
        return await self._build_path_response(session, user_id, user_path)

    async def generate_learning_path(self, session: AsyncSession, user_id: int, payload: LearningPathGenerateRequest):
        plan = await self.generate_learning_path_plan(session, user_id, payload)
        return await self.activate_learning_path(
            session,
            user_id,
            LearningPathActivateRequest(selected_route=plan.route_options[0]),
        )

    async def update_learning_path_node(
        self,
        session: AsyncSession,
        user_id: int,
        user_path_id: int,
        node_id: int,
        payload: LearningPathNodeUpdateRequest,
    ):
        user_path = await self.repository.get_user_path(session, user_id, user_path_id)
        if not user_path:
            raise NotFoundError(message="Learning path not found.")

        updated = await self.repository.update_user_path_node(
            session,
            user_path_id,
            node_id,
            status=payload.status,
            progress_percent=payload.progress_percent,
        )
        if not updated:
            raise NotFoundError(message="Learning path node not found.")

        node_rows = await self.repository.list_user_path_nodes(session, user_path_id)
        if payload.status == "completed":
            for index, (user_node, node) in enumerate(node_rows):
                if node.id != node_id:
                    continue
                if index + 1 < len(node_rows):
                    next_user_node, next_node = node_rows[index + 1]
                    if next_user_node.status == "locked":
                        await self.repository.update_user_path_node(
                            session,
                            user_path_id,
                            next_node.id,
                            status="unlocked",
                            progress_percent=float(next_user_node.progress_percent or 0),
                        )
                break
            node_rows = await self.repository.list_user_path_nodes(session, user_path_id)

        completed_count = sum(1 for user_node, _ in node_rows if user_node.status == "completed")
        progress_percent = round(completed_count / len(node_rows) * 100, 2) if node_rows else 0
        current_node = next((node for user_node, node in node_rows if user_node.status != "completed"), None)
        await self.repository.update_user_path_progress(
            session,
            user_path_id,
            progress_percent=progress_percent,
            current_node_id=current_node.id if current_node else None,
            status="completed" if node_rows and completed_count == len(node_rows) else "active",
        )
        await session.commit()
        await session.refresh(user_path)
        return await self._build_path_response(session, user_id, user_path)

    async def generate_node_practice(
        self,
        session: AsyncSession,
        user_id: int,
        user_path_id: int,
        node_id: int,
    ) -> LearningPathNodePracticeGenerateResponse:
        user_path = await self.repository.get_user_path(session, user_id, user_path_id)
        if not user_path:
            raise NotFoundError(message="Learning path not found.")

        path = await self.repository.get_path(session, user_path.path_id)
        node_rows = await self.repository.list_user_path_nodes(session, user_path_id)
        target_pair = next(((user_node, node) for user_node, node in node_rows if node.id == node_id), None)
        if not target_pair:
            raise NotFoundError(message="Learning path node not found.")

        user_node, node = target_pair
        if user_node.status == "locked":
            raise BadRequestError(message="Please unlock this stage before generating practice.")

        metadata = self._decode_stage_metadata(user_node.ai_feedback)
        assessment = dict(metadata.get("a") or {})
        bank_id = assessment.get("bid")
        session_id = assessment.get("sid")
        if bank_id and session_id:
            return LearningPathNodePracticeGenerateResponse(
                bank_id=int(bank_id),
                bank_title=f"{node.title}阶段练习",
                session_id=int(session_id),
            )

        try:
            generated_bank = await self._generate_stage_question_bank(
                session=session,
                user_id=user_id,
                path_name=path.name if path else "学习路径",
                node=node,
                metadata=metadata,
            )
            assessment["bid"] = generated_bank["bank_id"]
            assessment["sid"] = generated_bank["session_id"]
            metadata["a"] = assessment
            await self.repository.update_user_path_node_feedback(
                session,
                user_path_id,
                node_id,
                self._encode_stage_metadata_from_dict(metadata),
            )
            if user_node.status == "unlocked":
                await self.repository.update_user_path_node(
                    session,
                    user_path_id,
                    node_id,
                    status="in_progress",
                    progress_percent=float(user_node.progress_percent or 0),
                )
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        return LearningPathNodePracticeGenerateResponse(
            bank_id=generated_bank["bank_id"],
            bank_title=generated_bank["bank_title"],
            session_id=generated_bank["session_id"],
        )

    async def _build_snapshot_response(self, session: AsyncSession, snapshot) -> SkillSnapshotResponse:
        score_rows = await self.repository.list_scores(session, snapshot.id)
        return SkillSnapshotResponse(
            id=snapshot.id,
            user_id=snapshot.user_id,
            source_type=snapshot.source_type,
            source_ref_id=snapshot.source_ref_id,
            snapshot_version=snapshot.snapshot_version,
            total_score=float(snapshot.total_score or 0),
            rank_percent=float(snapshot.rank_percent or 0),
            generated_by=snapshot.generated_by,
            generated_at=snapshot.generated_at,
            scores=[
                SkillScoreResponse(
                    dimension_id=dimension.id,
                    code=dimension.code,
                    name=dimension.name,
                    score=float(score.score),
                    percentile=float(score.percentile) if score.percentile is not None else None,
                    level=score.level,
                    insight=score.insight,
                )
                for score, dimension in score_rows
            ],
        )

    async def _build_path_response(
        self,
        session: AsyncSession,
        user_id: int,
        user_path,
    ) -> UserLearningPathResponse:
        path = await self.repository.get_path(session, user_path.path_id)
        node_rows = await self.repository.list_user_path_nodes(session, user_path.id)

        metadata_rows = []
        content_ids: list[int] = []
        for user_node, node in node_rows:
            metadata = self._decode_stage_metadata(user_node.ai_feedback)
            metadata_rows.append((user_node, node, metadata))
            for resource in metadata.get("r") or []:
                if resource.get("s") == "sys" and resource.get("i"):
                    content_ids.append(int(resource["i"]))

        content_rows = await self.content_repository.get_content_rows_by_ids(
            session,
            viewer_user_id=user_id,
            content_ids=list(dict.fromkeys(content_ids)),
        )
        content_map = {int(row["id"]): row for row in content_rows}

        return UserLearningPathResponse(
            id=user_path.id,
            path_id=user_path.path_id,
            name=path.name if path else "",
            description=path.description if path else None,
            target_role=path.target_role if path else None,
            status=user_path.status,
            progress_percent=float(user_path.progress_percent),
            current_node_id=user_path.current_node_id,
            ai_summary=user_path.ai_summary,
            nodes=[
                LearningPathNodeResponse(
                    id=user_node.id,
                    node_id=node.id,
                    title=node.title,
                    description=node.description,
                    node_type=node.node_type,
                    course_id=node.course_id,
                    status=user_node.status,
                    progress_percent=float(user_node.progress_percent),
                    sort_order=node.sort_order,
                    recommended_reason=node.recommended_reason,
                    estimated_minutes=node.estimated_minutes,
                    stage_code=metadata.get("c"),
                    stage_goal=metadata.get("g"),
                    resources=self._build_resource_responses(metadata.get("r") or [], content_map),
                    assessment=self._build_assessment_response(metadata.get("a")),
                )
                for user_node, node, metadata in metadata_rows
            ],
        )

    async def _normalize_route_option(
        self,
        session: AsyncSession,
        user_id: int,
        payload: LearningPathGenerateRequest,
        *,
        raw_route: dict[str, Any],
        route_index: int,
        weak_dimensions: list[str],
    ) -> LearningPathPlanRouteResponse:
        title = str(raw_route.get("title") or f"路线 {route_index}").strip()
        summary = str(raw_route.get("summary") or raw_route.get("description") or "").strip()
        fit_reason = str(raw_route.get("fit_reason") or raw_route.get("recommended_reason") or "").strip()
        difficulty = str(raw_route.get("difficulty") or payload.current_level or "beginner").strip().lower()
        if difficulty not in {"beginner", "intermediate", "advanced"}:
            difficulty = payload.current_level
        estimated_weeks = int(raw_route.get("estimated_weeks") or max(4, payload.weekly_hours // 2 + 4))
        route_code = str(raw_route.get("route_code") or f"route_{route_index}").strip() or f"route_{route_index}"

        stages = raw_route.get("stages")
        if not isinstance(stages, list) or not stages:
            default_routes = self._build_default_route_blueprints(payload, weak_dimensions)
            stages = default_routes[min(route_index - 1, len(default_routes) - 1)]["stages"]

        normalized_stages: list[LearningPathPlanStageResponse] = []
        for stage_index, raw_stage in enumerate(stages, start=1):
            stage_data = raw_stage if isinstance(raw_stage, dict) else {}
            stage_title = str(stage_data.get("title") or f"阶段 {stage_index}").strip()
            stage_goal = str(stage_data.get("goal") or stage_data.get("description") or "").strip() or f"完成 {stage_title} 的学习目标"
            stage_description = str(stage_data.get("description") or "").strip() or None
            stage_reason = str(stage_data.get("recommended_reason") or stage_data.get("reason") or "").strip() or None
            estimated_hours = int(stage_data.get("estimated_hours") or max(4, payload.weekly_hours))
            resources = await self._recommend_stage_resources(
                session,
                user_id,
                payload,
                route_title=title,
                stage_title=stage_title,
                stage_goal=stage_goal,
                weak_dimensions=weak_dimensions,
            )
            assessment = self._normalize_stage_assessment(stage_data.get("assessment"), stage_index)
            normalized_stages.append(
                LearningPathPlanStageResponse(
                    stage_code=str(stage_data.get("stage_code") or f"{route_code}_stage_{stage_index}"),
                    title=stage_title,
                    goal=stage_goal,
                    description=stage_description,
                    estimated_hours=estimated_hours,
                    recommended_reason=stage_reason,
                    resources=resources,
                    assessment=assessment,
                )
            )

        return LearningPathPlanRouteResponse(
            route_code=route_code,
            title=title[:120],
            summary=(summary or f"围绕 {payload.target_role or '当前目标'} 设计的第 {route_index} 条学习路线。")[:500],
            fit_reason=(fit_reason or "适合当前阶段循序渐进推进，并结合资源和练习完成阶段性提升。")[:500],
            difficulty=difficulty,
            estimated_weeks=max(2, estimated_weeks),
            stages=normalized_stages,
        )

    async def _recommend_stage_resources(
        self,
        session: AsyncSession,
        user_id: int,
        payload: LearningPathGenerateRequest,
        *,
        route_title: str,
        stage_title: str,
        stage_goal: str,
        weak_dimensions: list[str],
    ) -> list[LearningPathStageResourceResponse]:
        mode = (payload.preferred_resource_mode or "mixed").strip().lower()
        queries = [stage_title, stage_goal, f"{payload.target_role or ''} {stage_title}".strip()]
        if weak_dimensions:
            queries.append(weak_dimensions[0])

        resources: list[LearningPathStageResourceResponse] = []
        seen_ids: set[int] = set()

        if mode != "online":
            for query in queries:
                normalized = query.strip()
                if not normalized:
                    continue
                rows, _ = await self.content_repository.search_content_rows(
                    session,
                    viewer_user_id=user_id,
                    keyword=normalized,
                    category_id=None,
                    offset=0,
                    limit=4,
                )
                for row in rows:
                    content_id = int(row["id"])
                    if content_id in seen_ids:
                        continue
                    seen_ids.add(content_id)
                    resources.append(
                        LearningPathStageResourceResponse(
                            resource_type="video",
                            source="system",
                            title=str(row.get("title") or "系统资源"),
                            description=str(row.get("summary") or "").strip() or None,
                            content_id=content_id,
                            category_name=str(row.get("category_name") or "").strip() or None,
                            cover_url=str(row.get("cover_public_url") or "").strip() or None,
                            video_url=str(row.get("video_public_url") or row.get("external_video_url") or "").strip() or None,
                        )
                    )
                    if len(resources) >= 2:
                        break
                if len(resources) >= 2:
                    break

        if mode != "system":
            external_title, external_url = self._build_external_resource(route_title, stage_title, stage_goal)
            resources.append(
                LearningPathStageResourceResponse(
                    resource_type="article",
                    source="external",
                    title=external_title,
                    description="补充阅读与查漏补缺",
                    external_url=external_url,
                )
            )

        return resources[:3]

    async def _generate_stage_question_bank(
        self,
        *,
        session: AsyncSession,
        user_id: int,
        path_name: str,
        node,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        stage_goal = str(metadata.get("g") or node.title or "").strip()
        resources = metadata.get("r") or []
        assessment = metadata.get("a") or {}
        question_count = int(assessment.get("q") or 6)

        system_ids = [int(item["i"]) for item in resources if item.get("s") == "sys" and item.get("i")]
        system_rows = await self.content_repository.get_content_rows_by_ids(
            session,
            viewer_user_id=user_id,
            content_ids=system_ids,
        )

        evidence_lines: list[str] = []
        for row in system_rows:
            title = str(row.get("title") or "").strip()
            summary = str(row.get("summary") or "").strip()
            evidence_lines.append(f"- 系统资源：{title}" + (f"；摘要：{summary}" if summary else ""))
        for item in resources:
            if item.get("s") == "ext":
                evidence_lines.append(f"- 外部资源：{item.get('t') or '参考资料'}；链接：{item.get('u') or ''}")

        prompt = f"""
你是一名题库生成助手，请基于以下学习路径阶段内容生成一套结构化练习题。

学习路径：{path_name}
阶段标题：{node.title}
阶段目标：{stage_goal}
阶段说明：{node.description or ''}
推荐理由：{node.recommended_reason or ''}
参考资源：
{chr(10).join(evidence_lines) if evidence_lines else '- 请围绕阶段目标自行补全基础练习'}

规则：
- 只输出 JSON。
- 生成 3 到 {question_count} 题。
- 题型优先 single_choice，必要时可 mixed。
- 每题尽量提供 4 个选项。
- explanation 要简明，便于复盘。

JSON Schema:
{{
  "bank_title": "string",
  "bank_description": "string",
  "difficulty": "easy|medium|hard|mixed",
  "questions": [
    {{
      "question_type": "single_choice|multiple_choice",
      "content": "string",
      "difficulty": "easy|medium|hard",
      "explanation": "string",
      "options": [
        {{"content": "string", "is_correct": true}},
        {{"content": "string", "is_correct": false}}
      ]
    }}
  ]
}}
"""
        try:
            response = await asyncio.wait_for(
                self.agent_manager.llm.ainvoke(
                    [
                        SystemMessage(content="You generate production-ready practice banks for learning checkpoints."),
                        HumanMessage(content=prompt),
                    ]
                ),
                timeout=60,
            )
            parsed = self._extract_json_object(str(getattr(response, "content", response)).strip())
            normalized_bank = self._normalize_generated_bank(
                parsed,
                fallback_title=f"{node.title}阶段练习",
                fallback_summary=node.description or stage_goal,
                question_count=question_count,
            )
        except Exception as exc:
            raise InfrastructureError(message=f"Failed to generate practice for this stage: {exc}") from exc

        category_name = str(system_rows[0].get("category_name") or "").strip() if system_rows else ""
        category = await self.practice_repository.find_category_by_name(session, category_name)
        category_id = category.id if category else None

        bank = await self.practice_repository.create_question_bank(
            session,
            title=normalized_bank["bank_title"],
            description=normalized_bank["bank_description"],
            category_id=category_id,
            difficulty=normalized_bank["difficulty"],
            question_count=len(normalized_bank["questions"]),
            created_by=user_id,
        )
        for question_data in normalized_bank["questions"]:
            question = await self.practice_repository.create_question(
                session,
                bank_id=bank.id,
                category_id=category_id,
                question_type=question_data["question_type"],
                content=question_data["content"],
                explanation=question_data["explanation"],
                correct_answer_text=question_data["correct_answer_text"],
                difficulty=question_data["difficulty"],
                sort_order=question_data["sort_order"],
            )
            for option_data in question_data["options"]:
                await self.practice_repository.create_question_option(
                    session,
                    question_id=question.id,
                    option_key=option_data["option_key"],
                    content=option_data["content"],
                    is_correct=option_data["is_correct"],
                    sort_order=option_data["sort_order"],
                )

        practice_session = await self.practice_repository.create_practice_session(
            session,
            user_id=user_id,
            bank_id=bank.id,
            session_type="checkpoint",
            total_questions=len(normalized_bank["questions"]),
        )
        return {"bank_id": bank.id, "bank_title": bank.title, "session_id": practice_session.id}

    def _normalize_stage_assessment(self, raw_assessment: Any, stage_index: int) -> LearningPathStageAssessmentResponse:
        assessment = raw_assessment if isinstance(raw_assessment, dict) else {}
        question_count = int(assessment.get("question_count") or (6 if stage_index < 3 else 8))
        pass_score = int(assessment.get("pass_score") or 70)
        return LearningPathStageAssessmentResponse(
            mode=str(assessment.get("mode") or "generated_quiz"),
            question_count=max(3, min(question_count, 12)),
            pass_score=max(50, min(pass_score, 100)),
            generated_bank_id=assessment.get("generated_bank_id"),
            generated_session_id=assessment.get("generated_session_id"),
        )

    def _build_route_generation_goal(self, payload: LearningPathGenerateRequest, weak_dimensions: list[str]) -> str:
        target_role = payload.target_role or "通用能力提升"
        weak_text = "、".join(weak_dimensions) if weak_dimensions else "暂无明显短板"
        return f"""
请围绕“{target_role}”生成 {payload.route_count} 条不同风格的学习路线，适合 {payload.current_level} 学习者，
每周可投入 {payload.weekly_hours} 小时，资源偏好为 {payload.preferred_resource_mode}。

请在 path_plan 字段中直接输出以下 JSON，不要使用 Markdown 代码块：
{{
  "route_options": [
    {{
      "route_code": "string",
      "title": "string",
      "summary": "string",
      "fit_reason": "string",
      "difficulty": "beginner|intermediate|advanced",
      "estimated_weeks": 8,
      "stages": [
        {{
          "stage_code": "string",
          "title": "string",
          "goal": "string",
          "description": "string",
          "estimated_hours": 8,
          "recommended_reason": "string",
          "assessment": {{
            "mode": "generated_quiz",
            "question_count": 6,
            "pass_score": 70
          }}
        }}
      ]
    }}
  ]
}}

补充约束：
- 每条路线 3 到 4 个阶段。
- 路线之间风格要不同，例如“稳扎稳打”“练习驱动”“项目实战”。
- 重点关注这些待提升维度：{weak_text}。
""".strip()

    def _build_default_route_blueprints(
        self,
        payload: LearningPathGenerateRequest,
        weak_dimensions: list[str],
    ) -> list[dict[str, Any]]:
        target = payload.target_role or "当前目标"
        weak_text = "、".join(weak_dimensions) if weak_dimensions else "核心基础"
        return [
            {
                "route_code": "foundation_track",
                "title": f"{target}夯实路线",
                "summary": "先补基础、再做专题训练，适合希望稳扎稳打推进的学习者。",
                "fit_reason": f"优先补齐 {weak_text}，再进入专项练习和综合输出，更适合当前阶段打牢底座。",
                "difficulty": payload.current_level,
                "estimated_weeks": 8,
                "stages": [
                    {
                        "stage_code": "foundation_stage_1",
                        "title": "基础补齐",
                        "goal": f"补齐 {target} 所需的关键概念与环境准备",
                        "description": "先完成概念梳理、环境搭建和基本操作训练。",
                        "estimated_hours": max(6, payload.weekly_hours),
                        "recommended_reason": "把高频基础问题先解决，后面的练习和项目才更顺。",
                    },
                    {
                        "stage_code": "foundation_stage_2",
                        "title": "专题练习",
                        "goal": "围绕核心知识点做连续练习，形成可复用的方法",
                        "description": "用题目和案例提升掌握度，减少纸面理解和真实应用之间的落差。",
                        "estimated_hours": max(6, payload.weekly_hours + 2),
                        "recommended_reason": "通过持续练习把抽象知识变成稳定输出。",
                    },
                    {
                        "stage_code": "foundation_stage_3",
                        "title": "综合输出",
                        "goal": "完成一次阶段总结或小项目，形成可展示成果",
                        "description": "用实战输出检验学习成果，并完成一轮复盘。",
                        "estimated_hours": max(8, payload.weekly_hours + 2),
                        "recommended_reason": "把知识真正沉淀为可迁移能力。",
                    },
                ],
            },
            {
                "route_code": "practice_track",
                "title": f"{target}练习驱动路线",
                "summary": "以刷题、阶段测验和高频复盘为主，适合想快速建立反馈闭环的学习者。",
                "fit_reason": "如果你希望尽快知道自己会不会、稳不稳，这条路线的反馈速度更快。",
                "difficulty": payload.current_level,
                "estimated_weeks": 6,
                "stages": [
                    {
                        "stage_code": "practice_stage_1",
                        "title": "快速导读",
                        "goal": "快速建立主题地图，明确知识边界和常见题型",
                        "description": "先了解知识全貌，再进入高频练习。",
                        "estimated_hours": max(4, payload.weekly_hours - 1),
                        "recommended_reason": "先看全局，练习时更容易抓重点。",
                    },
                    {
                        "stage_code": "practice_stage_2",
                        "title": "高频练习",
                        "goal": "集中攻克高频题点和易错点",
                        "description": "围绕核心知识点做多轮练习和讲解复盘。",
                        "estimated_hours": max(8, payload.weekly_hours + 2),
                        "recommended_reason": "用连续反馈把薄弱点暴露出来并逐个清掉。",
                    },
                    {
                        "stage_code": "practice_stage_3",
                        "title": "阶段考核",
                        "goal": "完成一次阶段测评，确认掌握度",
                        "description": "通过正式考核检查理解质量，再决定是否进入下一阶段。",
                        "estimated_hours": max(6, payload.weekly_hours),
                        "recommended_reason": "没有考核就很难确认是否真的掌握。",
                    },
                ],
            },
            {
                "route_code": "project_track",
                "title": f"{target}项目实战路线",
                "summary": "围绕案例和项目倒推知识点，适合喜欢边做边学的学习者。",
                "fit_reason": "如果你更需要可落地成果和项目感知，这条路线更有成就感。",
                "difficulty": payload.current_level,
                "estimated_weeks": 10,
                "stages": [
                    {
                        "stage_code": "project_stage_1",
                        "title": "关键概念导入",
                        "goal": "围绕目标项目补齐必须的先备知识",
                        "description": "只先学项目必需的那部分内容，降低启动成本。",
                        "estimated_hours": max(5, payload.weekly_hours),
                        "recommended_reason": "项目学习不等于跳过基础，而是先学最关键的基础。",
                    },
                    {
                        "stage_code": "project_stage_2",
                        "title": "案例拆解",
                        "goal": "拆解一个典型案例，理解实现思路和关键步骤",
                        "description": "通过完整案例理解知识点在真实场景中的位置。",
                        "estimated_hours": max(8, payload.weekly_hours + 1),
                        "recommended_reason": "案例能帮助你把分散知识串成一条线。",
                    },
                    {
                        "stage_code": "project_stage_3",
                        "title": "项目输出",
                        "goal": "独立完成一个小项目并整理成果",
                        "description": "形成自己的项目版本，并补齐过程中的薄弱点。",
                        "estimated_hours": max(10, payload.weekly_hours + 2),
                        "recommended_reason": "最终要把知识转换成真正能展示、能复用的作品。",
                    },
                ],
            },
            {
                "route_code": "steady_track",
                "title": f"{target}稳步进阶路线",
                "summary": "控制节奏、边学边复盘，适合希望长期稳定推进的学习者。",
                "fit_reason": "如果你学习时间有限但希望持续积累，这条路线更容易坚持。",
                "difficulty": payload.current_level,
                "estimated_weeks": 12,
                "stages": [
                    {
                        "stage_code": "steady_stage_1",
                        "title": "知识起步",
                        "goal": "建立主题认知和学习边界",
                        "description": "用更平缓的节奏进入目标主题。",
                        "estimated_hours": max(4, payload.weekly_hours),
                        "recommended_reason": "先把入口走顺，再提升强度。",
                    },
                    {
                        "stage_code": "steady_stage_2",
                        "title": "重点突破",
                        "goal": "围绕关键模块做阶段强化",
                        "description": "有选择地攻克最影响进步的部分。",
                        "estimated_hours": max(6, payload.weekly_hours),
                        "recommended_reason": "把有限时间放到最值得突破的点上。",
                    },
                    {
                        "stage_code": "steady_stage_3",
                        "title": "复盘巩固",
                        "goal": "完成复盘、考核和下一阶段准备",
                        "description": "形成一轮闭环，并为下一阶段做准备。",
                        "estimated_hours": max(5, payload.weekly_hours),
                        "recommended_reason": "稳定复盘能显著提升长期学习质量。",
                    },
                ],
            },
        ]

    def _extract_weak_dimensions(self, score_rows: list[tuple[Any, Any]]) -> list[str]:
        sorted_rows = sorted(score_rows, key=lambda item: float(item[0].score))
        return [dimension.name for score, dimension in sorted_rows[:2] if dimension.name]

    def _build_external_resource(self, route_title: str, stage_title: str, stage_goal: str) -> tuple[str, str]:
        seed = f"{route_title} {stage_title} {stage_goal}".lower()
        mapping = [
            ("mysql", ("MySQL 官方文档", "https://dev.mysql.com/doc/")),
            ("python", ("Python 官方教程", "https://docs.python.org/3/tutorial/")),
            ("react", ("React 官方学习文档", "https://react.dev/learn")),
            ("java", ("Oracle Java 教程", "https://docs.oracle.com/javase/tutorial/")),
            ("sql", ("SQL 教程参考", "https://www.w3schools.com/sql/")),
        ]
        for keyword, target in mapping:
            if keyword in seed:
                return target
        return ("MDN 学习资源", "https://developer.mozilla.org/zh-CN/docs/Learn")

    def _build_resource_responses(
        self,
        resources: list[dict[str, Any]],
        content_map: dict[int, dict[str, Any]],
    ) -> list[LearningPathStageResourceResponse]:
        output: list[LearningPathStageResourceResponse] = []
        for resource in resources:
            if resource.get("s") == "sys" and resource.get("i"):
                row = content_map.get(int(resource["i"]))
                if not row:
                    continue
                output.append(
                    LearningPathStageResourceResponse(
                        resource_type=resource.get("rt") or "video",
                        source="system",
                        title=str(row.get("title") or "系统资源"),
                        description=str(row.get("summary") or "").strip() or None,
                        content_id=int(row["id"]),
                        category_name=str(row.get("category_name") or "").strip() or None,
                        cover_url=str(row.get("cover_public_url") or "").strip() or None,
                        video_url=str(row.get("video_public_url") or row.get("external_video_url") or "").strip() or None,
                    )
                )
            elif resource.get("s") == "ext":
                output.append(
                    LearningPathStageResourceResponse(
                        resource_type=resource.get("rt") or "article",
                        source="external",
                        title=str(resource.get("t") or "外部资源"),
                        description=str(resource.get("d") or "").strip() or None,
                        external_url=str(resource.get("u") or "").strip() or None,
                    )
                )
        return output

    def _build_assessment_response(self, assessment: dict[str, Any] | None):
        if not isinstance(assessment, dict) or not assessment:
            return None
        return LearningPathStageAssessmentResponse(
            mode=str(assessment.get("m") or "generated_quiz"),
            question_count=int(assessment.get("q") or 6),
            pass_score=int(assessment.get("p") or 70),
            generated_bank_id=int(assessment["bid"]) if assessment.get("bid") else None,
            generated_session_id=int(assessment["sid"]) if assessment.get("sid") else None,
        )

    def _encode_stage_metadata(self, stage: LearningPathPlanStageResponse) -> str:
        data = {
            "c": stage.stage_code,
            "g": stage.goal,
            "r": [],
            "a": {
                "m": stage.assessment.mode if stage.assessment else "generated_quiz",
                "q": stage.assessment.question_count if stage.assessment else 6,
                "p": stage.assessment.pass_score if stage.assessment else 70,
            },
        }
        for resource in stage.resources[:3]:
            if resource.source == "system" and resource.content_id:
                data["r"].append({"s": "sys", "i": resource.content_id, "rt": resource.resource_type})
            elif resource.source == "external" and resource.external_url:
                data["r"].append(
                    {
                        "s": "ext",
                        "t": resource.title[:40],
                        "u": resource.external_url[:180],
                        "rt": resource.resource_type,
                    }
                )
        return self._encode_stage_metadata_from_dict(data)

    def _encode_stage_metadata_from_dict(self, data: dict[str, Any]) -> str:
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        if len(payload) <= 500:
            return payload

        trimmed = dict(data)
        trimmed_resources = list(trimmed.get("r") or [])
        while trimmed_resources and len(
            json.dumps({**trimmed, "r": trimmed_resources}, ensure_ascii=False, separators=(",", ":"))
        ) > 500:
            trimmed_resources.pop()
        trimmed["r"] = trimmed_resources
        payload = json.dumps(trimmed, ensure_ascii=False, separators=(",", ":"))
        if len(payload) <= 500:
            return payload

        trimmed["g"] = str(trimmed.get("g") or "")[:80]
        payload = json.dumps(trimmed, ensure_ascii=False, separators=(",", ":"))
        if len(payload) <= 500:
            return payload

        minimal = {
            "c": trimmed.get("c"),
            "g": str(trimmed.get("g") or "")[:40],
            "a": trimmed.get("a") or {"m": "generated_quiz", "q": 6, "p": 70},
        }
        return json.dumps(minimal, ensure_ascii=False, separators=(",", ":"))

    def _decode_stage_metadata(self, raw: str | None) -> dict[str, Any]:
        if not raw:
            return {}
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _unwrap_text(value: Any) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            for key in ("raw", "content", "summary", "overview"):
                inner = value.get(key)
                if isinstance(inner, str) and inner.strip():
                    return inner.strip()
        return ""

    @staticmethod
    def _extract_json_object(raw: str) -> dict[str, Any] | None:
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        match = re.search(r"\{.*\}", raw, re.S)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    def _normalize_planning_summary(
        self,
        raw_summary: str,
        payload: LearningPathGenerateRequest,
        route_count: int,
    ) -> str:
        summary = (raw_summary or "").strip()
        if self._looks_like_bad_summary(summary):
            target = payload.target_role or "当前目标"
            return (
                "## 规划说明\n"
                f"- 目标方向：**{target}**\n"
                f"- 当前水平：**{payload.current_level}**\n"
                f"- 每周投入：**{payload.weekly_hours} 小时**\n"
                f"- 已生成 **{route_count} 条候选路线**，建议先比较路线风格，再激活其中一条。\n"
                "- 激活后可按阶段学习，并为每个阶段生成题库与考核。"
            )
        return summary[:1200]

    @staticmethod
    def _looks_like_bad_summary(summary: str) -> bool:
        normalized = summary.lower()
        return (
            not summary
            or "route_options" in normalized
            or "json" in normalized
            or "goal analysis" in normalized
            or "不要使用 markdown 代码块" in normalized
            or len(summary) > 800
        )

    @staticmethod
    def _normalize_question_type(question_type: str, correct_count: int) -> str:
        normalized = (question_type or "").strip().lower()
        mapping = {
            "single": "single_choice",
            "single_choice": "single_choice",
            "single-choice": "single_choice",
            "multiple": "multiple_choice",
            "multiple_choice": "multiple_choice",
            "multiple-choice": "multiple_choice",
        }
        resolved = mapping.get(normalized)
        if resolved == "single_choice" and correct_count != 1:
            return "multiple_choice"
        if resolved:
            return resolved
        return "multiple_choice" if correct_count > 1 else "single_choice"

    @classmethod
    def _normalize_generated_bank(
        cls,
        payload: dict[str, Any] | None,
        *,
        fallback_title: str,
        fallback_summary: str,
        question_count: int,
    ) -> dict[str, Any]:
        data = payload or {}
        bank_title = str(data.get("bank_title") or "").strip() or fallback_title
        bank_description = str(data.get("bank_description") or "").strip() or fallback_summary.strip()
        difficulty = str(data.get("difficulty") or "mixed").strip().lower()
        if difficulty not in {"easy", "medium", "hard", "mixed"}:
            difficulty = "mixed"

        normalized_questions: list[dict[str, Any]] = []
        for raw_question in data.get("questions") or []:
            if not isinstance(raw_question, dict):
                continue
            content = str(
                raw_question.get("content")
                or raw_question.get("question")
                or raw_question.get("stem")
                or ""
            ).strip()
            if not content:
                continue

            normalized_options: list[dict[str, Any]] = []
            for option_index, raw_option in enumerate(raw_question.get("options") or []):
                if not isinstance(raw_option, dict):
                    continue
                option_content = str(
                    raw_option.get("content")
                    or raw_option.get("text")
                    or raw_option.get("option_text")
                    or ""
                ).strip()
                if not option_content:
                    continue
                normalized_options.append(
                    {
                        "option_key": chr(65 + option_index),
                        "content": option_content,
                        "is_correct": bool(raw_option.get("is_correct")),
                        "sort_order": option_index + 1,
                    }
                )
            if len(normalized_options) < 2:
                continue
            correct_options = [option for option in normalized_options if option["is_correct"]]
            if not correct_options:
                continue

            question_difficulty = str(raw_question.get("difficulty") or difficulty).strip().lower()
            if question_difficulty not in {"easy", "medium", "hard"}:
                question_difficulty = "medium"
            normalized_questions.append(
                {
                    "content": content,
                    "question_type": cls._normalize_question_type(
                        str(raw_question.get("question_type") or ""),
                        len(correct_options),
                    ),
                    "difficulty": question_difficulty,
                    "explanation": str(raw_question.get("explanation") or "").strip() or None,
                    "correct_answer_text": ", ".join(option["option_key"] for option in correct_options),
                    "options": normalized_options,
                    "sort_order": len(normalized_questions) + 1,
                }
            )
            if len(normalized_questions) >= question_count:
                break

        if len(normalized_questions) < 3:
            raise InfrastructureError(message="Stage practice generation returned too few valid questions.")

        return {
            "bank_title": bank_title[:120],
            "bank_description": bank_description[:1000] if bank_description else None,
            "difficulty": difficulty,
            "questions": normalized_questions,
        }
