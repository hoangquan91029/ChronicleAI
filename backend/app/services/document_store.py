import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from app.models.document import DocumentIngestResponse, DocumentMetadata, ChunkMetadata
from app.config import settings

logger = logging.getLogger(__name__)

DB_PATH = settings.BASE_DIR / "data" / "chronicle.db"


class DocumentStore:
    """
    SQLite-backed persistent document and chunk store for ChronicleAI.
    Ensures document metadata, chunks, and citations survive process restarts.
    """
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    source_type TEXT NOT NULL DEFAULT 'upload_pdf',
                    total_pages INTEGER NOT NULL DEFAULT 0,
                    total_chunks INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'INDEXED',
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    file_path TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    page INTEGER NOT NULL DEFAULT 1,
                    chunk_index INTEGER NOT NULL DEFAULT 0,
                    text TEXT NOT NULL,
                    source TEXT NOT NULL,
                    word_count INTEGER NOT NULL DEFAULT 0,
                    source_id TEXT,
                    source_title TEXT,
                    original_url TEXT,
                    folio_ref TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON document_chunks(document_id);")
            conn.commit()

    def save_document(
        self,
        doc: DocumentIngestResponse,
        source_type: str = "upload_pdf",
        status: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> DocumentIngestResponse:
        now = datetime.utcnow().isoformat()
        doc_status = status or doc.status

        with self._get_connection() as conn:
            meta_json = json.dumps(doc.metadata.model_dump())
            conn.execute("""
                INSERT INTO documents (
                    id, filename, source_type, total_pages, total_chunks,
                    status, metadata_json, file_path, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    filename=excluded.filename,
                    total_pages=excluded.total_pages,
                    total_chunks=excluded.total_chunks,
                    status=excluded.status,
                    metadata_json=excluded.metadata_json,
                    file_path=excluded.file_path,
                    updated_at=excluded.updated_at;
            """, (
                doc.document_id,
                doc.filename,
                source_type,
                doc.total_pages,
                len(doc.chunks),
                doc_status,
                meta_json,
                file_path,
                now,
                now
            ))

            # Replace chunks for this document
            conn.execute("DELETE FROM document_chunks WHERE document_id = ?;", (doc.document_id,))
            for chunk in doc.chunks:
                conn.execute("""
                    INSERT INTO document_chunks (
                        chunk_id, document_id, page, chunk_index, text,
                        source, word_count, source_id, source_title, original_url,
                        folio_ref, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk.chunk_id,
                    doc.document_id,
                    chunk.page,
                    chunk.chunk_index,
                    chunk.text,
                    chunk.source,
                    chunk.word_count,
                    chunk.source_id,
                    chunk.source_title,
                    chunk.original_url,
                    chunk.folio_ref,
                    now
                ))
            conn.commit()
        return doc

    def get_document(self, document_id: str) -> Optional[DocumentIngestResponse]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM documents WHERE id = ?;", (document_id,)).fetchone()
            if not row:
                return None

            chunks = self.get_document_chunks(document_id)
            meta_dict = json.loads(row["metadata_json"])
            metadata = DocumentMetadata(**meta_dict)

            return DocumentIngestResponse(
                document_id=row["id"],
                filename=row["filename"],
                total_pages=row["total_pages"],
                total_chunks=len(chunks),
                status=row["status"],
                metadata=metadata,
                chunks=chunks
            )

    def list_documents(self) -> List[DocumentIngestResponse]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC;").fetchall()
            results = []
            for row in rows:
                meta_dict = json.loads(row["metadata_json"])
                metadata = DocumentMetadata(**meta_dict)
                doc_id = row["id"]
                # Fetch chunks count and sample
                chunk_rows = conn.execute(
                    "SELECT chunk_id, page, text, source, document_id, chunk_index, word_count, source_id, source_title, original_url, folio_ref FROM document_chunks WHERE document_id = ? ORDER BY chunk_index ASC;",
                    (doc_id,)
                ).fetchall()
                chunks = [
                    ChunkMetadata(
                        chunk_id=c["chunk_id"],
                        page=c["page"],
                        text=c["text"],
                        source=c["source"],
                        document_id=c["document_id"],
                        chunk_index=c["chunk_index"],
                        word_count=c["word_count"],
                        source_id=c["source_id"],
                        source_title=c["source_title"],
                        original_url=c["original_url"],
                        folio_ref=c["folio_ref"]
                    ) for c in chunk_rows
                ]
                results.append(DocumentIngestResponse(
                    document_id=row["id"],
                    filename=row["filename"],
                    total_pages=row["total_pages"],
                    total_chunks=len(chunks),
                    status=row["status"],
                    metadata=metadata,
                    chunks=chunks
                ))
            return results

    def get_document_chunks(self, document_id: str) -> List[ChunkMetadata]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM document_chunks WHERE document_id = ? ORDER BY chunk_index ASC;",
                (document_id,)
            ).fetchall()
            return [
                ChunkMetadata(
                    chunk_id=r["chunk_id"],
                    page=r["page"],
                    text=r["text"],
                    source=r["source"],
                    document_id=r["document_id"],
                    chunk_index=r["chunk_index"],
                    word_count=r["word_count"],
                    source_id=r["source_id"],
                    source_title=r["source_title"],
                    original_url=r["original_url"],
                    folio_ref=r["folio_ref"]
                ) for r in rows
            ]

    def get_all_chunks(self) -> List[ChunkMetadata]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM document_chunks ORDER BY document_id, chunk_index ASC;"
            ).fetchall()
            return [
                ChunkMetadata(
                    chunk_id=r["chunk_id"],
                    page=r["page"],
                    text=r["text"],
                    source=r["source"],
                    document_id=r["document_id"],
                    chunk_index=r["chunk_index"],
                    word_count=r["word_count"],
                    source_id=r["source_id"],
                    source_title=r["source_title"],
                    original_url=r["original_url"],
                    folio_ref=r["folio_ref"]
                ) for r in rows
            ]

    def delete_document(self, document_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM documents WHERE id = ?;", (document_id,))
            conn.commit()
            return cursor.rowcount > 0

    def update_document_status(self, document_id: str, status: str):
        now = datetime.utcnow().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE documents SET status = ?, updated_at = ? WHERE id = ?;",
                (status, now, document_id)
            )
            conn.commit()


# Global document store instance
global_document_store = DocumentStore()
