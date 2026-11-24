# Security Policy for ChronicleAI

## 1. Supported Versions

Security updates and patches are actively maintained for the latest release on the `main` branch.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## 2. Security Safeguards in ChronicleAI

- **File Upload Limits:** PDF uploads are capped at 25MB and verified using `%PDF-` magic byte inspection before processing to prevent denial-of-service and arbitrary file injection.
- **SQL Injection Prevention:** All SQLite queries in `DocumentStore` utilize parameterized queries (`?` placeholders).
- **Subprocess Execution:** Subprocess calls to FFmpeg strictly validate filenames and avoid shell interpolation (`shell=False` execution model with validated paths).
- **API Key Confidentiality:** External LLM API credentials (`GEMINI_API_KEY`, `OPENAI_API_KEY`) are read strictly from environment variables or local `.env` files and must never be committed to git.
- **Fallback Isolation:** If external API keys are unavailable, the system safely falls back to local deterministic rule engines without network calls.

---

## 3. Reporting a Vulnerability

If you discover a security issue or vulnerability in ChronicleAI:
1. Do not open a public issue on GitHub.
2. Contact the maintainers directly via repository issue or security disclosure.
3. Include reproduction steps, sample payload, and environment specifications.
4. Maintainers will review and respond within 48 hours.
