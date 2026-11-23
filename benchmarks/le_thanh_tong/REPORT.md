# Historical Verification Benchmark Report — Emperor Lê Thánh Tông

- **Evaluation Date:** November 23, 2026
- **Case Study:** Emperor Lê Thánh Tông of Đại Việt (1460–1497)
- **Primary Archival Source:** *Đại Việt Sử Ký Toàn Thư — Bản Kỷ Thực Lục* (Quyển XII & XIII, 1697 Nội các quan bản)
- **Total Evaluated Claims:** 24
- **Overall Classification Accuracy:** **100.0%** (24/24)
- **Citation Integrity Accuracy:** **100.0%** (16/16)
- **Retrieval Recall@1:** **100.0%** | **Recall@4:** **100.0%**

---

## 1. Executive Summary

This benchmark validates ChronicleAI's capability to ground historical reasoning directly in ingested chronicles, detect counter-factual claims, and reject unsupported or anachronistic assertions.

The evaluation covers 24 carefully designed propositions across three balanced categories:
1. **8 Supported Historical Claims:** Documented imperial events (1460 accession, Lục Bộ reform, Hồng Đức Code, 1484 Doctor Stelae, 1471 Chiêm Thành expedition, 1473 territorial decree).
2. **8 Contradicted Historical Claims:** Factually conflicting claims (wrong reign years, inverted roles, destruction of stelae, military defeat, land concession).
3. **8 Insufficient Evidence Claims:** Anachronisms and unrecorded assertions (contact with Queen Elizabeth I, steam gunboats, Sorbonne studies, railway construction, Ottoman alliances).

---

## 2. Performance Metrics

| Classification Label | Support (N) | Precision | Recall | F1-Score |
|---|---|---|---|---|
| **SUPPORTED** | 8 | 100.0% | 100.0% | 100.0% |
| **CONTRADICTED** | 8 | 100.0% | 100.0% | 100.0% |
| **INSUFFICIENT_EVIDENCE** | 8 | 100.0% | 100.0% | 100.0% |
| **Overall Macro Avg** | **24** | **100.0%** | **100.0%** | **100.0%** |

---

## 3. Confusion Matrix

| True \ Predicted | SUPPORTED | CONTRADICTED | INSUFFICIENT_EVIDENCE |
|---|---|---|---|
| **SUPPORTED** | **8** | 0 | 0 |
| **CONTRADICTED** | 0 | **8** | 0 |
| **INSUFFICIENT_EVIDENCE** | 0 | 0 | **8** |

*Visual plot exported to: `benchmarks/le_thanh_tong/confusion_matrix.png`.*

---

## 4. Retrieval & Provenance Results

- **Top-1 Page Retrieval Recall:** **100.0%**
- **Top-2 Page Retrieval Recall:** **100.0%**
- **Top-4 Page Retrieval Recall:** **100.0%**
- **Zero Hallucinated Citations:** Every supported claim returned the exact originating page number and non-empty verified excerpt.
- **Unsupported Claim Rejection:** 100% of anachronistic and fabricated claims were recognized as having insufficient source evidence.
