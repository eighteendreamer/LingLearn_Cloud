from __future__ import annotations

import argparse
import asyncio
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import Select, select, update

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from app.db.session import get_engine, get_session_factory
from app.infra.video.streaming_service import VideoStreamingService
from app.modules.content.models import ContentItem
from app.modules.storage.models import MediaAsset


@dataclass
class StreamJob:
    asset_id: int
    object_key: str
    asset_duration_seconds: int | None = None
    content_ids: list[int] = field(default_factory=list)
    content_titles: list[str] = field(default_factory=list)
    missing_content_duration: bool = False


@dataclass
class StreamJobResult:
    asset_id: int
    status: str
    detail: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch rebuild faststart MP4 + HLS streaming assets for existing videos.",
    )
    parser.add_argument("--asset-id", dest="asset_ids", action="append", type=int, default=[])
    parser.add_argument("--content-id", dest="content_ids", action="append", type=int, default=[])
    parser.add_argument("--limit", type=int, default=0, help="Process at most N assets after filtering.")
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="How many videos to process at the same time. Default is 1 for safer rollout.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild even when an HLS manifest already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print the assets that would be rebuilt.",
    )
    return parser.parse_args()


async def fetch_jobs(
    *,
    asset_ids: list[int],
    content_ids: list[int],
    limit: int,
) -> list[StreamJob]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        stmt: Select = (
            select(
                MediaAsset.id.label("asset_id"),
                MediaAsset.object_key.label("object_key"),
                MediaAsset.duration_seconds.label("asset_duration_seconds"),
                ContentItem.id.label("content_id"),
                ContentItem.title.label("content_title"),
                ContentItem.duration_seconds.label("content_duration_seconds"),
            )
            .join(ContentItem, ContentItem.primary_media_asset_id == MediaAsset.id)
            .where(
                MediaAsset.asset_type == "video",
                MediaAsset.status == "active",
                ContentItem.deleted_at.is_(None),
                ContentItem.primary_media_asset_id.is_not(None),
                ContentItem.external_video_url.is_(None),
            )
            .order_by(MediaAsset.id.asc(), ContentItem.id.asc())
        )
        if asset_ids:
            stmt = stmt.where(MediaAsset.id.in_(asset_ids))
        if content_ids:
            stmt = stmt.where(ContentItem.id.in_(content_ids))

        rows = list((await session.execute(stmt)).mappings().all())

    jobs_by_asset: dict[int, StreamJob] = {}
    for row in rows:
        asset_id = int(row["asset_id"])
        job = jobs_by_asset.get(asset_id)
        if job is None:
            job = StreamJob(
                asset_id=asset_id,
                object_key=str(row["object_key"]),
                asset_duration_seconds=int(row["asset_duration_seconds"]) if row["asset_duration_seconds"] is not None else None,
            )
            jobs_by_asset[asset_id] = job

        content_id = int(row["content_id"])
        if content_id not in job.content_ids:
            job.content_ids.append(content_id)
        if row["content_duration_seconds"] is None:
            job.missing_content_duration = True
        content_title = str(row["content_title"] or "").strip()
        if content_title and content_title not in job.content_titles:
            job.content_titles.append(content_title)

    jobs = list(jobs_by_asset.values())
    if limit > 0:
        jobs = jobs[:limit]
    return jobs


async def process_job(
    *,
    job: StreamJob,
    streaming_service: VideoStreamingService,
    semaphore: asyncio.Semaphore,
    force: bool,
    dry_run: bool,
) -> StreamJobResult:
    async with semaphore:
        manifest_key = streaming_service.build_manifest_object_key(job.object_key)
        title_preview = " / ".join(job.content_titles[:2]) or f"asset:{job.asset_id}"
        prefix = f"[asset {job.asset_id}] {title_preview}"
        metadata_only = False

        if not force:
            exists = await streaming_service.has_hls_manifest(object_key=job.object_key)
            if exists:
                if job.asset_duration_seconds is not None and not job.missing_content_duration:
                    print(f"{prefix} -> skip (already has {manifest_key})")
                    return StreamJobResult(asset_id=job.asset_id, status="skipped", detail="already_processed")
                metadata_only = True

        if dry_run:
            action = "metadata-sync" if metadata_only else f"rebuild {manifest_key}"
            print(f"{prefix} -> dry-run {action}")
            return StreamJobResult(asset_id=job.asset_id, status="dry_run", detail=action)

        print(f"{prefix} -> {'syncing metadata' if metadata_only else 'rebuilding'}")
        try:
            if metadata_only:
                duration_seconds = await streaming_service.probe_object_duration_seconds(
                    object_key=job.object_key,
                )
            else:
                duration_seconds = await streaming_service.prepare_streaming_assets(object_key=job.object_key)
        except Exception as exc:
            detail = f"{type(exc).__name__}: {exc}"
            print(f"{prefix} -> failed: {detail}")
            traceback.print_exc()
            return StreamJobResult(asset_id=job.asset_id, status="failed", detail=detail)

        await persist_duration_metadata(
            asset_id=job.asset_id,
            content_ids=job.content_ids,
            duration_seconds=duration_seconds,
        )

        manifest_exists = await streaming_service.has_hls_manifest(object_key=job.object_key)
        if not metadata_only and not manifest_exists:
            detail = f"manifest missing after rebuild: {manifest_key}"
            print(f"{prefix} -> failed: {detail}")
            return StreamJobResult(asset_id=job.asset_id, status="failed", detail=detail)

        print(f"{prefix} -> ok")
        return StreamJobResult(asset_id=job.asset_id, status="processed", detail=manifest_key)


async def persist_duration_metadata(
    *,
    asset_id: int,
    content_ids: list[int],
    duration_seconds: int | None,
) -> None:
    if duration_seconds is None:
        return

    session_factory = get_session_factory()
    async with session_factory() as session:
        async with session.begin():
            await session.execute(
                update(MediaAsset)
                .where(MediaAsset.id == asset_id)
                .values(duration_seconds=duration_seconds)
            )
            if content_ids:
                await session.execute(
                    update(ContentItem)
                    .where(ContentItem.id.in_(content_ids))
                    .values(duration_seconds=duration_seconds)
                )


async def main() -> int:
    args = parse_args()
    if args.limit < 0:
        raise SystemExit("--limit must be >= 0")
    if args.concurrency < 1:
        raise SystemExit("--concurrency must be >= 1")

    jobs = await fetch_jobs(
        asset_ids=args.asset_ids,
        content_ids=args.content_ids,
        limit=args.limit,
    )
    if not jobs:
        print("No matching video assets found.")
        return 0

    print(
        f"Matched {len(jobs)} video asset(s). "
        f"force={args.force} dry_run={args.dry_run} concurrency={args.concurrency}"
    )

    streaming_service = VideoStreamingService()
    semaphore = asyncio.Semaphore(args.concurrency)
    results = await asyncio.gather(
        *[
            process_job(
                job=job,
                streaming_service=streaming_service,
                semaphore=semaphore,
                force=args.force,
                dry_run=args.dry_run,
            )
            for job in jobs
        ]
    )

    processed = sum(1 for item in results if item.status == "processed")
    skipped = sum(1 for item in results if item.status == "skipped")
    dry_runs = sum(1 for item in results if item.status == "dry_run")
    failed = [item for item in results if item.status == "failed"]

    print("")
    print("Summary")
    print(f"  processed: {processed}")
    print(f"  skipped:   {skipped}")
    print(f"  dry-run:   {dry_runs}")
    print(f"  failed:    {len(failed)}")

    if failed:
        print("")
        print("Failures")
        for item in failed:
            print(f"  asset_id={item.asset_id} -> {item.detail}")

    await get_engine().dispose()
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
