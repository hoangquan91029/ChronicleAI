from pydantic import BaseModel, Field
from typing import List, Optional


class SearchQuery(BaseModel):
    query: str = Field(..., description="Query text to search across indexed historical sources")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of relevant chunks to retrieve")
    document_id: Optional[str] = Field(None, description="Optional document ID to scope search")


class Citation(BaseModel):
    filename: str = Field(..., description="Source document filename")
    page: int = Field(..., description="Original page number in source document")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    quote: str = Field(default="", description="Relevant excerpt quote supporting the statement")
    score: float = Field(default=0.0, description="Relevance / similarity score")

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
