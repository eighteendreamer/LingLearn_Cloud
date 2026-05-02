from app.infra.ai.video_content_analyzer import VideoContentAnalyzer


def test_build_frame_sampling_filter_spreads_samples_across_full_duration() -> None:
    filter_expr = VideoContentAnalyzer._build_frame_sampling_filter(
        max_frames=6,
        fallback_interval_seconds=20,
        video_duration_seconds=1020.0,
    )

    assert filter_expr.startswith("fps=0.005882,")
    assert "scale='min(960,iw)':-2" in filter_expr


def test_build_frame_sampling_filter_falls_back_to_configured_interval_without_duration() -> None:
    filter_expr = VideoContentAnalyzer._build_frame_sampling_filter(
        max_frames=6,
        fallback_interval_seconds=20,
        video_duration_seconds=None,
    )

    assert filter_expr == "fps=1/20,scale='min(960,iw)':-2"
