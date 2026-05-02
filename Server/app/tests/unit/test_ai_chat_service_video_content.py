import asyncio

from app.modules.ai_chat.service import AIChatService


class _StubAgentManager:
    def __init__(self, result: dict) -> None:
        self.result = result

    async def run_video_content_agent(self, *args, **kwargs) -> dict:
        return self.result


def test_generate_video_content_response_prefers_polished_output() -> None:
    async def run_case() -> None:
        service = AIChatService()
        service.agent_manager = _StubAgentManager(
            {
                "generated_output": "## Video Summary\nPolished final summary.",
                "visual_analysis": "Raw visual analysis",
                "transcript": "Raw transcript",
            }
        )

        result = await service._generate_video_content_response(
            None,
            user_id=1,
            latest_user_text="summarize the current video",
            page_context={"current_video": {"video_url": "https://example.com/video.mp4", "title": "Demo"}},
        )

        assert result == "## Video Summary\nPolished final summary."

    asyncio.run(run_case())


def test_generate_video_content_response_appends_evidence_when_requested() -> None:
    async def run_case() -> None:
        service = AIChatService()
        service.agent_manager = _StubAgentManager(
            {
                "generated_output": "## Video Summary\nPolished final summary.",
                "visual_analysis": "Raw visual analysis",
                "transcript": "Raw transcript",
            }
        )

        result = await service._generate_video_content_response(
            None,
            user_id=1,
            latest_user_text="give me transcript and frame evidence",
            page_context={"current_video": {"video_url": "https://example.com/video.mp4", "title": "Demo"}},
        )

        assert result is not None
        assert "Polished final summary." in result
        assert "Raw visual analysis" in result
        assert "Raw transcript" in result

    asyncio.run(run_case())
