import pytest
from pathlib import Path
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import CitationVectorStore
from app.services.scriptwriter import ScriptwriterService
from app.services.storyboard_generator import StoryboardGeneratorService
from app.models.script import ScriptGenerationRequest

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


@pytest.fixture
def services():
    store = CitationVectorStore()
    pdf_path = SAMPLE_DIR / "le_thanh_tong_dai_viet.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    proc = PDFProcessor()
    res = proc.process_pdf(pdf_bytes, "le_thanh_tong_dai_viet.pdf", "doc_le_thanh_tong")
    store.add_chunks(res.chunks)

    sw = ScriptwriterService(vector_store=store)
    sb = StoryboardGeneratorService()
    return sw, sb


@pytest.mark.asyncio
async def test_storyboard_generation_and_minimalist_2d_style(services):
    sw, sb = services
    script = await sw.generate_script(ScriptGenerationRequest(subject="Lê Thánh Tông"))
    storyboard = await sb.generate_storyboard(script)

    assert storyboard.total_scenes == len(script.scenes)
    assert storyboard.total_duration_seconds > 0
    assert "stick-figure" in storyboard.visual_theme.lower()

    for scene in storyboard.scenes:
        assert scene.scene_number > 0
        assert len(scene.narration) > 0
        assert len(scene.historical_setting) > 0
        assert len(scene.camera_direction) > 0
        assert len(scene.ai_image_prompt) > 0

        # Verify minimalist 2D stick-figure animation aesthetic
        prompt_lower = scene.ai_image_prompt.lower()
        assert "minimalist" in prompt_lower
        assert "2d" in prompt_lower
        assert "stick-figure" in prompt_lower
        assert "vietnamese" in prompt_lower

        # Verify duration
        assert scene.estimated_duration_seconds >= 60


@pytest.mark.asyncio
async def test_storyboard_evidence_preservation(services):
    sw, sb = services
    script = await sw.generate_script(ScriptGenerationRequest(subject="Lê Thánh Tông"))
    storyboard = await sb.generate_storyboard(script)

    # Find scene 6 (Nam Chinh & territorial oath)
    scene_6 = next(s for s in storyboard.scenes if s.scene_number == 6)
    assert len(scene_6.evidence_references) > 0
    assert scene_6.evidence_references[0].page == 5
    assert scene_6.evidence_references[0].filename == "le_thanh_tong_dai_viet.pdf"
