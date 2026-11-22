from fastapi import APIRouter
from app.models.rag import (
    SearchQuery,
    SearchResponse,
    GroundedAnswerRequest,
    GroundedAnswerResponse
)
from app.services.vector_store import global_vector_store
from app.services.llm_provider import get_llm_provider

router = APIRouter(prefix="/api/rag", tags=["RAG & Retrieval"])
llm = get_llm_provider()


@router.post("/search", response_model=SearchResponse)
async def search_evidence(req: SearchQuery):
    """
    Search historical passages across ingested documents.
    Returns matched chunks along with citations (filename, page, chunk_id).
    """
    results = global_vector_store.search(
        query=req.query,
        top_k=req.top_k,
        document_id=req.document_id,
        min_score=0.04
    )
    return SearchResponse(
        query=req.query,
        total_matches=len(results),
        results=results
    )


@router.post("/answer", response_model=GroundedAnswerResponse)
async def grounded_qa(req: GroundedAnswerRequest):
    """
    Generate an answer grounded strictly in retrieved historical documents.
    Attaches page-level citations; refuses to hallucinate facts outside the sources.
    """
    retrieved = global_vector_store.search(
        query=req.question,
        top_k=req.top_k,
        document_id=req.document_id,
        min_score=0.06
    )

    qa_res = await llm.generate_grounded_answer(req.question, retrieved)
    return GroundedAnswerResponse(
        question=req.question,
        answer=qa_res["answer"],
        grounded=qa_res["grounded"],
        citations=qa_res["citations"],
        retrieved_chunks=retrieved
    )
