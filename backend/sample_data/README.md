# ChronicleAI Sample Test Fixtures & Archival Roadmap

## 1. Nature of Current Sample Fixtures

The PDF files located in this directory (`le_thanh_tong_dai_viet.pdf`, `scanned_historical_record.pdf`, `empty_document.pdf`) are **synthetic benchmark fixtures** generated automatically via ReportLab (`generate_sample_pdf.py`).

- **`le_thanh_tong_dai_viet.pdf`**: A 5-page synthetic document formatted to simulate historical chronicles regarding Emperor Lê Thánh Tông (1460–1497). While the historical facts, quotes, and legal reforms reflect consensus scholarly history (e.g., *Đại Việt Sử Ký Toàn Thư*, *Khâm Định Việt Sử Thông Giám Cương Mục*), this file is **not** an authentic primary archival manuscript or digitized primary artifact.
- **`scanned_historical_record.pdf`**: A synthetic test fixture containing an image raster without embedded text streams, used to verify OCR fallback detection.
- **`empty_document.pdf`**: An empty 1-page canvas used to verify zero-content handling and graceful error reporting.

These fixtures exist exclusively for deterministic CI/CD regression testing, PyMuPDF Unicode extraction validation, and offline retrieval demonstrations.

---

## 2. Ingestion Roadmap for Authentic Historical Sources

For production deployments and scholarly historical research, ChronicleAI will ingest authentic primary and secondary archival materials:

1. **Digitized Han-Nom Archival Manuscripts**:
   - Integration with open archives from the **National Library of Vietnam (Thư viện Quốc gia Việt Nam)** and the **Institute of Han-Nom Studies (Viện Nghiên cứu Hán Nôm)**.
   - Processing woodblock prints (*Mộc bản triều Nguyễn*) and stone steles (*Văn bia tiến sĩ Văn Miếu*).
2. **Archival OCR & Transkribus / Hán-Nôm OCR Integration**:
   - For scanned woodblocks and manuscripts, routing through specialized Sino-Nom character recognition models or dual-layer searchable PDF engines rather than ungrounded hallucination.
3. **Multi-Source Cross-Referencing & Historiographical Discrepancies**:
   - Ingesting parallel historical chronicles (*Đại Việt Sử Ký Toàn Thư*, *Việt Sử Tiêu Án*, *Khâm Định Việt Sử Thông Giám Cương Mục*) to detect and highlight historiographical discrepancies (e.g., conflicting accounts of military campaigns or administrative changes) rather than presenting a single source as unquestioned truth.
4. **Scholarly Citation & Provenance**:
   - Standardizing archival citations according to archival call numbers, volume (*quyển*), and folio/leaf numbers (*tờ*), connecting chunks directly to digital archival repository permalinks.
