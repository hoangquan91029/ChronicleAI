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
        # 1. Broad cross-document search (without document filter)
        search_payload = {"query": "Luật Hồng Đức phụ nữ", "top_k": 3}
        search_resp = await client.post("/api/rag/search", json=search_payload)
        assert search_resp.status_code == 200
        search_data = search_resp.json()
        assert search_data["total_matches"] > 0
        # Check deterministic descending score ranking
        scores = [r["score"] for r in search_data["results"]]
        assert scores == sorted(scores, reverse=True)
        # Verify content relevance
        assert any("hồng đức" in r["text"].lower() or "phụ nữ" in r["text"].lower() for r in search_data["results"])

        # 2. Scoped document filter search: specifically in sample PDF (doc_le_thanh_tong_001)
        doc_filter_payload = {
            "query": "Luật Hồng Đức phụ nữ",
            "document_id": "doc_le_thanh_tong_001",
            "top_k": 3
        }
        doc_resp = await client.post("/api/rag/search", json=doc_filter_payload)
        assert doc_resp.status_code == 200
        doc_data = doc_resp.json()
        assert doc_data["total_matches"] > 0
        assert all(r["document_id"] == "doc_le_thanh_tong_001" for r in doc_data["results"])
        # In sample PDF, administrative and legal reforms are located on page 2
        assert doc_data["results"][0]["page"] == 2
        assert "hồng đức" in doc_data["results"][0]["text"].lower()

        # 3. Explicit page range filter
        page_filter_payload = {
            "query": "Luật Hồng Đức",
            "document_id": "doc_le_thanh_tong_001",
            "min_page": 2,
            "max_page": 2,
            "top_k": 3
        }
        page_resp = await client.post("/api/rag/search", json=page_filter_payload)
        assert page_resp.status_code == 200
        page_data = page_resp.json()
        assert len(page_data["results"]) > 0
        assert all(r["page"] == 2 for r in page_data["results"])

        # 4. Source collection filter (Archival collection)
        src_filter_payload = {
            "query": "cải cách hành chính 13 đạo thừa tuyên",
            "source_id": "DVSKTT-1697-NOI-CAC-QUAN-BAN",
            "top_k": 2
        }
        src_resp = await client.post("/api/rag/search", json=src_filter_payload)
        assert src_resp.status_code == 200
        src_data = src_resp.json()
        if src_data["total_matches"] > 0:
            assert all(r["citation"]["source_id"] == "DVSKTT-1697-NOI-CAC-QUAN-BAN" for r in src_data["results"])

        # 5. Grounded Q&A with document scoping
        qa_payload = {
            "question": "Ai là tác giả câu nói Hiền tài là nguyên khí của quốc gia?",
            "document_id": "doc_le_thanh_tong_001"
        }
        qa_resp = await client.post("/api/rag/answer", json=qa_payload)
        assert qa_resp.status_code == 200
        qa_data = qa_resp.json()
        assert qa_data["grounded"] is True
        assert len(qa_data["citations"]) > 0
        assert qa_data["citations"][0]["page"] == 3
        assert "Thân Nhân Trung" in qa_data["answer"]


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


@pytest.mark.asyncio
async def test_api_document_validation_and_url_registration():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Invalid PDF magic bytes
        fake_files = {"file": ("fake.pdf", b"NOT_A_REAL_PDF_DATA", "application/pdf")}
        resp = await client.post("/api/documents/upload", files=fake_files)
        assert resp.status_code == 400
        assert "Missing %PDF-" in resp.json()["detail"] or "Invalid PDF" in resp.json()["detail"]

        # Register URL source
        url_payload = {
            "url": "https://digitizingvietnam.com/items/show/dvsktt-vol12",
            "title": "Đại Việt Sử Ký Toàn Thư Quyển XII Bản Kỷ Thực Lục",
            "text": "Năm Quang Thuận thứ 8 (1467), vua Lê Thánh Tông sai các nha môn hiệu khám lại sách vở và hoàn thiện điển chế quốc gia.",
            "source_id": "dvsktt_1697",
            "folio_ref": "XII_1a_1b"
        }
        url_resp = await client.post("/api/documents/register-url", json=url_payload)
        assert url_resp.status_code == 200
        url_data = url_resp.json()
        doc_id = url_data["document_id"]
        assert "doc_url_" in doc_id
        assert url_data["total_chunks"] >= 1

        # Retrieve registered document
        get_doc_resp = await client.get(f"/api/documents/{doc_id}")
        assert get_doc_resp.status_code == 200
        assert get_doc_resp.json()["filename"] == url_payload["title"]

        # Delete document
        del_resp = await client.delete(f"/api/documents/{doc_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["status"] == "success"

        # Verify 404 after deletion
        get_after_del = await client.get(f"/api/documents/{doc_id}")
        assert get_after_del.status_code == 404


@pytest.mark.asyncio
async def test_api_rag_query_and_stats():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # RAG Query endpoint
        query_payload = {"query": "Bộ luật Hồng Đức bảo vệ quyền lợi phụ nữ như thế nào?", "top_k": 3}
        query_resp = await client.post("/api/rag/query", json=query_payload)
        assert query_resp.status_code == 200
        q_data = query_resp.json()
        assert q_data["grounded"] is True
        assert len(q_data["citations"]) > 0
        assert len(q_data["retrieved_chunks"]) > 0

        # RAG Stats endpoint
        stats_resp = await client.get("/api/rag/stats")
        assert stats_resp.status_code == 200
        s_data = stats_resp.json()
        assert s_data["total_chunks"] > 0
        assert s_data["total_documents"] > 0
        assert "storage_engine" in s_data

