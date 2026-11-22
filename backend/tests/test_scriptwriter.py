import pytest
from pathlib import Path
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import CitationVectorStore
from app.services.scriptwriter import ScriptwriterService
from app.models.script import ScriptGenerationRequest, DialogueType

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


@pytest.fixture
def scriptwriter():
    store = CitationVectorStore()
    pdf_path = SAMPLE_DIR / "le_thanh_tong_dai_viet.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    proc = PDFProcessor()
    res = proc.process_pdf(pdf_bytes, "le_thanh_tong_dai_viet.pdf", "doc_le_thanh_tong")
    store.add_chunks(res.chunks)
    return ScriptwriterService(vector_store=store)


@pytest.mark.asyncio
async def test_generate_15_to_20_minute_script(scriptwriter):
    req = ScriptGenerationRequest(
        subject="Emperor Lê Thánh Tông (1460–1497)",
        target_minutes=16
    )
    script = await scriptwriter.generate_script(req)

    assert script.title is not None
    assert "Lê Thánh Tông" in script.subject
    
    # Check duration bounds (15-20 min target)
    assert 14.0 <= script.target_duration_minutes <= 22.0
    assert script.total_estimated_duration_seconds >= 800

    # Check structural components
    assert len(script.hook) > 20
    assert len(script.background_summary) > 20
    assert len(script.conclusion) > 20
    assert script.total_scenes >= 5

    # Check that dialogues clearly distinguish historical quotes from fictional dramatization
    all_dialogues = [d for s in script.scenes for d in s.dialogues]
    assert len(all_dialogues) > 0

    has_fictional = any(d.dialogue_type == DialogueType.FICTIONAL_DRAMATIZATION for d in all_dialogues)
    has_historical_quote = any(d.dialogue_type == DialogueType.HISTORICAL_QUOTE for d in all_dialogues)

    assert has_fictional is True, "Must contain clearly labeled fictional dialogue dramatizations"
    assert has_historical_quote is True, "Must contain authentic historical quotes"

    # Check citations on historical quotes
    hist_quotes = [d for d in all_dialogues if d.dialogue_type == DialogueType.HISTORICAL_QUOTE]
    for quote in hist_quotes:
        if quote.citation:
            assert quote.citation.filename == "le_thanh_tong_dai_viet.pdf"
            assert quote.citation.page in [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_script_scene_traceability(scriptwriter):
    req = ScriptGenerationRequest(subject="Lê Thánh Tông")
    script = await scriptwriter.generate_script(req)

    # Check that key scenes have citations referencing authentic pages
    scene_3 = next(s for s in script.scenes if s.scene_number == 3)  # Hồng Đức Code
    assert len(scene_3.citations) > 0
    assert scene_3.citations[0].page == 2

    scene_4 = next(s for s in script.scenes if s.scene_number == 4)  # Văn Miếu stelae
    assert len(scene_4.citations) > 0
    assert scene_4.citations[0].page == 3
