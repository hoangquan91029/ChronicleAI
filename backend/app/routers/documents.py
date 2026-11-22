from typing import List, Dict
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.document import DocumentIngestResponse, ChunkMetadata
from app.services.pdf_processor import PDFProcessor, PDFProcessingError
from app.services.vector_store import global_vector_store

router = APIRouter(prefix="/api/documents", tags=["Documents"])

# In-memory document registry
uploaded_docs: Dict[str, DocumentIngestResponse] = {}
pdf_processor = PDFProcessor()


@router.post("/upload", response_model=DocumentIngestResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a historical PDF document, extract Vietnamese text with PyMuPDF,
    preserve page numbers, detect scanned PDFs / OCR requirements, and index chunks.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        content = await file.read()
        res = pdf_processor.process_pdf(
            pdf_bytes=content,
            filename=file.filename
        )
    except PDFProcessingError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error processing PDF: {str(e)}")

    uploaded_docs[res.document_id] = res

    # Index into vector store if chunks were successfully extracted
    if res.chunks:
        global_vector_store.add_chunks(res.chunks)

    return res


@router.get("", response_model=List[DocumentIngestResponse])
async def list_documents():
    """List all ingested historical documents."""
    return list(uploaded_docs.values())


@router.get("/{document_id}", response_model=DocumentIngestResponse)
async def get_document(document_id: str):
    """Retrieve details and metadata for a specific document."""
    if document_id not in uploaded_docs:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")
    return uploaded_docs[document_id]


@router.get("/{document_id}/chunks", response_model=List[ChunkMetadata])
async def get_document_chunks(document_id: str):
    """Retrieve all chunked text excerpts for a document with page numbers."""
    if document_id not in uploaded_docs:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")
    return uploaded_docs[document_id].chunks
