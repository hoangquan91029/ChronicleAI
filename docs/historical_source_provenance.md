# Historical Source Provenance & Archival Grounding

## 1. Primary Source Overview

For the inaugural historical case study of ChronicleAI — **Emperor Lê Thánh Tông of Đại Việt (1460–1497)** — factual grounding is anchored directly in the preeminent official dynastic chronicle of Vietnam:

**Đại Việt Sử Ký Toàn Thư (大越史記全書)**  
*Section: Bản Kỷ Thực Lục (本紀實錄)*  
- **Quyển XII (Volume 12):** Thánh Tông Thuần Hoàng Đế (Thượng) — Covers years 1460–1472 (Quang Thuận 1 to Hồng Đức 3).
- **Quyển XIII (Volume 13):** Thánh Tông Thuần Hoàng Đế (Hạ) — Covers years 1473–1497 (Hồng Đức 4 to Hồng Đức 28).

---

## 2. Textual Transmission & Print Editions

1. **The 1697 Imperial Cabinet Edition (Nội các quan bản — 內閣官板):**
   - Printed in the 18th year of Chính Hòa (1697) under Emperor Lê Hy Tông, supervised by Court Historian Lê Hy and Nguyễn Quý Đức.
   - This woodblock edition compiles the foundational 1479 chronicle of Ngô Sĩ Liên, supplemented by Vũ Quỳnh, Phạm Công Trứ, and subsequent imperial historiographers.
   - Surviving sets are cataloged in the Institute of Han-Nom Studies (Hanoi), the National Library of France (BnF), and École française d'Extrême-Orient (EFEO).

2. **Digital Preservation & IIIF Facsimiles:**
   - **Repository:** Digitizing Vietnam (a collaborative digital humanities initiative by Columbia University and Fulbright University Vietnam).
   - **Catalog Record:** `https://www.digitizingvietnam.com/vi/our-collections/dai-viet-su-ky-toan-thu/ban-ky-thuc-luc`
   - **IIIF Image Endpoint:** `https://iiif.digitizingvietnam.com/iiif/2/ban-ky-thuc-luc/`
   - **Folio Naming Standards:**
     - Quyển 12: `DVSKTT_ban_thuc_XII_{folio}.jpg` (e.g. `1a`, `1b`, `14b`, `51b`, `62a`)
     - Quyển 13: `DVSKTT_ban_thuc_XIII_{folio}.jpg` (e.g. `1a`, `23b`, `48a`, `64b`, `88b`)

3. **Academic National Language Translation (Bản dịch Quốc ngữ):**
   - **Edition:** *Đại Việt Sử Ký Toàn Thư*, translated by Hoàng Văn Lâu, annotated by Prof. Hà Văn Tấn.
   - **Publisher:** Social Sciences Publishing House (Nhà xuất bản Khoa học Xã hội), Hanoi, 1993.
   - **Role:** Serves as the authoritative semantic bridge connecting traditional Hán-Nôm imperial prose with contemporary Vietnamese natural language processing and retrieval pipelines.

---

## 3. Structural Distinction in Archival Texts

To ensure rigorous factual verification, ChronicleAI explicitly categorizes historical text elements:

| Tier | Category | Description | Citation Policy in ChronicleAI |
|---|---|---|---|
| **Tier 1** | **Imperial Decree & Official Annals** (*Chính sử*) | Chronological court events, administrative decrees, appointments, military logs, and legal statutes. | Classified as verifiable historical facts. Requires exact volume, year, and folio reference. |
| **Tier 2** | **Historiographer Commentary** (*Sử thần bàn*) | Evaluative commentaries inserted by Ngô Sĩ Liên or subsequent compilers (e.g., *Sử thần Ngô Sĩ Liên bàn rằng...*). | Must be labeled as historiographical interpretation, not factual court events. |
| **Tier 3** | **Synthetic Benchmark Fixtures** | Programmatically generated PDF documents (e.g. `backend/sample_data/le_thanh_tong_dai_viet.pdf`) used for hermetic CI/CD testing and unit test validation. | Explicitly demarcated with `[SYNTHETIC TEST FIXTURE]`. Never cited as independent primary archives. |

---

## 4. Legal & Licensing Framework

- **Historical Text:** The text of *Đại Việt Sử Ký Toàn Thư* (1697) is fundamentally in the **Public Domain** worldwide.
- **Digital Facsimiles:** Digitizing Vietnam grants open access for academic, educational, and non-commercial research purposes. Commercial redistribution of high-resolution facsimile scans is prohibited by repository terms.
- **Fair Use Alignment:** ChronicleAI ingests excerpts, generates retrieval index hashes, and validates citations under non-profit educational and research fair use standards. Full text works are not repackaged or sold.

---

## 5. Technical Limitations & Hán-Nôm Recognition Roadmap

1. **Character Recognition Challenges:**
   - Woodblock Sino-Nom (Hán-Nôm) manuscripts contain complex calligraphic variants, archaic glyphs, and ligatures not present in standard modern Unicode CJK ideograph sets.
   - Standard OCR engines (Tesseract, Google Vision) fail significantly on unprocessed Sino-Nom woodblock rubbings.
2. **Roadmap to Direct Facsimile Grounding:**
   - **Phase 1 (Current):** Align validated Quốc ngữ historical transcripts with corresponding IIIF folio IDs (`ban_thuc_XII_62a`).
   - **Phase 2 (Next Milestone):** Integrate Transkribus / TrOCR vision models fine-tuned on Nom Na Group and Institute of Han-Nom Studies woodblock corpora to directly link bounding boxes on woodblock scans to extracted textual chunks.
