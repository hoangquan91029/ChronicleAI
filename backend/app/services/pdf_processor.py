import re
import uuid
from typing import List, Tuple, Optional
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
        if not pdf_bytes:
            raise PDFProcessingError(f"Uploaded file '{filename}' is empty (0 bytes).")

        doc_id = document_id or f"doc_{uuid.uuid4().hex[:8]}"

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
        """Normalize whitespaces, tabs, and linebreaks while keeping Vietnamese diacritics."""
        if not text:
            return ""
        # Replace carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Normalize continuous spaces/tabs within lines
        text = re.sub(r"[ \t]+", " ", text)
        # Collapse excessive newlines (keep paragraph breaks)
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
        """
        chunks: List[ChunkMetadata] = []
        
        # If the page text is already within chunk size, return it as a single chunk
        if len(text) <= self.chunk_size:
            chunk_idx = start_index + 1
            chunks.append(
                ChunkMetadata(
                    chunk_id=f"{doc_id}_p{page_num:02d}_c{chunk_idx:03d}",
                    page=page_num,
                    text=text,
                    source=filename,
                    document_id=doc_id,
                    chunk_index=chunk_idx,
                    word_count=len(text.split())
                )
            )
            return chunks

        # Otherwise, split by paragraphs or sliding window
        paragraphs = text.split("\n\n")
        current_chunk_parts: List[str] = []
        current_length = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If a single paragraph is larger than chunk_size, split by sentences
            if len(para) > self.chunk_size:
                sentences = re.split(r"(?<=[.!?])\s+", para)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    if current_length + len(sentence) + 1 > self.chunk_size and current_chunk_parts:
                        # Flush current chunk
                        chunk_str = " ".join(current_chunk_parts)
                        chunk_idx = start_index + len(chunks) + 1
                        chunks.append(
                            ChunkMetadata(
                                chunk_id=f"{doc_id}_p{page_num:02d}_c{chunk_idx:03d}",
                                page=page_num,
                                text=chunk_str,
                                source=filename,
                                document_id=doc_id,
                                chunk_index=chunk_idx,
                                word_count=len(chunk_str.split())
                            )
                        )
                        # Overlap: keep last part if helpful
                        if self.chunk_overlap > 0 and len(current_chunk_parts[-1]) <= self.chunk_overlap:
                            current_chunk_parts = [current_chunk_parts[-1], sentence]
                            current_length = sum(len(p) for p in current_chunk_parts) + len(current_chunk_parts) - 1
                        else:
                            current_chunk_parts = [sentence]
                            current_length = len(sentence)
                    else:
                        current_chunk_parts.append(sentence)
                        current_length += len(sentence) + 1
            else:
                if current_length + len(para) + 1 > self.chunk_size and current_chunk_parts:
                    chunk_str = "\n\n".join(current_chunk_parts)
                    chunk_idx = start_index + len(chunks) + 1
                    chunks.append(
                        ChunkMetadata(
                            chunk_id=f"{doc_id}_p{page_num:02d}_c{chunk_idx:03d}",
                            page=page_num,
                            text=chunk_str,
                            source=filename,
                            document_id=doc_id,
                            chunk_index=chunk_idx,
                            word_count=len(chunk_str.split())
                        )
                    )
                    current_chunk_parts = [para]
                    current_length = len(para)
                else:
                    current_chunk_parts.append(para)
                    current_length += len(para) + 2

        # Flush remainder
        if current_chunk_parts:
            chunk_str = "\n\n".join(current_chunk_parts).strip()
            if len(chunk_str) >= self.min_chunk_chars or not chunks:
                chunk_idx = start_index + len(chunks) + 1
                chunks.append(
                    ChunkMetadata(
                        chunk_id=f"{doc_id}_p{page_num:02d}_c{chunk_idx:03d}",
                        page=page_num,
                        text=chunk_str,
                        source=filename,
                        document_id=doc_id,
                        chunk_index=chunk_idx,
                        word_count=len(chunk_str.split())
                    )
                )

        return chunks
