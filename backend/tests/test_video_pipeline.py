import pytest
import os
import tempfile
from pathlib import Path
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.storyboard import Storyboard, StoryboardScene
from app.models.rag import Citation
from app.services.video_renderer import VideoRendererService


@pytest.fixture
def sample_storyboard():
    citation = Citation(
        filename="le_thanh_tong_dai_viet.pdf",
        page=1,
        chunk_id="chunk_test_001",
        quote="Năm 1460, Hoàng đế Lê Thánh Tông lên ngôi ở tuổi 18.",
        score=0.9
    )
    scenes = [
        StoryboardScene(
            scene_number=1,
            title="Mở đầu: Vị Hoàng đế Lên Ngôi",
            estimated_duration_seconds=4,
            narration="Năm 1460, Hoàng đế Lê Thánh Tông lên ngôi ở tuổi 18 và mở ra thời kỳ hoàng kim.",
            character_dialogue="Trẫm muốn đất nước thái bình thịnh trị.",
            historical_setting="Hoàng thành Thăng Long",
            visual_description="Phim hoạt hình 2D tối giản, vua Lê Thánh Tông khoác hoàng bào vàng.",
            camera_direction="Wide shot",
            character_poses=["Vua đứng uy nghi"],
            ai_image_prompt="Minimalist 2D vector animation style, Emperor Le Thanh Tong, Thang Long",
            evidence_references=[citation]
        ),
        StoryboardScene(
            scene_number=2,
            title="Lời Thề Giữ Đất",
            estimated_duration_seconds=4,
            narration="Vua Lê Thánh Tông khẳng định chủ quyền lãnh thổ bất khả xâm phạm.",
            character_dialogue="Một thước núi, một tấc sông của ta, lẽ nào lại tự tiện vứt bỏ đi được?",
            historical_setting="Biên cương Đại Việt",
            visual_description="Vua chỉ kiếm về biên giới sông núi hùng vĩ.",
            camera_direction="Dynamic angle",
            character_poses=["Vua chỉ kiếm"],
            ai_image_prompt="Emperor holding sword, Vietnamese mountains, border marker",
            evidence_references=[citation]
        )
    ]
    return Storyboard(
        script_title="Khảo Cứu Vua Lê Thánh Tông Test",
        subject="Lê Thánh Tông",
        total_scenes=2,
        total_duration_seconds=8,
        aspect_ratio="16:9",
        visual_theme="Minimalist 2D vector stick-figure",
        scenes=scenes
    )


def test_video_renderer_components(sample_storyboard):
    with tempfile.TemporaryDirectory() as td:
        service = VideoRendererService(exports_dir=Path(td))

        # Test card generation
        card_p = Path(td) / "card.png"
        service.render_scene_card(
            scene=sample_storyboard.scenes[0],
            scene_idx=1,
            total_scenes=2,
            aspect_ratio="16:9",
            output_file=card_p
        )
        assert card_p.exists()
        assert os.path.getsize(card_p) > 1000

        # Test audio generation
        audio_p = Path(td) / "audio.wav"
        service.generate_ambient_scene_audio(duration_seconds=3, output_file=audio_p, scene_idx=1)
        assert audio_p.exists()
        assert os.path.getsize(audio_p) > 10000

        # Test subtitles generation
        srt_p = Path(td) / "subtitles.srt"
        service.generate_subtitles_srt(sample_storyboard.scenes, srt_p)
        assert srt_p.exists()
        content = srt_p.read_text(encoding="utf-8")
        assert "-->" in content
        assert "Lê Thánh Tông" in content

        # Test video rendering to mp4
        status = service.render_storyboard_to_video(
            storyboard=sample_storyboard,
            video_id="test_vid_unit"
        )
        assert status.status == "completed"
        assert status.file_size_bytes > 20000
        assert os.path.exists(status.file_path)


@pytest.mark.asyncio
async def test_video_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Render a short test video
        render_payload = {
            "subject": "Hoàng đế Lê Thánh Tông",
            "format": "SHORTS",
            "aspect_ratio": "16:9"
        }
        resp = await client.post("/api/videos/render", json=render_payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        vid_id = data["video_id"]
        assert data["file_size_bytes"] > 0

        # List videos
        list_resp = await client.get("/api/videos")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

        # Get latest video
        latest_resp = await client.get("/api/videos/latest")
        assert latest_resp.status_code == 200
        assert latest_resp.json()["status"] == "completed"

        # Check status
        status_resp = await client.get(f"/api/videos/{vid_id}/status")
        assert status_resp.status_code == 200
        assert status_resp.json()["video_id"] == vid_id

        # Stream endpoint
        stream_resp = await client.get(f"/api/videos/{vid_id}/stream")
        assert stream_resp.status_code == 200
        assert stream_resp.headers["content-type"] == "video/mp4"

        # Download endpoint
        dl_resp = await client.get(f"/api/videos/{vid_id}/download")
        assert dl_resp.status_code == 200
        assert dl_resp.headers["content-type"] == "video/mp4"
