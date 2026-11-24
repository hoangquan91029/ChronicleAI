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


@pytest.mark.asyncio
async def test_gemini_verify_claim_mock():
    provider = GeminiLLMProvider(api_key="test-key-gemini", model="gemini-1.5-flash")
    chunk = create_sample_chunk("c1", 1, "Năm 1460, Hoàng đế Lê Thánh Tông lên ngôi ở tuổi 18.")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": '{"status": "SUPPORTED", "confidence": 0.96, "explanation": "Tư liệu chứng thực Lê Thánh Tông lên ngôi năm 1460.", "has_conflict": false}'}]
                }
            }
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        verif = await provider.verify_claim("Lê Thánh Tông lên ngôi năm 1460", [chunk])
        assert verif.status.value == "SUPPORTED"
        assert verif.confidence >= 0.9
        assert verif.provider_diagnostics["is_fallback"] is False
        assert "gemini" in verif.provider_diagnostics["provider"]


@pytest.mark.asyncio
async def test_gemini_fallback_on_network_error():
    provider = GeminiLLMProvider(api_key="test-key-gemini", model="gemini-1.5-flash")
    chunk = create_sample_chunk("c1", 1, "Năm 1460, Hoàng đế Lê Thánh Tông lên ngôi.")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=httpx.ConnectTimeout("Network timeout")):
        verif = await provider.verify_claim("Lê Thánh Tông lên ngôi năm 1460", [chunk])
        assert verif.status.value == "SUPPORTED"
        assert verif.provider_diagnostics["is_fallback"] is True
        assert verif.provider_diagnostics["provider"] == "offline_fallback"


@pytest.mark.asyncio
async def test_openai_verify_claim_mock():
    provider = OpenAILLMProvider(api_key="test-key-openai", model="gpt-4o")
    chunk = create_sample_chunk("c1", 1, "Năm 1460, Hoàng đế Lê Thánh Tông lên ngôi ở tuổi 18.")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {"content": '{"status": "SUPPORTED", "confidence": 0.95, "explanation": "Đúng theo sử liệu 1460.", "has_conflict": false}'}
            }
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        verif = await provider.verify_claim("Lê Thánh Tông lên ngôi năm 1460", [chunk])
        assert verif.status.value == "SUPPORTED"
        assert verif.provider_diagnostics["is_fallback"] is False
        assert "openai" in verif.provider_diagnostics["provider"]


@pytest.mark.asyncio
async def test_llm_edge_cases_and_fallbacks():
    """Verify robust edge case handling: malformed JSON, empty chunks, timeouts, and ungrounded claims."""
    gemini = GeminiLLMProvider(api_key="test-key", model="gemini-1.5-flash")
    openai = OpenAILLMProvider(api_key="test-key", model="gpt-4o")

    # 1. Empty retrieval chunks
    res_gemini_empty = await gemini.verify_claim("Vua Lê Thánh Tông du học tại Pháp năm 1470.", [])
    assert res_gemini_empty.status.value == "INSUFFICIENT_EVIDENCE"
    assert len(res_gemini_empty.citations) == 0
    assert res_gemini_empty.provider_diagnostics["is_fallback"] is True

    res_openai_empty = await openai.verify_claim("Đại Việt chế tạo tàu hỏa năm 1480.", [])
    assert res_openai_empty.status.value == "INSUFFICIENT_EVIDENCE"
    assert len(res_openai_empty.citations) == 0
    assert res_openai_empty.provider_diagnostics["is_fallback"] is True

    # 2. Malformed JSON from Gemini -> triggers fallback
    mock_bad_json = MagicMock()
    mock_bad_json.status_code = 200
    mock_bad_json.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "THIS IS NOT VALID JSON {status: true"}]}}]
    }
    chunk = create_sample_chunk("c1", 1, "Năm 1460, Hoàng đế Lê Thánh Tông lên ngôi ở tuổi 18.")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_bad_json
        res_bad = await gemini.verify_claim("Lê Thánh Tông lên ngôi năm 1460", [chunk])
        assert res_bad.status.value == "SUPPORTED"
        assert res_bad.provider_diagnostics["is_fallback"] is True
        assert res_bad.provider_diagnostics["provider"] == "offline_fallback"

    # 3. Missing/Invalid fields in Gemini JSON -> defaults safely
    mock_missing_fields = MagicMock()
    mock_missing_fields.status_code = 200
    mock_missing_fields.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": '{"unknown_key": "some text"}'}]}}]
    }
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_missing_fields
        res_missing = await gemini.verify_claim("Lê Thánh Tông lên ngôi năm 1460", [chunk])
        assert res_missing.status.value == "INSUFFICIENT_EVIDENCE"
        assert res_missing.provider_diagnostics["is_fallback"] is False

    # 4. Timeout / HTTP error on OpenAI -> triggers fallback
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=httpx.ReadTimeout("Timeout from API")):
        res_timeout = await openai.verify_claim("Lê Thánh Tông lên ngôi năm 1460", [chunk])
        assert res_timeout.status.value == "SUPPORTED"
        assert res_timeout.provider_diagnostics["is_fallback"] is True
        assert res_timeout.provider_diagnostics["provider"] == "offline_fallback"

    # 5. Unsupported / Contradicted claim rejection ensures zero citations attached
    mock_contradicted = MagicMock()
    mock_contradicted.status_code = 200
    mock_contradicted.json.return_value = {
        "choices": [{"message": {"content": '{"status": "CONTRADICTED", "confidence": 0.98, "explanation": "Vua không hề thất trận.", "has_conflict": true}'}}]
    }
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_contradicted
        res_contra = await openai.verify_claim("Lê Thánh Tông bị đánh bại năm 1471", [chunk])
        assert res_contra.status.value == "CONTRADICTED"
        assert len(res_contra.citations) == 0
        assert res_contra.provider_diagnostics["is_fallback"] is False


