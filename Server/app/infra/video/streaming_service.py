from __future__ import annotations

import asyncio
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath
from uuid import uuid4

import imageio_ffmpeg

from app.core.config import get_settings
from app.core.exceptions import InfrastructureError
from app.infra.storage.service import StorageService


class VideoStreamingService:
    playlist_name = "index.m3u8"
    init_segment_name = "init.mp4"

    def __init__(self, storage_service: StorageService | None = None) -> None:
        self.settings = get_settings()
        self.storage_service = storage_service or StorageService()

    @classmethod
    def build_hls_prefix(cls, object_key: str) -> str:
        base_path = PurePosixPath(object_key)
        stem = base_path.with_suffix("")
        return f"{stem.as_posix()}/hls"

    @classmethod
    def build_manifest_object_key(cls, object_key: str) -> str:
        return f"{cls.build_hls_prefix(object_key)}/{cls.playlist_name}"

    async def has_hls_manifest(self, *, object_key: str | None) -> bool:
        if not object_key:
            return False
        return await self.storage_service.object_exists(
            object_key=self.build_manifest_object_key(object_key),
        )

    async def prepare_streaming_assets(self, *, object_key: str) -> int | None:
        base_temp_dir = Path(__file__).resolve().parents[3] / ".tmp" / "video-streaming"
        base_temp_dir.mkdir(parents=True, exist_ok=True)
        workdir = base_temp_dir / f"job-{uuid4().hex}"
        workdir.mkdir(parents=True, exist_ok=True)
        try:
            source_path = workdir / "source.mp4"
            faststart_path = workdir / "playback.mp4"
            hls_dir = workdir / "hls"
            hls_dir.mkdir(parents=True, exist_ok=True)

            await self.storage_service.download_object_to_path(
                object_key=object_key,
                target_path=source_path,
            )
            duration_seconds = await self._probe_duration_seconds(source_path)

            await self._rewrite_faststart(source_path=source_path, target_path=faststart_path)
            await self.storage_service.upload_file(
                object_key=object_key,
                file_path=faststart_path,
                content_type="video/mp4",
            )

            await self._generate_hls(source_path=faststart_path, output_dir=hls_dir)
            await self._upload_hls_directory(object_key=object_key, source_dir=hls_dir)
            return duration_seconds
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    async def probe_object_duration_seconds(self, *, object_key: str) -> int | None:
        base_temp_dir = Path(__file__).resolve().parents[3] / ".tmp" / "video-streaming"
        base_temp_dir.mkdir(parents=True, exist_ok=True)
        workdir = base_temp_dir / f"probe-{uuid4().hex}"
        workdir.mkdir(parents=True, exist_ok=True)
        try:
            source_path = workdir / "source.mp4"
            await self.storage_service.download_object_to_path(
                object_key=object_key,
                target_path=source_path,
            )
            return await self._probe_duration_seconds(source_path)
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    async def build_signed_manifest(self, *, object_key: str) -> str:
        manifest_key = self.build_manifest_object_key(object_key)
        manifest_text = await self.storage_service.read_text_object(object_key=manifest_key)
        manifest_dir = PurePosixPath(manifest_key).parent
        lines = manifest_text.splitlines()

        segment_lines: list[tuple[int, str]] = []
        map_lines: list[tuple[int, str]] = []
        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#EXT-X-MAP:URI="):
                map_lines.append((index, line))
                continue
            if stripped.startswith("#"):
                continue
            segment_lines.append((index, stripped))

        segment_urls = await asyncio.gather(
            *[
                self.storage_service.build_access_url(
                    object_key=(manifest_dir / item).as_posix(),
                    public_url=None,
                )
                for _, item in segment_lines
            ]
        )

        for (index, _), url in zip(segment_lines, segment_urls):
            if url is not None:
                lines[index] = url

        for index, line in map_lines:
            prefix = '#EXT-X-MAP:URI="'
            suffix = '"'
            start = line.find(prefix)
            end = line.rfind(suffix)
            if start < 0 or end <= start + len(prefix):
                continue
            relative_path = line[start + len(prefix):end]
            url = await self.storage_service.build_access_url(
                object_key=(manifest_dir / relative_path).as_posix(),
                public_url=None,
            )
            if url is not None:
                lines[index] = f'{prefix}{url}"'

        return "\n".join(lines) + "\n"

    async def _rewrite_faststart(self, *, source_path: Path, target_path: Path) -> None:
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        command = [
            ffmpeg,
            "-y",
            "-i",
            str(source_path),
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(target_path),
        ]
        completed = await asyncio.to_thread(
            subprocess.run,
            command,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise InfrastructureError(message=f"Failed to optimize MP4 for streaming: {completed.stderr.strip()}")

    async def _probe_duration_seconds(self, video_path: Path) -> int | None:
        ffmpeg = Path(imageio_ffmpeg.get_ffmpeg_exe())
        ffprobe = ffmpeg.with_name("ffprobe.exe" if ffmpeg.suffix.lower() == ".exe" else "ffprobe")
        if not ffprobe.exists():
            return await self._probe_duration_seconds_with_ffmpeg(ffmpeg, video_path)

        command = [
            str(ffprobe),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ]
        completed = await asyncio.to_thread(
            subprocess.run,
            command,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            return await self._probe_duration_seconds_with_ffmpeg(ffmpeg, video_path)

        try:
            duration = float((completed.stdout or "").strip())
        except ValueError:
            return await self._probe_duration_seconds_with_ffmpeg(ffmpeg, video_path)
        if duration <= 0:
            return await self._probe_duration_seconds_with_ffmpeg(ffmpeg, video_path)
        return max(1, int(round(duration)))

    async def _probe_duration_seconds_with_ffmpeg(self, ffmpeg: Path, video_path: Path) -> int | None:
        command = [
            str(ffmpeg),
            "-i",
            str(video_path),
        ]
        completed = await asyncio.to_thread(
            subprocess.run,
            command,
            capture_output=True,
            text=True,
        )
        output = (completed.stderr or "") + "\n" + (completed.stdout or "")
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
        if not match:
            return None
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))
        total_seconds = (hours * 3600) + (minutes * 60) + seconds
        if total_seconds <= 0:
            return None
        return max(1, int(round(total_seconds)))

    async def _generate_hls(self, *, source_path: Path, output_dir: Path) -> None:
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        output_playlist = output_dir / self.playlist_name

        copy_command = [
            ffmpeg,
            "-y",
            "-i",
            str(source_path),
            "-c",
            "copy",
            "-f",
            "hls",
            "-hls_time",
            "4",
            "-hls_playlist_type",
            "vod",
            "-hls_segment_type",
            "fmp4",
            "-hls_fmp4_init_filename",
            self.init_segment_name,
            "-hls_segment_filename",
            str(output_dir / "segment_%03d.m4s"),
            str(output_playlist),
        ]
        copy_result = await asyncio.to_thread(
            subprocess.run,
            copy_command,
            capture_output=True,
            text=True,
        )
        if copy_result.returncode == 0:
            return

        transcode_command = [
            ffmpeg,
            "-y",
            "-i",
            str(source_path),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-f",
            "hls",
            "-hls_time",
            "4",
            "-hls_playlist_type",
            "vod",
            "-hls_segment_type",
            "fmp4",
            "-hls_fmp4_init_filename",
            self.init_segment_name,
            "-hls_segment_filename",
            str(output_dir / "segment_%03d.m4s"),
            str(output_playlist),
        ]
        transcode_result = await asyncio.to_thread(
            subprocess.run,
            transcode_command,
            capture_output=True,
            text=True,
        )
        if transcode_result.returncode != 0:
            raise InfrastructureError(message=f"Failed to generate HLS stream: {transcode_result.stderr.strip()}")

    async def _upload_hls_directory(self, *, object_key: str, source_dir: Path) -> None:
        hls_prefix = self.build_hls_prefix(object_key)
        upload_tasks = []
        for file_path in source_dir.iterdir():
            if not file_path.is_file():
                continue
            if file_path.suffix == ".m3u8":
                content_type = "application/vnd.apple.mpegurl"
            elif file_path.suffix == ".m4s":
                content_type = "video/iso.segment"
            else:
                content_type = "video/mp4"
            upload_tasks.append(
                self.storage_service.upload_file(
                    object_key=f"{hls_prefix}/{file_path.name}",
                    file_path=file_path,
                    content_type=content_type,
                )
            )

        if upload_tasks:
            await asyncio.gather(*upload_tasks)
