from __future__ import annotations

import asyncio
import base64
import json
import mimetypes
import subprocess
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import imageio_ffmpeg

from app.core.config import get_settings
from app.core.exceptions import InfrastructureError


@dataclass
class VideoExtractionArtifacts:
    transcript: str
    visual_analysis: str
    frame_count: int
    video_duration_seconds: float | None
    audio_path: str | None
    frame_paths: list[str]


class VideoContentAnalyzer:
    """Extract audio and frames from a video, then call external multimodal models."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def analyze(
        self,
        *,
        video_url: str,
        user_request: str,
        video_title: str = "",
        video_summary: str = "",
    ) -> VideoExtractionArtifacts:
        if not video_url.strip():
            raise InfrastructureError(message="Video URL is required for video understanding.")

        base_temp_dir = Path(__file__).resolve().parents[3] / ".tmp" / "linglearn-video"
        base_temp_dir.mkdir(parents=True, exist_ok=True)
        workdir = base_temp_dir / f"job-{uuid4().hex}"
        workdir.mkdir(parents=True, exist_ok=True)
        try:
            video_path = workdir / "source.mp4"
            audio_path = workdir / f"audio.{self.settings.video_extract_audio_format}"
            frames_dir = workdir / "frames"
            frames_dir.mkdir(parents=True, exist_ok=True)

            await self._download_video(video_url, video_path)
            video_duration_seconds = await self._probe_video_duration(video_path)
            extracted_audio = await self._extract_audio(video_path, audio_path)
            frame_paths = await self._extract_frames(
                video_path,
                frames_dir,
                video_duration_seconds=video_duration_seconds,
            )

            transcript = ""
            if extracted_audio is not None:
                try:
                    transcript = await self._caption_audio(extracted_audio)
                except Exception as exc:
                    transcript = f"Audio captioning failed: {exc}"

            visual_analysis = await self._analyze_frames(
                frame_paths=frame_paths,
                user_request=user_request,
                video_title=video_title,
                video_summary=video_summary,
            )

            return VideoExtractionArtifacts(
                transcript=transcript.strip(),
                visual_analysis=visual_analysis.strip(),
                frame_count=len(frame_paths),
                video_duration_seconds=video_duration_seconds,
                audio_path=str(extracted_audio) if extracted_audio else None,
                frame_paths=[str(path) for path in frame_paths],
            )
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    async def _download_video(self, video_url: str, target_path: Path) -> None:
        timeout = httpx.Timeout(180.0, connect=30.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            try:
                async with client.stream("GET", video_url) as response:
                    response.raise_for_status()
                    with target_path.open("wb") as file_obj:
                        async for chunk in response.aiter_bytes():
                            file_obj.write(chunk)
            except httpx.HTTPError as exc:
                raise InfrastructureError(message=f"Failed to download video: {exc}") from exc

    async def _probe_video_duration(self, video_path: Path) -> float | None:
        ffmpeg = Path(imageio_ffmpeg.get_ffmpeg_exe())
        ffprobe = ffmpeg.with_name("ffprobe.exe" if ffmpeg.suffix.lower() == ".exe" else "ffprobe")
        if not ffprobe.exists():
            return None

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
            return None

        try:
            duration = float((completed.stdout or "").strip())
        except ValueError:
            return None
        return duration if duration > 0 else None

    async def _extract_audio(self, video_path: Path, target_path: Path) -> Path | None:
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        command = [
            ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            str(target_path),
        ]
        completed = await asyncio.to_thread(
            subprocess.run,
            command,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            # Some videos may not have an audio track; degrade gracefully.
            return None
        return target_path if target_path.exists() else None

    @staticmethod
    def _build_frame_sampling_filter(
        *,
        max_frames: int,
        fallback_interval_seconds: int,
        video_duration_seconds: float | None,
    ) -> str:
        if video_duration_seconds and video_duration_seconds > 0:
            fps = min(max_frames / video_duration_seconds, float(max_frames))
            fps = max(fps, 1.0 / max(video_duration_seconds, 1.0))
            return f"fps={fps:.6f},scale='min(960,iw)':-2"

        interval_seconds = max(1, int(fallback_interval_seconds))
        return f"fps=1/{interval_seconds},scale='min(960,iw)':-2"

    async def _extract_frames(
        self,
        video_path: Path,
        frames_dir: Path,
        *,
        video_duration_seconds: float | None,
    ) -> list[Path]:
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        max_frames = max(1, int(self.settings.video_extract_max_frames))
        filter_expr = self._build_frame_sampling_filter(
            max_frames=max_frames,
            fallback_interval_seconds=self.settings.video_extract_interval_seconds,
            video_duration_seconds=video_duration_seconds,
        )
        output_pattern = frames_dir / "frame_%03d.jpg"
        command = [
            ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-vf",
            filter_expr,
            "-frames:v",
            str(max_frames),
            "-q:v",
            "4",
            str(output_pattern),
        ]
        completed = await asyncio.to_thread(
            subprocess.run,
            command,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise InfrastructureError(message=f"Failed to extract frames: {completed.stderr.strip()}")

        frame_paths = sorted(frames_dir.glob("frame_*.jpg"))
        if not frame_paths:
            raise InfrastructureError(message="No frames were extracted from the video.")
        return frame_paths

    async def _caption_audio(self, audio_path: Path) -> str:
        api_key = self.settings.video_audio_api_key.strip()
        if not api_key:
            raise InfrastructureError(message="VIDEO_AUDIO_API_KEY is not configured.")

        data = f"data:;base64,{base64.b64encode(audio_path.read_bytes()).decode('utf-8')}"
        payload = {
            "model": self.settings.video_audio_model,
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": data,
                            },
                        }
                    ],
                }
            ],
        }
        response = await self._post_chat_completion(
            base_url=self.settings.video_audio_base_url,
            api_key=api_key,
            payload=payload,
            timeout_seconds=self.settings.video_audio_timeout_seconds,
        )
        return self._extract_response_text(response)

    async def _analyze_frames(
        self,
        *,
        frame_paths: list[Path],
        user_request: str,
        video_title: str,
        video_summary: str,
    ) -> str:
        api_key = self.settings.video_vision_api_key.strip()
        if not api_key:
            raise InfrastructureError(message="VIDEO_VISION_API_KEY is not configured.")

        content_items: list[dict[str, Any]] = [
            {
                "type": "text",
                "text": (
                    "You are a video understanding assistant. Analyze the sampled video frames, "
                    "read slide text when visible, infer the teaching topic, and summarize what "
                    "is being explained. The frames were sampled across the full video timeline, "
                    "so explicitly cover the beginning, middle, and ending when the evidence supports it. "
                    "Return concise but information-dense Markdown.\n\n"
                    f"User request: {user_request or 'Summarize the video content.'}\n"
                    f"Video title: {video_title or 'Unknown'}\n"
                    f"Video summary: {video_summary or 'Unknown'}\n"
                    "Please include: 1) core topic, 2) visible slide or screen text, 3) key knowledge points, "
                    "4) suitable follow-up learning actions."
                ),
            }
        ]
        for path in frame_paths:
            mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
            data_url = f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('utf-8')}"
            content_items.append(
                {
                    "type": "image_url",
                    "image_url": {"url": data_url},
                }
            )

        payload = {
            "model": self.settings.video_vision_model,
            "stream": False,
            "temperature": 0.2,
            "messages": [{"role": "user", "content": content_items}],
        }
        response = await self._post_chat_completion(
            base_url=self.settings.video_vision_base_url,
            api_key=api_key,
            payload=payload,
            timeout_seconds=self.settings.video_vision_timeout_seconds,
        )
        return self._extract_response_text(response)

    async def _post_chat_completion(
        self,
        *,
        base_url: str,
        api_key: str,
        payload: dict[str, Any],
        timeout_seconds: int,
    ) -> dict[str, Any]:
        url = base_url.rstrip("/")
        if not url.endswith("/chat/completions"):
            url = f"{url}/chat/completions"

        timeout = httpx.Timeout(float(timeout_seconds), connect=30.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                    },
                    json=payload,
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = exc.response.text
                raise InfrastructureError(message=f"Video model returned HTTP {exc.response.status_code}: {detail}") from exc
            except httpx.HTTPError as exc:
                raise InfrastructureError(message=f"Video model request failed: {exc}") from exc

        try:
            return response.json()
        except json.JSONDecodeError as exc:
            raise InfrastructureError(message="Video model returned invalid JSON.") from exc

    @staticmethod
    def _extract_response_text(response: dict[str, Any]) -> str:
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            return ""

        choice = choices[0] or {}
        message = choice.get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str) and text.strip():
                        parts.append(text.strip())
            return "\n".join(parts).strip()
        text = choice.get("text")
        return str(text or "").strip()
