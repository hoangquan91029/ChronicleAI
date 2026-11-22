import pytest
from pathlib import Path
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import CitationVectorStore
from app.services.claim_verifier import ClaimVerifier
from app.models.verification import VerificationLabel

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


@pytest.fixture
def verifier():
    store = CitationVectorStore()
    pdf_path = SAMPLE_DIR / "le_thanh_tong_dai_viet.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    proc = PDFProcessor()
    res = proc.process_pdf(pdf_bytes, "le_thanh_tong_dai_viet.pdf", "doc_le_thanh_tong")
    store.add_chunks(res.chunks)
    return ClaimVerifier(vector_store=store)


@pytest.mark.asyncio
async def test_verify_supported_claim(verifier):
    claim = "Năm 1484, vua Lê Thánh Tông ra lệnh dựng bia đá khắc tên các vị đỗ Tiến sĩ tại Văn Miếu"
    resp = await verifier.verify_claims([claim])

    assert resp.total_claims == 1
    assert resp.supported_count == 1
    result = resp.results[0]
    assert result.status == VerificationLabel.SUPPORTED
    assert result.confidence > 0.5
    assert len(result.citations) > 0
    assert result.citations[0].page == 3
    assert result.citations[0].filename == "le_thanh_tong_dai_viet.pdf"


@pytest.mark.asyncio
async def test_verify_contradicted_claim(verifier):
    # Contradicting accession year (1520 instead of 1460)
    claim = "Năm 1520, Lê Thánh Tông lên ngôi hoàng đế triều Hậu Lê"
    resp = await verifier.verify_claims([claim])

    assert resp.contradicted_count == 1
    result = resp.results[0]
    assert result.status == VerificationLabel.CONTRADICTED
    assert "Mâu thuẫn" in result.explanation
    assert len(result.citations) > 0


@pytest.mark.asyncio
async def test_verify_insufficient_evidence_claim(verifier):
    # Claim outside historical records
    claim = "Hoàng đế Lê Thánh Tông đã cử phái đoàn ngoại giao vượt biển sang châu Âu diện kiến Nữ hoàng Elizabeth"
    resp = await verifier.verify_claims([claim])

    assert resp.insufficient_evidence_count == 1
    result = resp.results[0]
    assert result.status == VerificationLabel.INSUFFICIENT_EVIDENCE
    assert len(result.citations) == 0
    assert "không chứa đủ thông tin" in result.explanation


@pytest.mark.asyncio
async def test_batch_claim_verification(verifier):
    claims = [
        "Lê Thánh Tông bãi bỏ chức Tể tướng để tập trung quyền lực",
        "Bộ luật Hồng Đức có điều khoản bảo vệ quyền thừa kế của phụ nữ",
        "Vua Lê Thánh Tông bị quân Chiêm Thành đánh bại hoàn toàn năm 1471",  # Contradicted (đại thắng)
        "Vua Lê Thánh Tông phát minh ra máy bay hơi nước"  # Insufficient evidence
    ]
    resp = await verifier.verify_claims(claims)

    assert resp.total_claims == 4
    assert resp.supported_count >= 2
    assert resp.contradicted_count >= 1
    assert resp.insufficient_evidence_count >= 1
