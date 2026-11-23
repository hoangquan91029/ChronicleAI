# Synthetic Baseline Benchmark Report — Emperor Lê Thánh Tông

- **Evaluation Date:** November 23, 2026
- **Benchmark Type:** `synthetic_baseline`
- **Evaluation Target:** `backend/sample_data/le_thanh_tong_dai_viet.pdf` (Synthetic ReportLab Fixture)
- **Archival Provenance Note:** **This benchmark evaluates pipeline heuristics against a synthetic ReportLab fixture generated for hermetic CI.** It does NOT represent direct ingestion of the authentic 1697 woodblock archive. See `benchmarks/authentic_archival/` for the real historical evaluation.
- **Total Evaluated Claims:** 24
- **Overall Classification Accuracy:** **95.8%** (23/24)
- **Macro F1 Score:** **95.8%**
- **Citation Integrity Accuracy:** **95.8%**
- **Retrieval Recall@1:** **100.0%** | **Recall@4:** **100.0%**

---

## 1. Executive Summary

This synthetic baseline validates ChronicleAI's core retrieval and heuristic verification pipeline against the controlled 5-page sample document fixture. It covers:
1. **8 Supported Historical Claims:** Accession, administrative restructuring (Lục Bộ), Hồng Đức Code inheritance, Văn Miếu stelae (1484), 1471 Chiêm Thành campaign, 1473 territorial decree.
2. **8 Contradicted Claims:** Temporal clashes (1520), role inversions, stelae destruction, military defeat assertions.
3. **8 Insufficient Evidence Claims:** Uncorroborated anachronisms (Queen Elizabeth I, steam gunboats, Sorbonne Paris, railway construction, Ottoman alliances).

---

## 2. Performance Metrics

| Classification Label | Support (N) | Precision | Recall | F1-Score |
|---|---|---|---|---|
| **SUPPORTED** | 8 | 100.0% | 100.0% | 100.0% |
| **CONTRADICTED** | 8 | 100.0% | 87.5% | 93.3% |
| **INSUFFICIENT_EVIDENCE** | 8 | 88.9% | 100.0% | 94.1% |
| **Overall Macro Avg** | **24** | **100.0%** | **100.0%** | **95.8%** |

---

## 3. Confusion Matrix

| True \ Predicted | SUPPORTED | CONTRADICTED | INSUFFICIENT_EVIDENCE |
|---|---|---|---|
| **SUPPORTED** | **8** | 0 | 0 |
| **CONTRADICTED** | 0 | **7** | 1 |
| **INSUFFICIENT_EVIDENCE** | 0 | 0 | **8** |

*Visual plot exported to: `benchmarks/synthetic_baseline/confusion_matrix.png`.*
