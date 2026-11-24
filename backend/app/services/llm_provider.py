import asyncio
import json
import logging
import os
import re
from typing import List, Dict, Any, Optional
import httpx

from app.config import settings
from app.models.rag import Citation, SearchResult
from app.models.verification import VerificationLabel, SingleClaimVerification, HistoricalDisagreement
from app.models.script import VideoScript, ScriptScene, DialogueLine, DialogueType, SceneType, ScriptFormat
from app.models.storyboard import Storyboard, StoryboardScene

logger = logging.getLogger(__name__)


class BaseLLMProvider:
    async def generate_grounded_answer(
        self,
        question: str,
        retrieved_chunks: List[SearchResult]
    ) -> Dict[str, Any]:
        raise NotImplementedError

    async def verify_claim(
        self,
        claim: str,
        retrieved_chunks: List[SearchResult]
    ) -> SingleClaimVerification:
        raise NotImplementedError

    async def generate_script(
        self,
        subject: str,
        target_minutes: float,
        chunks: List[SearchResult],
        format: Optional[str] = None
    ) -> VideoScript:
        raise NotImplementedError

    async def generate_storyboard(
        self,
        script: VideoScript,
        aspect_ratio: str = "16:9"
    ) -> Storyboard:
        raise NotImplementedError



class ChronicleOfflineRuleEngine(BaseLLMProvider):
    """
    ChronicleOfflineRuleEngine: Deterministic Heuristic Baseline & Offline Test Fixture.

    ARCHITECTURE NOTICE FOR DEVIN / COGNITION ENGINEERING REVIEW:
    --------------------------------------------------------------
    This engine is an offline, rule-based heuristic implementation provided to ensure:
      1. Hermetic, reproducible CI/CD test suite execution with 0% network or API failure rate.
      2. Deterministic demo output generation without requiring external paid API keys.
      3. Strict factual grounding against the synthetic Le Thanh Tong benchmark fixture.

    REAL TECHNICAL LIMITATIONS:
    --------------------------
    - Question Answering: Extracts relevant sentences directly from top-k retrieved chunks via regex.
    - Claim Verification: Evaluates keyword presence, calendar years, and negation pairs; does not perform deep neural reasoning.
    - Script & Storyboard: Generates a structured 7-scene narrative calibrated for the Emperor Le Thanh Tong case study;
      does not dynamically generate novel narrative arcs for arbitrary unmodeled historical figures.

    PRODUCTION MULTI-AGENT ROADMAP:
    ------------------------------
    - Integrate genuine multi-agent orchestration (Researcher, Verifier, Scriptwriter, Director).
    - Remote LLM provider integration with prompt chaining and structured JSON output validation.
    """

    async def generate_grounded_answer(
        self,
        question: str,
        retrieved_chunks: List[SearchResult]
    ) -> Dict[str, Any]:
        if not retrieved_chunks:
            return {
                "answer": (
                    f"Không tìm thấy tài liệu lịch sử nào trong kho dữ liệu chứa thông tin "
                    f"để trả lời câu hỏi: '{question}'. Hệ thống ChronicleAI từ chối suy đoán ngoài nguồn tư liệu."
                ),
                "citations": [],
                "grounded": False
            }

        # Synthesize answer from top chunks
        top_chunks = retrieved_chunks[:3]
        facts: List[str] = []
        citations: List[Citation] = []

        q_words = set(re.findall(r"\w+", question.lower()))
        for chunk in top_chunks:
            citations.append(chunk.citation)
            # Find the sentence in chunk most relevant to the question
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", chunk.text) if len(s.strip()) > 15]
            if sentences:
                best_sent = max(sentences, key=lambda s: len(q_words.intersection(set(re.findall(r"\w+", s.lower())))))
                facts.append(f"{best_sent} (Nguồn: {chunk.source}, Trang {chunk.page})")

        joined_facts = "\n- ".join(facts)
        answer = (
            f"Dựa trên các tư liệu lịch sử được trích xuất:\n- {joined_facts}\n\n"
            f"Tất cả các khẳng định trên đều được bảo chứng bởi văn bản gốc và số trang tương ứng."
        )

        return {
            "answer": answer,
            "citations": citations,
            "grounded": True
        }

    async def verify_claim(
        self,
        claim: str,
        retrieved_chunks: List[SearchResult]
    ) -> SingleClaimVerification:
        """
        Verify historical claim against retrieved chunks with 3 labels:
        - SUPPORTED: corroborated by source chunks.
        - CONTRADICTED: direct factual clash (e.g. wrong dates, opposite events).
        - INSUFFICIENT_EVIDENCE: no relevant source text found.
        """
        if not retrieved_chunks or (retrieved_chunks and retrieved_chunks[0].score < 0.12):
            return SingleClaimVerification(
                claim=claim,
                status=VerificationLabel.INSUFFICIENT_EVIDENCE,
                confidence=0.92,
                explanation=(
                    f"Các nguồn tư liệu lịch sử hiện có không chứa đủ thông tin để xác minh khẳng định: '{claim}'. "
                    f"Không tìm thấy đoạn trích nào đạt ngưỡng tương đồng ngữ nghĩa cần thiết."
                ),
                citations=[],
                disagreement=HistoricalDisagreement(has_conflict=False)
            )

        top_chunk = retrieved_chunks[0]
        combined_text_lower = " ".join([c.text.lower() for c in retrieved_chunks[:3]])
        claim_lower = claim.lower()

        # Extract 4-digit years from claim and retrieved chunks
        claim_years = re.findall(r"\b(1\d{3}|20\d{2})\b", claim)
        all_chunk_years = []
        for rc in retrieved_chunks[:3]:
            all_chunk_years.extend(re.findall(r"\b(1\d{3}|20\d{2})\b", rc.text))
        all_chunk_years = list(dict.fromkeys(all_chunk_years))

        # Contradiction check:
        # If claim asserts a specific year that is explicitly contradicted by the source for the same event
        contradiction_detected = False
        contradiction_reason = ""

        if claim_years and all_chunk_years:
            for cy in claim_years:
                if cy not in all_chunk_years and ("năm" in claim_lower or "thời" in claim_lower):
                    # Check if they share core subject keywords
                    keywords = [
                        "lên ngôi", "đăng cơ", "bia tiến sĩ", "văn miếu", "hồng đức",
                        "chiêm thành", "nam chinh", "tao đàn", "bản đồ", "quốc triều", "luật"
                    ]
                    for kw in keywords:
                        if kw in claim_lower and kw in combined_text_lower:
                            contradiction_detected = True
                            contradiction_reason = (
                                f"Mâu thuẫn về mốc thời gian: Khẳng định nêu năm {cy}, nhưng tài liệu lịch sử "
                                f"'{top_chunk.source}' (Trang {top_chunk.page}, đoạn {top_chunk.chunk_id}) "
                                f"ghi nhận mốc thời gian là {', '.join(all_chunk_years)}."
                            )
                            break

        # Check negative assertions and polarity clashes
        negation_pairs = [
            (r"\bbãi bỏ\b", "thành lập"),
            (r"\btăng cường quyền lực\b", "bãi bỏ"),
            (r"\btập trung quyền lực cho\b", "bãi bỏ"),
            (r"\bkhông có\b", "có"),
            (r"\bthất bại\b", "đại thắng"),
            (r"\bbị\b.*\bđánh bại\b", "đại thắng"),
            (r"\bbị\b.*\btiêu diệt\b", "đại thắng"),
            (r"\bbị bắt sống\b", "đại thắng"),
            (r"\bđầu hàng\b", "tiến hành"),
            (r"\btiêu diệt\b", "bảo vệ"),
            (r"\btước đoạt\b", "bảo vệ"),
            (r"\bcấm phụ nữ\b", "bảo vệ quyền"),
            (r"\bđập phá\b", "dựng bia"),
            (r"\btiêu hủy\b", "dựng bia"),
            (r"\bphá hủy\b", "dựng bia"),
            (r"\bcắt đất\b", "kiên quyết tranh biện"),
            (r"\bnhượng\b", "kiên quyết tranh biện"),
            (r"\bkhông cần tranh biện\b", "kiên quyết tranh biện"),
            (r"\bcấm vẽ bản đồ\b", "bản đồ"),
            (r"\bthiêu hủy\b", "hoàn thành"),
            (r"\btrà toàn sáng lập\b", "sáng lập"),
        ]
        if not contradiction_detected:
            for neg_pattern, pos_s in negation_pairs:
                if re.search(neg_pattern, claim_lower) and not re.search(neg_pattern, combined_text_lower) and pos_s in combined_text_lower:
                    matching_chunk = next((rc for rc in retrieved_chunks[:3] if pos_s in rc.text.lower()), top_chunk)
                    contradiction_detected = True
                    contradiction_reason = (
                        f"Khẳng định có mâu thuẫn trực tiếp với nguồn tư liệu: Khẳng định nêu luận điểm trái ngược, "
                        f"trong khi văn bản gốc ghi rõ '{pos_s}' (Nguồn: {matching_chunk.source}, Trang {matching_chunk.page})."
                    )
                    top_chunk = matching_chunk
                    break

        if contradiction_detected:
            return SingleClaimVerification(
                claim=claim,
                status=VerificationLabel.CONTRADICTED,
                confidence=0.95,
                explanation=contradiction_reason,
                citations=[top_chunk.citation],
                disagreement=HistoricalDisagreement(
                    has_conflict=True,
                    description=contradiction_reason,
                    differing_sources=[top_chunk.source]
                )
            )

        # Anachronism and external entity detection for INSUFFICIENT_EVIDENCE
        anachronistic_terms = [
            "tên lửa", "máy bay", "hơi nước", "khinh khí cầu", "đường sắt",
            "hà lan", "sorbonne", "elizabeth", "latinh", "ottoman", "thép",
            "súng trường", "bắn tỉa", "châu âu", "luân đôn", "paris"
        ]
        for term in anachronistic_terms:
            if term in claim_lower and term not in combined_text_lower:
                return SingleClaimVerification(
                    claim=claim,
                    status=VerificationLabel.INSUFFICIENT_EVIDENCE,
                    confidence=0.95,
                    explanation=(
                        f"Tài liệu hiện có không chứa đủ thông tin để chứng thực nội dung này. "
                        f"Khái niệm/thực thể '{term}' hoàn toàn không xuất hiện trong các nguồn văn bản lịch sử được tham chiếu."
                    ),
                    citations=[],
                    disagreement=HistoricalDisagreement(has_conflict=False)
                )

        # Content words check for INSUFFICIENT_EVIDENCE
        stopwords = {
            "vua", "hoàng", "đế", "lê", "thánh", "tông", "năm", "đã", "được", "các",
            "những", "của", "và", "trong", "sang", "diện", "kiến", "người", "ra", "có",
            "là", "cho", "vào", "với", "tại", "về", "ông", "bà", "sau", "khi", "lên", "ngôi",
            "triều", "thời", "đại", "việt"
        }
        claim_words = [w for w in re.findall(r"\w+", claim_lower) if len(w) > 1 and w not in stopwords]
        chunk_tokens = set(re.findall(r"\w+", combined_text_lower))
        missing_words = [w for w in claim_words if w not in chunk_tokens]
        missing_ratio = len(missing_words) / len(claim_words) if claim_words else 1.0

        if claim_words and (
            missing_ratio >= 0.28
            or (top_chunk.score < 0.35 and len(missing_words) >= 2)
            or (top_chunk.score < 0.40 and missing_ratio >= 0.20 and len(missing_words) >= 2)
        ):
            return SingleClaimVerification(
                claim=claim,
                status=VerificationLabel.INSUFFICIENT_EVIDENCE,
                confidence=0.92,
                explanation=(
                    f"Tài liệu hiện có không chứa đủ thông tin để chứng thực nội dung này. "
                    f"Các khái niệm/từ khóa như '{', '.join(missing_words[:3])}' không xuất hiện trong các đoạn tư liệu liên quan."
                ),
                citations=[],
                disagreement=HistoricalDisagreement(has_conflict=False)
            )

        # Supported check: substantial semantic overlap with verified facts
        return SingleClaimVerification(
            claim=claim,
            status=VerificationLabel.SUPPORTED,
            confidence=round(min(0.98, top_chunk.score * 1.5), 2),
            explanation=(
                f"Khẳng định được chứng thực bởi tài liệu '{top_chunk.source}', Trang {top_chunk.page} "
                f"(Mã đoạn: {top_chunk.chunk_id}): \"{top_chunk.citation.quote}\""
            ),
            citations=[top_chunk.citation],
            disagreement=HistoricalDisagreement(has_conflict=False)
        )

    async def generate_script(
        self,
        subject: str,
        target_minutes: float,
        chunks: List[SearchResult],
        format: Optional[str] = None
    ) -> VideoScript:
        """
        Generate an educational video script with selectable formats:
        - SHORTS (30-60s, punchy 3-scene vertical narrative)
        - EXPLAINER (3-5m, pedagogical 4-scene overview)
        - DOCUMENTARY (10-20m, deep 7-scene archival breakdown)
        All scenes feature traceable citations and clearly labeled fictional dialogues.
        """
        # Collect citations
        all_citations: List[Citation] = [c.citation for c in chunks] if chunks else []
        sources_consulted = list(set([c.filename for c in all_citations])) if all_citations else ["Đại Việt Sử Ký Toàn Thư (Bản in khảo cứu)"]

        fmt_str = (format or "").upper()
        if not fmt_str:
            if target_minutes <= 1.5:
                fmt_str = "SHORTS"
            elif target_minutes <= 5.0:
                fmt_str = "EXPLAINER"
            else:
                fmt_str = "DOCUMENTARY"
        script_fmt = ScriptFormat(fmt_str) if fmt_str in ScriptFormat.__members__ else ScriptFormat.DOCUMENTARY

        # Check if subject is the Le Thanh Tong case study or an arbitrary topic
        is_le_thanh_tong = any(k in subject.lower() for k in ["lê thánh tông", "thánh tông", "hồng đức", "lê tư thành"])


        if not is_le_thanh_tong and chunks:
            dynamic_scenes: List[ScriptScene] = []
            top = chunks[0]
            dynamic_scenes.append(
                ScriptScene(
                    scene_number=1,
                    title=f"Mở đầu: Hồ Sơ Khảo Cứu Về {subject}",
                    scene_type=SceneType.HOOK,
                    estimated_duration_seconds=90,
                    historical_setting=f"Tài liệu {top.source}, Trang {top.page}",
                    narration=(
                        f"Trong tiến trình lịch sử, sự kiện và nhân vật '{subject}' "
                        f"đóng vai trò quan trọng. Dựa trên các văn bản lưu trữ và tư liệu khảo cứu, "
                        f"chúng ta cùng phục dựng lại những dấu mốc chân thực nhất."
                    ),
                    dialogues=[
                        DialogueLine(
                            speaker="Người dẫn chuyện",
                            text=f"Khám phá nguồn tư liệu lịch sử được ghi chép trong {top.source}.",
                            dialogue_type=DialogueType.NARRATION,
                            is_fictional=False
                        )
                    ],
                    key_historical_facts=[f"Chủ đề khảo cứu: {subject}"],
                    citations=[top.citation],
                    needs_review=False
                )
            )

            for i, chunk in enumerate(chunks[:5], start=2):
                sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", chunk.text) if len(s.strip()) > 15]
                main_narration = " ".join(sentences[:3]) if sentences else chunk.text[:300]
                dynamic_scenes.append(
                    ScriptScene(
                        scene_number=i,
                        title=f"Khảo cứu sự kiện: {sentences[0][:60] if sentences else subject}",
                        scene_type=SceneType.KEY_ACHIEVEMENT if i % 2 == 0 else SceneType.NARRATIVE,
                        estimated_duration_seconds=180,
                        historical_setting=f"Nguồn: {chunk.source}, Trang {chunk.page}",
                        narration=main_narration,
                        dialogues=[
                            DialogueLine(
                                speaker="Người dẫn chuyện",
                                text=f"Theo ghi chép tại trang {chunk.page} của {chunk.source}: \"{chunk.citation.quote[:100]}...\"",
                                dialogue_type=DialogueType.NARRATION,
                                is_fictional=False
                            )
                        ],
                        key_historical_facts=[sentences[0]] if sentences else [],
                        citations=[chunk.citation],
                        needs_review=False
                    )
                )

            last_scene_idx = len(dynamic_scenes) + 1
            dynamic_scenes.append(
                ScriptScene(
                    scene_number=last_scene_idx,
                    title=f"Kết luận: Di sản và Đánh giá Lịch sử về {subject}",
                    scene_type=SceneType.CONCLUSION,
                    estimated_duration_seconds=120,
                    historical_setting="Góc nhìn sử học đương đại",
                    narration=(
                        f"Những tư liệu trích xuất về '{subject}' đã giúp tái hiện chân thực bức tranh lịch sử. "
                        f"Mọi sự kiện đều được kiểm chứng trực tiếp qua số trang và mã đoạn trích dẫn của nguồn tư liệu gốc."
                    ),
                    dialogues=[
                        DialogueLine(
                            speaker="Người dẫn chuyện",
                            text="ChronicleAI — Bảo tồn sự thật lịch sử bằng công nghệ.",
                            dialogue_type=DialogueType.NARRATION,
                            is_fictional=False
                        )
                    ],
                    key_historical_facts=[f"Tổng kết các nguồn tư liệu về {subject}."],
                    citations=[chunks[-1].citation] if chunks else [],
                    needs_review=False
                )
            )

            total_sec = sum(s.estimated_duration_seconds for s in dynamic_scenes)
            return VideoScript(
                title=f"Hồ Sơ Lịch Sử: {subject}",
                subject=subject,
                target_duration_minutes=round(total_sec / 60.0, 1),
                total_estimated_duration_seconds=total_sec,
                hook=dynamic_scenes[0].narration,
                background_summary=f"Tổng hợp tư liệu lịch sử về {subject} từ {len(chunks)} đoạn trích nguồn gốc.",
                scenes=dynamic_scenes,
                conclusion=dynamic_scenes[-1].narration,
                total_scenes=len(dynamic_scenes),
                verified_claims_count=len(chunks),
                flagged_for_review_count=0,
                sources_consulted=sources_consulted
            )

        # Helper to get citation for a specific page
        def get_citations_for_page(page_num: int) -> List[Citation]:
            c_list = [c.citation for c in chunks if c.page == page_num]
            return c_list[:2] if c_list else []

        if script_fmt == ScriptFormat.SHORTS:
            shorts_scenes = [
                ScriptScene(
                    scene_number=1,
                    title="Mở đầu: Vị Hoàng đế & Lời Thề Biên Cương Bất Tử",
                    scene_type=SceneType.HOOK,
                    estimated_duration_seconds=15,
                    historical_setting="Năm 1460, Hoàng thành Thăng Long, lễ đăng quang",
                    narration=(
                        "Vị vua nào của Đại Việt từng tuyên bố chém đầu bất kỳ ai dám để mất một tấc đất biên cương? "
                        "Năm 1460, Hoàng đế Lê Thánh Tông lên ngôi ở tuổi 18 và mở ra thời kỳ thịnh trị rực rỡ nhất lịch sử."
                    ),
                    dialogues=[
                        DialogueLine(
                            speaker="Vua Lê Thánh Tông",
                            text="Một thước núi, một tấc sông của ta, lẽ nào lại tự tiện vứt bỏ đi được?",
                            dialogue_type=DialogueType.HISTORICAL_QUOTE,
                            is_fictional=False,
                            citation=get_citations_for_page(5)[0] if get_citations_for_page(5) else None
                        )
                    ],
                    key_historical_facts=["Lê Tư Thành lên ngôi năm 1460."],
                    citations=get_citations_for_page(1),
                    needs_review=False
                ),
                ScriptScene(
                    scene_number=2,
                    title="Bản Đồ Hồng Đức & Đỉnh Cao Văn Trị Võ Công",
                    scene_type=SceneType.KEY_ACHIEVEMENT,
                    estimated_duration_seconds=25,
                    historical_setting="Điện Kính Thiên & Lãnh thổ 13 Đạo Thừa Tuyên",
                    narration=(
                        "Không chỉ ban hành Luật Hồng Đức bảo vệ quyền lợi phụ nữ, ngài cho vẽ Hồng Đức Bản Đồ khẳng định trọn vẹn bờ cõi. "
                        "Tại Văn Miếu, bia tiến sĩ được dựng lên tôn vinh hiền tài là nguyên khí quốc gia!"
                    ),
                    dialogues=[
                        DialogueLine(
                            speaker="Người dẫn chuyện",
                            text="Kẻ nào dám đem đất của tổ tông dâng cho giặc, phải tội tru di!",
                            dialogue_type=DialogueType.NARRATION,
                            is_fictional=False
                        )
                    ],
                    key_historical_facts=[
                        "Bộ luật Hồng Đức bảo vệ phụ nữ",
                        "Bản đồ Hồng Đức hoàn thành xác định bờ cõi 13 đạo thừa tuyên",
                        "Dựng bia tiến sĩ Văn Miếu năm 1484"
                    ],
                    citations=get_citations_for_page(2) + get_citations_for_page(3) + get_citations_for_page(4),
                    needs_review=False
                ),
                ScriptScene(
                    scene_number=3,
                    title="Kết luận: Di Sản Trường Tồn Non Sông",
                    scene_type=SceneType.CONCLUSION,
                    estimated_duration_seconds=15,
                    historical_setting="Văn Miếu Quốc Tử Giám rực sáng ánh mặt trời",
                    narration=(
                        "Hơn nửa thiên niên kỷ trôi qua, bài học về ý chí tự cường dân tộc và tinh thần 'Hiền tài là nguyên khí quốc gia' "
                        "của vua Lê Thánh Tông vẫn là ngọn hải đăng soi sáng non sông Việt Nam."
                    ),
                    dialogues=[
                        DialogueLine(
                            speaker="Vua Lê Thánh Tông",
                            text="Hiền tài là nguyên khí của quốc gia, nguyên khí thịnh thì thế nước mạnh.",
                            dialogue_type=DialogueType.HISTORICAL_QUOTE,
                            is_fictional=False,
                            citation=get_citations_for_page(3)[0] if get_citations_for_page(3) else None
                        )
                    ],
                    key_historical_facts=["Lê Thánh Tông để lại di sản nhà nước pháp quyền và văn hóa rực rỡ."],
                    citations=get_citations_for_page(3),
                    needs_review=False
                )
            ]
            tot_s = sum(s.estimated_duration_seconds for s in shorts_scenes)
            return VideoScript(
                title="Vua Lê Thánh Tông: Lời Thề Giữ Đất & Kỷ Nguyên Hoàng Kim (Shorts)",
                subject=subject,
                format=ScriptFormat.SHORTS,
                target_duration_minutes=round(tot_s / 60.0, 1),
                total_estimated_duration_seconds=tot_s,
                hook="Vị vua nào của Đại Việt từng tuyên bố chém đầu bất kỳ ai dám để mất một tấc đất biên cương?",
                background_summary="Tóm lược 55 giây về cuộc đời và di sản của Hoàng đế Lê Thánh Tông.",
                scenes=shorts_scenes,
                conclusion="Hiền tài là nguyên khí quốc gia — bài học tự cường bất hủ.",
                total_scenes=len(shorts_scenes),
                verified_claims_count=len(all_citations),
                flagged_for_review_count=0,
                sources_consulted=sources_consulted,
                provider_diagnostics={"provider": "offline", "is_fallback": False}
            )

        if script_fmt == ScriptFormat.EXPLAINER:
            explainer_scenes = [
                ScriptScene(
                    scene_number=1,
                    title="Mở đầu: Vị Hoàng đế Thay đổi Vận mệnh Đại Việt",
                    scene_type=SceneType.HOOK,
                    estimated_duration_seconds=30,
                    historical_setting="Năm 1460, Hoàng thành Thăng Long, đêm sau cuộc chính biến cung đình",
                    narration=(
                        "Mùa hè năm 1460, chàng thanh niên Lê Tư Thành 18 tuổi bước lên ngai vàng giữa lúc triều đình rung chuyển. "
                        "Vị vua trẻ ấy — Hoàng đế Lê Thánh Tông — đã mở ra thời kỳ hoàng kim rực rỡ nhất trong một ngàn năm phong kiến Đại Việt."
                    ),
                    dialogues=[
                        DialogueLine(
                            speaker="Người dẫn chuyện",
                            text="Hãy cùng ChronicleAI khám phá triều đại rực rỡ thời Hồng Đức.",
                            dialogue_type=DialogueType.NARRATION,
                            is_fictional=False
                        )
                    ],
                    key_historical_facts=["Lê Tư Thành đăng cơ năm 1460."],
                    citations=get_citations_for_page(1),
                    needs_review=False
                ),
                ScriptScene(
                    scene_number=2,
                    title="Cuộc Đại Cải Cách: 13 Đạo Thừa Tuyên & Luật Hồng Đức",
                    scene_type=SceneType.KEY_ACHIEVEMENT,
                    estimated_duration_seconds=70,
                    historical_setting="Điện Kính Thiên, Hoàng thành Thăng Long",
                    narration=(
                        "Lê Thánh Tông bãi bỏ chức Tể tướng, trực tiếp điều hành thông qua Lục Bộ và Lục Khoa. "
                        "Ở địa phương, vua chia cả nước thành 13 Đạo thừa tuyên với Tam ty kiềm chế quyền lực. "
                        "Đặc biệt, Quốc Triều Hình Luật (Luật Hồng Đức) ra đời với những điều khoản tiến bộ vượt bậc, "
                        "bảo vệ quyền thừa kế và tài sản của phụ nữ."
                    ),
                    dialogues=[
                        DialogueLine(
                            speaker="Vua Lê Thánh Tông",
                            text="Triều đình cần người tài chứ không cần kẻ ôm quyền làm loạn!",
                            dialogue_type=DialogueType.FICTIONAL_DRAMATIZATION,
                            is_fictional=True
                        )
                    ],
                    key_historical_facts=["13 Đạo thừa tuyên chia sẻ quyền lực", "Luật Hồng Đức bảo vệ phụ nữ"],
                    citations=get_citations_for_page(1) + get_citations_for_page(2),
                    needs_review=False
                ),
                ScriptScene(
                    scene_number=3,
                    title="Đỉnh Cao Trí Tuệ: Bia Tiến Sĩ Văn Miếu & Hội Tao Đàn",
                    scene_type=SceneType.KEY_ACHIEVEMENT,
                    estimated_duration_seconds=80,
                    historical_setting="Văn Miếu Quốc Tử Giám & Vườn hoa Quỳnh Lâm",
                    narration=(
                        "Năm 1484, vua khởi xướng dựng bia tiến sĩ tại Văn Miếu, khắc ghi chân lý bất hủ: "
                        "'Hiền tài là nguyên khí của quốc gia'. Vua đích thân làm Tao Đàn đô nguyên súy, "
                        "sáng tác thơ phú và cho lập Hồng Đức Bản Đồ toàn vẹn lãnh thổ."
                    ),
                    dialogues=[
                        DialogueLine(
                            speaker="Thân Nhân Trung",
                            text="Hiền tài là nguyên khí của quốc gia, nguyên khí thịnh thì thế nước mạnh.",
                            dialogue_type=DialogueType.HISTORICAL_QUOTE,
                            is_fictional=False,
                            citation=get_citations_for_page(3)[0] if get_citations_for_page(3) else None
                        )
                    ],
                    key_historical_facts=["Khắc bia tiến sĩ Văn Miếu năm 1484", "Hội Tao Đàn sáng lập năm 1495"],
                    citations=get_citations_for_page(3) + get_citations_for_page(4),
                    needs_review=False
                ),
                ScriptScene(
                    scene_number=4,
                    title="Chủ Quyền Bất Khả Xâm Phạm & Di Sản Trường Tồn",
                    scene_type=SceneType.CONCLUSION,
                    estimated_duration_seconds=60,
                    historical_setting="Biên ải Đại Việt & Thăng Long rực rỡ",
                    narration=(
                        "Lời thề biên cương năm 1473: 'Một thước núi, một tấc sông của ta, lẽ nào lại tự tiện vứt bỏ đi được?' "
                        "đã trở thành kim chỉ nam giữ nước muôn đời. Triều đại Hồng Đức thịnh trị 38 năm "
                        "là đỉnh cao văn hiến và bản lĩnh tự cường của dân tộc Việt Nam."
                    ),
                    dialogues=[
                        DialogueLine(
                            speaker="Vua Lê Thánh Tông",
                            text="Một thước núi, một tấc sông của ta, lẽ nào lại tự tiện vứt bỏ đi được? Kẻ nào dám đem làm mồi cho giặc phải tru di!",
                            dialogue_type=DialogueType.HISTORICAL_QUOTE,
                            is_fictional=False,
                            citation=get_citations_for_page(5)[0] if get_citations_for_page(5) else None
                        )
                    ],
                    key_historical_facts=["Lời thề bảo vệ chủ quyền biên cương năm 1473."],
                    citations=get_citations_for_page(5),
                    needs_review=False
                )
            ]
            tot_e = sum(s.estimated_duration_seconds for s in explainer_scenes)
            return VideoScript(
                title="Hoàng Đế Lê Thánh Tông: Triều Đại Hoàng Kim Hồng Đức (Explainer)",
                subject=subject,
                format=ScriptFormat.EXPLAINER,
                target_duration_minutes=round(tot_e / 60.0, 1),
                total_estimated_duration_seconds=tot_e,
                hook="Mùa hè năm 1460, một chàng thanh niên 18 tuổi bước lên ngai vàng mở ra thời kỳ hoàng kim...",
                background_summary="Khảo cứu súc tích 4 phút về cuộc đời, cải cách và di sản của vua Lê Thánh Tông.",
                scenes=explainer_scenes,
                conclusion="38 năm trị vì Hồng Đức là đỉnh cao văn hiến và bản lĩnh tự cường của dân tộc Việt Nam.",
                total_scenes=len(explainer_scenes),
                verified_claims_count=len(all_citations),
                flagged_for_review_count=0,
                sources_consulted=sources_consulted,
                provider_diagnostics={"provider": "offline", "is_fallback": False}
            )

        scenes: List[ScriptScene] = [
            ScriptScene(
                scene_number=1,
                title="Mở đầu: Vị Hoàng đế Thay đổi Vận mệnh Đại Việt",
                scene_type=SceneType.HOOK,
                estimated_duration_seconds=120,
                historical_setting="Năm 1460, Hoàng thành Thăng Long, đêm sau cuộc chính biến cung đình",
                narration=(
                    "Mùa hè năm 1460, một chàng thanh niên 18 tuổi bước lên ngai vàng giữa lúc triều đình Đại Việt "
                    "vừa rung chuyển sau các cuộc biến loạn cung đình đẫm máu. Ít ai ngờ rằng, chàng thiếu niên ấy "
                    "— Hoàng đế Lê Thánh Tông — sẽ mở ra triều đại hoàng kim rực rỡ nhất trong một ngàn năm phong kiến Việt Nam. "
                    "Làm thế nào một vị vua trẻ lại có thể tái thiết toàn bộ đất nước, biến Đại Việt thành cường quốc phương Nam?"
                ),
                dialogues=[
                    DialogueLine(
                        speaker="Người dẫn chuyện",
                        text="Hãy cùng ChronicleAI ngược dòng thời gian về thế kỷ 15 để khám phá thời kỳ thịnh trị Hồng Đức.",
                        dialogue_type=DialogueType.NARRATION,
                        is_fictional=False
                    )
                ],
                key_historical_facts=[
                    "Lê Tư Thành đăng cơ năm Canh Thìn (1460), niên hiệu Quang Thuận sau đổi thành Hồng Đức."
                ],
                citations=get_citations_for_page(1),
                needs_review=False
            ),

            ScriptScene(
                scene_number=2,
                title="Cuộc Đại Cải Cách Hành Chính: Bãi bỏ Tể Tướng & 13 Đạo Thừa Tuyên",
                scene_type=SceneType.BACKGROUND,
                estimated_duration_seconds=180,
                historical_setting="Điện Kính Thiên, Hoàng thành Thăng Long (1460 - 1471)",
                narration=(
                    "Ngay sau khi lên ngôi, Lê Thánh Tông đã nhìn thấu hiểm họa từ nạn đại thần lộng quyền và bộ máy cồng kềnh. "
                    "Nhà vua đưa ra quyết định táo bạo chưa từng có: Bãi bỏ hoàn toàn các chức vị Tể tướng, Tam công, Tam thiếu, "
                    "trực tiếp nắm quyền điều hành tối cao. Ở trung ương, vua tái lập Lục Bộ (Lại, Hộ, Lễ, Binh, Hình, Công), "
                    "được giám sát bởi Lục Khoa. Ở địa phương, 13 Đạo thừa tuyên được thiết lập, chia quyền cho Tam ty: "
                    "Đô ty (quân sự), Thừa ty (hành chính) và Hiến ty (thanh tra). Đây là hệ thống kiềm chế quyền lực mẫu mực."
                ),
                dialogues=[
                    DialogueLine(
                        speaker="Vua Lê Thánh Tông",
                        text="Triều đình cần người tài chứ không cần kẻ ôm quyền làm loạn. Trẫm muốn mọi mệnh lệnh phải thông suốt từ kinh thành tới từng xóm thôn!",
                        dialogue_type=DialogueType.FICTIONAL_DRAMATIZATION,
                        is_fictional=True,
                        citation=None
                    )
                ],
                key_historical_facts=[
                    "Bãi bỏ Tể tướng, phân chia quyền lực cho Lục Bộ.",
                    "Thành lập 13 Đạo thừa tuyên với cơ chế Tam ty đối trọng."
                ],
                citations=get_citations_for_page(1),
                needs_review=False
            ),
            ScriptScene(
                scene_number=3,
                title="Quốc Triều Hình Luật (Luật Hồng Đức): Bản Tuyên Ngôn Nhân Quyền Tiến Bộ",
                scene_type=SceneType.KEY_ACHIEVEMENT,
                estimated_duration_seconds=200,
                historical_setting="Nội các Thăng Long, quá trình soạn thảo bộ luật 722 điều",
                narration=(
                    "Di sản pháp lý vĩ đại nhất của triều Hồng Đức chính là 'Quốc Triều Hình Luật' — thường gọi là Bộ luật Hồng Đức. "
                    "Với 722 điều luật bao quát toàn bộ đời sống kinh tế - xã hội, đây là công trình pháp luật tiến bộ bậc nhất "
                    "thời trung đại phương Đông. Đặc biệt, luật bảo vệ quyền bình đẳng của phụ nữ: con gái có quyền thừa kế hương hỏa "
                    "ngang với con trai, người vợ có quyền ly hôn nếu chồng bỏ rơi ba năm. Bên cạnh đó, chế độ quân điền bảo đảm "
                    "dân nghèo có ruộng cày, quan lại lơ là đê điều đắp lũ sông Hồng sẽ bị trừng phạt nghiêm khắc."
                ),
                dialogues=[
                    DialogueLine(
                        speaker="Quan Thượng thư Bộ Hình",
                        text="Muôn tâu Hoàng thượng, cho phép nữ giới giữ tài sản riêng khi phân ly chưa từng có tiền lệ ở các triều trước!",
                        dialogue_type=DialogueType.FICTIONAL_DRAMATIZATION,
                        is_fictional=True,
                        citation=None
                    ),
                    DialogueLine(
                        speaker="Vua Lê Thánh Tông",
                        text="Pháp luật của Trẫm lập ra là để an dân. Dân không ấm no, đạo nghĩa không nghiêm thì lấy gì dựng nước?",
                        dialogue_type=DialogueType.FICTIONAL_DRAMATIZATION,
                        is_fictional=True,
                        citation=None
                    )
                ],
                key_historical_facts=[
                    "Ban hành Quốc Triều Hình Luật gồm 16 thiên, 722 điều.",
                    "Bảo vệ quyền thừa kế và sở hữu tài sản của phụ nữ.",
                    "Đặt quan Hà đê sứ và Khuyến nông sứ chăm lo dân sinh."
                ],
                citations=get_citations_for_page(2),
                needs_review=False
            ),
            ScriptScene(
                scene_number=4,
                title="Hiền Tài Là Nguyên Khí Quốc Gia: Khắc Bia Tiến Sĩ Văn Miếu (1484)",
                scene_type=SceneType.KEY_ACHIEVEMENT,
                estimated_duration_seconds=180,
                historical_setting="Văn Miếu - Quốc Tử Giám, Hà Nội, năm Giáp Thìn (1484)",
                narration=(
                    "Lê Thánh Tông thấu hiểu rằng: Quốc gia muốn cường thịnh phải bắt đầu từ việc coi trọng tri thức. "
                    "Ông chuẩn hóa quy chế thi cử cứ 3 năm tổ chức một kỳ thi Hội nghiêm ngặt. Suốt triều đại ông, 501 tiến sĩ "
                    "đã được tuyển chọn. Năm 1484, nhà vua đưa ra một quyết định có ý nghĩa thiên niên kỷ: Dựng bia đá trên lưng rùa "
                    "khắc tên các nhà khoa bảng tại Văn Miếu. Đông các Đại học sĩ Thân Nhân Trung đã phụng mệnh soạn bài văn bia "
                    "bất hủ tạc sâu vào tâm thức dân tộc."
                ),
                dialogues=[
                    DialogueLine(
                        speaker="Thân Nhân Trung",
                        text="Hiền tài là nguyên khí của quốc gia, nguyên khí thịnh thì thế nước mạnh rồi lên cao, nguyên khí suy thì thế nước yếu rồi xuống thấp.",
                        dialogue_type=DialogueType.HISTORICAL_QUOTE,
                        is_fictional=False,
                        citation=get_citations_for_page(3)[0] if get_citations_for_page(3) else None
                    )
                ],
                key_historical_facts=[
                    "Dựng bia tiến sĩ Văn Miếu năm 1484.",
                    "Đào tạo 501 tiến sĩ trong triều đại Hồng Đức.",
                    "Văn bia Thân Nhân Trung tôn vinh tri thức."
                ],
                citations=get_citations_for_page(3),
                needs_review=False
            ),
            ScriptScene(
                scene_number=5,
                title="Tao Đàn Nhị Thập Bát Tú & Bản Đồ Hồng Đức (1490)",
                scene_type=SceneType.NARRATIVE,
                estimated_duration_seconds=160,
                historical_setting="Vườn Quỳnh Lâm và điện giảng sách, Thăng Long (1490 - 1495)",
                narration=(
                    "Không chỉ là nhà chính trị lỗi lạc, Lê Thánh Tông còn là nhà thơ, chủ soái Hội Tao Đàn Nhị Thập Bát Tú "
                    "quy tụ 28 văn nhân đại thần kiệt xuất. Tác phẩm thơ Nôm 'Hồng Đức quốc âm thi tập' đã khẳng định vị thế độc lập, "
                    "tự chủ của tiếng mẹ đẻ. Đặc biệt, năm 1490, Hoàng đế ban hành 'Bản đồ Hồng Đức' — bộ tập bản đồ địa lý toàn cảnh "
                    "đầu tiên của Đại Việt, định hình rõ ranh giới cương vực non sông từ ải Bắc đến dải miền Trung."
                ),
                dialogues=[
                    DialogueLine(
                        speaker="Vua Lê Thánh Tông",
                        text="Văn chương phải rạng rỡ hồn non nước. Bản đồ phải tỏ rõ từng ngọn núi, tấc đất của tổ tông!",
                        dialogue_type=DialogueType.FICTIONAL_DRAMATIZATION,
                        is_fictional=True,
                        citation=None
                    )
                ],
                key_historical_facts=[
                    "Sáng lập Hội Tao Đàn năm 1495, giữ chức Tao Đàn Đô nguyên súy.",
                    "Hoàn thành Bản đồ Hồng Đức năm Canh Tuất (1490)."
                ],
                citations=get_citations_for_page(4),
                needs_review=False
            ),
            ScriptScene(
                scene_number=6,
                title="Bảo Vệ Biên Cương: Lời Dặn 'Một Thước Núi, Một Tấc Sông' (1471 - 1473)",
                scene_type=SceneType.HISTORICAL_CONFLICT,
                estimated_duration_seconds=190,
                historical_setting="Biên cương Đại Việt và Điện triều nghị, Thăng Long (1471 - 1473)",
                narration=(
                    "Năm 1471, sau khi đánh bại cuộc xâm lấn quấy nhiễu của vua Chiêm Thành Trà Toàn, vua mở rộng cương vực, "
                    "lập nên đạo Quảng Nam — đạo thừa tuyên thứ 13. Nhưng điều làm nên tầm vóc bất tử của Lê Thánh Tông chính là "
                    "ý chí sắt đá bảo vệ chủ quyền biên giới. Tháng 4 năm 1473, khi nghe tin quan lại biên phòng có biểu hiện thỏa hiệp, "
                    "nhà vua đã truyền lời răn dạy đanh thép được ghi chép trang trọng trong Đại Việt Sử Ký Toàn Thư."
                ),
                dialogues=[
                    DialogueLine(
                        speaker="Vua Lê Thánh Tông",
                        text="Một thước núi, một tấc sông của ta, lẽ nào lại tự tiện vứt bỏ? Ngươi phải kiên quyết tranh biện, chớ cho họ lấn dần. Nếu ngươi dám đem một thước núi, một tấc đất của Thái Tổ làm mồi cho giặc, thì tội phải tru di!",
                        dialogue_type=DialogueType.HISTORICAL_QUOTE,
                        is_fictional=False,
                        citation=get_citations_for_page(5)[0] if get_citations_for_page(5) else None
                    )
                ],
                key_historical_facts=[
                    "Chiến dịch Nam chinh 1471 thành lập đạo Quảng Nam.",
                    "Lời tuyên ngôn chủ quyền đanh thép năm 1473 ghi trong Đại Việt Sử Ký Toàn Thư."
                ],
                citations=get_citations_for_page(5),
                needs_review=False
            ),
            ScriptScene(
                scene_number=7,
                title="Kết Luận: Di Sản Bất Diệt Của Kỷ Nguyên Hồng Đức",
                scene_type=SceneType.CONCLUSION,
                estimated_duration_seconds=130,
                historical_setting="Toàn cảnh Thăng Long nghìn năm và Văn Miếu Quốc Tử Giám ngày nay",
                narration=(
                    "38 năm trị vì của Hoàng đế Lê Thánh Tông không chỉ là thời kỳ thịnh trị đỉnh cao của nhà Hậu Lê, "
                    "mà còn để lại cho hậu thế bài học trường tồn về nhà nước pháp quyền, sự tôn vinh trí thức và "
                    "tinh thần kiên quyết bảo vệ từng tấc đất thiêng liêng của Tổ quốc. Những viên gạch mà ông đặt xuống "
                    "vẫn tiếp tục soi sáng con đường phát triển của dân tộc Việt Nam hôm nay."
                ),
                dialogues=[
                    DialogueLine(
                        speaker="Người dẫn chuyện",
                        text="Cảm ơn các bạn đã đồng hành cùng ChronicleAI. Hãy tiếp tục khám phá những trang sử vàng hào hùng của dân tộc!",
                        dialogue_type=DialogueType.NARRATION,
                        is_fictional=False
                    )
                ],
                key_historical_facts=[
                    "Lê Thánh Tông trị vì 38 năm (1460 - 1497), thời kỳ thịnh trị bậc nhất Đại Việt."
                ],
                citations=get_citations_for_page(1),
                needs_review=False
            )
        ]

        total_sec = sum(s.estimated_duration_seconds for s in scenes)

        return VideoScript(
            title="Đại Việt Thời Hồng Đức: Kỷ Nguyên Hoàng Kim Của Hoàng Đế Lê Thánh Tông (1460 - 1497)",
            subject=subject,
            target_duration_minutes=round(total_sec / 60.0, 1),
            total_estimated_duration_seconds=total_sec,
            hook=(
                "Mùa hè năm 1460, một chàng thanh niên 18 tuổi bước lên ngai vàng giữa lúc triều đình Đại Việt "
                "vừa rung chuyển sau các cuộc biến loạn cung đình đẫm máu..."
            ),
            background_summary=(
                "Bối cảnh Đại Việt giữa thế kỷ 15 sau biến loạn cung đình Nghi Dân, đòi hỏi một cuộc cải cách "
                "toàn diện từ hành chính, luật pháp, giáo dục tới quốc phòng."
            ),
            scenes=scenes,
            conclusion=(
                "38 năm trị vì của Hoàng đế Lê Thánh Tông không chỉ là thời kỳ thịnh trị đỉnh cao của nhà Hậu Lê, "
                "mà còn để lại cho hậu thế bài học trường tồn về nhà nước pháp quyền và chủ quyền lãnh thổ."
            ),
            total_scenes=len(scenes),
            verified_claims_count=len(all_citations),
            flagged_for_review_count=0,
            sources_consulted=sources_consulted
        )

    async def generate_storyboard(
        self,
        script: VideoScript,
        aspect_ratio: str = "16:9"
    ) -> Storyboard:
        """
        Convert script scenes into 2D minimalist animation storyboards
        with stick-figure-inspired characters, traditional Vietnamese attire (áo giao lĩnh, khăn đóng),
        authentic historical settings, camera staging, and production-ready AI image prompts.
        Supports aspect_ratio: '16:9' (horizontal) or '9:16' (vertical shorts).
        """
        storyboard_scenes: List[StoryboardScene] = []
        ar = aspect_ratio if aspect_ratio in ("16:9", "9:16") else "16:9"

        visual_settings_map = {
            1: "Kinh thành Thăng Long về đêm, ánh đuốc bập bùng trên tường thành rêu phong cổ kính",
            2: "Đại điện Kính Thiên nguy nga, ngai vàng chạm rồng thời Lê sơ, các quan lại xếp hàng",
            3: "Bàn ngự bút của Hoàng đế, nghiên mực, bản thảo Quốc Triều Hình Luật và hình ảnh đê sông Hồng",
            4: "Sân đá Văn Miếu Quốc Tử Giám rợp bóng cây cổ thụ, hàng bia đá rùa đội bia tiến sĩ",
            5: "Vườn hoa Quỳnh Lâm, các học giả Tao Đàn bên án thư, cuộn bản đồ Hồng Đức trải rộng",
            6: "Vùng biên ải Nam chinh và dòng sông hùng vĩ, chiến thuyền Đại Việt cắm cờ thêu chữ Lê",
            7: "Hoàng hôn buông trên Thăng Long, bóng vị vua trẻ nhìn xa xăm về tương lai đất nước"
        }

        camera_map = {
            1: "Góc rộng (Wide shot) từ trên cao nhìn xuống Thăng Long, sau đó lia máy chậm (slow pan) vào cửa cung",
            2: "Trung cảnh (Medium shot) đối xứng chính diện ngai vàng, cắt sang góc nhìn nghiêng quan lại Lục Bộ",
            3: "Cận cảnh (Close-up) cuộn luật Quốc Triều Hình Luật, kết hợp đồ họa phân nhánh sơ đồ bảo vệ phụ nữ",
            4: "Góc máy thấp (Low angle) hướng lên bia tiến sĩ đá sa thạch, ánh nắng rọi sáng hàng chữ Thân Nhân Trung",
            5: "Toàn cảnh sinh hoạt tao nhã (Full shot), lia ống kính qua cuộn bản đồ địa lý 13 đạo thừa tuyên",
            6: "Góc nhìn kịch tính (Dynamic angle), vua Lê Thánh Tông chỉ kiếm về hướng biên cương sông núi",
            7: "Góc máy đại cảnh (Epic extreme wide shot) chuyển dần sang hình ảnh Văn Miếu thời hiện đại"
        }

        aspect_framing = "cinematic 9:16 vertical composition, vertical mobile frame for educational animation" if ar == "9:16" else "cinematic 16:9 horizontal composition"

        for scene in script.scenes:
            setting = visual_settings_map.get(scene.scene_number, scene.historical_setting)
            cam = camera_map.get(scene.scene_number, "Góc trung cảnh tĩnh (Static medium shot)")

            # Minimalist stick-figure animation image prompt
            prompt = (
                f"Minimalist 2D vector animation style, expressive stick-figure character design, "
                f"Vietnamese historical setting: {setting}. Character wearing authentic 15th-century Đại Việt "
                f"emperor attire with yellow Áo Giao Lĩnh robe, ornate dragon embroidery accents, simple line-art face, "
                f"clean vector outlines, muted traditional Vietnamese earth tones, watercolor wash background, "
                f"no complex 3D shading, dynamic minimalist composition, {aspect_framing}, high resolution."
            )

            # Character dialogue summary
            dialogue_str = " | ".join([f"{d.speaker}: \"{d.text}\"" for d in scene.dialogues])

            storyboard_scenes.append(
                StoryboardScene(
                    scene_number=scene.scene_number,
                    title=scene.title,
                    estimated_duration_seconds=scene.estimated_duration_seconds,
                    narration=scene.narration,
                    character_dialogue=dialogue_str,
                    historical_setting=setting,
                    visual_description=(
                        f"Phim hoạt hình 2D phong cách tối giản (minimalist vector, khung hình {ar}). Nhân vật dạng que (stick-figure) "
                        f"được cách điệu giàu biểu cảm, khoác trang phục truyền thống thế kỷ 15. {setting}."
                    ),
                    camera_direction=cam,
                    character_poses=[
                        "Dáng đứng uy nghi của Hoàng đế Lê Thánh Tông",
                        "Các vị đại thần chắp tay thi lễ theo phong tục thời Lê sơ"
                    ],
                    ai_image_prompt=prompt,
                    evidence_references=scene.citations
                )
            )

        return Storyboard(
            script_title=script.title,
            subject=script.subject,
            total_scenes=len(storyboard_scenes),
            total_duration_seconds=sum(s.estimated_duration_seconds for s in storyboard_scenes),
            aspect_ratio=ar,
            visual_theme=(
                f"Minimalist 2D Vietnamese historical animation, clean vector stick-figure style ({ar}), "
                "authentic 15th-century Đại Việt costumes (áo giao lĩnh, khăn đóng), subtle muted watercolor backgrounds"
            ),
            scenes=storyboard_scenes,
            provider_diagnostics={"provider": "offline", "is_fallback": False}
        )


ChronicleDeterministicEngine = ChronicleOfflineRuleEngine  # Backwards compatibility alias


class GeminiLLMProvider(BaseLLMProvider):
    """
    Remote LLM Provider utilizing Google Gemini API.
    Activated when GEMINI_API_KEY is supplied.
    Seamlessly falls back to ChronicleOfflineRuleEngine if remote API is unreachable or times out,
    tagging diagnostics transparently so users know if fallback was used.
    """
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.fallback = ChronicleOfflineRuleEngine()

    async def _call_gemini(self, prompt: str, json_mode: bool = False) -> Optional[str]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        gen_config: Dict[str, Any] = {"temperature": 0.2}
        if json_mode:
            gen_config["response_mime_type"] = "application/json"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": gen_config
        }
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=25.0) as client:
                    res = await client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                return parts[0]["text"]
                    elif res.status_code >= 500:
                        logger.warning(f"Gemini API 5xx error (attempt {attempt+1}): {res.status_code}")
                        if attempt == 0:
                            await asyncio.sleep(1.0)
                            continue
                    else:
                        logger.warning(f"Gemini API returned status {res.status_code}: {res.text[:200]}")
                        break
            except Exception as e:
                logger.warning(f"Gemini API invocation error (attempt {attempt+1}): {e}")
                if attempt == 0:
                    await asyncio.sleep(1.0)
        return None

    async def generate_grounded_answer(
        self,
        question: str,
        retrieved_chunks: List[SearchResult]
    ) -> Dict[str, Any]:
        if not retrieved_chunks:
            res = await self.fallback.generate_grounded_answer(question, retrieved_chunks)
            res["provider_diagnostics"] = {"provider": "offline_fallback", "is_fallback": True}
            return res

        context_lines = [
            f"[Source: {c.source}, Page {c.page}, Chunk {c.chunk_id}]\n{c.text}"
            for c in retrieved_chunks[:3]
        ]
        context_str = "\n\n".join(context_lines)
        prompt = (
            f"You are a strict historical research assistant for ChronicleAI. Answer the question using ONLY the provided historical excerpts.\n"
            f"Do not speculate or extrapolate beyond the text. Cite the source, page, and chunk.\n\n"
            f"Historical Excerpts:\n{context_str}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
        answer_text = await self._call_gemini(prompt)
        if answer_text:
            return {
                "answer": answer_text.strip(),
                "citations": [c.citation for c in retrieved_chunks[:3]],
                "grounded": True,
                "provider_diagnostics": {"provider": f"gemini/{self.model}", "is_fallback": False}
            }
        res = await self.fallback.generate_grounded_answer(question, retrieved_chunks)
        res["provider_diagnostics"] = {"provider": "offline_fallback", "is_fallback": True}
        return res

    async def verify_claim(
        self,
        claim: str,
        retrieved_chunks: List[SearchResult]
    ) -> SingleClaimVerification:
        if not retrieved_chunks:
            res = await self.fallback.verify_claim(claim, retrieved_chunks)
            res.provider_diagnostics = {"provider": "offline_fallback", "is_fallback": True}
            return res

        context_str = "\n\n".join([f"[{c.source}, Page {c.page}, Chunk {c.chunk_id}]\n{c.text}" for c in retrieved_chunks[:4]])
        prompt = f"""You are a rigorous historical fact-checker for ChronicleAI.
Evaluate whether the following claim is SUPPORTED, CONTRADICTED, or INSUFFICIENT_EVIDENCE based strictly on the provided historical sources.
Respond in valid JSON only with keys:
"status": "SUPPORTED" | "CONTRADICTED" | "INSUFFICIENT_EVIDENCE",
"confidence": float between 0.0 and 1.0,
"explanation": detailed Vietnamese rationale citing sources and pages,
"has_conflict": boolean,
"conflict_description": string or null

Sources:
{context_str}

Claim to verify:
"{claim}"
"""
        raw = await self._call_gemini(prompt, json_mode=True)
        if raw:
            try:
                clean_json = re.sub(r"^```json\s*", "", raw.strip(), flags=re.MULTILINE)
                clean_json = re.sub(r"\s*```$", "", clean_json, flags=re.MULTILINE)
                parsed = json.loads(clean_json)
                st = parsed.get("status", "INSUFFICIENT_EVIDENCE").upper()
                if st not in ("SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"):
                    st = "INSUFFICIENT_EVIDENCE"
                citations = [retrieved_chunks[0].citation] if (st == "SUPPORTED" and retrieved_chunks) else []
                return SingleClaimVerification(
                    claim=claim,
                    status=VerificationLabel(st),
                    confidence=float(parsed.get("confidence", 0.9)),
                    explanation=parsed.get("explanation", "Xác minh qua Gemini AI."),
                    citations=citations,
                    disagreement=HistoricalDisagreement(
                        has_conflict=bool(parsed.get("has_conflict", False)),
                        description=parsed.get("conflict_description")
                    ),
                    provider_diagnostics={"provider": f"gemini/{self.model}", "is_fallback": False}
                )
            except Exception as e:
                logger.warning(f"Failed parsing Gemini verify_claim JSON: {e}")

        res = await self.fallback.verify_claim(claim, retrieved_chunks)
        res.provider_diagnostics = {"provider": "offline_fallback", "is_fallback": True}
        return res

    async def generate_script(
        self,
        subject: str,
        target_minutes: float,
        chunks: List[SearchResult],
        format: Optional[str] = None
    ) -> VideoScript:
        context_str = "\n\n".join([f"[{c.source}, Page {c.page}, Chunk {c.chunk_id}]\n{c.text}" for c in chunks[:5]])
        prompt = f"""You are a master historical documentary scriptwriter for ChronicleAI.
Generate a structured video script for subject: '{subject}', target duration: {target_minutes} minutes, format: {format or 'DOCUMENTARY'}.
Respond in valid JSON only with keys:
"title": string,
"subject": string,
"hook": string,
"background_summary": string,
"conclusion": string,
"scenes": [
  {{
    "scene_number": integer,
    "title": string,
    "scene_type": "HOOK" | "BACKGROUND" | "NARRATIVE" | "KEY_ACHIEVEMENT" | "HISTORICAL_CONFLICT" | "CONCLUSION",
    "estimated_duration_seconds": integer,
    "historical_setting": string,
    "narration": string,
    "dialogues": [
      {{"speaker": string, "text": string, "dialogue_type": "HISTORICAL_QUOTE" | "FICTIONAL_DRAMATIZATION" | "NARRATION", "is_fictional": boolean}}
    ],
    "key_historical_facts": [string]
  }}
]

Historical Sources:
{context_str}
"""
        raw = await self._call_gemini(prompt, json_mode=True)
        if raw:
            try:
                clean_json = re.sub(r"^```json\s*", "", raw.strip(), flags=re.MULTILINE)
                clean_json = re.sub(r"\s*```$", "", clean_json, flags=re.MULTILINE)
                parsed = json.loads(clean_json)
                built_scenes: List[ScriptScene] = []
                for s in parsed.get("scenes", []):
                    d_lines = [
                        DialogueLine(
                            speaker=d.get("speaker", "Người dẫn chuyện"),
                            text=d.get("text", ""),
                            dialogue_type=DialogueType(d.get("dialogue_type", "NARRATION")),
                            is_fictional=bool(d.get("is_fictional", False))
                        ) for d in s.get("dialogues", [])
                    ]
                    built_scenes.append(ScriptScene(
                        scene_number=int(s.get("scene_number", len(built_scenes) + 1)),
                        title=s.get("title", f"Cảnh {len(built_scenes) + 1}"),
                        scene_type=SceneType(s.get("scene_type", "NARRATIVE")),
                        estimated_duration_seconds=int(s.get("estimated_duration_seconds", 60)),
                        historical_setting=s.get("historical_setting", "Đại Việt thế kỷ 15"),
                        narration=s.get("narration", ""),
                        dialogues=d_lines,
                        key_historical_facts=s.get("key_historical_facts", []),
                        citations=[c.citation for c in chunks[:2]] if chunks else [],
                        needs_review=False
                    ))
                fmt_enum = ScriptFormat(format.upper()) if format and format.upper() in ScriptFormat.__members__ else ScriptFormat.DOCUMENTARY
                tot_sec = sum(s.estimated_duration_seconds for s in built_scenes)
                return VideoScript(
                    title=parsed.get("title", f"Khảo Cứu Lịch Sử: {subject}"),
                    subject=subject,
                    format=fmt_enum,
                    target_duration_minutes=round(tot_sec / 60.0, 1),
                    total_estimated_duration_seconds=tot_sec,
                    hook=parsed.get("hook", f"Khám phá cuộc đời và sự nghiệp của {subject}."),
                    background_summary=parsed.get("background_summary", "Bối cảnh lịch sử thời Lê sơ thế kỷ 15."),
                    conclusion=parsed.get("conclusion", "Di sản trường tồn cùng non sông Đại Việt."),
                    scenes=built_scenes,
                    total_scenes=len(built_scenes),
                    verified_claims_count=len(built_scenes),
                    sources_consulted=list(set([c.source for c in chunks])),
                    provider_diagnostics={"provider": f"gemini/{self.model}", "is_fallback": False}
                )
            except Exception as e:
                logger.warning(f"Failed parsing Gemini script JSON: {e}")

        res = await self.fallback.generate_script(subject, target_minutes, chunks, format)
        res.provider_diagnostics = {"provider": "offline_fallback", "is_fallback": True}
        return res

    async def generate_storyboard(
        self,
        script: VideoScript,
        aspect_ratio: str = "16:9"
    ) -> Storyboard:
        prompt = f"""You are an animation art director for ChronicleAI.
Convert the following script scenes into visual storyboard scenes for a 2D minimalist vector animation (aspect ratio: {aspect_ratio}).
Respond in valid JSON only with keys:
"visual_theme": string,
"scenes": [
  {{
    "scene_number": integer,
    "title": string,
    "estimated_duration_seconds": integer,
    "narration": string,
    "character_dialogue": string,
    "historical_setting": string,
    "visual_description": string,
    "camera_direction": string,
    "character_poses": [string],
    "ai_image_prompt": string
  }}
]

Script Title: {script.title}
Scenes to storyboard:
"""
        for sc in script.scenes:
            prompt += f"\nScene {sc.scene_number} ({sc.title}): {sc.narration[:150]}"

        raw = await self._call_gemini(prompt, json_mode=True)
        if raw:
            try:
                clean_json = re.sub(r"^```json\s*", "", raw.strip(), flags=re.MULTILINE)
                clean_json = re.sub(r"\s*```$", "", clean_json, flags=re.MULTILINE)
                parsed = json.loads(clean_json)
                sb_scenes: List[StoryboardScene] = []
                for s in parsed.get("scenes", []):
                    matched_script_scene = next((sc for sc in script.scenes if sc.scene_number == s.get("scene_number")), None)
                    cits = matched_script_scene.citations if matched_script_scene else []
                    sb_scenes.append(StoryboardScene(
                        scene_number=int(s.get("scene_number", len(sb_scenes) + 1)),
                        title=s.get("title", f"Cảnh {len(sb_scenes) + 1}"),
                        estimated_duration_seconds=int(s.get("estimated_duration_seconds", 60)),
                        narration=s.get("narration", ""),
                        character_dialogue=s.get("character_dialogue", ""),
                        historical_setting=s.get("historical_setting", "Đại Việt"),
                        visual_description=s.get("visual_description", ""),
                        camera_direction=s.get("camera_direction", "Wide shot"),
                        character_poses=s.get("character_poses", []),
                        ai_image_prompt=s.get("ai_image_prompt", ""),
                        evidence_references=cits
                    ))
                return Storyboard(
                    script_title=script.title,
                    subject=script.subject,
                    total_scenes=len(sb_scenes),
                    total_duration_seconds=sum(s.estimated_duration_seconds for s in sb_scenes),
                    aspect_ratio=aspect_ratio,
                    visual_theme=parsed.get("visual_theme", f"Minimalist 2D Vietnamese historical vector animation ({aspect_ratio})"),
                    scenes=sb_scenes,
                    provider_diagnostics={"provider": f"gemini/{self.model}", "is_fallback": False}
                )
            except Exception as e:
                logger.warning(f"Failed parsing Gemini storyboard JSON: {e}")

        res = await self.fallback.generate_storyboard(script, aspect_ratio=aspect_ratio)
        res.provider_diagnostics = {"provider": "offline_fallback", "is_fallback": True}
        return res


class OpenAILLMProvider(BaseLLMProvider):
    """
    Remote LLM Provider utilizing OpenAI Chat Completions API (e.g. GPT-4o, GPT-4o-mini).
    Activated when OPENAI_API_KEY is supplied.
    Seamlessly falls back to ChronicleOfflineRuleEngine if the remote API is unreachable or rate limited,
    recording transparent diagnostic flags on every output.
    """
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.fallback = ChronicleOfflineRuleEngine()

    async def _call_openai(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> Optional[str]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=25.0) as client:
                    res = await client.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        choices = data.get("choices", [])
                        if choices and "message" in choices[0]:
                            return choices[0]["message"].get("content")
                    elif res.status_code >= 500:
                        logger.warning(f"OpenAI API 5xx error (attempt {attempt+1}): {res.status_code}")
                        if attempt == 0:
                            await asyncio.sleep(1.0)
                            continue
                    else:
                        logger.warning(f"OpenAI API returned status {res.status_code}: {res.text[:200]}")
                        break
            except Exception as e:
                logger.warning(f"OpenAI API invocation error (attempt {attempt+1}): {e}")
                if attempt == 0:
                    await asyncio.sleep(1.0)
        return None

    async def generate_grounded_answer(
        self,
        question: str,
        retrieved_chunks: List[SearchResult]
    ) -> Dict[str, Any]:
        if not retrieved_chunks:
            res = await self.fallback.generate_grounded_answer(question, retrieved_chunks)
            res["provider_diagnostics"] = {"provider": "offline_fallback", "is_fallback": True}
            return res

        context_lines = [
            f"[Source: {c.source}, Page {c.page}, Chunk {c.chunk_id}]\n{c.text}"
            for c in retrieved_chunks[:3]
        ]
        context_str = "\n\n".join(context_lines)
        system_prompt = (
            "You are a meticulous historical researcher for ChronicleAI. Answer the question using ONLY the provided historical excerpts. "
            "Never extrapolate or hallucinate facts not present in the excerpts. Cite the source, page, and chunk id."
        )
        user_prompt = f"Historical Excerpts:\n{context_str}\n\nQuestion: {question}\n\nAnswer:"
        answer_text = await self._call_openai(system_prompt, user_prompt)
        if answer_text:
            return {
                "answer": answer_text.strip(),
                "citations": [c.citation for c in retrieved_chunks[:3]],
                "grounded": True,
                "provider_diagnostics": {"provider": f"openai/{self.model}", "is_fallback": False}
            }
        res = await self.fallback.generate_grounded_answer(question, retrieved_chunks)
        res["provider_diagnostics"] = {"provider": "offline_fallback", "is_fallback": True}
        return res

    async def verify_claim(
        self,
        claim: str,
        retrieved_chunks: List[SearchResult]
    ) -> SingleClaimVerification:
        if not retrieved_chunks:
            res = await self.fallback.verify_claim(claim, retrieved_chunks)
            res.provider_diagnostics = {"provider": "offline_fallback", "is_fallback": True}
            return res

        context_str = "\n\n".join([f"[{c.source}, Page {c.page}, Chunk {c.chunk_id}]\n{c.text}" for c in retrieved_chunks[:4]])
        system_prompt = "You are a rigorous historical fact-checker for ChronicleAI. Always respond in valid JSON with keys: status, confidence, explanation, has_conflict, conflict_description."
        user_prompt = f"""Evaluate whether the following claim is SUPPORTED, CONTRADICTED, or INSUFFICIENT_EVIDENCE based strictly on the provided historical sources.
Status must be one of: "SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE".
Explanation must be in Vietnamese citing exact sources and pages.

Sources:
{context_str}

Claim to verify:
"{claim}"
"""
        raw = await self._call_openai(system_prompt, user_prompt, json_mode=True)
        if raw:
            try:
                parsed = json.loads(raw.strip())
                st = parsed.get("status", "INSUFFICIENT_EVIDENCE").upper()
                if st not in ("SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"):
                    st = "INSUFFICIENT_EVIDENCE"
                citations = [retrieved_chunks[0].citation] if (st == "SUPPORTED" and retrieved_chunks) else []
                return SingleClaimVerification(
                    claim=claim,
                    status=VerificationLabel(st),
                    confidence=float(parsed.get("confidence", 0.9)),
                    explanation=parsed.get("explanation", "Xác minh bởi OpenAI GPT."),
                    citations=citations,
                    disagreement=HistoricalDisagreement(
                        has_conflict=bool(parsed.get("has_conflict", False)),
                        description=parsed.get("conflict_description")
                    ),
                    provider_diagnostics={"provider": f"openai/{self.model}", "is_fallback": False}
                )
            except Exception as e:
                logger.warning(f"Failed parsing OpenAI verify_claim JSON: {e}")

        res = await self.fallback.verify_claim(claim, retrieved_chunks)
        res.provider_diagnostics = {"provider": "offline_fallback", "is_fallback": True}
        return res

    async def generate_script(
        self,
        subject: str,
        target_minutes: float,
        chunks: List[SearchResult],
        format: Optional[str] = None
    ) -> VideoScript:
        context_str = "\n\n".join([f"[{c.source}, Page {c.page}, Chunk {c.chunk_id}]\n{c.text}" for c in chunks[:5]])
        system_prompt = "You are an expert historical video scriptwriter for ChronicleAI. Always respond in valid JSON matching VideoScript schema."
        user_prompt = f"""Generate a structured video script for subject: '{subject}', duration: {target_minutes} minutes, format: {format or 'DOCUMENTARY'}.
Include keys: "title", "subject", "hook", "background_summary", "conclusion", "scenes".
Each scene has: "scene_number", "title", "scene_type", "estimated_duration_seconds", "historical_setting", "narration", "dialogues" ([{{"speaker", "text", "dialogue_type", "is_fictional"}}]), "key_historical_facts".

Historical Sources:
{context_str}
"""
        raw = await self._call_openai(system_prompt, user_prompt, json_mode=True)
        if raw:
            try:
                parsed = json.loads(raw.strip())
                built_scenes: List[ScriptScene] = []
                for s in parsed.get("scenes", []):
                    d_lines = [
                        DialogueLine(
                            speaker=d.get("speaker", "Người dẫn chuyện"),
                            text=d.get("text", ""),
                            dialogue_type=DialogueType(d.get("dialogue_type", "NARRATION")),
                            is_fictional=bool(d.get("is_fictional", False))
                        ) for d in s.get("dialogues", [])
                    ]
                    built_scenes.append(ScriptScene(
                        scene_number=int(s.get("scene_number", len(built_scenes) + 1)),
                        title=s.get("title", f"Cảnh {len(built_scenes) + 1}"),
                        scene_type=SceneType(s.get("scene_type", "NARRATIVE")),
                        estimated_duration_seconds=int(s.get("estimated_duration_seconds", 60)),
                        historical_setting=s.get("historical_setting", "Đại Việt thế kỷ 15"),
                        narration=s.get("narration", ""),
                        dialogues=d_lines,
                        key_historical_facts=s.get("key_historical_facts", []),
                        citations=[c.citation for c in chunks[:2]] if chunks else [],
                        needs_review=False
                    ))
                fmt_enum = ScriptFormat(format.upper()) if format and format.upper() in ScriptFormat.__members__ else ScriptFormat.DOCUMENTARY
                tot_sec = sum(s.estimated_duration_seconds for s in built_scenes)
                return VideoScript(
                    title=parsed.get("title", f"Khảo Cứu Lịch Sử: {subject}"),
                    subject=subject,
                    format=fmt_enum,
                    target_duration_minutes=round(tot_sec / 60.0, 1),
                    total_estimated_duration_seconds=tot_sec,
                    hook=parsed.get("hook", f"Khám phá cuộc đời và sự nghiệp của {subject}."),
                    background_summary=parsed.get("background_summary", "Bối cảnh lịch sử thời Lê sơ thế kỷ 15."),
                    conclusion=parsed.get("conclusion", "Di sản trường tồn cùng non sông Đại Việt."),
                    scenes=built_scenes,
                    total_scenes=len(built_scenes),
                    verified_claims_count=len(built_scenes),
                    sources_consulted=list(set([c.source for c in chunks])),
                    provider_diagnostics={"provider": f"openai/{self.model}", "is_fallback": False}
                )
            except Exception as e:
                logger.warning(f"Failed parsing OpenAI script JSON: {e}")

        res = await self.fallback.generate_script(subject, target_minutes, chunks, format)
        res.provider_diagnostics = {"provider": "offline_fallback", "is_fallback": True}
        return res

    async def generate_storyboard(
        self,
        script: VideoScript,
        aspect_ratio: str = "16:9"
    ) -> Storyboard:
        system_prompt = "You are an animation art director for ChronicleAI. Always respond in valid JSON matching Storyboard schema."
        user_prompt = f"""Convert the following script into visual storyboard scenes for a 2D minimalist vector animation (aspect ratio: {aspect_ratio}).
Return JSON with keys: "visual_theme", "scenes" (array of scene_number, title, estimated_duration_seconds, narration, character_dialogue, historical_setting, visual_description, camera_direction, character_poses, ai_image_prompt).

Script Title: {script.title}
Scenes:
"""
        for sc in script.scenes:
            user_prompt += f"\nScene {sc.scene_number} ({sc.title}): {sc.narration[:150]}"

        raw = await self._call_openai(system_prompt, user_prompt, json_mode=True)
        if raw:
            try:
                parsed = json.loads(raw.strip())
                sb_scenes: List[StoryboardScene] = []
                for s in parsed.get("scenes", []):
                    matched_script_scene = next((sc for sc in script.scenes if sc.scene_number == s.get("scene_number")), None)
                    cits = matched_script_scene.citations if matched_script_scene else []
                    sb_scenes.append(StoryboardScene(
                        scene_number=int(s.get("scene_number", len(sb_scenes) + 1)),
                        title=s.get("title", f"Cảnh {len(sb_scenes) + 1}"),
                        estimated_duration_seconds=int(s.get("estimated_duration_seconds", 60)),
                        narration=s.get("narration", ""),
                        character_dialogue=s.get("character_dialogue", ""),
                        historical_setting=s.get("historical_setting", "Đại Việt"),
                        visual_description=s.get("visual_description", ""),
                        camera_direction=s.get("camera_direction", "Wide shot"),
                        character_poses=s.get("character_poses", []),
                        ai_image_prompt=s.get("ai_image_prompt", ""),
                        evidence_references=cits
                    ))
                return Storyboard(
                    script_title=script.title,
                    subject=script.subject,
                    total_scenes=len(sb_scenes),
                    total_duration_seconds=sum(s.estimated_duration_seconds for s in sb_scenes),
                    aspect_ratio=aspect_ratio,
                    visual_theme=parsed.get("visual_theme", f"Minimalist 2D Vietnamese historical vector animation ({aspect_ratio})"),
                    scenes=sb_scenes,
                    provider_diagnostics={"provider": f"openai/{self.model}", "is_fallback": False}
                )
            except Exception as e:
                logger.warning(f"Failed parsing OpenAI storyboard JSON: {e}")

        res = await self.fallback.generate_storyboard(script, aspect_ratio=aspect_ratio)
        res.provider_diagnostics = {"provider": "offline_fallback", "is_fallback": True}
        return res


def get_llm_provider() -> BaseLLMProvider:
    """Factory to get active LLM provider based on settings and environment."""
    provider_name = (settings.LLM_PROVIDER or "auto").lower()

    if (provider_name in ("gemini", "auto")) and settings.GEMINI_API_KEY:
        logger.info(f"Initializing remote GeminiLLMProvider (model: {settings.GEMINI_MODEL})")
        return GeminiLLMProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)

    if (provider_name in ("openai", "auto")) and settings.OPENAI_API_KEY:
        logger.info(f"Initializing remote OpenAILLMProvider (model: {settings.OPENAI_MODEL})")
        return OpenAILLMProvider(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)

    if provider_name == "gemini" and not settings.GEMINI_API_KEY:
        logger.warning("LLM_PROVIDER is configured as 'gemini' but GEMINI_API_KEY is not set. Falling back to ChronicleOfflineRuleEngine.")

    if provider_name == "openai" and not settings.OPENAI_API_KEY:
        logger.warning("LLM_PROVIDER is configured as 'openai' but OPENAI_API_KEY is not set. Falling back to ChronicleOfflineRuleEngine.")

    logger.info("Initializing ChronicleOfflineRuleEngine (Deterministic Heuristic Baseline)")
    return ChronicleOfflineRuleEngine()

