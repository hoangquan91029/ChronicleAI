# ChronicleAI Automated Test Results & Quality Report

- **Date of Execution**: November 23, 2026
- **Test Framework**: Pytest 9.2.0, Python 3.11.15, Linux x86_64
- **Coverage Plugin**: pytest-cov 7.1.0, coverage 7.17.4
- **Status**: **36 PASSED, 0 FAILED** (100% test pass rate)
- **Overall Statement Coverage**: **90%** (848/946 statements)
- **Historical Benchmark**: **100.0% Accuracy** (24/24 claims on Emperor Lê Thánh Tông)

---

## 1. Reproduction Commands

```bash
# Run full automated test suite with coverage
pytest --cov=backend/app --cov-report=term-missing backend/tests

# Run historical benchmark evaluation
python scripts/evaluate_benchmark.py
```

---

## 2. Test Execution Summary

```
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0
rootdir: /home/kieu-hoang-quan/Videos/ChronicleAI
configfile: pytest.ini
plugins: anyio-4.16.0, cov-7.1.0, asyncio-1.5.0
asyncio: mode=Mode.STRICT, debug=False

backend/tests/test_api_endpoints.py .....                                [ 13%]
backend/tests/test_claim_verifier.py ....                                [ 25%]
backend/tests/test_e2e_integration.py .                                  [ 27%]
backend/tests/test_historical_benchmark.py ..                            [ 33%]
backend/tests/test_llm_providers.py .....                                [ 47%]
backend/tests/test_pdf_processor.py ...........                          [ 77%]
backend/tests/test_scriptwriter.py ..                                    [ 83%]
backend/tests/test_storyboard.py ..                                      [ 88%]
backend/tests/test_vector_and_retrieval.py ....                          [100%]

================================ tests coverage ================================
Name                                           Stmts   Miss  Cover
------------------------------------------------------------------
backend/app/config.py                             49     13    73%
backend/app/main.py                               46      4    91%
backend/app/models/__init__.py                     6      0   100%
backend/app/models/document.py                    33      0   100%
backend/app/models/rag.py                         45      1    98%
backend/app/models/script.py                      50      0   100%
backend/app/models/storyboard.py                  26      0   100%
backend/app/models/verification.py                28      0   100%
backend/app/routers/__init__.py                    6      0   100%
backend/app/routers/documents.py                  36     10    72%
backend/app/routers/rag.py                        15      0   100%
backend/app/routers/scripts.py                    38      3    92%
backend/app/routers/storyboards.py                38      6    84%
backend/app/routers/verify.py                      8      0   100%
backend/app/services/claim_verifier.py            32      3    91%
backend/app/services/embedding_service.py         25      3    88%
backend/app/services/llm_provider.py             205     25    88%
backend/app/services/pdf_processor.py            140     13    91%
backend/app/services/scriptwriter.py              29      3    90%
backend/app/services/storyboard_generator.py       9      0   100%
backend/app/services/vector_store.py              82     14    83%
------------------------------------------------------------------
TOTAL                                            946     98    90%
============================== 36 passed in 2.27s ==============================
```

---

## 3. Test Suite Breakdown by Component

### A. PDF Ingestion & Extraction (`test_pdf_processor.py` — 11 Tests)
1. `test_process_valid_historical_pdf`: Verifies 5 pages extracted, 15 chunks generated, 0% page skips, all chunk references preserved.
2. `test_page_numbers_preserved`: Confirms pages 1 through 5 are sequential with zero off-by-one errors.
3. `test_scanned_pdf_detected`: Proves raster-only PDFs trigger `is_scanned=True` with `ocr_required` warning, preventing silent hallucination.
4. `test_empty_pdf_handled`: Graceful zero-chunk handling on blank canvases.
5. `test_corrupt_pdf_handled`: Raises `PDFProcessingError` without unhandled crashes.
6. `test_chunk_traceability`: Verifies each chunk contains `chunk_id`, `document_id`, `source`, `page`, and `word_count`.
7. `test_chunk_size_boundaries`: Validates chunk lengths obey max thresholds across edge inputs.
8. `test_oversized_sentence_subdivision`: Verifies single sentences longer than `chunk_size` are cleanly split at word boundaries.
9. `test_chunk_overlap_preservation`: Validates consecutive chunks share overlapping context across boundaries.
10. `test_no_missing_text`: Exhaustively compares reconstructed words from chunks against raw page text (0 lost tokens).
11. `test_unicode_preservation`: Validates all Vietnamese diacritics and tone marks (`ă`, `â`, `đ`, `ê`, `ô`, `ơ`, `ư`) are preserved with NFC normalization.

### B. Vector Indexing & Retrieval (`test_vector_and_retrieval.py` — 4 Tests)
1. `test_indexing_and_vectorization`: Correct shape generation and vocabulary creation.
2. `test_retrieval_ranking_specific_achievement`: Ranks 1484 Doctor Stelae chunk as #1 result for education query.
3. `test_retrieval_territorial_defense`: Ranks 1473 territorial decree chunk as #1 for sovereignty query.
4. `test_retrieval_low_similarity_rejection`: Unrelated queries score below threshold, rejecting irrelevant citations.

### C. Historical Benchmark Evaluation (`test_historical_benchmark.py` — 2 Tests)
1. `test_historical_benchmark_dataset_integrity`: Validates structure, fields, and balance across the 24 claims (8/8/8).
2. `test_historical_benchmark_execution`: Runs the 24-claim benchmark and asserts >= 85% accuracy (measured: 100.0%).

### D. Multi-Provider LLM & Dynamic Generation (`test_llm_providers.py` — 5 Tests)
1. `test_offline_engine_grounded_qa`: Grounded question-answering with exact citation attribution.
2. `test_dynamic_script_generation_for_arbitrary_subject`: Proves arbitrary historical figures (e.g. Trần Hưng Đạo) dynamically synthesize scenes directly from ingested chunks rather than falling back to hardcoded text.
3. `test_gemini_provider_mock`: Remote Gemini 1.5 Flash provider API integration via httpx.
4. `test_openai_provider_mock`: Remote OpenAI GPT-4o provider API integration via httpx.
5. `test_provider_factory_fallback`: Provider factory selection, environment variable configuration, and automatic fallback.

### E. Claim Verification (`test_claim_verifier.py` — 4 Tests)
1. `test_verify_supported_claim`: Verified claim is classified `SUPPORTED` with page and quote citation.
2. `test_verify_contradicted_claim`: Temporal mismatch (e.g. 1520 vs 1460) classified `CONTRADICTED`.
3. `test_verify_insufficient_evidence_claim`: Anachronisms classified `INSUFFICIENT_EVIDENCE` with zero citations.
4. `test_batch_claim_verification`: Batch processing across mixed labels.

### F. Scriptwriting & Storyboard Agents (`test_scriptwriter.py`, `test_storyboard.py` — 4 Tests)
1. `test_scriptwriter_generation`: 7-scene narrative, chronological progression, citations, and review flag auditing.
2. `test_scriptwriter_fictional_dialogue_labeling`: Explicit `[HƯ CẤU / KỊCH BẢN]` separation from authentic quotes.
3. `test_storyboard_generation`: Visual settings, camera staging, and 2D minimalist vector directions.
4. `test_storyboard_prompts_contain_historical_costumes`: Image prompts contain authentic 15th-century attire (`áo giao lĩnh`, `khăn đóng`).

### G. API Endpoints & E2E Integration (`test_api_endpoints.py`, `test_e2e_integration.py` — 6 Tests)
1. `test_api_health`: Health status, indexed chunk counts, active provider class, and available providers.
2. `test_api_document_listing`: List uploaded documents with metadata.
3. `test_api_search_and_qa`: RAG search and grounded Q&A with citations.
4. `test_api_claim_verification`: API batch verification endpoint.
5. `test_api_script_and_storyboard_pipeline`: Full script and storyboard generation and markdown export.
6. `test_end_to_end_journey`: Ingestion -> Chunking -> Vector Indexing -> Retrieval -> Verification -> Scriptwriting -> Storyboard.
