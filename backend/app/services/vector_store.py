import re
from typing import List, Dict, Optional, Tuple, Any
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
        """Add new chunks to the vector store and re-index embeddings. Avoids duplicate indexing."""
        if not chunks:
            return

        new_count = 0
        for chunk in chunks:
            if chunk.chunk_id not in self.chunks or self.chunks[chunk.chunk_id].text != chunk.text:
                self.chunks[chunk.chunk_id] = chunk
                new_count += 1

        # Recompute index if new chunks were added or index uninitialized
        if new_count > 0 or self.embeddings is None:
            self.chunk_list = list(self.chunks.values())
            texts = [c.text for c in self.chunk_list]
            self.embedding_service.fit(texts)
            self.embeddings = self.embedding_service.transform(texts)

    def search(
        self,
        query: str,
        top_k: int = 5,
        document_id: Optional[str] = None,
        source_id: Optional[str] = None,
        min_page: Optional[int] = None,
        max_page: Optional[int] = None,
        min_score: float = 0.05
    ) -> List[SearchResult]:
        """
        Search indexed chunks by query similarity with fine-grained metadata filtering.
        Avoids mixing evidence from unrelated documents or sources.
        Returns ranked SearchResult objects with citations.
        """
        if not self.chunk_list or self.embeddings is None:
            return []

        # Generate query vector
        query_vec = self.embedding_service.embed_query(query).reshape(1, -1)
        
        # Calculate cosine similarity against all chunks
        scores = cosine_similarity(query_vec, self.embeddings)[0]

        # Combine with candidate indices and apply metadata filters
        results: List[Tuple[float, ChunkMetadata]] = []
        for idx, score in enumerate(scores):
            chunk = self.chunk_list[idx]
            if document_id and chunk.document_id != document_id:
                continue
            if source_id and getattr(chunk, "source_id", None) != source_id:
                continue
            if min_page is not None and chunk.page < min_page:
                continue
            if max_page is not None and chunk.page > max_page:
                continue
            if score >= min_score:
                results.append((float(score), chunk))

        # Sort descending by similarity score, breaking ties deterministically by chunk_id
        results.sort(key=lambda x: (-round(x[0], 5), x[1].chunk_id))
        top_results = results[:top_k]

        search_results: List[SearchResult] = []
        for score, chunk in top_results:
            quote = self._extract_relevant_quote(query, chunk.text)
            citation = Citation(
                filename=chunk.source,
                page=chunk.page,
                chunk_id=chunk.chunk_id,
                quote=quote,
                score=round(score, 4),
                source_id=getattr(chunk, "source_id", None),
                source_title=getattr(chunk, "source_title", None),
                original_url=getattr(chunk, "original_url", None),
                document_id=chunk.document_id,
                folio_ref=getattr(chunk, "folio_ref", None)
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

    def delete_document(self, document_id: str):
        """Remove all chunks associated with a document and refit index if necessary."""
        keys_to_del = [k for k, c in self.chunks.items() if c.document_id == document_id]
        for k in keys_to_del:
            del self.chunks[k]
        self.chunk_list = list(self.chunks.values())
        if self.chunk_list:
            texts = [c.text for c in self.chunk_list]
            self.embedding_service.fit(texts)
            self.embeddings = self.embedding_service.transform(texts)
        else:
            self.embeddings = None

    def sync_from_store(self, document_store):
        """Sync chunks from persistent SQLite store into active retrieval index."""
        chunks = document_store.get_all_chunks()
        if chunks:
            self.add_chunks(chunks)

    def get_stats(self) -> Dict[str, Any]:
        """Return operational statistics about the vector store."""
        doc_ids = self.get_document_ids()
        vocab_size = 0
        if hasattr(self.embedding_service, "vectorizer") and getattr(self.embedding_service.vectorizer, "vocabulary_", None):
            vocab_size = len(self.embedding_service.vectorizer.vocabulary_)
        return {
            "total_chunks": len(self.chunk_list),
            "total_documents": len(doc_ids),
            "document_ids": doc_ids,
            "vocabulary_size": vocab_size,
            "storage_engine": "sqlite3_backed_multilingual_vector_store",
            "is_indexed": self.embeddings is not None and len(self.chunk_list) > 0
        }

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
