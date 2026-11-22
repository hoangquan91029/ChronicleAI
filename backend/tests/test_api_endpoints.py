import pytest
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from app.main import app

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_api_root_and_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "ChronicleAI"
        assert "Lê Thánh Tông" in data["case_study"]

        health_resp = await client.get("/api/health")
        assert health_resp.status_code == 200
        health_data = health_resp.json()
        assert health_data["status"] == "healthy"


@pytest.mark.asyncio
async def test_api_document_upload_and_chunks():
    pdf_path = SAMPLE_DIR / "le_thanh_tong_dai_viet.pdf"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with open(pdf_path, "rb") as f:
            files = {"file": ("le_thanh_tong_dai_viet.pdf", f, "application/pdf")}
            upload_resp = await client.post("/api/documents/upload", files=files)
        
        assert upload_resp.status_code == 200
        doc = upload_resp.json()
        doc_id = doc["document_id"]
        assert doc["total_pages"] == 5
        assert doc["total_chunks"] > 0
        assert doc["status"] == "success"

        chunks_resp = await client.get(f"/api/documents/{doc_id}/chunks")
        assert chunks_resp.status_code == 200
        chunks = chunks_resp.json()
        assert len(chunks) == doc["total_chunks"]
        assert chunks[0]["page"] == 1


@pytest.mark.asyncio
async def test_api_rag_search_and_qa():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Search
        search_payload = {"query": "Luật Hồng Đức phụ nữ", "top_k": 3}
        search_resp = await client.post("/api/rag/search", json=search_payload)
        assert search_resp.status_code == 200
        search_data = search_resp.json()
        assert search_data["total_matches"] > 0
        assert search_data["results"][0]["page"] == 2

        # Grounded Q&A
        qa_payload = {"question": "Ai là tác giả câu nói Hiền tài là nguyên khí của quốc gia?"}
        qa_resp = await client.post("/api/rag/answer", json=qa_payload)
        assert qa_resp.status_code == 200
        qa_data = qa_resp.json()
        assert qa_data["grounded"] is True
        assert len(qa_data["citations"]) > 0
        assert qa_data["citations"][0]["page"] == 3


@pytest.mark.asyncio
async def test_api_claim_verification():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "claims": [
                "Lê Thánh Tông thành lập Hội Tao Đàn Nhị Thập Bát Tú năm 1495",
                "Lê Thánh Tông lên ngôi năm 1900",  # Contradicted
                "Lê Thánh Tông chế tạo tên lửa hành trình"  # Insufficient evidence
            ]
        }
        resp = await client.post("/api/verify/claims", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_claims"] == 3
        assert data["supported_count"] >= 1
        assert data["contradicted_count"] >= 1
        assert data["insufficient_evidence_count"] >= 1


@pytest.mark.asyncio
async def test_api_script_and_storyboard_pipeline():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Generate script
        script_payload = {"subject": "Hoàng đế Lê Thánh Tông", "target_minutes": 16}
        script_resp = await client.post("/api/scripts/generate", json=script_payload)
        assert script_resp.status_code == 200
        script = script_resp.json()
        assert script["total_scenes"] >= 5
        assert script["total_estimated_duration_seconds"] >= 800

        # Generate storyboard
        sb_payload = {"subject": "Hoàng đế Lê Thánh Tông"}
        sb_resp = await client.post("/api/storyboards/generate", json=sb_payload)
        assert sb_resp.status_code == 200
        storyboard = sb_resp.json()
        assert storyboard["total_scenes"] == script["total_scenes"]

        # Export script as markdown
        export_script_resp = await client.post("/api/scripts/export/markdown", json=script)
        assert export_script_resp.status_code == 200
        assert "# " in export_script_resp.text
        assert "Cảnh 1" in export_script_resp.text

        # Export storyboard as markdown
        export_sb_resp = await client.post("/api/storyboards/export/markdown", json=storyboard)
        assert export_sb_resp.status_code == 200
        assert "AI Image-Generation Prompt" in export_sb_resp.text
