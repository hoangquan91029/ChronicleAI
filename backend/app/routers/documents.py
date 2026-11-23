import re
import hashlib
from typing import List, Dict, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.document import (
    DocumentIngestResponse,
    ChunkMetadata,
    DocumentMetadata,
    RegisterURLRequest
)
from app.services.pdf_processor import PDFProcessor, PDFProcessingError
from app.services.vector_store import global_vector_store
from app.services.document_store import global_document_store

router = APIRouter(prefix="/api/documents", tags=["Documents"])

MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB
pdf_processor = PDFProcessor()

# Compatibility dictionary referencing persistent store
class DocumentRegistryProxy(dict):
    """Proxy dictionary that reads from and syncs with global_document_store for backward compatibility."""
    def __getitem__(self, item):
        doc = global_document_store.get_document(item)
        if doc is None:
            raise KeyError(item)
        return doc

    def __contains__(self, item):
        return global_document_store.get_document(item) is not None

    def values(self):
        return global_document_store.list_documents()

    def get(self, item, default=None):
        doc = global_document_store.get_document(item)
        return doc if doc is not None else default

    def __len__(self):
        return len(global_document_store.list_documents())

uploaded_docs = DocumentRegistryProxy()


@router.post("/upload", response_model=DocumentIngestResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a historical PDF document, validate magic bytes and size,
    extract Vietnamese text with PyMuPDF, preserve page numbers,
    detect scanned PDFs / OCR requirements, persist to SQLite, and index into vector store.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()

    # Size validation
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size ({len(content)/(1024*1024):.1f}MB) exceeds maximum allowed limit of 25MB."
        )

    # Magic byte check
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file: File does not start with valid '%PDF-' header."
        )

    try:
        res = pdf_processor.process_pdf(
            pdf_bytes=content,
            filename=file.filename
        )
    except PDFProcessingError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error processing PDF: {str(e)}")

    # Persist in SQLite
    global_document_store.save_document(res, source_type="upload_pdf")

    # Index into vector store if chunks were successfully extracted
    if res.chunks:
        global_vector_store.add_chunks(res.chunks)

    return res


@router.post("/register-url", response_model=DocumentIngestResponse)
async def register_url_document(req: RegisterURLRequest):
    """
    Register a historical digital archive or web source (e.g. Digitizing Vietnam IIIF folio).
    Stores metadata and chunks into SQLite and indexes for RAG retrieval.
    """
    if not req.url or not req.title:
        raise HTTPException(status_code=400, detail="URL and title are required.")

    # Generate stable document ID
    hash_id = hashlib.md5(f"{req.url}_{req.title}".encode("utf-8")).hexdigest()[:10]
    doc_id = f"doc_url_{hash_id}"

    text_content = req.text.strip() if req.text else f"Source URL: {req.url}\nTitle: {req.title}"
    words = text_content.split()
    total_words = len(words)

    # Chunk text
    chunk_size = 180
    chunks: List[ChunkMetadata] = []
    
    if total_words <= chunk_size:
        chunks.append(ChunkMetadata(
            chunk_id=f"{doc_id}_c001",
            page=1,
            text=text_content,
            source=req.title,
            document_id=doc_id,
            chunk_index=0,
            word_count=total_words,
            source_id=req.source_id,
            source_title=req.title,
            original_url=req.url,
            folio_ref=req.folio_ref
        ))
    else:
        # Split into overlapping chunks
        step = 140
        c_idx = 0
        for i in range(0, total_words, step):
            sub_words = words[i:i + chunk_size]
            if not sub_words:
                break
            chunk_text = " ".join(sub_words)
            chunks.append(ChunkMetadata(
                chunk_id=f"{doc_id}_c{c_idx+1:03d}",
                page=1 + (i // chunk_size),
                text=chunk_text,
                source=req.title,
                document_id=doc_id,
                chunk_index=c_idx,
                word_count=len(sub_words),
                source_id=req.source_id,
                source_title=req.title,
                original_url=req.url,
                folio_ref=req.folio_ref
            ))
            c_idx += 1

    metadata = DocumentMetadata(
        title=req.title,
        total_pages=max(1, len(chunks)),
        file_size_bytes=len(text_content.encode("utf-8")),
        is_scanned=False,
        ocr_required=False,
        extra={"url": req.url, "source_id": req.source_id, "folio_ref": req.folio_ref}
    )

    doc_res = DocumentIngestResponse(
        document_id=doc_id,
        filename=req.title,
        total_pages=metadata.total_pages,
        total_chunks=len(chunks),
        status="INDEXED",
        metadata=metadata,
        chunks=chunks
    )

    global_document_store.save_document(doc_res, source_type="url_archive", status="INDEXED")
    if chunks:
        global_vector_store.add_chunks(chunks)

    return doc_res


@router.get("", response_model=List[DocumentIngestResponse])
async def list_documents():
    """List all ingested historical documents from persistent SQLite storage."""
    return global_document_store.list_documents()


@router.get("/{document_id}", response_model=DocumentIngestResponse)
async def get_document(document_id: str):
    """Retrieve details and metadata for a specific document."""
    doc = global_document_store.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")
    return doc


@router.get("/{document_id}/chunks", response_model=List[ChunkMetadata])
async def get_document_chunks(document_id: str):
    """Retrieve all chunked text excerpts for a document with page numbers."""
    chunks = global_document_store.get_document_chunks(document_id)
    if not chunks and not global_document_store.get_document(document_id):
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")
    return chunks


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and all its chunks from SQLite and the active vector store index."""
    doc = global_document_store.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")

    deleted = global_document_store.delete_document(document_id)
    global_vector_store.delete_document(document_id)

    return {
        "status": "success",
        "message": f"Document '{document_id}' ({doc.filename}) successfully deleted.",
        "document_id": document_id
    }
