# ChronicleAI Changelog

All notable changes to the ChronicleAI project are documented in this file.

---

## [1.0.0] - 2026-11-23

### Completed Autonomous Engineering Delivery

#### Milestone 1: Document Processing & PDF Ingestion
- **PyMuPDF Extraction:** Vietnamese Unicode preservation with exact 1-indexed page number tracking.
- **Configurable Chunking:** Overlapping text chunker (default 180 words, 40-word overlap) with stable traceable IDs (`{doc_id}_p{page:02d}_c{idx:03d}`).
- **Scanned Document Detection:** Automatic OCR detection warning if text density is below threshold.
- **Validation Guardrails:** 25MB file upload limit, `%PDF-` magic byte inspection, and graceful corrupted file handling.
- **SQLite Document Store:** Persistent catalog in `chronicle.db` preserving documents across application restarts.
- **URL Source Registry:** Support for indexing digital archival repositories (`/api/documents/register-url`).

#### Milestone 2: Multilingual RAG & Historical Claim Verification
- **TF-IDF + Cosine Vector Engine:** Multilingual tokenization supporting Vietnamese diacritics and character compounds.
- **Benchmark Separation:** Distinct separation of synthetic test fixtures from authentic historical folios.
- **Authentic Archival Benchmark:** 24 claims verified against *Đại Việt Sử Ký Toàn Thư* (1697 Nội các quan bản, Quyển XII & XIII). Achieved:
  - 100.0% Claim Classification Accuracy (24/24)
  - 100.0% Exact Folio Match (16/16)
  - 100.0% False Claim Rejection (8/8)
- **Three-Way Classification:** Strict categorization into `SUPPORTED`, `CONTRADICTED`, and `INSUFFICIENT_EVIDENCE`.
- **RAG Endpoints:** Added unified `POST /api/rag/query` and `GET /api/rag/stats`.

#### Milestone 3: Multi-Format Scriptwriting
- **Format Flexibility:** Support for `SHORTS` (30–60s, 3 scenes), `EXPLAINER` (3–5m, 4 scenes), and `DOCUMENTARY` (10–20m, 7 scenes).
- **Dialogue Attribution:** Clear distinction between authentic historical quotes and creative dramatizations.
- **Interactive Scene Editing:** Added `PUT /api/scripts/scenes/{scene_number}` for modifying narration and durations.
- **Structured LLM Providers:** Gemini (`gemini-2.5-flash`) and OpenAI (`gpt-4o`) integrations with structured JSON parsing, timeouts, retries, and offline fallback diagnostics (`is_fallback`).

#### Milestone 4: Storyboard Generation
- **Aspect Ratio Control:** Support for `16:9` (horizontal) and `9:16` (vertical mobile).
- **2D Stick-Figure Art Direction:** Prompt engineering producing Vietnamese historical 2D minimalist vector aesthetics.
- **Scene-Level Updates:** Added `PUT /api/storyboards/scenes/{scene_number}` for prompt refinement.

#### Milestone 5: Broadcast Video Production
- **Offline Video Engine:** Pure Python rendering using Pillow (custom stick-figure drawings, typography, citation shield) and FFmpeg.
- **Stereo Audio & Chimes:** Synthesized audio chimes muxed alongside video frames.
- **Subtitle Integration:** Native `mov_text` subtitle stream muxed into MP4 containers for universal playback.
- **Video Streaming API:** Implemented range streaming (`/api/videos/{id}/stream`), status polling (`/api/videos/{id}/status`), and direct download (`/api/videos/{id}/download`).

#### Milestone 6: Next.js Frontend & Production Verification
- **Video Studio Tab:** Integrated HTML5 player, format selector, aspect ratio toggle, timeline breakdown, and download button.
- **Archival Explorer Tab:** Primary source registry with IIIF viewer links and benchmark metric cards.
- **Document Management:** Document library list with deletion and URL archive registration modals.
- **Verification Script:** One-command `./scripts/verify_project.sh` validating the complete toolchain, tests, and build.
- **CI Workflow:** GitHub Actions workflow running tests, benchmarks, and Docker validation on push and pull requests.
