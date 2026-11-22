import re
from typing import List, Dict, Optional, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.models.document import ChunkMetadata
from app.models.rag import Citation, SearchResult
from app.services.embedding_service import MultilingualEmbeddingService


class CitationVectorStore:
    """
    In-memory vector store with citation preservation and metadata filtering.
    Preserves exact document ID, page number, chunk ID, and source filename
    for 100% academic citation integrity.
    """
    def __init__(self):
        self.chunks: Dict[str, ChunkMetadata] = {}  # chunk_id -> ChunkMetadata
        self.chunk_list: List[ChunkMetadata] = []
        self.embedding_service = MultilingualEmbeddingService()
        self.embeddings: Optional[np.ndarray] = None

    def add_chunks(self, chunks: List[ChunkMetadata]):
        """Add new chunks to the vector store and re-index embeddings."""
        if not chunks:
            return

        for chunk in chunks:
            self.chunks[chunk.chunk_id] = chunk

        # Deduplicate and sort chunk_list
        self.chunk_list = list(self.chunks.values())
        texts = [c.text for c in self.chunk_list]

        # Fit embedding service on all chunk texts and generate vectors
        self.embedding_service.fit(texts)
        self.embeddings = self.embedding_service.transform(texts)

    def search(
        self,
        query: str,
        top_k: int = 5,
        document_id: Optional[str] = None,
        min_score: float = 0.05
    ) -> List[SearchResult]:
        """
        Search indexed chunks by query similarity.
        Returns ranked SearchResult objects with citations.
        """
        if not self.chunk_list or self.embeddings is None:
            return []

        # Generate query vector
        query_vec = self.embedding_service.embed_query(query).reshape(1, -1)
        
        # Calculate cosine similarity against all chunks
        scores = cosine_similarity(query_vec, self.embeddings)[0]

        # Combine with candidate indices
        results: List[Tuple[float, ChunkMetadata]] = []
        for idx, score in enumerate(scores):
            chunk = self.chunk_list[idx]
            if document_id and chunk.document_id != document_id:
                continue
            if score >= min_score:
                results.append((float(score), chunk))

        # Sort descending by similarity score
        results.sort(key=lambda x: x[0], reverse=True)
        top_results = results[:top_k]

        search_results: List[SearchResult] = []
        for score, chunk in top_results:
            quote = self._extract_relevant_quote(query, chunk.text)
            citation = Citation(
                filename=chunk.source,
                page=chunk.page,
                chunk_id=chunk.chunk_id,
                quote=quote,
                score=round(score, 4)
            )
            search_results.append(
                SearchResult(
                    chunk_id=chunk.chunk_id,
                    page=chunk.page,
                    text=chunk.text,
                    source=chunk.source,
                    document_id=chunk.document_id,
                    score=round(score, 4),
                    citation=citation
                )
            )

        return search_results

    def get_chunk(self, chunk_id: str) -> Optional[ChunkMetadata]:
        return self.chunks.get(chunk_id)

    def get_all_chunks(self, document_id: Optional[str] = None) -> List[ChunkMetadata]:
        if document_id:
            return [c for c in self.chunk_list if c.document_id == document_id]
        return self.chunk_list

    def get_document_ids(self) -> List[str]:
        return list(set(c.document_id for c in self.chunk_list))

    def clear(self):
        self.chunks.clear()
        self.chunk_list.clear()
        self.embeddings = None

    def _extract_relevant_quote(self, query: str, text: str, max_chars: int = 160) -> str:
        """Find the sentence or snippet in the chunk most relevant to the query."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        if not sentences:
            return text[:max_chars]

        # Find sentence with highest token overlap with query
        query_words = set(re.findall(r"\w+", query.lower()))
        best_sentence = sentences[0]
        max_overlap = -1

        for sent in sentences:
            sent_words = set(re.findall(r"\w+", sent.lower()))
            overlap = len(query_words.intersection(sent_words))
            if overlap > max_overlap:
                max_overlap = overlap
                best_sentence = sent

        clean_quote = best_sentence.strip()
        if len(clean_quote) > max_chars:
            return clean_quote[:max_chars] + "..."
        return clean_quote


# Global singleton instance for in-app retrieval
global_vector_store = CitationVectorStore()
