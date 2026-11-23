from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ChunkMetadata(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier, e.g. chunk_001")
    page: int = Field(..., description="Original 1-indexed page number where chunk was extracted")
    text: str = Field(..., description="Extracted Vietnamese or multilingual text snippet")
    source: str = Field(..., description="Original PDF filename")
    document_id: str = Field(..., description="Parent document identifier")
    chunk_index: int = Field(..., description="Sequence index of chunk within the document")
    word_count: int = Field(default=0, description="Word count of the chunk text")
    source_id: Optional[str] = Field(None, description="Source collection identifier")
    source_title: Optional[str] = Field(None, description="Source collection title")
    original_url: Optional[str] = Field(None, description="Archive or IIIF URL")
    folio_ref: Optional[str] = Field(None, description="Traditional volume and folio reference")


class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    total_pages: int = 0
    file_size_bytes: int = 0
    is_scanned: bool = False
    ocr_required: bool = False
    warning_message: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class DocumentIngestResponse(BaseModel):
    document_id: str
    filename: str
    total_pages: int
    total_chunks: int
    status: str = Field(..., description="'success', 'scanned_ocr_required', 'empty_document', 'error'")
    metadata: DocumentMetadata
    chunks: List[ChunkMetadata] = Field(default_factory=list)
