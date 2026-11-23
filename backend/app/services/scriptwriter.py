from typing import List, Optional
from app.models.script import VideoScript, ScriptGenerationRequest
from app.services.vector_store import CitationVectorStore, global_vector_store
from app.services.llm_provider import get_llm_provider


class ScriptwriterService:
    def __init__(self, vector_store: Optional[CitationVectorStore] = None):
        self.vector_store = vector_store or global_vector_store
        self.llm = get_llm_provider()

    async def generate_script(
        self,
        request: ScriptGenerationRequest
    ) -> VideoScript:
        """
        Generate an educational, 15-20 min video script about the specified historical subject.
        Retrieves relevant historical evidence chunks, structures the narrative chronologically,
        attaches citations, and flags unverified facts for review.
        """
        # Retrieve key historical chunks for subject
        search_terms = [
            request.subject,
            "cải cách hành chính 13 đạo thừa tuyên",
            "Quốc Triều Hình Luật luật Hồng Đức",
            "bia tiến sĩ Văn Miếu Thân Nhân Trung",
            "Tao Đàn bản đồ Hồng Đức",
            "chiêm thành 1471 một thước núi một tấc sông"
        ]

        retrieved_chunks = []
        for term in search_terms:
            res = self.vector_store.search(query=term, top_k=3, min_score=0.08)
            retrieved_chunks.extend(res)

        # Deduplicate retrieved chunks by chunk_id
        seen_ids = set()
        deduped_chunks = []
        for c in retrieved_chunks:
            if c.chunk_id not in seen_ids:
                seen_ids.add(c.chunk_id)
                deduped_chunks.append(c)

        # Determine duration & format
        fmt = request.format
        target_mins = request.target_minutes
        if fmt is None:
            if target_mins is not None:
                if target_mins <= 1.5:
                    fmt = "SHORTS"
                elif target_mins <= 5.0:
                    fmt = "EXPLAINER"
                else:
                    fmt = "DOCUMENTARY"
            else:
                fmt = "DOCUMENTARY"
                target_mins = 16.0
        elif target_mins is None:
            fmt_val = fmt.value if hasattr(fmt, "value") else str(fmt)
            if fmt_val == "SHORTS":
                target_mins = 1.0
            elif fmt_val == "EXPLAINER":
                target_mins = 4.0
            else:
                target_mins = 16.0

        fmt_str = fmt.value if hasattr(fmt, "value") else str(fmt)

        script = await self.llm.generate_script(
            subject=request.subject,
            target_minutes=float(target_mins),
            chunks=deduped_chunks,
            format=fmt_str
        )


        # Audit script: any scenes without citations must be flagged for review
        flagged_count = 0
        for scene in script.scenes:
            if not scene.citations and scene.scene_type not in ["HOOK", "CONCLUSION"]:
                scene.needs_review = True
                scene.review_notes = "Cảnh thiếu trích dẫn tư liệu gốc trực tiếp — cần chuyên gia sử học đối chiếu."
                flagged_count += 1

        script.flagged_for_review_count = flagged_count
        return script
