from __future__ import annotations

import asyncio
import json
import re
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph

from app.infra.ai.video_content_analyzer import VideoContentAnalyzer


class VideoContentState(TypedDict):
    user_id: int
    video_url: str
    video_title: str
    video_summary: str
    request_text: str
    page_context: dict[str, Any]
    transcript: str
    visual_analysis: str
    frame_count: int
    video_duration_seconds: float | None
    generated_output: str
    suggested_actions: list[dict[str, Any]]
    status: str


async def _ask(llm: Any, system: str, prompt: str) -> str:
    response = await asyncio.wait_for(
        llm.ainvoke([SystemMessage(content=system), HumanMessage(content=prompt)]),
        timeout=60,
    )
    return str(getattr(response, "content", response)).strip()


def _extract_json_object(raw: str) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.S)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None


def _default_video_output(state: VideoContentState) -> str:
    page_context = state.get("page_context") or {}
    current_video = page_context.get("current_video") if isinstance(page_context, dict) else None
    action_lines: list[str] = []
    if isinstance(page_context.get("available_actions"), list):
        for action in page_context["available_actions"][:4]:
            if not isinstance(action, dict):
                continue
            label = str(action.get("label") or "").strip()
            href = str(action.get("href") or "").strip()
            if not label:
                continue
            action_lines.append(f"- [{label}]({href})" if href else f"- {label}")

    lines = [
        "## 视频内容总结",
        f"- 视频标题：**{state.get('video_title') or '未命名视频'}**",
        f"- 抽帧数量：{state.get('frame_count', 0)}",
        "",
        "## 画面理解",
        state.get("visual_analysis") or "暂未提取到稳定的画面理解结果。",
        "",
        "## 语音内容",
        state.get("transcript") or "暂未提取到稳定的语音内容。",
    ]

    if isinstance(current_video, dict) and current_video.get("summary"):
        lines.extend(["", "## 页面已有摘要", str(current_video.get("summary"))])

    if action_lines:
        lines.extend(["", "## 可继续执行", *action_lines])

    return "\n".join(lines).strip()


class VideoContentAgent:
    """Dedicated LangGraph agent for extracting and reusing video content."""

    def __init__(self, llm: Any, analyzer: VideoContentAnalyzer) -> None:
        self.llm = llm
        self.analyzer = analyzer
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(VideoContentState)
        graph.add_node("extract_video_content", self._extract_video_content)
        graph.add_node("generate_artifact", self._generate_artifact)
        graph.set_entry_point("extract_video_content")
        graph.add_edge("extract_video_content", "generate_artifact")
        graph.add_edge("generate_artifact", "__end__")
        return graph.compile()

    async def _extract_video_content(self, state: VideoContentState) -> VideoContentState:
        artifacts = await self.analyzer.analyze(
            video_url=state["video_url"],
            user_request=state["request_text"],
            video_title=state.get("video_title", ""),
            video_summary=state.get("video_summary", ""),
        )
        state["transcript"] = artifacts.transcript
        state["visual_analysis"] = artifacts.visual_analysis
        state["frame_count"] = artifacts.frame_count
        state["video_duration_seconds"] = artifacts.video_duration_seconds
        state["status"] = "content_extracted"
        return state

    async def _generate_artifact(self, state: VideoContentState) -> VideoContentState:
        page_context = state.get("page_context") or {}
        available_actions = page_context.get("available_actions") if isinstance(page_context, dict) else []
        prompt = f"""
You are LingLearn's video-content agent.
You already have extracted information from a lecture video. Based on the user's request, generate a practical result.

User request:
{state["request_text"]}

Video title:
{state.get("video_title") or "Unknown"}

Video summary:
{state.get("video_summary") or "Unknown"}

Extracted speech/audio content:
{state.get("transcript") or "No stable audio extraction result."}

Extracted visual content:
{state.get("visual_analysis") or "No stable visual analysis result."}

Video duration in seconds:
{state.get("video_duration_seconds") or "Unknown"}

Sampled frame count:
{state.get("frame_count") or 0}

Current page actions:
{available_actions}

Return strict JSON:
{{
  "generated_output": "A polished Markdown result tailored to the user's request. For summaries, synthesize the full video into one coherent answer instead of pasting raw transcript or raw frame analysis. Cover the opening, the core teaching flow, and the ending or transition when supported by the extracted evidence.",
  "suggested_actions": [
    {{"label": "动作名称", "href": "/practice", "reason": "为什么推荐"}}
  ]
}}
"""
        try:
            raw = await _ask(
                self.llm,
                "You are a practical educational content generator that turns extracted video understanding into useful artifacts.",
                prompt,
            )
            parsed = _extract_json_object(raw) or {}
        except Exception:
            parsed = {}

        generated_output = str(parsed.get("generated_output") or "").strip()
        if not generated_output:
            generated_output = _default_video_output(state)

        suggested_actions = parsed.get("suggested_actions")
        state["generated_output"] = generated_output
        state["suggested_actions"] = suggested_actions if isinstance(suggested_actions, list) else []
        state["status"] = "completed"
        return state

    async def run(self, state: VideoContentState) -> VideoContentState:
        return await self.graph.ainvoke(state)
