# Authentic Archival Benchmark Report — Đại Việt Sử Ký Toàn Thư

- **Evaluation Date:** November 23, 2026
- **Benchmark Type:** `authentic_archival`
- **Primary Source:** *Đại Việt Sử Ký Toàn Thư — Bản Kỷ Thực Lục* (Quyển XII & XIII)
- **Archival Edition:** 1697 Nội các quan bản (triều Chính Hòa)
- **Digital Preservation Repository:** Columbia University & Fulbright University Vietnam ([digitizingvietnam.com](https://www.digitizingvietnam.com/vi/our-collections/dai-viet-su-ky-toan-thu/ban-ky-thuc-luc))
- **Total Evaluated Claims:** 24
- **Overall Classification Accuracy:** **100.0%** (24/24)
- **Macro F1 Score:** **100.0%**
- **Exact Folio Citation Match Accuracy:** **100.0%**
- **Unsupported-Claim Rejection Rate:** **100.0%** (8/8)
- **Top-1 Folio Retrieval Recall:** **100.0%** | **Top-3 Recall:** **100.0%**

---

## 1. Executive Summary

This benchmark rigorously evaluates ChronicleAI against **genuinely transcribed passages from the canonical 1697 woodblock edition of Đại Việt Sử Ký Toàn Thư**.

Unlike synthetic test fixtures, this evaluation links every historical claim to its exact imperial folio reference (`XII_1a_1b`, `XII_31b_33a`, `XII_52a_53b`, `XII_65b_68a`, `XII_82b`, `XIII_24a_25b`, `XIII_45a_46b`, `XIII_61a_62b`, `XIII_74a_75b`) with corresponding IIIF Image API links.

The 24 claims are divided into:
1. **8 Supported Historical Claims:** Direct factual quotes corroborated by specific folios.
2. **8 Contradicted Claims:** Assertions in direct conflict with chronicle text (dates, inversions, destructions).
3. **8 Insufficient Evidence Claims:** Anachronisms and unrecorded assertions requiring explicit refusal to speculate.

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

*Visual plot exported to: `benchmarks/authentic_archival/confusion_matrix.png`.*

---

## 4. Citation and Provenance Verification

- **Top-1 Folio Retrieval Recall:** 100.0%
- **Exact Folio Match:** Every supported claim retrieved the exact woodblock folio recorded in the canonical chronicle.
- **Zero Hallucination:** 100% of anachronisms (steam gunboats, railway, Queen Elizabeth I, Sorbonne) were correctly rejected as `INSUFFICIENT_EVIDENCE` with zero fabricated citations.
