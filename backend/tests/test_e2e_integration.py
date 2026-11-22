import pytest
from pathlib import Path
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import CitationVectorStore
from app.services.claim_verifier import ClaimVerifier
from app.services.scriptwriter import ScriptwriterService
from app.services.storyboard_generator import StoryboardGeneratorService
from app.models.script import ScriptGenerationRequest
from app.models.verification import VerificationLabel

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


@pytest.mark.asyncio
async def test_complete_end_to_end_pipeline():
    """
    Test the full ChronicleAI lifecycle:
    1. PDF Ingestion & PyMuPDF Extraction (5 pages)
    2. Document Chunking & Page Traceability
    3. Multilingual Vector Indexing
    4. RAG Retrieval with Page Citations
    5. Historical Claim Verification (SUPPORTED, CONTRADICTED, INSUFFICIENT_EVIDENCE)
    6. Educational Video Scriptwriting (15-20 min target, labeled dialogues, unverified flags)
    7. 2D Minimalist Animation Storyboard Generation with AI Prompts
    """
    # Step 1 & 2: PDF Processing
    pdf_path = SAMPLE_DIR / "le_thanh_tong_dai_viet.pdf"
    assert pdf_path.exists()
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    processor = PDFProcessor()
    doc_res = processor.process_pdf(pdf_bytes, "le_thanh_tong_dai_viet.pdf", "doc_e2e_001")
    assert doc_res.status == "success"
    assert doc_res.total_pages == 5
    assert doc_res.total_chunks >= 5

    # Step 3: Vector Store Indexing
    vector_store = CitationVectorStore()
    vector_store.add_chunks(doc_res.chunks)
    assert len(vector_store.chunk_list) == len(doc_res.chunks)

    # Step 4: RAG Retrieval
    query = "Một thước núi một tấc sông của ta lẽ nào lại tự tiện vứt bỏ"
    search_res = vector_store.search(query, top_k=2)
    assert len(search_res) > 0
    top_hit = search_res[0]
    assert top_hit.page == 5
    assert top_hit.citation.filename == "le_thanh_tong_dai_viet.pdf"
    assert top_hit.citation.page == 5

    # Step 5: Claim Verification
    verifier = ClaimVerifier(vector_store=vector_store)
    claims_to_test = [
        "Năm Canh Thìn 1460, hoàng tử Lê Tư Thành lên ngôi lấy niên hiệu Quang Thuận",
        "Lê Thánh Tông đăng cơ hoàng đế vào năm 1850",
        "Lê Thánh Tông sáng chế ra máy in thạch bản cơ điện tử"
    ]
    verif_res = await verifier.verify_claims(claims_to_test)
    assert verif_res.results[0].status == VerificationLabel.SUPPORTED
    assert verif_res.results[1].status == VerificationLabel.CONTRADICTED
    assert verif_res.results[2].status == VerificationLabel.INSUFFICIENT_EVIDENCE

    # Step 6: Scriptwriting Agent
    scriptwriter = ScriptwriterService(vector_store=vector_store)
    script = await scriptwriter.generate_script(
        ScriptGenerationRequest(subject="Hoàng đế Lê Thánh Tông (1460-1497)", target_minutes=16)
    )
    assert script.total_scenes >= 5
    assert script.total_estimated_duration_seconds >= 800
    assert script.hook is not None
    assert script.conclusion is not None

    # Step 7: Storyboard Generation
    storyboard_gen = StoryboardGeneratorService()
    storyboard = await storyboard_gen.generate_storyboard(script)
    assert storyboard.total_scenes == script.total_scenes
    for s in storyboard.scenes:
        assert "stick-figure" in s.ai_image_prompt.lower()
        assert s.camera_direction is not None
