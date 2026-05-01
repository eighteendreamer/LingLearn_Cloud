from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import utc_now_naive
from app.modules.learning_path.models import (
    LearningPath,
    LearningPathNode,
    SkillDimension,
    UserLearningPath,
    UserLearningPathNode,
    UserSkillScore,
    UserSkillSnapshot,
)


class LearningPathRepository:
    async def list_dimensions(self, session: AsyncSession) -> list[SkillDimension]:
        result = await session.execute(
            select(SkillDimension)
            .where(SkillDimension.status == "active")
            .order_by(SkillDimension.sort_order, SkillDimension.id)
        )
        return list(result.scalars().all())

    async def ensure_default_dimensions(self, session: AsyncSession) -> list[SkillDimension]:
        dimensions = await self.list_dimensions(session)
        if dimensions:
            return dimensions

        now = utc_now_naive()
        seeds = [
            ("programming", "编程基础", "语法、工程习惯与代码阅读能力"),
            ("algorithm", "算法思维", "抽象、复杂度与解题策略"),
            ("database", "数据库", "SQL、数据建模与查询优化"),
            ("frontend", "前端开发", "交互、组件化与浏览器基础"),
            ("learning", "学习自驱", "计划制定、复盘与持续学习"),
        ]
        objects = [
            SkillDimension(code=code, name=name, description=desc_text, sort_order=index, created_at=now, updated_at=now)
            for index, (code, name, desc_text) in enumerate(seeds, start=1)
        ]
        session.add_all(objects)
        await session.flush()
        return objects

    async def get_latest_snapshot(self, session: AsyncSession, user_id: int) -> UserSkillSnapshot | None:
        return await session.scalar(
            select(UserSkillSnapshot)
            .where(UserSkillSnapshot.user_id == user_id)
            .order_by(desc(UserSkillSnapshot.generated_at), desc(UserSkillSnapshot.id))
            .limit(1)
        )

    async def list_snapshots(self, session: AsyncSession, user_id: int, limit: int) -> list[UserSkillSnapshot]:
        result = await session.execute(
            select(UserSkillSnapshot)
            .where(UserSkillSnapshot.user_id == user_id)
            .order_by(desc(UserSkillSnapshot.generated_at), desc(UserSkillSnapshot.id))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_scores(self, session: AsyncSession, snapshot_id: int):
        result = await session.execute(
            select(UserSkillScore, SkillDimension)
            .join(SkillDimension, SkillDimension.id == UserSkillScore.dimension_id)
            .where(UserSkillScore.snapshot_id == snapshot_id)
            .order_by(SkillDimension.sort_order, SkillDimension.id)
        )
        return list(result.all())

    async def create_snapshot(self, session: AsyncSession, *, user_id: int, source_type: str, source_ref_id: int | None, scores: list[dict]) -> UserSkillSnapshot:
        latest_version = await session.scalar(
            select(func.max(UserSkillSnapshot.snapshot_version)).where(UserSkillSnapshot.user_id == user_id)
        )
        now = utc_now_naive()
        total_score = round(sum(item["score"] for item in scores) / len(scores), 2) if scores else 0
        snapshot = UserSkillSnapshot(
            user_id=user_id,
            source_type=source_type,
            source_ref_id=source_ref_id,
            snapshot_version=int(latest_version or 0) + 1,
            total_score=total_score,
            rank_percent=75.0,
            generated_by="langgraph",
            generated_at=now,
            created_at=now,
            updated_at=now,
        )
        session.add(snapshot)
        await session.flush()
        session.add_all(
            [
                UserSkillScore(
                    snapshot_id=snapshot.id,
                    dimension_id=item["dimension_id"],
                    score=item["score"],
                    percentile=item.get("percentile"),
                    level=item.get("level"),
                    insight=item.get("insight"),
                    created_at=now,
                )
                for item in scores
            ]
        )
        await session.flush()
        await session.refresh(snapshot)
        return snapshot

    async def create_path_with_nodes(self, session: AsyncSession, *, user_id: int, snapshot_id: int | None, target_role: str | None, nodes: list[dict], ai_summary: str) -> UserLearningPath:
        now = utc_now_naive()
        path = LearningPath(
            path_type="personalized",
            name=f"{target_role or '个性化'}学习路径",
            description="根据能力画像和近期学习表现生成的学习路径",
            target_role=target_role,
            based_on_snapshot_id=snapshot_id,
            created_by=user_id,
            status="active",
            is_default=False,
            created_at=now,
            updated_at=now,
        )
        session.add(path)
        await session.flush()

        node_objects: list[LearningPathNode] = []
        for index, item in enumerate(nodes, start=1):
            node = LearningPathNode(
                path_id=path.id,
                course_id=item.get("course_id"),
                node_type=item.get("node_type", "course"),
                title=item["title"],
                description=item.get("description"),
                sort_order=index,
                default_status="unlocked" if index == 1 else "locked",
                recommended_reason=item.get("recommended_reason"),
                estimated_minutes=int(item.get("estimated_minutes") or 60),
                created_at=now,
                updated_at=now,
            )
            session.add(node)
            node_objects.append(node)
        await session.flush()

        user_path = UserLearningPath(
            user_id=user_id,
            path_id=path.id,
            snapshot_id=snapshot_id,
            status="active",
            progress_percent=0,
            started_at=now,
            current_node_id=node_objects[0].id if node_objects else None,
            ai_summary=ai_summary,
            created_at=now,
            updated_at=now,
        )
        session.add(user_path)
        await session.flush()
        session.add_all(
            [
                UserLearningPathNode(
                    user_path_id=user_path.id,
                    node_id=node.id,
                    status="unlocked" if index == 0 else "locked",
                    progress_percent=0,
                    unlocked_at=now if index == 0 else None,
                    created_at=now,
                    updated_at=now,
                )
                for index, node in enumerate(node_objects)
            ]
        )
        await session.flush()
        await session.refresh(user_path)
        return user_path

    async def get_active_user_path(self, session: AsyncSession, user_id: int) -> UserLearningPath | None:
        return await session.scalar(
            select(UserLearningPath)
            .where(UserLearningPath.user_id == user_id, UserLearningPath.status == "active")
            .order_by(desc(UserLearningPath.created_at), desc(UserLearningPath.id))
            .limit(1)
        )

    async def get_user_path(self, session: AsyncSession, user_id: int, user_path_id: int) -> UserLearningPath | None:
        return await session.scalar(
            select(UserLearningPath).where(UserLearningPath.id == user_path_id, UserLearningPath.user_id == user_id)
        )

    async def get_path(self, session: AsyncSession, path_id: int) -> LearningPath | None:
        return await session.get(LearningPath, path_id)

    async def list_user_path_nodes(self, session: AsyncSession, user_path_id: int):
        result = await session.execute(
            select(UserLearningPathNode, LearningPathNode)
            .join(LearningPathNode, LearningPathNode.id == UserLearningPathNode.node_id)
            .where(UserLearningPathNode.user_path_id == user_path_id)
            .order_by(LearningPathNode.sort_order, LearningPathNode.id)
        )
        return list(result.all())

    async def update_user_path_node(self, session: AsyncSession, user_path_id: int, node_id: int, *, status: str, progress_percent: float) -> bool:
        now = utc_now_naive()
        values = {"status": status, "progress_percent": progress_percent, "updated_at": now}
        if status == "in_progress":
            values["started_at"] = now
        if status == "completed":
            values["completed_at"] = now
        result = await session.execute(
            update(UserLearningPathNode)
            .where(UserLearningPathNode.user_path_id == user_path_id, UserLearningPathNode.node_id == node_id)
            .values(**values)
        )
        return bool(result.rowcount)

    async def update_user_path_progress(
        self,
        session: AsyncSession,
        user_path_id: int,
        *,
        progress_percent: float,
        current_node_id: int | None,
        status: str,
    ) -> None:
        now = utc_now_naive()
        values = {
            "progress_percent": progress_percent,
            "current_node_id": current_node_id,
            "status": status,
            "updated_at": now,
        }
        if status == "completed":
            values["completed_at"] = now
        await session.execute(
            update(UserLearningPath)
            .where(UserLearningPath.id == user_path_id)
            .values(**values)
        )
