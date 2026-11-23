# ChronicleAI Implementation Status & Execution Checklist

- **Branch:** `feature/chronicleai-completion`
- **Baseline Commit:** `ec77753e44083139948980753e3444355622f035`
- **Updated:** November 23, 2026
- **Status:** IN PROGRESS

---

## Phase Checklist

### Phase A — Codebase Audit & Gap Analysis
- [ ] Inspect full backend (FastAPI, routers, services, models, tests)
- [ ] Inspect full frontend (Next.js components, pages, API clients)
- [ ] Inspect infra (Dockerfiles, Docker Compose, CI workflows)
- [ ] Document verified findings and gap analysis

### Phase B — Fix Historical Benchmark (P0)
- [ ] Rename & preserve synthetic evaluation as `benchmarks/synthetic_baseline/`
- [ ] Remove misleading claims that synthetic fixture represents archival ingestion
- [ ] Investigate authentic primary source passages from *Đại Việt Sử Ký Toàn Thư — Bản Kỷ Thực Lục* (Quyển XII & XIII)
- [ ] Ingest authentic historical text corpus with verified folio and page citations
- [ ] Create authentic-source benchmark (20+ claims: SUPPORTED, CONTRADICTED, INSUFFICIENT_EVIDENCE)
- [ ] Implement rigorous evaluation metrics (Precision, Recall, F1, Recall@K, exact citation matching)
- [ ] Generate separate reports for synthetic baseline vs. authentic archival evaluation

### Phase C — Production-Ready Document Ingestion (P0)
- [ ] Implement persistent document storage (SQLite / metadata DB + disk files)
- [ ] Add upload status workflow: `UPLOADED` -> `PROCESSING` -> `INDEXED` -> `FAILED`
- [ ] Support searchable PDFs, image-only/scanned detection, Vietnamese Unicode, English
- [ ] Add OCR fallback pipeline where possible (Tesseract / pure-python or clear error reporting)
- [ ] Add URL source registration and multi-document collection support
- [ ] Add robust error handling (corrupted, empty, oversized, MIME validation)

### Phase D — Persistent & Scalable RAG Engine (P0)
- [ ] Implement persistent vector storage with disk indexing (e.g., ChromaDB / persistent vector store)
- [ ] Support hybrid semantic + lexical search with metadata filtering
- [ ] Add duplicate removal and source-aware ranking
- [ ] Preserve exact citation metadata (document_id, source_id, page, chunk_id, folio_ref)
- [ ] Implement `/api/rag/query` with structured evidence responses and citation verification

### Phase E — Complete Gemini & OpenAI Integration (P1)
- [ ] Complete real Gemini provider implementation with Pydantic structured output
- [ ] Complete real OpenAI provider implementation with Pydantic structured output
- [ ] Add transparent status diagnostics (never silently fake real API outputs)
- [ ] Add retry with backoff, timeouts, and token/usage logging
- [ ] Add prompt injection defenses for uploaded untrusted documents

### Phase F — Advanced Historical Fact Checker (P1)
- [ ] Claim decomposition and evidence extraction
- [ ] Multi-source comparison and historical disagreement vs. contradiction distinction
- [ ] Uncertainty handling and detailed contradiction explanations
- [ ] Robust entity and date validation

### Phase G — Dynamic Multi-Format Scriptwriter (P1)
- [ ] Support multiple durations: Shorts (30-60s), Explainers (3-5m), Documentaries (10-20m)
- [ ] Dynamic scene generation for arbitrary historical subjects without hardcoding
- [ ] Clear demarcation of verified historical quotes vs. fictional dramatizations
- [ ] Support scene-level editing and regeneration
- [ ] Export to structured JSON and formatted Markdown

### Phase H — Enhanced Storyboard Generator (P1)
- [ ] Scene-by-scene planning with camera staging, motion, character specifications
- [ ] Minimalist 2D Vietnamese historical educational animation style (16:9 & 9:16)
- [ ] AI image generation prompts with costume authenticity
- [ ] Scene-level regeneration support

### Phase I — Playable Video Production Pipeline (P2)
- [ ] Implement FFmpeg-based video rendering pipeline
- [ ] Generate visual scene cards with titles, character art, and historical captions
- [ ] Offline audio/narration generation (TTS or synthesized voiceover/audio timeline)
- [ ] Synchronized timed subtitle generation (SRT / ASS / burn-in)
- [ ] Scene transitions and timeline assembly
- [ ] Render verified playable 60-90s MP4 demonstration video
- [ ] Support download and playback directly from web dashboard

### Phase J — Complete Next.js Frontend (P1/P2)
- [ ] Connect all UI views to live backend endpoints
- [ ] Document library & details view with persistence
- [ ] RAG evidence explorer & interactive Q&A
- [ ] Batch claim verification interface with disagreement badges
- [ ] Script studio with multi-format generation & scene editing
- [ ] Storyboard editor & visual preview
- [ ] Video preview player & download center
- [ ] Clean modern SaaS UI with loading, error, and empty states

### Phase K — Security & Reliability Hardening (P2)
- [ ] File upload validation (magic bytes, size limits, filename sanitization)
- [ ] Prompt injection sanitization for uploaded text
- [ ] Sensitive information & secret leak prevention
- [ ] Temporary file cleanup and timeout controls

### Phase L — Docker & Deployment Validation (P1)
- [ ] Hardened multi-stage Dockerfiles
- [ ] Verified Docker Compose startup and networking
- [ ] Safe `.env.example` with clear documentation
- [ ] Smoke test script for container verification

### Phase M — Comprehensive Quality Assurance (P2)
- [ ] Unit tests, integration tests, provider tests, security tests
- [ ] Maintain >= 85% statement coverage across backend
- [ ] Automated `./scripts/verify_project.sh` testing entire stack
- [ ] GitHub Actions CI workflow covering tests, build, and benchmark

### Phase N — Open-Source Release Documentation (P2)
- [ ] Complete `LICENSE` (Standard MIT)
- [ ] `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`
- [ ] Updated `README.md` and `DEVIN_REVIEW.md`
- [ ] Honest architectural and benchmark documentation

### Phase O — GitHub Pull Request Delivery (Final)
- [ ] Verify clean git state with no secrets
- [ ] Commit incremental changes
- [ ] Push `feature/chronicleai-completion` branch to GitHub
- [ ] Create Pull Request and generate final report
