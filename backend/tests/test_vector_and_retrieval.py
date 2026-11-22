import pytest
from pathlib import Path
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import CitationVectorStore

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


@pytest.fixture
def populated_vector_store():
    store = CitationVectorStore()
    pdf_path = SAMPLE_DIR / "le_thanh_tong_dai_viet.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    proc = PDFProcessor()
    res = proc.process_pdf(pdf_bytes, "le_thanh_tong_dai_viet.pdf", "doc_hist_01")
    store.add_chunks(res.chunks)
    return store


def test_vector_store_indexing(populated_vector_store):
    assert len(populated_vector_store.chunk_list) > 0
    assert "doc_hist_01" in populated_vector_store.get_document_ids()


def test_retrieval_accuracy_and_citations(populated_vector_store):
    # Query regarding Doctor Stelae / Than Nhan Trung
    results = populated_vector_store.search("bia tiến sĩ Văn Miếu Thân Nhân Trung", top_k=3)
    assert len(results) > 0
    top = results[0]
    
    # Must retrieve page 3 where Văn Miếu & Thân Nhân Trung are described
    assert top.page == 3
    assert top.source == "le_thanh_tong_dai_viet.pdf"
    assert "Thân Nhân Trung" in top.text
    
    # Citation verification
    cit = top.citation
    assert cit.filename == "le_thanh_tong_dai_viet.pdf"
    assert cit.page == 3
    assert cit.chunk_id == top.chunk_id
    assert len(cit.quote) > 0


def test_retrieval_territory_defense(populated_vector_store):
    # Query regarding territorial defense oath
    results = populated_vector_store.search("Một thước núi một tấc sông của ta lẽ nào tự tiện vứt bỏ", top_k=2)
    assert len(results) > 0
    top = results[0]
    
    # Must retrieve page 5
    assert top.page == 5
    assert "Một thước núi" in top.text


def test_empty_query_or_unrelated_query(populated_vector_store):
    results = populated_vector_store.search("vệ tinh nhân tạo GPS không gian", top_k=3, min_score=0.4)
    # Modern satellite GPS topic must not match 15th-century Dai Viet historical corpus with high score
    assert len(results) == 0
