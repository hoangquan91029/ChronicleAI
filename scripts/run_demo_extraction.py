#!/usr/bin/env python3
"""
ChronicleAI — Verifiable PDF Extraction Demo Script
Demonstrates PyMuPDF text extraction, page preservation, and chunking
on the synthetic test fixture 'le_thanh_tong_dai_viet.pdf'.

NOTE: The sample PDF is a synthetic test fixture generated for automated testing,
benchmarking, and pipeline verification. It is NOT an archival primary manuscript scan.
"""

import sys
import json
from pathlib import Path

# Add backend directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.services.pdf_processor import PDFProcessor

def run_demo():
    fixture_path = BASE_DIR / "backend" / "sample_data" / "le_thanh_tong_dai_viet.pdf"
    output_dir = BASE_DIR / "demo_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "chunks.json"

    if not fixture_path.exists():
        print(f"Generating test fixture at {fixture_path}...")
        import subprocess
        subprocess.run([sys.executable, str(BASE_DIR / "backend" / "sample_data" / "generate_sample_pdf.py")], check=True)

    print(f"Reading synthetic test fixture: {fixture_path} ({fixture_path.stat().st_size} bytes)")
    with open(fixture_path, "rb") as f:
        pdf_bytes = f.read()

    # Process using PDFProcessor
    processor = PDFProcessor(chunk_size=450, chunk_overlap=60)
    result = processor.process_pdf(
        pdf_bytes=pdf_bytes,
        filename="le_thanh_tong_dai_viet.pdf",
        document_id="doc_demo"
    )

    print(f"Extraction successful: {result.total_pages} pages, {result.total_chunks} chunks extracted.")
    
    # Format chunks exactly according to Task 2 specifications
    formatted_chunks = [
        {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "source": chunk.source,
            "page": chunk.page,
            "text": chunk.text,
            "word_count": chunk.word_count
        }
        for chunk in result.chunks
    ]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(formatted_chunks, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(formatted_chunks)} chunks saved to: {output_file}")
    return formatted_chunks

if __name__ == "__main__":
    run_demo()
