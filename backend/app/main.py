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
    storyboards_router
)
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import global_vector_store
from app.services.llm_provider import get_llm_provider
from app.routers.documents import uploaded_docs


def ensure_sample_data_loaded():
    """Ensure baseline historical sample document on Le Thanh Tong is loaded."""
    if not global_vector_store.chunk_list:
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
                    global_vector_store.add_chunks(res.chunks)
                    uploaded_docs[res.document_id] = res
                    print(f"[ChronicleAI] Initialized sample historical document: {res.filename} ({len(res.chunks)} chunks)")
            except Exception as e:
                print(f"[ChronicleAI] Warning initializing sample document: {e}")


# Initialize sample data on module load
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
