import re
import hashlib
import unicodedata
from pathlib import Path
from typing import List, Tuple, Optional, Union
import pymupdf

from app.config import settings
from app.models.document import (
    ChunkMetadata,
    DocumentMetadata,
    DocumentIngestResponse
)


class PDFProcessingError(Exception):
    """Custom exception raised during PDF extraction or parsing."""
    pass


class PDFProcessor:
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
        min_chunk_chars: int = settings.MIN_CHUNK_CHARS,
        scanned_char_threshold: int = settings.SCANNED_THRESHOLD_CHARS_PER_PAGE,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_chars = min_chunk_chars
        self.scanned_char_threshold = scanned_char_threshold

    def process_pdf(
        self,
        pdf_bytes: bytes,
        filename: str,
        document_id: Optional[str] = None
    ) -> DocumentIngestResponse:
        """
        Extract Vietnamese/multilingual text from a PDF, inspect for scanned content,
        preserve exact page numbers, split into retrieval-friendly chunks, and return
        a structured DocumentIngestResponse.
        """
        if isinstance(pdf_bytes, (str, Path)):
            with open(pdf_bytes, "rb") as f:
                pdf_bytes = f.read()

        if not pdf_bytes:
            raise PDFProcessingError(f"Uploaded file '{filename}' is empty (0 bytes).")

        # Stable, deterministic document_id based on file content hash if not provided
        content_hash = hashlib.sha256(pdf_bytes).hexdigest()[:8]
        doc_id = document_id or f"doc_{content_hash}"

        try:
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            raise PDFProcessingError(f"Failed to parse PDF '{filename}': {str(e)}")

        total_pages = len(doc)
        if total_pages == 0:
            doc.close()
            return DocumentIngestResponse(
                document_id=doc_id,
                filename=filename,
                total_pages=0,
                total_chunks=0,
                status="empty_document",
                metadata=DocumentMetadata(
                    title=filename,
                    total_pages=0,
                    file_size_bytes=len(pdf_bytes),
                    warning_message="The uploaded PDF contains 0 pages."
                ),
                chunks=[]
            )

        # Extract PDF metadata
        raw_metadata = doc.metadata or {}
        doc_metadata = DocumentMetadata(
            title=raw_metadata.get("title") or filename,
            author=raw_metadata.get("author"),
            subject=raw_metadata.get("subject"),
            creator=raw_metadata.get("creator"),
            total_pages=total_pages,
            file_size_bytes=len(pdf_bytes),
            extra={k: v for k, v in raw_metadata.items() if v}
        )

        page_texts: List[Tuple[int, str]] = []
        total_text_length = 0
        total_images_count = 0

        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_num = page_idx + 1  # 1-indexed page
            text = page.get_text("text") or ""
            clean_text = self._clean_text(text)
            page_texts.append((page_num, clean_text))
            total_text_length += len(clean_text)

            # Check for embedded images
            images = page.get_images(full=True)
            total_images_count += len(images)

        doc.close()

        # Check for scanned PDF condition:
        # High images or pages, but virtually zero extractable text
        avg_chars_per_page = total_text_length / max(total_pages, 1)
        is_scanned = (
            total_images_count > 0 and avg_chars_per_page < self.scanned_char_threshold
        ) or (total_pages > 0 and total_text_length < 20 and total_images_count > 0)

        if is_scanned:
            doc_metadata.is_scanned = True
            doc_metadata.ocr_required = True
            doc_metadata.warning_message = (
                f"Scanned document detected: '{filename}' contains {total_images_count} image(s) "
                f"across {total_pages} page(s) with negligible embedded text (average {avg_chars_per_page:.1f} chars/page). "
                f"OCR processing is required to extract text from this document. "
                f"ChronicleAI refuses to fabricate content for scanned documents without OCR."
            )
            return DocumentIngestResponse(
                document_id=doc_id,
                filename=filename,
                total_pages=total_pages,
                total_chunks=0,
                status="scanned_ocr_required",
                metadata=doc_metadata,
                chunks=[]
            )

        # Check for completely blank/empty text
        if total_text_length == 0:
            doc_metadata.warning_message = f"Document '{filename}' contains no readable text."
            return DocumentIngestResponse(
                document_id=doc_id,
                filename=filename,
                total_pages=total_pages,
                total_chunks=0,
                status="empty_document",
                metadata=doc_metadata,
                chunks=[]
            )

        # Chunk generation with strict page traceability
        all_chunks: List[ChunkMetadata] = []
        global_chunk_idx = 0

        for page_num, text in page_texts:
            if not text.strip():
                continue
            page_chunks = self._chunk_page_text(
                text=text,
                page_num=page_num,
                doc_id=doc_id,
                filename=filename,
                start_index=global_chunk_idx
            )
            all_chunks.extend(page_chunks)
            global_chunk_idx += len(page_chunks)

        return DocumentIngestResponse(
            document_id=doc_id,
            filename=filename,
            total_pages=total_pages,
            total_chunks=len(all_chunks),
            status="success",
            metadata=doc_metadata,
            chunks=all_chunks
        )

    def _clean_text(self, text: str) -> str:
        """
        Normalize whitespaces, tabs, and linebreaks while keeping Vietnamese diacritics.
        Applies Unicode Normalization Form C (NFC).
        """
        if not text:
            return ""
        # Unicode Normalization Form C
        text = unicodedata.normalize("NFC", text)
        # Replace carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Normalize continuous horizontal spaces/tabs
        text = re.sub(r"[ \t]+", " ", text)
        # Collapse excessive newlines (preserve double newline paragraph breaks)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _chunk_page_text(
        self,
        text: str,
        page_num: int,
        doc_id: str,
        filename: str,
        start_index: int
    ) -> List[ChunkMetadata]:
        """
        Split a single page's text into retrieval-friendly chunks using sliding window
        and natural paragraph/sentence boundaries, strictly keeping the exact page number.
        Guarantees no missing text and handles oversized sentences.
        """
        text = text.strip()
        if not text:
            return []

        # If the page text is already within chunk size, return it as a single chunk
        if len(text) <= self.chunk_size:
            chunk_idx = start_index + 1
            return [
                ChunkMetadata(
                    chunk_id=f"{doc_id}_p{page_num:02d}_c{chunk_idx:03d}",
                    page=page_num,
                    text=text,
                    source=filename,
                    document_id=doc_id,
                    chunk_index=chunk_idx,
                    word_count=len(text.split())
                )
            ]

        # Break text into atomic semantic units (sentences or word-groups if sentence is oversized)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        units: List[str] = []

        for p in paragraphs:
            # Split paragraph into sentences
            sentences = re.split(r"(?<=[.!?])\s+", p)
            for s in sentences:
                s = s.strip()
                if not s:
                    continue
                if len(s) > self.chunk_size:
                    # Break oversized sentence by words
                    words = s.split(" ")
                    sub_unit: List[str] = []
                    sub_len = 0
                    for w in words:
                        if not w:
                            continue
                        if sub_len + len(w) + 1 > self.chunk_size and sub_unit:
                            units.append(" ".join(sub_unit))
                            sub_unit = [w]
                            sub_len = len(w)
                        else:
                            sub_unit.append(w)
                            sub_len += len(w) + 1
                    if sub_unit:
                        units.append(" ".join(sub_unit))
                else:
                    units.append(s)

        # Assemble units into chunks with overlap
        chunks: List[ChunkMetadata] = []
        curr = ""

        for u in units:
            if not curr:
                curr = u
            elif len(curr) + 1 + len(u) <= self.chunk_size:
                curr = curr + " " + u
            else:
                chunk_idx = start_index + len(chunks) + 1
                chunks.append(
                    ChunkMetadata(
                        chunk_id=f"{doc_id}_p{page_num:02d}_c{chunk_idx:03d}",
                        page=page_num,
                        text=curr.strip(),
                        source=filename,
                        document_id=doc_id,
                        chunk_index=chunk_idx,
                        word_count=len(curr.strip().split())
                    )
                )

                # Compute word-boundary overlap from tail of curr
                if self.chunk_overlap > 0:
                    words = curr.split(" ")
                    overlap_words: List[str] = []
                    overlap_len = 0
                    for w in reversed(words):
                        if overlap_len + len(w) + 1 <= self.chunk_overlap:
                            overlap_words.insert(0, w)
                            overlap_len += len(w) + 1
                        else:
                            break
                    curr = (" ".join(overlap_words) + " " + u).strip() if overlap_words else u
                else:
                    curr = u

        # Flush remainder
        if curr:
            curr_str = curr.strip()
            # If the remainder is smaller than min_chunk_chars and we already have chunks on this page,
            # we can merge it into the previous chunk if it doesn't exceed 1.25x chunk_size
            if chunks and len(curr_str) < self.min_chunk_chars and (len(chunks[-1].text) + 1 + len(curr_str) <= int(self.chunk_size * 1.25)):
                prev = chunks[-1]
                updated_text = prev.text + " " + curr_str
                chunks[-1] = ChunkMetadata(
                    chunk_id=prev.chunk_id,
                    page=prev.page,
                    text=updated_text,
                    source=prev.source,
                    document_id=prev.document_id,
                    chunk_index=prev.chunk_index,
                    word_count=len(updated_text.split())
                )
            else:
                chunk_idx = start_index + len(chunks) + 1
                chunks.append(
                    ChunkMetadata(
                        chunk_id=f"{doc_id}_p{page_num:02d}_c{chunk_idx:03d}",
                        page=page_num,
                        text=curr_str,
                        source=filename,
                        document_id=doc_id,
                        chunk_index=chunk_idx,
                        word_count=len(curr_str.split())
                    )
                )

        return chunks
