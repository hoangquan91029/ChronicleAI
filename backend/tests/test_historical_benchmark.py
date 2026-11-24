import pytest
import json
from pathlib import Path

from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import CitationVectorStore
from app.services.llm_provider import ChronicleOfflineRuleEngine
from app.models.verification import VerificationLabel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BENCHMARK_DIR = BASE_DIR / "benchmarks" / "le_thanh_tong"
CLAIMS_PATH = BENCHMARK_DIR / "claims.json"
PDF_PATH = BASE_DIR / "backend" / "sample_data" / "le_thanh_tong_dai_viet.pdf"


@pytest.fixture(scope="module")
def benchmark_data():
    with open(CLAIMS_PATH, "r", encoding="utf-8") as f:
        claims = json.load(f)

    processor = PDFProcessor()
    ingest_res = processor.process_pdf(str(PDF_PATH), filename="le_thanh_tong_dai_viet.pdf", document_id="doc_bench")
    
    vector_store = CitationVectorStore()
    vector_store.add_chunks(ingest_res.chunks)

    engine = ChronicleOfflineRuleEngine()
    return claims, vector_store, engine


@pytest.fixture(scope="module")
def authentic_benchmark_data():
    archive_file = BASE_DIR / "data" / "sources" / "dai_viet_su_ky_toan_thu_ban_ky_thuc_luc_quyen_12_13.json"
    claims_file = BASE_DIR / "benchmarks" / "authentic_archival" / "claims.json"
    
    if not claims_file.exists() or not archive_file.exists():
        pytest.skip("Authentic archival benchmark files not found")

    with open(claims_file, "r", encoding="utf-8") as f:
        claims = json.load(f)

    with open(archive_file, "r", encoding="utf-8") as f:
        archive_data = json.load(f)

    from app.models.document import ChunkMetadata
    chunks = []
    for i, sec in enumerate(archive_data["sections"]):
        chunk_id = f"chunk_dvsktt_{sec['folio_ref']}"
        chunk = ChunkMetadata(
            chunk_id=chunk_id,
            document_id="doc_dvsktt_1697_bktl",
            chunk_index=i,
            page=sec["quyen"],
            text=sec["text"],
            source=archive_data["source_title"],
            word_count=len(sec["text"].split()),
            source_id=archive_data["source_id"],
            source_title=sec["historical_topic"],
            original_url=sec["iiif_image_url"],
            folio_ref=sec["folio_ref"]
        )
        chunks.append(chunk)

    vector_store = CitationVectorStore()
    vector_store.add_chunks(chunks)
    engine = ChronicleOfflineRuleEngine()
    return claims, vector_store, engine


def test_benchmark_dataset_integrity(benchmark_data):
    claims, _, _ = benchmark_data
    assert len(claims) >= 20, "Benchmark must contain at least 20 evaluation claims"

    labels = set(c["expected_label"] for c in claims)
    assert "SUPPORTED" in labels
    assert "CONTRADICTED" in labels
    assert "INSUFFICIENT_EVIDENCE" in labels


@pytest.mark.asyncio
async def test_historical_benchmark_execution(benchmark_data):
    claims, vector_store, engine = benchmark_data

    correct = 0
    total = len(claims)

    for item in claims:
        claim_text = item["claim"]
        expected = item["expected_label"]

        retrieved = vector_store.search(claim_text, top_k=4, min_score=0.08)
        verif = await engine.verify_claim(claim_text, retrieved)

        if verif.status.value == expected:
            correct += 1

        # Check citation validity for supported claims
        if expected == "SUPPORTED":
            assert len(verif.citations) > 0, f"Supported claim {item['claim_id']} must have at least one citation"
            assert verif.citations[0].page > 0
            assert len(verif.citations[0].quote) > 0

    accuracy = correct / total
    assert accuracy >= 0.85, f"Benchmark accuracy must be >= 85%, got {accuracy*100:.1f}%"


@pytest.mark.asyncio
async def test_authentic_archival_benchmark_execution(authentic_benchmark_data):
    claims, vector_store, engine = authentic_benchmark_data

    correct = 0
    total = len(claims)

    for item in claims:
        claim_text = item["claim"]
        expected = item["expected_label"]

        retrieved = vector_store.search(claim_text, top_k=4, min_score=0.06)
        verif = await engine.verify_claim(claim_text, retrieved)

        if verif.status.value == expected:
            correct += 1

        if expected == "SUPPORTED":
            assert len(verif.citations) > 0, f"Supported claim {item['claim_id']} must have citation"
            assert verif.citations[0].page > 0

    accuracy = correct / total
    assert accuracy >= 0.90, f"Authentic benchmark accuracy must be >= 90%, got {accuracy*100:.1f}%"

