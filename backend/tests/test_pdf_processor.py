import pytest
import unicodedata
from pathlib import Path
from app.services.pdf_processor import PDFProcessor, PDFProcessingError

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def test_process_valid_historical_pdf():
    pdf_path = SAMPLE_DIR / "le_thanh_tong_dai_viet.pdf"
    assert pdf_path.exists(), "Sample historical PDF must exist"
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    processor = PDFProcessor(chunk_size=400, chunk_overlap=50)
    result = processor.process_pdf(
        pdf_bytes=pdf_bytes,
        filename="le_thanh_tong_dai_viet.pdf",
        document_id="doc_le_thanh_tong_001"
    )

    assert result.status == "success"
    assert result.total_pages == 5
    assert result.total_chunks > 0
    assert result.document_id == "doc_le_thanh_tong_001"
    assert result.filename == "le_thanh_tong_dai_viet.pdf"
    
    # Check that chunks contain expected Vietnamese historical terms
    all_text = " ".join([c.text for c in result.chunks])
    assert "Lê Thánh Tông" in all_text
    assert "Hồng Đức" in all_text
    assert "Thân Nhân Trung" in all_text
    assert "Tao Đàn" in all_text
    assert "Chiêm Thành" in all_text

    # Verify structured chunk attributes
    first_chunk = result.chunks[0]
    assert first_chunk.chunk_id.startswith("doc_le_thanh_tong_001_p01_")
    assert first_chunk.page == 1
    assert first_chunk.source == "le_thanh_tong_dai_viet.pdf"
    assert len(first_chunk.text) > 20
    assert first_chunk.word_count > 0


def test_page_number_preservation():
    pdf_path = SAMPLE_DIR / "le_thanh_tong_dai_viet.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    processor = PDFProcessor()
    result = processor.process_pdf(pdf_bytes, "le_thanh_tong_dai_viet.pdf")

    # Group chunks by page
    page_numbers = {chunk.page for chunk in result.chunks}
    # All 5 pages must be represented
    assert page_numbers == {1, 2, 3, 4, 5}

    # Verify page 3 chunks contain Education / Than Nhan Trung
    p3_chunks = [c for c in result.chunks if c.page == 3]
    assert len(p3_chunks) > 0
    p3_text = " ".join([c.text for c in p3_chunks])
    assert "Thân Nhân Trung" in p3_text
    assert "nguyên khí" in p3_text

    # Verify page 5 chunks contain Nam Chinh 1471 & territorial defense quote
    p5_chunks = [c for c in result.chunks if c.page == 5]
    assert len(p5_chunks) > 0
    p5_text = " ".join([c.text for c in p5_chunks])
    assert "Một thước núi" in p5_text
    assert "Chiêm Thành" in p5_text


def test_scanned_pdf_detection():
    pdf_path = SAMPLE_DIR / "scanned_historical_record.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    processor = PDFProcessor()
    result = processor.process_pdf(pdf_bytes, "scanned_historical_record.pdf")

    # Must detect OCR required and refuse to fabricate text
    assert result.status == "scanned_ocr_required"
    assert result.metadata.is_scanned is True
    assert result.metadata.ocr_required is True
    assert "OCR processing is required" in result.metadata.warning_message
    assert len(result.chunks) == 0


def test_empty_pdf_handling():
    pdf_path = SAMPLE_DIR / "empty_document.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    processor = PDFProcessor()
    result = processor.process_pdf(pdf_bytes, "empty_document.pdf")

    assert result.status == "empty_document"
    assert result.total_chunks == 0
    assert len(result.chunks) == 0


def test_corrupted_or_zero_bytes_pdf():
    processor = PDFProcessor()
    with pytest.raises(PDFProcessingError):
        processor.process_pdf(b"", "empty_file.pdf")
    with pytest.raises(PDFProcessingError):
        processor.process_pdf(b"not a valid pdf header", "corrupt.pdf")


# --- Regression Tests for Priority 0 (Task 1) ---

def test_chunk_size_boundaries():
    """Verify that chunks respect specified chunk_size limits."""
    chunk_size = 120
    chunk_overlap = 20
    proc = PDFProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    text = (
        "Triều đại vua Lê Thánh Tông là giai đoạn phát triển rực rỡ nhất của Đại Việt. "
        "Bộ luật Hồng Đức được ban hành với nhiều điều khoản tiến bộ vượt bậc so với thời đại. "
        "Hội Tao Đàn do vua sáng lập quy tụ 28 vị đại thần uyên bác nhất kinh thành Thăng Long."
    )
    chunks = proc._chunk_page_text(text, page_num=1, doc_id="doc_bounds", filename="sample.pdf", start_index=0)
    assert len(chunks) > 1
    for c in chunks:
        # Each chunk text should be reasonably bounded (allowing minor word-boundary slack)
        assert len(c.text) <= int(chunk_size * 1.35), f"Chunk exceeds bound: {len(c.text)} > {chunk_size * 1.35}"


def test_oversized_sentence_handling():
    """Verify that a sentence longer than chunk_size is cleanly subdivided without data loss."""
    chunk_size = 80
    chunk_overlap = 15
    proc = PDFProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    # A single continuous sentence of ~240 characters without terminal punctuation
    oversized_sentence = (
        "Hoàng đế Lê Thánh Tông ban hành 43 điều quân chính và thiết lập quy chế thao diễn chiến thuật "
        "vô cùng nghiêm ngặt nhằm chấn hưng quân đội và củng cố toàn diện an ninh quốc phòng Đại Việt "
        "trước các nguy cơ xâm lấn biên cương phía Nam"
    )
    assert len(oversized_sentence) > chunk_size * 2
    
    chunks = proc._chunk_page_text(oversized_sentence, page_num=1, doc_id="doc_long", filename="sample.pdf", start_index=0)
    assert len(chunks) >= 3
    
    # Reconstruct text and verify all original words are present
    all_words = set(oversized_sentence.split())
    chunked_words = set(" ".join(c.text for c in chunks).split())
    assert all_words.issubset(chunked_words), "All words from oversized sentence must be preserved"


def test_chunk_overlap_preservation():
    """Verify that consecutive chunks preserve word-boundary overlap."""
    chunk_size = 100
    chunk_overlap = 30
    proc = PDFProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    text = (
        "Đoạn thứ nhất bàn về cải cách hành chính bãi bỏ chức tể tướng và thành lập lục bộ. "
        "Đoạn thứ hai bàn về quy chế thi cử Nho học và khắc bia tiến sĩ tại Văn Miếu."
    )
    chunks = proc._chunk_page_text(text, page_num=2, doc_id="doc_overlap", filename="sample.pdf", start_index=0)
    assert len(chunks) >= 2
    
    # Check that Chunk 2 shares common words from the end of Chunk 1
    words_c1 = chunks[0].text.split()
    words_c2 = chunks[1].text.split()
    common_words = set(words_c1[-5:]).intersection(set(words_c2[:5]))
    assert len(common_words) > 0, "Consecutive chunks must share overlapping words"


def test_no_missing_text():
    """Verify that no paragraphs or trailing sentences are dropped during chunking."""
    proc = PDFProcessor(chunk_size=100, chunk_overlap=25, min_chunk_chars=30)
    paragraphs = [
        "Đoạn đầu tiên ghi chép năm lên ngôi Canh Thìn 1460.",
        "Đoạn thứ hai ghi chép về cải cách 13 đạo thừa tuyên.",
        "Đoạn thứ ba kết luận về thịnh trị Hồng Đức."  # Trailing short paragraph
    ]
    full_text = "\n\n".join(paragraphs)
    chunks = proc._chunk_page_text(full_text, page_num=1, doc_id="doc_no_loss", filename="sample.pdf", start_index=0)
    
    combined_chunk_text = " ".join(c.text for c in chunks)
    for p in paragraphs:
        # Check every paragraph has its core words present
        p_words = p.split()
        for w in p_words:
            assert w in combined_chunk_text, f"Word '{w}' from paragraph was dropped!"


def test_vietnamese_unicode_preservation():
    """Verify that complex Vietnamese diacritics and NFC normalization are strictly preserved."""
    proc = PDFProcessor()
    vietnamese_sample = (
        "Vua Lê Thánh Tông trị vì: Hồng Đức, Thuận Hóa, Thừa tuyên, Quảng Nam, "
        "Thân Nhân Trung, nguyên khí quốc gia, hiền tài, Quốc Triều Hình Luật, "
        "Một thước núi, một tấc sông của ta lẽ nào lại tự tiện vứt bỏ?"
    )
    cleaned = proc._clean_text(vietnamese_sample)
    assert unicodedata.is_normalized("NFC", cleaned)
    
    chunks = proc._chunk_page_text(cleaned, page_num=1, doc_id="doc_vn", filename="sample.pdf", start_index=0)
    assert len(chunks) > 0
    chunk_text = chunks[0].text
    
    # Exact Unicode diacritic matches
    for term in ["Lê Thánh Tông", "Hồng Đức", "Thừa tuyên", "Quảng Nam", "Thân Nhân Trung", "nguyên khí", "Một thước núi"]:
        assert term in chunk_text, f"Unicode term '{term}' was altered or corrupted"


def test_stable_deterministic_chunk_ids():
    """Verify that chunk IDs and document IDs are deterministic and stable across repeated runs."""
    pdf_path = SAMPLE_DIR / "le_thanh_tong_dai_viet.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    proc = PDFProcessor()
    res1 = proc.process_pdf(pdf_bytes, "le_thanh_tong_dai_viet.pdf")
    res2 = proc.process_pdf(pdf_bytes, "le_thanh_tong_dai_viet.pdf")

    assert res1.document_id == res2.document_id
    assert len(res1.chunks) == len(res2.chunks)
    for c1, c2 in zip(res1.chunks, res2.chunks):
        assert c1.chunk_id == c2.chunk_id
        assert c1.page == c2.page
        assert c1.text == c2.text
