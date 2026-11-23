from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    documents_router,
    rag_router,
    verify_router,
    scripts_router,
    storyboards_router,
    videos_router
)
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import global_vector_store
from app.services.llm_provider import get_llm_provider
from app.routers.documents import uploaded_docs


import json
from app.services.document_store import global_document_store
from app.models.document import ChunkMetadata, DocumentMetadata, DocumentIngestResponse


def ensure_sample_data_loaded():
    """Ensure persistent SQLite store and in-memory vector store are initialized and synced."""
    # First sync any existing data in SQLite into vector store
    global_vector_store.sync_from_store(global_document_store)

    # If no documents are stored yet, populate default historical sources
    if len(global_document_store.list_documents()) == 0:
        # 1. Sample PDF
        sample_pdf = settings.BASE_DIR / "sample_data" / "le_thanh_tong_dai_viet.pdf"
        if sample_pdf.exists():
            try:
                with open(sample_pdf, "rb") as f:
                    content = f.read()
                processor = PDFProcessor()
                res = processor.process_pdf(
                    pdf_bytes=content,
                    filename="le_thanh_tong_dai_viet.pdf",
                    document_id="doc_le_thanh_tong_001"
                )
                if res.chunks:
                    global_document_store.save_document(res, source_type="synthetic_fixture", status="INDEXED")
                    global_vector_store.add_chunks(res.chunks)
                    print(f"[ChronicleAI] Initialized sample historical document: {res.filename} ({len(res.chunks)} chunks)")
            except Exception as e:
                print(f"[ChronicleAI] Warning initializing sample document: {e}")

        # 2. Authentic Archival Corpus (DVSKTT)
        archive_file = settings.BASE_DIR / "data" / "sources" / "dai_viet_su_ky_toan_thu_ban_ky_thuc_luc_quyen_12_13.json"
        if archive_file.exists():
            try:
                with open(archive_file, "r", encoding="utf-8") as f:
                    archive_data = json.load(f)
                arch_chunks = []
                for i, sec in enumerate(archive_data.get("sections", [])):
                    chunk_id = f"chunk_dvsktt_{sec['folio_ref']}"
                    arch_chunks.append(ChunkMetadata(
                        chunk_id=chunk_id,
                        document_id="doc_dvsktt_1697_bktl",
                        chunk_index=i,
                        page=sec.get("quyen", 12),
                        text=sec["text"],
                        source=archive_data["source_title"],
                        word_count=len(sec["text"].split()),
                        source_id=archive_data["source_id"],
                        source_title=sec.get("historical_topic", archive_data["source_title"]),
                        original_url=sec.get("iiif_image_url"),
                        folio_ref=sec.get("folio_ref")
                    ))
                arch_meta = DocumentMetadata(
                    title=archive_data["source_title"],
                    author=archive_data.get("compiler", "Nội các quan bản"),
                    subject="Đại Việt Sử Ký Toàn Thư (Bản Kỷ Thực Lục)",
                    total_pages=len(arch_chunks),
                    file_size_bytes=sum(c.word_count for c in arch_chunks),
                    extra={"edition": archive_data.get("original_edition", "1697")}
                )
                arch_doc = DocumentIngestResponse(
                    document_id="doc_dvsktt_1697_bktl",
                    filename="dai_viet_su_ky_toan_thu_ban_ky_thuc_luc_quyen_12_13.json",
                    total_pages=len(arch_chunks),
                    total_chunks=len(arch_chunks),
                    status="INDEXED",
                    metadata=arch_meta,
                    chunks=arch_chunks
                )
                global_document_store.save_document(arch_doc, source_type="authentic_archival", status="INDEXED")
                global_vector_store.add_chunks(arch_chunks)
                print(f"[ChronicleAI] Initialized authentic archival corpus: {archive_data['source_title']} ({len(arch_chunks)} folios)")
            except Exception as e:
                print(f"[ChronicleAI] Warning initializing archival corpus: {e}")



ensure_sample_data_loaded()


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_sample_data_loaded()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Open-Source AI Historical Research & Video Production Platform",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(documents_router)
app.include_router(rag_router)
app.include_router(verify_router)
app.include_router(scripts_router)
app.include_router(storyboards_router)
app.include_router(videos_router)



@app.get("/")
async def root():
    return {
        "platform": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "online",
        "case_study": "Emperor Lê Thánh Tông of Đại Việt (1460–1497)",
        "docs_url": "/docs"
    }


@app.get("/api/health")
async def health_check():
    provider = get_llm_provider()
    provider_class = provider.__class__.__name__
    model_name = getattr(provider, "model", "rule-heuristic-v1")
    return {
        "status": "healthy",
        "documents_indexed": len(uploaded_docs),
        "total_chunks_indexed": len(global_vector_store.chunk_list),
        "llm_provider": settings.LLM_PROVIDER,
        "active_provider_class": provider_class,
        "model": model_name,
        "available_providers": ["offline", "gemini", "openai"]
    }
