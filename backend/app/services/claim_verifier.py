from typing import List, Optional
from app.models.verification import (
    ClaimVerificationRequest,
    ClaimVerificationResponse,
    SingleClaimVerification,
    VerificationLabel,
    HistoricalDisagreement
)
from app.services.vector_store import CitationVectorStore, global_vector_store
from app.services.llm_provider import get_llm_provider


class ClaimVerifier:
    def __init__(self, vector_store: Optional[CitationVectorStore] = None):
        self.vector_store = vector_store or global_vector_store
        self.llm = get_llm_provider()

    async def verify_claims(
        self,
        claims: List[str],
        document_ids: Optional[List[str]] = None
    ) -> ClaimVerificationResponse:
        """
        Verify a list of historical claims against retrieved evidence in the vector store.
        Distinguishes:
        - SUPPORTED
        - CONTRADICTED
        - INSUFFICIENT_EVIDENCE
        And detects disagreements across sources.
        """
        results: List[SingleClaimVerification] = []
        supported_count = 0
        contradicted_count = 0
        insufficient_evidence_count = 0

        for claim in claims:
            claim_text = claim.strip()
            if not claim_text:
                continue

            # Retrieve top matching chunks from vector store
            retrieved = self.vector_store.search(
                query=claim_text,
                top_k=4,
                document_id=document_ids[0] if document_ids and len(document_ids) == 1 else None,
                min_score=0.08
            )

            # Check multi-source disagreement if multiple distinct sources retrieved
            unique_sources = list(set([r.source for r in retrieved]))
            disagreement = None
            if len(unique_sources) > 1:
                # Potential multi-source comparison
                disagreement = HistoricalDisagreement(
                    has_conflict=False,
                    description=f"Khảo sát chéo qua {len(unique_sources)} nguồn tư liệu: {', '.join(unique_sources)}.",
                    differing_sources=unique_sources
                )

            # Execute verification
            verif = await self.llm.verify_claim(claim_text, retrieved)
            if disagreement and not verif.disagreement:
                verif.disagreement = disagreement

            if verif.status == VerificationLabel.SUPPORTED:
                supported_count += 1
            elif verif.status == VerificationLabel.CONTRADICTED:
                contradicted_count += 1
            else:
                insufficient_evidence_count += 1

            results.append(verif)

        return ClaimVerificationResponse(
            total_claims=len(results),
            supported_count=supported_count,
            contradicted_count=contradicted_count,
            insufficient_evidence_count=insufficient_evidence_count,
            results=results
        )
