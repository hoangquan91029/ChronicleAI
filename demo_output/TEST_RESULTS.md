# ChronicleAI Automated Test Results & Quality Report

- **Date of Execution**: November 22, 2026
- **Test Framework**: Pytest 9.2.0, Python 3.11.15, Linux x86_64
- **Coverage Plugin**: pytest-cov 7.1.0, coverage 7.17.4
- **Status**: **29 PASSED, 0 FAILED** (100% test pass rate)

---

## 1. Reproduction Command

```bash
# From repository root
pytest --cov=backend/app --cov-report=term-missing backend/tests
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

backend/tests/test_api_endpoints.py .....                                [ 17%]
backend/tests/test_claim_verifier.py ....                                [ 31%]
backend/tests/test_e2e_integration.py .                                  [ 34%]
backend/tests/test_pdf_processor.py ...........                          [ 72%]
backend/tests/test_scriptwriter.py ..                                    [ 79%]
backend/tests/test_storyboard.py ..                                      [ 86%]
backend/tests/test_vector_and_retrieval.py ....                          [100%]

================================ tests coverage ================================
Name                                           Stmts   Miss  Cover
------------------------------------------------------------------
backend/app/config.py                             49     13    73%
backend/app/main.py                               42      4    90%
backend/app/models/__init__.py                     6      0   100%
backend/app/models/document.py                    29      0   100%
backend/app/models/rag.py                         37      1    97%
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
backend/app/services/llm_provider.py             144     40    72%
backend/app/services/pdf_processor.py            140     15    89%
backend/app/services/scriptwriter.py              29      3    90%
backend/app/services/storyboard_generator.py       9      0   100%
backend/app/services/vector_store.py              72     11    85%
------------------------------------------------------------------
TOTAL                                            859    112    87%
============================== 29 passed in 2.48s ==============================
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
11. `test_unicode_normalization_nfc`: Verifies Vietnamese composite and precomposed diacritics normalize consistently to Unicode NFC.

### B. Retrieval & Grounding (`test_vector_and_retrieval.py` — 4 Tests)
1. `test_vector_store_indexing`: Document registration and chunk indexing.
2. `test_retrieval_doctor_stelae`: Precise top-k semantic retrieval for Van Mieu 1484 stelae.
3. `test_retrieval_territory_defense`: High-confidence retrieval of 1473 territorial defense decree.
4. `test_empty_query_or_unrelated_query`: Rejection of out-of-domain modern queries (e.g., GPS satellites) with score < 0.4.

### C. Claim Verification (`test_claim_verifier.py` — 4 Tests)
1. `test_verify_supported_claim`: Correctly labels verified historical claim as `SUPPORTED` with exact page/chunk citations.
2. `test_verify_contradicted_claim`: Correctly labels inverted dates/events as `CONTRADICTED` with counter-evidence.
3. `test_verify_insufficient_evidence_claim`: Flags uncorroborated assertions as `INSUFFICIENT_EVIDENCE`.
4. `test_unsupported_claim_never_invents_citations`: Verifies zero citation fabrication for ungrounded claims.

### D. Educational Script & Storyboard (`test_scriptwriter.py`, `test_storyboard.py` — 4 Tests)
1. `test_generate_script_structure`: Enforces 7 canonical scenes (Hook, Background, Narrative, Achievements, Conflict, Conclusion).
2. `test_fictional_dialogues_clearly_labeled`: Validates `is_fictional=True` and `DialogueType.FICTIONAL_DRAMATIZATION` on dramatized scenes.
3. `test_generate_storyboard_scenes`: Validates 2D vector stick-figure visual descriptions, camera directions, and AI image prompts.
4. `test_storyboard_evidence_references`: Validates traceability linking storyboard scenes to source citations.

### E. API Endpoints & E2E Integration (`test_api_endpoints.py`, `test_e2e_integration.py` — 6 Tests)
1. `test_health_check`: Fast ping at `/api/health`.
2. `test_list_documents`: Document catalog inspection.
3. `test_search_rag`: Search API response schema.
4. `test_verify_claims_endpoint`: Multi-claim verification endpoint.
5. `test_generate_script_endpoint`: Video script generator endpoint.
6. `test_e2e_pipeline_journey`: Complete end-to-end journey from PDF bytes -> chunk extraction -> vector indexing -> retrieval -> verification -> script generation -> storyboard generation.
