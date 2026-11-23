import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.models.document import ChunkMetadata
from app.models.rag import Citation, SearchResult
from app.models.script import ScriptGenerationRequest
from app.services.llm_provider import (
    ChronicleOfflineRuleEngine,
    GeminiLLMProvider,
    OpenAILLMProvider,
    get_llm_provider
)
from app.services.scriptwriter import ScriptwriterService
from app.services.vector_store import CitationVectorStore


def create_sample_chunk(chunk_id: str, page: int, text: str, source: str = "custom_history.pdf") -> SearchResult:
    citation = Citation(
        filename=source,
        page=page,
        chunk_id=chunk_id,
        quote=text[:80],
        score=0.85,
        document_id="doc_custom_001"
    )
    return SearchResult(
        chunk_id=chunk_id,
        page=page,
        text=text,
        source=source,
        document_id="doc_custom_001",
        score=0.85,
        citation=citation
    )


@pytest.mark.asyncio
async def test_offline_engine_grounded_qa():
    engine = ChronicleOfflineRuleEngine()
    chunk = create_sample_chunk("c1", 1, "Năm 1288, Hưng Đạo Vương Trần Quốc Tuấn đại phá quân Nguyên Mông trên sông Bạch Đằng.")
    res = await engine.generate_grounded_answer("Trần Quốc Tuấn chiến thắng ở đâu?", [chunk])

    assert res["grounded"] is True
    assert len(res["citations"]) == 1
    assert "Bạch Đằng" in res["answer"]


@pytest.mark.asyncio
async def test_dynamic_script_generation_for_arbitrary_subject():
    """Verify that arbitrary historical subjects generate dynamic scenes from chunks, not hardcoded Le Thanh Tong."""
    engine = ChronicleOfflineRuleEngine()
    chunks = [
        create_sample_chunk("c101", 1, "Trần Hưng Đạo chỉ huy quân dân Đại Việt ba lần đánh tan quân Nguyên Mông xâm lược.", "dai_viet_su_ky.pdf"),
        create_sample_chunk("c102", 2, "Hịch Tướng Sĩ được viết nhằm khích lệ tinh thần binh sĩ trước cuộc chiến chống Thoát Hoan.", "dai_viet_su_ky.pdf"),
        create_sample_chunk("c103", 3, "Chiến thắng Bạch Đằng năm 1288 chôn vùi đạo thủy binh địch, bắt sống tướng Ô Mã Nhi.", "dai_viet_su_ky.pdf")
    ]

    script = await engine.generate_script(subject="Quốc Công Tiết Chế Trần Hưng Đạo", target_minutes=15, chunks=chunks)

    assert script.subject == "Quốc Công Tiết Chế Trần Hưng Đạo"
    assert "Trần Hưng Đạo" in script.title
    assert script.total_scenes >= 3
    # Check that scenes incorporate the provided historical chunks
    assert any("Bạch Đằng" in s.narration for s in script.scenes)
    assert any("Hịch Tướng Sĩ" in s.narration for s in script.scenes)
    # Check citations
    assert script.verified_claims_count >= 3


@pytest.mark.asyncio
async def test_gemini_provider_mock():
    provider = GeminiLLMProvider(api_key="test-key-gemini", model="gemini-1.5-flash")
    chunk = create_sample_chunk("c1", 1, "Quang Trung đại phá quân Thanh vào dịp Tết Kỷ Dậu 1789.")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Vua Quang Trung đại phá 29 vạn quân Thanh vào mùa xuân Kỷ Dậu 1789 tại Ngọc Hồi - Đống Đa."}]
                }
            }
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        res = await provider.generate_grounded_answer("Quang Trung đại phá quân Thanh năm nào?", [chunk])

        assert res["grounded"] is True
        assert "Ngọc Hồi - Đống Đa" in res["answer"]
        assert len(res["citations"]) == 1


@pytest.mark.asyncio
async def test_openai_provider_mock():
    provider = OpenAILLMProvider(api_key="test-key-openai", model="gpt-4o")
    chunk = create_sample_chunk("c2", 2, "Lý Thường Kiệt đọc bài thơ thần Nam Quốc Sơn Hà bên sông Như Nguyệt năm 1077.")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {"content": "Bài thơ Nam Quốc Sơn Hà được vang lên trên phòng tuyến sông Như Nguyệt năm 1077."}
            }
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        res = await provider.generate_grounded_answer("Nam Quốc Sơn Hà được đọc ở đâu?", [chunk])

        assert res["grounded"] is True
        assert "sông Như Nguyệt" in res["answer"]
        assert len(res["citations"]) == 1


def test_provider_factory_fallback():
    with patch("app.config.settings.LLM_PROVIDER", "offline"):
        provider = get_llm_provider()
        assert isinstance(provider, ChronicleOfflineRuleEngine)

    with patch("app.config.settings.LLM_PROVIDER", "gemini"), patch("app.config.settings.GEMINI_API_KEY", ""):
        provider = get_llm_provider()
        assert isinstance(provider, ChronicleOfflineRuleEngine)

    with patch("app.config.settings.LLM_PROVIDER", "gemini"), patch("app.config.settings.GEMINI_API_KEY", "valid-key"):
        provider = get_llm_provider()
        assert isinstance(provider, GeminiLLMProvider)

    with patch("app.config.settings.LLM_PROVIDER", "openai"), patch("app.config.settings.OPENAI_API_KEY", "valid-key"):
        provider = get_llm_provider()
        assert isinstance(provider, OpenAILLMProvider)
