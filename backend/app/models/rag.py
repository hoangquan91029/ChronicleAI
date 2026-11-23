from pydantic import BaseModel, Field
from typing import List, Optional


class SearchQuery(BaseModel):
    query: str = Field(..., description="Query text to search across indexed historical sources")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of relevant chunks to retrieve")
    document_id: Optional[str] = Field(None, description="Optional document ID to scope search")
    source_id: Optional[str] = Field(None, description="Optional source collection ID to scope search")
    min_page: Optional[int] = Field(None, description="Optional minimum page number filter")
    max_page: Optional[int] = Field(None, description="Optional maximum page number filter")


class Citation(BaseModel):
    filename: str = Field(..., description="Source document filename")
    page: int = Field(..., description="Original page number in source document")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    quote: str = Field(default="", description="Relevant excerpt quote supporting the statement")
    score: float = Field(default=0.0, description="Relevance / similarity score")
    source_id: Optional[str] = Field(None, description="Identifier of the historical source collection/registry")
    source_title: Optional[str] = Field(None, description="Full formal title of the historical source")
    original_url: Optional[str] = Field(None, description="Digital archive permalink or IIIF manifest URL")
    document_id: Optional[str] = Field(None, description="Parent document identifier")
    folio_ref: Optional[str] = Field(None, description="Traditional volume and folio reference, e.g. Quyển XII, 62a")

    @property
    def source(self) -> str:
        return self.filename


class SearchResult(BaseModel):
    chunk_id: str
    page: int
    text: str
    source: str
    document_id: str
    score: float
    citation: Citation


class SearchResponse(BaseModel):
    query: str
    total_matches: int
    results: List[SearchResult]


class GroundedAnswerRequest(BaseModel):
    question: str
    top_k: int = 5
    document_id: Optional[str] = None


class GroundedAnswerResponse(BaseModel):
    question: str
    answer: str
    grounded: bool
    citations: List[Citation]
    retrieved_chunks: List[SearchResult]
