from app.routers.documents import router as documents_router
from app.routers.rag import router as rag_router
from app.routers.verify import router as verify_router
from app.routers.scripts import router as scripts_router
from app.routers.storyboards import router as storyboards_router
from app.routers.videos import router as videos_router

__all__ = [
    "documents_router",
    "rag_router",
    "verify_router",
    "scripts_router",
    "storyboards_router",
    "videos_router",
]

