# Contributing to ChronicleAI

Thank you for your interest in contributing to **ChronicleAI** — an open-source platform transforming historical documents into evidence-grounded educational videos and storyboards.

---

## 1. Code of Conduct & Academic Integrity

ChronicleAI is designed for verifiable historical research and education. When contributing:
- **Historical Grounding:** Never add fabricated historical claims or fake primary source citations.
- **Traceability:** Ensure every newly added source document preserves exact folio/page references and metadata.
- **Distinction of Creative Dialogue:** Clearly mark fictional reconstructions separately from authentic historical quotations.

---

## 2. Development Setup

### Backend (Python 3.11+)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Run test suite:
```bash
pytest backend/tests --cov=app --cov-report=term
```

### Frontend (Next.js 14+)
```bash
cd frontend
npm ci
npm run dev
```

Build verification:
```bash
npm run build
```

---

## 3. Pull Request Guidelines

1. Create a feature branch off `main` (e.g., `feature/your-feature-name`).
2. Run the end-to-end verification script:
   ```bash
   ./scripts/verify_project.sh
   ```
3. Ensure all tests pass with code coverage >= 80%.
4. Commit with Conventional Commits syntax (`feat:`, `fix:`, `test:`, `docs:`).
5. Open a Pull Request targeting `main` with clear context and testing notes.

---

## 4. Archival Benchmark Contributions

To contribute new primary sources or benchmark cases:
- Store structured archival corpora under `backend/data/sources/`.
- Register the edition, compiler, and repository catalog reference in `backend/data/sources/source_registry.json`.
- Add test assertions in `backend/tests/test_historical_benchmark.py`.
