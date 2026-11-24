import pytest
import io
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from app.main import app

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_document_validation_and_url_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Invalid PDF magic bytes
        fake_pdf = b"NOT_A_PDF_CONTENT_HERE"
        files = {"file": ("fake.pdf", fake_pdf, "application/pdf")}
        resp = await client.post("/api/documents/upload", files=files)
        assert resp.status_code == 400
        assert "Invalid PDF" in resp.json()["detail"]

        # 2. File too large (>25MB)
        large_fake = b"%PDF-1.4 " + (b"0" * (26 * 1024 * 1024))
        files = {"file": ("large.pdf", io.BytesIO(large_fake), "application/pdf")}
        resp = await client.post("/api/documents/upload", files=files)
        assert resp.status_code == 413
        assert "25MB" in resp.json()["detail"]

        # 3. Register URL document
        url_payload = {
            "url": "https://bvhttdl.gov.vn/di-san-le-thanh-tong-1234.htm",
            "title": "Bản ghi di sản Lê Thánh Tông",
            "description": "Nguồn thư tịch lịch sử số hóa",
            "sample_content": "Lê Thánh Tông đặt niên hiệu Quang Thuận và Hồng Đức. Ông lập Hội Tao Đàn năm 1495."
        }
        resp = await client.post("/api/documents/register-url", json=url_payload)
        assert resp.status_code == 200
        doc_data = resp.json()
        assert doc_data["status"] == "INDEXED"
        doc_id = doc_data["document_id"]
        assert doc_data["filename"] == "Bản ghi di sản Lê Thánh Tông"

        # Verify chunks exist
        chunks_resp = await client.get(f"/api/documents/{doc_id}/chunks")
        assert chunks_resp.status_code == 200
        assert len(chunks_resp.json()) > 0

        # 4. Delete document
        del_resp = await client.delete(f"/api/documents/{doc_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["status"] == "success"
        assert del_resp.json()["document_id"] == doc_id

        # Delete non-existent doc
        del_non_resp = await client.delete("/api/documents/non_existent_doc_id")
        assert del_non_resp.status_code == 404


@pytest.mark.asyncio
async def test_rag_query_and_stats_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Stats
        stats_resp = await client.get("/api/rag/stats")
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        assert "total_chunks" in stats
        assert "total_documents" in stats

        # Query
        query_payload = {
            "query": "Hội Tao Đàn được thành lập năm nào?",
            "top_k": 3
        }
        query_resp = await client.post("/api/rag/query", json=query_payload)
        assert query_resp.status_code == 200
        query_data = query_resp.json()
        assert query_data["question"] == query_payload["query"]
        assert "answer" in query_data


@pytest.mark.asyncio
async def test_script_formats_and_scene_update():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Generate Shorts
        shorts_resp = await client.post("/api/scripts/generate", json={
            "subject": "Lê Thánh Tông",
            "format": "SHORTS"
        })
        assert shorts_resp.status_code == 200
        shorts_data = shorts_resp.json()
        assert shorts_data["format"] == "SHORTS"
        assert shorts_data["total_scenes"] == 3

        # 2. Update Scene in Shorts
        update_payload = {
            "narration": "Cập nhật lời bình cảnh 1 với chứng cứ sử liệu chính xác.",
            "visual_description": "Cảnh quay cận cảnh sắc lệnh Quang Thuận.",
            "estimated_duration_seconds": 18
        }
        update_resp = await client.put("/api/scripts/scenes/1", json=update_payload)
        assert update_resp.status_code == 200
        updated_data = update_resp.json()
        assert updated_data["scenes"][0]["narration"] == update_payload["narration"]
        assert updated_data["scenes"][0]["estimated_duration_seconds"] == 18

        # 3. Update non-existent scene
        bad_scene_resp = await client.put("/api/scripts/scenes/999", json=update_payload)
        assert bad_scene_resp.status_code == 404

        # 4. Generate Explainer
        explainer_resp = await client.post("/api/scripts/generate", json={
            "subject": "Lê Thánh Tông",
            "format": "EXPLAINER"
        })
        assert explainer_resp.status_code == 200
        assert explainer_resp.json()["format"] == "EXPLAINER"

        # 5. Generate Documentary
        doc_resp = await client.post("/api/scripts/generate", json={
            "subject": "Lê Thánh Tông",
            "format": "DOCUMENTARY"
        })
        assert doc_resp.status_code == 200
        assert doc_resp.json()["format"] == "DOCUMENTARY"


@pytest.mark.asyncio
async def test_storyboard_aspect_ratio_and_scene_update():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Generate 9:16 vertical storyboard
        sb_resp = await client.post("/api/storyboards/generate", json={
            "format": "SHORTS",
            "aspect_ratio": "9:16"
        })
        assert sb_resp.status_code == 200
        sb_data = sb_resp.json()
        assert sb_data["aspect_ratio"] == "9:16"
        assert len(sb_data["scenes"]) > 0

        # 2. Update Storyboard Scene
        sb_update_payload = {
            "ai_image_prompt": "Updated visual prompt with historical lacquer painting.",
            "camera_direction": "Slow zoom in"
        }
        sb_update_resp = await client.put("/api/storyboards/scenes/1", json=sb_update_payload)
        assert sb_update_resp.status_code == 200
        updated_sb = sb_update_resp.json()
        assert updated_sb["scenes"][0]["ai_image_prompt"] == sb_update_payload["ai_image_prompt"]

        # 3. Update invalid storyboard scene
        bad_sb_resp = await client.put("/api/storyboards/scenes/999", json=sb_update_payload)
        assert bad_sb_resp.status_code == 404


@pytest.mark.asyncio
async def test_video_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. List videos
        list_resp = await client.get("/api/videos")
        assert list_resp.status_code == 200
        video_list = list_resp.json()
        assert isinstance(video_list, list)

        # 2. Get latest video
        latest_resp = await client.get("/api/videos/latest")
        if len(video_list) > 0:
            assert latest_resp.status_code == 200
            latest_data = latest_resp.json()
            assert "video_id" in latest_data

            vid_id = latest_data["video_id"]
            # 3. Get status
            status_resp = await client.get(f"/api/videos/{vid_id}/status")
            assert status_resp.status_code == 200
            assert status_resp.json()["status"] == "completed"

            # 4. Stream endpoint
            stream_resp = await client.get(f"/api/videos/{vid_id}/stream")
            assert stream_resp.status_code in (200, 206)
            assert "video/mp4" in stream_resp.headers.get("content-type", "")

            # 5. Download endpoint
            down_resp = await client.get(f"/api/videos/{vid_id}/download")
            assert down_resp.status_code == 200
            assert "attachment" in down_resp.headers.get("content-disposition", "")
        else:
            assert latest_resp.status_code == 404

        # 6. Status of non-existent video
        non_vid_status = await client.get("/api/videos/non_existent_vid_123/status")
        assert non_vid_status.status_code == 404
