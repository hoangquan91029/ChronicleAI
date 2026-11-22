from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.rag import Citation


class VerificationLabel(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class HistoricalDisagreement(BaseModel):
    has_conflict: bool = False
    description: Optional[str] = None
    differing_sources: List[str] = Field(default_factory=list)


class SingleClaimVerification(BaseModel):
    claim: str = Field(..., description="The individual historical statement or proposition")
    status: VerificationLabel = Field(..., description="SUPPORTED | CONTRADICTED | INSUFFICIENT_EVIDENCE")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Verification confidence score")
    explanation: str = Field(..., description="Detailed historical rationale based strictly on source text")
    citations: List[Citation] = Field(default_factory=list, description="Citations supporting or refuting the claim")
    disagreement: Optional[HistoricalDisagreement] = None


class ClaimVerificationRequest(BaseModel):
    claims: List[str] = Field(..., description="List of historical claims to verify")
    document_ids: Optional[List[str]] = Field(None, description="Optional list of document IDs to verify against")


class ClaimVerificationResponse(BaseModel):
    total_claims: int
    supported_count: int
    contradicted_count: int
    insufficient_evidence_count: int
    results: List[SingleClaimVerification]
