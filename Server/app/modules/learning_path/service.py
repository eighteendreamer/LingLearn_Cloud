from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.infra.ai.agent_manager import AgentManager
from app.modules.learning_path.repository import LearningPathRepository
from app.modules.learning_path.schemas import (
    LearningPathGenerateRequest,
    LearningPathNodeResponse,
    LearningPathNodeUpdateRequest,
    SkillProfileGenerateRequest,
    SkillScoreResponse,
    SkillSnapshotResponse,
    UserLearningPathResponse,
)


class LearningPathService:
    def __init__(self, *, repository: LearningPathRepository | None = None) -> None:
        self.repository = repository or LearningPathRepository()
        self.agent_manager = AgentManager()

    async def get_latest_skill_profile(self, session: AsyncSession, user_id: int):
        snapshot = await self.repository.get_latest_snapshot(session, user_id)
        return await self._build_snapshot_response(session, snapshot) if snapshot else None

    async def list_skill_profile_history(self, session: AsyncSession, user_id: int):
        snapshots = await self.repository.list_snapshots(session, user_id, limit=20)
        return [await self._build_snapshot_response(session, item) for item in snapshots]

    async def generate_skill_profile(self, session: AsyncSession, user_id: int, payload: SkillProfileGenerateRequest):
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
                    "insight": f"{dimension.name}表现稳定，建议结合项目练习继续强化。",
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
        return await self._build_path_response(session, user_path) if user_path else None

    async def get_learning_path(self, session: AsyncSession, user_id: int, user_path_id: int):
        user_path = await self.repository.get_user_path(session, user_id, user_path_id)
        if not user_path:
            raise NotFoundError(message="Learning path not found.")
        return await self._build_path_response(session, user_path)

    async def generate_learning_path(self, session: AsyncSession, user_id: int, payload: LearningPathGenerateRequest):
        snapshot = await self.repository.get_latest_snapshot(session, user_id)
        ai_summary = "已根据当前能力画像生成学习路径，建议按节点顺序推进并定期复盘。"
        try:
            result = await self.agent_manager.run_learning_path(
                session,
                user_id=user_id,
                current_level=payload.current_level,
                learning_history={"snapshot_id": snapshot.id if snapshot else None},
            )
            optimization = result.get("optimization") or {}
            ai_summary = optimization.get("detailed_optimization") or ai_summary
        except Exception:
            pass
        nodes = [
            {
                "title": "巩固核心基础",
                "description": "复习关键概念，补齐基础薄弱项。",
                "recommended_reason": "能力画像显示基础知识是后续提升的关键。",
                "estimated_minutes": 90,
            },
            {
                "title": "完成主题练习",
                "description": "围绕薄弱维度完成一组在线练习。",
                "recommended_reason": "用练习结果校验掌握度。",
                "estimated_minutes": 120,
            },
            {
                "title": "项目化输出",
                "description": "完成一个小型作品或学习总结。",
                "recommended_reason": "通过输出沉淀知识结构。",
                "estimated_minutes": 180,
            },
        ]
        user_path = await self.repository.create_path_with_nodes(
            session,
            user_id=user_id,
            snapshot_id=snapshot.id if snapshot else None,
            target_role=payload.target_role,
            nodes=nodes,
            ai_summary=ai_summary,
        )
        await session.commit()
        return await self._build_path_response(session, user_path)

    async def update_learning_path_node(self, session: AsyncSession, user_id: int, user_path_id: int, node_id: int, payload: LearningPathNodeUpdateRequest):
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
        return await self._build_path_response(session, user_path)

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

    async def _build_path_response(self, session: AsyncSession, user_path) -> UserLearningPathResponse:
        path = await self.repository.get_path(session, user_path.path_id)
        node_rows = await self.repository.list_user_path_nodes(session, user_path.id)
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
                )
                for user_node, node in node_rows
            ],
        )
