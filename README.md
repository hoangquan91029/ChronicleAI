# ChronicleAI 📜👑
### Open-Source AI Historical Research & Video Production Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2+-black.svg)](https://nextjs.org/)
[![Pytest](https://img.shields.io/badge/Pytest-52%20Passed%20(82%25%20Coverage)-brightgreen.svg)](https://pytest.org/)
[![Archival Benchmark](https://img.shields.io/badge/Archival%20Benchmark-100%25%20Accuracy%20(DVSKTT%201697)-blue.svg)](benchmarks/authentic_archival/REPORT.md)
[![Video Engine](https://img.shields.io/badge/Video%20Engine-Pillow%20%2B%20FFmpeg-red.svg)](backend/app/services/video_renderer.py)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Overview

**ChronicleAI** is an open-source AI platform that transforms historical documents into citation-backed educational video scripts, 2D minimalist animation storyboards, and broadcast-ready MP4 educational videos with embedded subtitles.

Designed for educators, historical researchers, and content creators, ChronicleAI enforces strict source traceability:
- Every claim is tied to its originating document and page/folio number.
- Claims are strictly verified into **SUPPORTED**, **CONTRADICTED**, and **INSUFFICIENT_EVIDENCE**.
- Scripts explicitly separate authentic historical quotes from creative dramatized dialogues.
- Scripts can be tailored across multiple durations: **SHORTS** (30–60s), **EXPLAINER** (3–5m), and **DOCUMENTARY** (10–20m).
- Completed scripts are converted into 2D minimalist animation storyboards (`16:9` widescreen or `9:16` vertical mobile).
- An offline video engine (Pillow + FFmpeg) renders complete, playable educational MP4 videos with custom artwork, synthesized audio chimes, citation shields, and embedded subtitles.

The launch case study is **Emperor Lê Thánh Tông of Đại Việt (1460–1497)**, covering his administrative reforms (13 Đạo thừa tuyên), the Hồng Đức Code (Quốc Triều Hình Luật), the Văn Miếu Doctor Stelae (1484), the Tao Đàn Society (1495), and the 1471 Chiêm Thành campaign grounded in the 1697 woodblock edition of *Đại Việt Sử Ký Toàn Thư*.

---

## 2. Core Workflow

```
PDF Ingestion & Archival URL Registry (PyMuPDF)
  ↳ Vietnamese Unicode Text Extraction & Scanned Document Guard (25MB Limit)
    ↳ Page-Preserving Sliding Window Chunker & SQLite Document Store (chronicle.db)
      ↳ Multilingual Character & Subword N-Gram Vector Indexer
        ↳ Citation-Aware Vector Store
          ↳ Grounded RAG Retrieval (/api/rag/query)
            ↳ Tri-State Claim Verifier (SUPPORTED / CONTRADICTED / INSUFFICIENT)
              ↳ Educational Scriptwriter Agent (Shorts / Explainer / Documentary)
                ↳ 2D Minimalist Storyboard Generator (16:9 & 9:16 Ratios)
                  ↳ Broadcast Video Engine (Pillow + FFmpeg + Stereo Audio + mov_text Subtitles)
                    ↳ Video Studio & Export (MP4 Streaming, Markdown, JSON)
```

---

## 3. Milestones & Capabilities

- ✅ **Milestone 1 — Document Processing & Persistent Store**:
  - Ingestion of Vietnamese historical PDFs using PyMuPDF.
  - Page-by-page preservation and document metadata extraction.
  - Detection of scanned image-only PDFs with explicit OCR notification (`status: "scanned_ocr_required"`), refusing to hallucinate content.
  - Page-bound chunking with unique IDs: `{doc_id}_p{page}_c{index}`.
  - Persistent SQLite storage in `backend/data/chronicle.db`.
  - Archival digital repository URL registration (`/api/documents/register-url`).
  - Document deletion and size guardrails (25MB limit, `%PDF-` magic byte inspection).
- ✅ **Milestone 2 — Multilingual RAG, Archival Provenance & Benchmarks**:
  - Grounded in canonical woodblock edition: *Đại Việt Sử Ký Toàn Thư — Bản Kỷ Thực Lục* (1697 Nội các quan bản, Quyển XII & XIII) with National Library of Vietnam & EFEO catalog links.
  - Multilingual subword embedding capturing Vietnamese diacritics and compound names without requiring GPU cold-start downloads.
  - Citation-aware vector store attaching `{filename, page, chunk_id, quote, folio_ref, source_id}`.
  - Tri-state verification engine: `SUPPORTED`, `CONTRADICTED`, and `INSUFFICIENT_EVIDENCE`.
  - **Authentic Archival Benchmark**: 24 balanced propositions achieving **100.0% accuracy** (16/16 exact folio matches, 8/8 false claims rejected).
  - **Synthetic Baseline Benchmark**: Evaluates synthetic fixtures separately for controlled regression testing.
- ✅ **Milestone 3 — Scriptwriting Studio & Multi-Provider LLM**:
  - Multi-duration video scripting: **SHORTS** (30–60s, 3 scenes), **EXPLAINER** (3–5m, 4 scenes), and **DOCUMENTARY** (10–20m, 7 scenes).
  - Explicit labeling: `[CHÍNH SỬ]` (historical quotes) vs. `[HƯ CẤU / KỊCH BẢN]` (fictional dramatizations).
  - Interactive scene-level editing via `PUT /api/scripts/scenes/{scene_number}`.
  - Multi-backend LLM integration: Google Gemini (`gemini-2.5-flash`), OpenAI (`gpt-4o`), and deterministic offline rule engine with transparent `is_fallback` diagnostics.
- ✅ **Milestone 4 — 2D Minimalist Storyboard Generator**:
  - Aspect ratio toggle: `16:9` (horizontal) and `9:16` (vertical mobile).
  - 2D minimalist animation scene cards with expressive stick-figure character aesthetic.
  - Authentic 15th-century Đại Việt costume specifications (áo giao lĩnh, khăn đóng).
  - Camera staging directions (pans, low angles, zooms) and timing estimates.
  - AI image-generation prompts ready for Midjourney, DALL-E 3, and Imagen.
  - Interactive scene prompt editing via `PUT /api/storyboards/scenes/{scene_number}`.
- ✅ **Milestone 5 — Broadcast Video Production Engine**:
  - Pure Python rendering using Pillow (custom stick-figure vector drawing, typography, citation shields) and FFmpeg.
  - Synthesized pentatonic audio chimes and stereo waveform generation.
  - Universal embedded `mov_text` subtitle streams muxed directly into the MP4 container.
  - Video streaming API with HTTP range request support (`/api/videos/{id}/stream`), status polling, and direct download.
  - Real verified playable 60s demonstration video: `demo_output/chronicle_demo_video.mp4` (1.8MB).
- ✅ **Milestone 6 — Next.js 14 Dashboard**:
  - 7 interactive workspaces:
    1. Document Ingestion & URL Registry
    2. RAG Evidence Explorer
    3. Claim Verifier
    4. Script Studio (with multi-duration tabs and scene editor)
    5. Storyboard Viewer (with aspect ratio toggle and prompt editor)
    6. Video Studio (with HTML5 player, specs card, and download button)
    7. Archival Provenance Explorer (with IIIF links and benchmark metrics)

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.11+
- FFmpeg
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
   
   # Run automated verification script (toolchains, benchmarks, tests, build)
   ./scripts/verify_project.sh
   
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

Run the entire platform in isolated containers with persistent volumes:
```bash
docker compose up --build
```
- Web Dashboard: `http://localhost:3000`
- REST API & Swagger Documentation: `http://localhost:8000/docs`
- Video Stream: `http://localhost:8000/api/videos/latest/stream`

---

## 5. Verification & Testing

Run all 52 unit and integration tests with statement coverage:
```bash
pytest backend/tests --cov=app --cov-report=term-missing
```

Run historical fact-checking benchmarks:
```bash
export PYTHONPATH=backend
python scripts/evaluate_synthetic_benchmark.py
python scripts/evaluate_authentic_benchmark.py
```

Run complete project verification:
```bash
./scripts/verify_project.sh
```

---

## 6. Directory Structure

```
ChronicleAI/
├── backend/
│   ├── app/
│   │   ├── config.py                   # App configuration & environment settings
│   │   ├── main.py                     # FastAPI entrypoint, lifespan loader & routes
│   │   ├── models/                     # Pydantic schemas (Document, RAG, Script, Storyboard, Video)
│   │   ├── services/
│   │   │   ├── document_store.py       # SQLite persistence (chronicle.db)
│   │   │   ├── pdf_processor.py        # PyMuPDF extraction, 25MB check & OCR guard
│   │   │   ├── embedding_service.py    # Multilingual n-gram vectorizer
│   │   │   ├── vector_store.py         # Citation-aware vector index & stats
│   │   │   ├── claim_verifier.py       # Grounded fact-checking service
│   │   │   ├── scriptwriter.py         # Multi-duration educational script agent
│   │   │   ├── storyboard_generator.py # 2D minimalist animation storyboard service
│   │   │   ├── video_renderer.py       # Pillow + FFmpeg video rendering engine
│   │   │   └── llm_provider.py         # Gemini, OpenAI & Chronicle deterministic engine
│   │   └── routers/                    # Documents, RAG, Verify, Scripts, Storyboards, Videos
│   ├── data/
│   │   ├── chronicle.db                # SQLite database (persisted documents & chunks)
│   │   └── sources/                    # Archival corpora & source registry
│   ├── sample_data/                    # Reference historical PDFs & sample fixtures
│   ├── tests/                          # 52 automated tests across 10 test suites
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                        # Next.js 14 App router & main page
│   │   └── components/                 # Ingestion, RAG, Verify, Script, Storyboard, VideoStudio, ArchivalExplorer
│   └── Dockerfile
├── benchmarks/
│   ├── authentic_archival/             # Authentic DVSKTT 1697 benchmark (results, report, confusion matrix)
│   └── le_thanh_tong/                  # Synthetic baseline benchmark
├── demo_output/
│   ├── chunks.json                     # Extracted chunks demo
│   └── chronicle_demo_video.mp4        # Rendered 60s broadcast demonstration video
├── scripts/
│   ├── verify_project.sh               # One-command end-to-end verification script
│   ├── evaluate_authentic_benchmark.py # Evaluates DVSKTT 1697 claims
│   ├── evaluate_synthetic_benchmark.py # Evaluates synthetic fixture claims
│   └── run_demo_extraction.py          # CLI demo script
├── docker-compose.yml
├── DEVIN_REVIEW.md                     # Engineering review & milestone evaluation
├── CONTRIBUTING.md                     # Contribution guidelines
├── SECURITY.md                         # Security policy & safeguards
├── CHANGELOG.md                        # Project change log
└── README.md
```

---

## 7. License

Open-source under the [MIT License](LICENSE).
