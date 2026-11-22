# DEVIN REVIEW — ChronicleAI Engineering Progress & MVP Evaluation Report

> **Target Audience:** Cognition / Devin Engineering Evaluation Team & Reviewers  
> **Project Title:** ChronicleAI — AI-Assisted Historical Research & Educational Video Production  
> **Case Study 1:** Emperor Le Thanh Tong of Dai Viet (1460–1497)  
> **Repository:** `https://github.com/hoangquan91029/ChronicleAI`  
> **Automated Test Results:** 29 Passed, 0 Failed (87% Measured Statement Coverage)  
> **Report Timestamp:** November 22, 2026

---

## 1. Project Overview

ChronicleAI is an open-source platform designed to address hallucination and citation fabrication in AI-assisted educational video generation. When converting historical manuscripts into video scripts, standard large language models frequently invent dates, attribute fictitious sayings, and hallucinate citations.

ChronicleAI enforces a strict provenance-first pipeline:
1. **Document Ingestion:** Ingests PDF documents, extracts text with Unicode fidelity using PyMuPDF, detects image-only/scanned files to mandate OCR, and segments text into traceable, page-bound chunks.
2. **Citation-Grounded Retrieval & Verification:** Indexes chunks and classifies claims into `SUPPORTED`, `CONTRADICTED`, and `INSUFFICIENT_EVIDENCE` strictly against ingested text.
3. **Structured Scriptwriting:** Generates educational video narratives that distinctly separate verified facts, authentic quotations, and creative fictional dramatizations.
4. **Minimalist Storyboard Generation:** Converts script scenes into visual storyboards with 2D minimalist vector animation directions and AI image generation prompts.

---

## 2. Implemented Features vs. Baseline Architecture

To maintain complete engineering honesty during review, we distinguish between fully implemented dynamic pipelines and deterministic baseline components:

| Feature Area | Current Implementation Status | Real Mechanism & Limitations |
|---|---|---|
| **PyMuPDF Ingestion** | **Production Grade** | Real PyMuPDF stream parsing, Unicode NFC normalization, oversized sentence splitting at word boundaries, overlap preservation, and scanned-PDF detection. |
| **Document Chunking** | **Production Grade** | Deterministic hash-based chunk IDs (`{doc_id}_p{page:02d}_c{idx:03d}`), strict page preservation, and zero text loss across boundaries. |
| **Vector Retrieval** | **Functional Baseline** | Multilingual n-gram and subword TF-IDF embedding vectorizer with cosine similarity ranking. Sufficient for localized benchmarks; needs ChromaDB/FAISS scaling for enterprise corpora. |
| **Claim Verification** | **Hybrid Engine** | Deterministic NLI heuristic baseline validating calendar years, key entities, and negation conflicts. Remote Gemini provider integration available when `GEMINI_API_KEY` is supplied. |
| **Script & Storyboard** | **Structured Prototype** | Built-in 7-scene narrative calibrated for the Emperor Le Thanh Tong benchmark fixture. Remote LLM provider integrated to dynamically generate novel scripts for arbitrary figures when API keys are configured. |
| **Web Dashboard** | **Fully Functional** | Next.js 14 App Router with responsive Tailwind CSS interface for document ingestion, chunk inspection, RAG querying, claim verification, and export. |
| **Containerization** | **Fully Operational** | Docker Compose orchestration with healthchecks, Pydantic CORS parsing, and multi-stage builds. |

---

## 3. Technical Architecture

```
                    +------------------------------------+
                    |        Uploaded Historical PDF     |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    |  PyMuPDF Text Extraction & OCR Scan |
                    |      (Unicode NFC Normalization)   |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    | Page-Bound Sliding Window Chunker  |
                    |   (Zero Text Loss, Stable Hash ID) |
                    +-----------------+------------------+
                                      |
                         +------------+------------+
                         |                         |
                         v                         v
              +----------+---------+    +----------+---------+
              | Multilingual Vector|    | JSON Chunk Export  |
              |   Store & Index    |    | (demo_output/)     |
              +----------+---------+    +--------------------+
                         |
            +------------+------------+
            |                         |
            v                         v
  +---------+----------+    +---------+----------+
  | Citation Retrieval |    | Claim Verification |
  | & Semantic Search  |    | (3-Label NLI Check)|
  +---------+----------+    +---------+----------+
            |                         |
            +------------+------------+
                         |
                         v
  +----------------------+-----------------------+
  | Educational Scriptwriter (15-20 Min Narrative|
  | Labeled Fictional Dialogue vs Verified Quotes|
  +----------------------+-----------------------+
                         |
                         v
  +----------------------+-----------------------+
  |  2D Minimalist Vector Storyboard Generator   |
  |  (AI Image Prompts, Pacing, Camera Directs)  |
  +----------------------------------------------+
```

---

## 4. Exact Reproduction Commands

All results can be independently reproduced from the repository root:

### A. Run Automated Pytest Suite with Statement Coverage
```bash
pytest --cov=backend/app --cov-report=term-missing backend/tests
```
*Expected Result:* 29 passed in ~2.5s, 87% statement coverage.

### B. Run Document Ingestion CLI Demo
```bash
python scripts/run_demo_extraction.py
```
*Expected Result:* Generates `demo_output/chunks.json` containing 15 structured chunks from the 5-page sample document.

### C. Build and Run Containerized Application
```bash
docker compose up --build
```
- Frontend Dashboard: `http://localhost:3000`
- FastAPI Backend Docs: `http://localhost:8000/docs`
- Healthcheck Endpoint: `http://localhost:8000/api/health`

---

## 5. Automated Test Results

The test suite contains 29 comprehensive automated tests across 7 test suites:
- `test_pdf_processor.py` (11 tests): Extraction, page preservation, scanned PDF handling, empty PDF handling, corrupt PDF handling, chunk boundary enforcement, oversized sentence splitting, overlap validation, zero text loss, and Unicode NFC normalization.
- `test_vector_and_retrieval.py` (4 tests): Document indexing, semantic retrieval of specific achievements, territorial defense search, and out-of-domain query rejection.
- `test_claim_verifier.py` (4 tests): Verified claims (`SUPPORTED`), counter-factual claims (`CONTRADICTED`), uncorroborated assertions (`INSUFFICIENT_EVIDENCE`), and citation anti-hallucination.
- `test_scriptwriter.py` (2 tests): 7-scene narrative structure and explicit labeling of dramatized fictional dialogue.
- `test_storyboard.py` (2 tests): 2D minimalist vector storyboard generation and visual prompt generation.
- `test_api_endpoints.py` (5 tests): Health, document listing, search, verification, and script generation endpoints.
- `test_e2e_integration.py` (1 test): Complete end-to-end user journey across all pipeline stages.

---

## 6. Sample Extraction Output

Extracted chunk format from `demo_output/chunks.json`:

```json
{
  "chunk_id": "doc_demo_p01_c001",
  "document_id": "doc_demo",
  "source": "le_thanh_tong_dai_viet.pdf",
  "page": 1,
  "text": "ĐẠI VIỆT THỜI LÊ THÁNH TÔNG (1460 - 1497)\nTrang 1: Lên ngôi & Cuộc Cải cách Hành chính Hồng Đức...",
  "word_count": 78
}
```

---

## 7. Known Limitations & Technical Debt

1. **Synthetic Benchmark Fixture:** `backend/sample_data/le_thanh_tong_dai_viet.pdf` is generated programmatically via ReportLab for automated testing. While historical facts and excerpts align with scholarly consensus, it is not an original archival scan.
2. **Vector Index Scalability:** The current vector store uses an in-memory TF-IDF index. While zero-dependency and fast for unit tests, production deployments will benefit from persistent ChromaDB or FAISS.
3. **Dynamic Scripting for Arbitrary Figures:** Dynamic generation for unmodeled historical figures requires remote LLM integration with an active API key (`GEMINI_API_KEY` or `OPENAI_API_KEY`). The offline engine uses a structured historical narrative template calibrated for Emperor Le Thanh Tong.

---

## 8. Work Packages for Additional Devin Bots

ChronicleAI is structured into modular packages suitable for concurrent development by additional Devin autonomous agents:

1. **Devin Work Package A (Archival OCR & Han-Nom Ingestion):**
   - Integrate Tesseract / TrOCR / Transkribus pipelines for scanned woodblock manuscripts.
   - Support dual-layer searchable PDF generation for Han-Nom historical archives.
2. **Devin Work Package B (Vector Store Scaling & Multilingual Embeddings):**
   - Implement persistent ChromaDB / pgvector backend.
   - Benchmark multilingual dense embedding models (e.g., `text-embedding-004` or `BGE-M3`).
3. **Devin Work Package C (Multi-Source Historiographical Conflict Detection):**
   - Ingest multi-source historical chronicles (*Đại Việt Sử Ký Toàn Thư* vs. *Khâm Định Việt Sử Thông Giám Cương Mục*).
   - Build a cross-source reconciliation agent that flags conflicting dates, casualty numbers, and events.
4. **Devin Work Package D (Automated Video Rendering Pipeline):**
   - Connect storyboard scene cards to Remotion.js or FFmpeg pipelines.
   - Render automated 9:16 vertical or 16:9 widescreen educational videos with synthetic TTS narration and synchronized subtitles.
