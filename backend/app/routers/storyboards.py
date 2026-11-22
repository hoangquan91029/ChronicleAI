from typing import Optional, Dict
from fastapi import APIRouter, Response
from app.models.script import VideoScript
from app.models.storyboard import Storyboard, StoryboardGenerationRequest
from app.services.storyboard_generator import StoryboardGeneratorService
from app.routers.scripts import cached_scripts

router = APIRouter(prefix="/api/storyboards", tags=["Storyboard Generator"])
storyboard_service = StoryboardGeneratorService()

cached_storyboards: Dict[str, Storyboard] = {}


@router.post("/generate", response_model=Storyboard)
async def generate_storyboard(req: StoryboardGenerationRequest):
    """
    Generate an animation storyboard from the latest or specified script.
    Produces minimalist 2D Vietnamese historical stick-figure character animation
    scene descriptions, staging, and AI image prompts.
    """
    script = cached_scripts.get("latest")
    if not script:
        # Generate default script first if none exists
        from app.services.scriptwriter import ScriptwriterService
        from app.models.script import ScriptGenerationRequest
        sw = ScriptwriterService()
        script = await sw.generate_script(ScriptGenerationRequest(subject=req.subject or "Lê Thánh Tông"))
        cached_scripts["latest"] = script

    storyboard = await storyboard_service.generate_storyboard(script)
    cached_storyboards["latest"] = storyboard
    return storyboard


@router.get("/latest", response_model=Optional[Storyboard])
async def get_latest_storyboard():
    return cached_storyboards.get("latest")


@router.post("/export/markdown")
async def export_storyboard_markdown(storyboard: Storyboard):
    """Export the storyboard as formatted Markdown."""
    lines = [
        f"# Bảng Phân Cảnh (Storyboard): {storyboard.script_title}",
        f"**Chủ đề:** {storyboard.subject}  ",
        f"**Tổng số cảnh:** {storyboard.total_scenes}  ",
        f"**Thời lượng ước tính:** {storyboard.total_duration_seconds} giây  ",
        f"**Định hướng mỹ thuật:** {storyboard.visual_theme}  ",
        "",
        "---",
        ""
    ]

    for s in storyboard.scenes:
        lines.extend([
            f"## Cảnh {s.scene_number}: {s.title} ({s.estimated_duration_seconds}s)",
            f"- **Bối cảnh lịch sử:** {s.historical_setting}",
            f"- **Mô tả thị giác (2D Minimalist Stick-figure):** {s.visual_description}",
            f"- **Góc máy & Chuyển động:** {s.camera_direction}",
            f"- **Lời bình (Narration):** {s.narration}",
            f"- **Hội thoại nhân vật:** {s.character_dialogue if s.character_dialogue else '(Không có)'}",
            "",
            "**🤖 AI Image-Generation Prompt (DALL-E / Midjourney / Imagen):**",
            f"```text\n{s.ai_image_prompt}\n```",
            ""
        ])

        if s.evidence_references:
            lines.append("**Bằng chứng lịch sử chứng thực cảnh quay:**")
            for c in s.evidence_references:
                lines.append(f"- 📄 `{c.filename}` (Trang {c.page}, Đoạn `{c.chunk_id}`): *\"{c.quote}\"*")
            lines.append("")

        lines.append("---")
        lines.append("")

    content = "\n".join(lines)
    return Response(
        content=content,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=chronicle_storyboard.md"}
    )
