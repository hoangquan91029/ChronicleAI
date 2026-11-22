import pytest
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
