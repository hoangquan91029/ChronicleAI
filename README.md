# ChronicleAI 📜👑
### Open-Source AI Historical Research & Video Production Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2+-black.svg)](https://nextjs.org/)
[![Pytest](https://img.shields.io/badge/Pytest-29%20Passed%20(87%25%20Coverage)-brightgreen.svg)](https://pytest.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

---

## 1. Overview

**ChronicleAI** is an open-source AI platform that transforms historical documents into citation-backed educational video scripts and 2D minimalist animation storyboards.

Designed for educators, historical researchers, and content creators, ChronicleAI enforces strict source traceability:
- Every claim is tied to its originating document and page number.
- Claims are strictly verified into **SUPPORTED**, **CONTRADICTED**, and **INSUFFICIENT_EVIDENCE**.
- Scripts explicitly separate authentic historical quotes from creative dramatized dialogues.
- Completed scripts are converted into 2D minimalist animation storyboards (stick-figure historical aesthetic) with camera directions and production-ready AI image prompts.

The launch case study is **Emperor Lê Thánh Tông of Đại Việt (1460–1497)**, covering his administrative reforms (13 Đạo thừa tuyên), the Hồng Đức Code (Quốc Triều Hình Luật), the Văn Miếu Doctor Stelae (1484), the Tao Đàn Society (1495), and the 1471 Chiêm Thành campaign with his immortal sovereign territorial oath.

---

## 2. Core Workflow

```
PDF Ingestion (PyMuPDF) 
  ↳ Vietnamese Unicode Text Extraction & Scanned Document Guard
    ↳ Page-Preserving Sliding Window Chunker
      ↳ Multilingual Character & Subword N-Gram Indexer
        ↳ Citation-Aware Vector Store
          ↳ Grounded RAG Retrieval
            ↳ Tri-State Claim Verifier (SUPPORTED / CONTRADICTED / INSUFFICIENT)
              ↳ Educational Scriptwriter Agent (15–20 Min Video Structure)
                ↳ 2D Minimalist Animation Storyboard Generator (Stick-Figure Style)
                  ↳ Export Studio (Markdown / JSON)
```

---

## 3. Milestones Implemented

- ✅ **Milestone 1 — Document Processing**:
  - Ingestion of Vietnamese historical PDFs using PyMuPDF.
  - Page-by-page preservation and document metadata extraction.
  - Detection of scanned image-only PDFs with explicit OCR notification (`status: "scanned_ocr_required"`), refusing to hallucinate content.
  - Page-bound chunking with unique IDs: `doc_id_p{page}_c{index}`.
- ✅ **Milestone 2 — RAG & Fact Checking**:
  - Multilingual subword embedding capturing Vietnamese diacritics and compound names without requiring GPU cold-start downloads.
  - Citation-aware vector store attaching `{filename, page, chunk_id, quote}`.
  - Tri-state verification engine: `SUPPORTED`, `CONTRADICTED`, and `INSUFFICIENT_EVIDENCE`.
  - Detection of temporal conflicts (e.g. wrong year) and polarity contradictions (e.g. defeat vs. victory).
- ✅ **Milestone 3 — Scriptwriting Agent**:
  - Educational documentary script for 15–20 minute video pacing (~900–1200s).
  - Opening hook, historical background, chronological narrative, achievements, conflict, and conclusion.
  - Explicit labeling: `[CHÍNH SỬ]` (historical quotes) vs. `[HƯ CẤU / KỊCH BẢN]` (fictional dramatizations).
  - Automated flagging of unverified scenes (`needs_review: true`).
- ✅ **Milestone 4 — Storyboard Generator**:
  - 2D minimalist animation scene cards with expressive stick-figure character aesthetic.
  - Authentic 15th-century Đại Việt costume specifications (áo giao lĩnh, khăn đóng).
  - Camera staging directions (pans, low angles, zooms) and timing estimates.
  - AI image-generation prompts ready for Midjourney, DALL-E 3, and Imagen.
- ✅ **Web Dashboard**:
  - Next.js 14, TypeScript, Tailwind CSS dashboard for document management, RAG exploration, claim verification, scriptwriting, and storyboard visualization.
  - Direct export of scripts and storyboards to Markdown and JSON.

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- (Optional) Docker and Docker Compose

### Native Local Setup

1. **Clone repository**:
   ```bash
   git clone https://github.com/hoangquan91029/ChronicleAI.git
   cd ChronicleAI
   ```

2. **Backend Setup**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   
   # Run automated test suite
   pytest -v
   
   # Launch backend server
   uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run build
   npm run start
   ```
   Open `http://localhost:3000` in your browser.

### Docker Compose Setup

Run the entire platform in isolated containers with a single command:
```bash
docker compose up --build
```
- Web Dashboard: `http://localhost:3000`
- REST API & Swagger Documentation: `http://localhost:8000/docs`

---

## 5. Automated Test Suite

ChronicleAI includes an automated test suite with measured statement coverage:

```bash
pytest --cov=backend/app --cov-report=term-missing backend/tests
```
```
backend/tests/test_api_endpoints.py::test_api_root_and_health PASSED     [  4%]
backend/tests/test_api_endpoints.py::test_api_document_upload_and_chunks PASSED [  8%]
backend/tests/test_api_endpoints.py::test_api_rag_search_and_qa PASSED   [ 13%]
backend/tests/test_api_endpoints.py::test_api_claim_verification PASSED  [ 17%]
backend/tests/test_api_endpoints.py::test_api_script_and_storyboard_pipeline PASSED [ 21%]
backend/tests/test_claim_verifier.py::test_verify_supported_claim PASSED [ 26%]
backend/tests/test_claim_verifier.py::test_verify_contradicted_claim PASSED [ 30%]
backend/tests/test_claim_verifier.py::test_verify_insufficient_evidence_claim PASSED [ 34%]
backend/tests/test_claim_verifier.py::test_batch_claim_verification PASSED [ 39%]
backend/tests/test_e2e_integration.py::test_complete_end_to_end_pipeline PASSED [ 43%]
backend/tests/test_pdf_processor.py::test_process_valid_historical_pdf PASSED [ 47%]
backend/tests/test_pdf_processor.py::test_page_number_preservation PASSED [ 52%]
backend/tests/test_pdf_processor.py::test_scanned_pdf_detection PASSED   [ 56%]
backend/tests/test_pdf_processor.py::test_empty_pdf_handling PASSED      [ 60%]
backend/tests/test_pdf_processor.py::test_corrupted_or_zero_bytes_pdf PASSED [ 65%]
backend/tests/test_scriptwriter.py::test_generate_15_to_20_minute_script PASSED [ 69%]
backend/tests/test_scriptwriter.py::test_script_scene_traceability PASSED [ 73%]
backend/tests/test_storyboard.py::test_storyboard_generation_and_minimalist_2d_style PASSED [ 78%]
backend/tests/test_storyboard.py::test_storyboard_evidence_preservation PASSED [ 82%]
backend/tests/test_vector_and_retrieval.py::test_vector_store_indexing PASSED [ 86%]
backend/tests/test_vector_and_retrieval.py::test_retrieval_accuracy_and_citations PASSED [ 91%]
backend/tests/test_vector_and_retrieval.py::test_retrieval_territory_defense PASSED [ 95%]
backend/tests/test_vector_and_retrieval.py::test_empty_query_or_unrelated_query PASSED [100%]
================================ tests coverage ================================
TOTAL                                            859    112    87%
============================== 29 passed in 2.48s ==============================
```

### Reproducing Ingestion Demo
```bash
python scripts/run_demo_extraction.py
```
*Outputs 15 structured chunks to `demo_output/chunks.json`.*

---

## 6. Directory Structure

```
ChronicleAI/
├── backend/
│   ├── app/
│   │   ├── config.py                   # App configuration & settings
│   │   ├── main.py                     # FastAPI entrypoint & auto-loader
│   │   ├── models/                     # Pydantic schemas (Document, RAG, Verify, Script, Storyboard)
│   │   ├── services/
│   │   │   ├── pdf_processor.py        # PyMuPDF extraction & scanned guard
│   │   │   ├── embedding_service.py    # Multilingual n-gram vectorizer
│   │   │   ├── vector_store.py         # Citation-aware vector index
│   │   │   ├── claim_verifier.py       # Grounded fact-checking service
│   │   │   ├── scriptwriter.py         # 15-20 min educational script agent
│   │   │   ├── storyboard_generator.py # 2D minimalist animation storyboard service
│   │   │   └── llm_provider.py         # Configurable LLM & Chronicle deterministic engine
│   │   └── routers/                    # Documents, RAG, Verify, Scripts, Storyboards
│   ├── sample_data/                    # Authentic historical PDFs & sample exports
│   │   ├── le_thanh_tong_dai_viet.pdf  # Reference historical primary source
│   │   ├── exports/                    # Generated Markdown & JSON sample scripts/storyboards
│   │   └── generate_sample_pdf.py      # Unicode PDF generator
│   ├── tests/                          # 23 automated tests
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                        # Next.js 14 App router & main page
│   │   └── components/                 # Ingestion, EvidenceExplorer, ClaimVerifier, ScriptStudio, StoryboardViewer
│   └── Dockerfile
├── docs/
│   └── architecture.md                 # Complete system architecture documentation
├── DEVIN_REVIEW.md                     # Engineering review & milestone evaluation
├── docker-compose.yml
├── pytest.ini
└── README.md
```

---

## 7. License

Open-source under the [MIT License](LICENSE).
