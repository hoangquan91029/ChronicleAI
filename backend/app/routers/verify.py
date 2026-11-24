from fastapi import APIRouter
from app.models.verification import ClaimVerificationRequest, ClaimVerificationResponse
from app.services.claim_verifier import ClaimVerifier

router = APIRouter(prefix="/api/verify", tags=["Claim Verification"])
verifier = ClaimVerifier()


@router.post("", response_model=ClaimVerificationResponse)
@router.post("/claims", response_model=ClaimVerificationResponse)
async def verify_historical_claims(req: ClaimVerificationRequest):
    """
    Verify historical claims against indexed source texts.
    Labels each claim as:
    - SUPPORTED: Corroborated with source filename, page, and chunk_id.
    - CONTRADICTED: Clashes with recorded dates, facts, or negation in source.
    - INSUFFICIENT_EVIDENCE: Source documents lack information to corroborate.
    """
    return await verifier.verify_claims(
        claims=req.claims,
        document_ids=req.document_ids
    )
