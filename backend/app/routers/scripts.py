from typing import Optional, Dict
from fastapi import APIRouter, Response
from app.models.script import VideoScript, ScriptGenerationRequest
from app.services.scriptwriter import ScriptwriterService

router = APIRouter(prefix="/api/scripts", tags=["Scriptwriting Agent"])
scriptwriter = ScriptwriterService()

# In-memory cached script for export
cached_scripts: Dict[str, VideoScript] = {}


@router.post("/generate", response_model=VideoScript)
async def generate_video_script(req: ScriptGenerationRequest):
    """
    Generate an educational video script (15-20 min structure)
    grounded in historical documents with citations, scene structure,
    and clearly demarcated fictional dramatizations.
    """
    script = await scriptwriter.generate_script(req)
    cached_scripts["latest"] = script
    return script


@router.get("/latest", response_model=Optional[VideoScript])
async def get_latest_script():
    return cached_scripts.get("latest")


@router.post("/export/markdown")
async def export_script_markdown(script: VideoScript):
    """Export the script as formatted Markdown."""
    md_lines = [
        f"# {script.title}",
        f"**Chủ đề:** {script.subject}  ",
        f"**Thời lượng ước tính:** {script.target_duration_minutes} phút ({script.total_estimated_duration_seconds} giây)  ",
        f"**Số phân cảnh:** {script.total_scenes}  ",
        f"**Số trích dẫn chứng thực:** {script.verified_claims_count}  ",
        "",
        "## Mở đầu (Hook)",
        f"> {script.hook}",
        "",
        "## Bối cảnh Lịch sử (Background)",
        f"{script.background_summary}",
        "",
        "---",
        "## Các Phân Cảnh Chi Tiết",
        ""
    ]

    for scene in script.scenes:
        md_lines.extend([
            f"### Cảnh {scene.scene_number}: {scene.title}",
            f"- **Phân loại:** `{scene.scene_type}` | **Thời lượng:** {scene.estimated_duration_seconds}s",
            f"- **Bối cảnh lịch sử:** {scene.historical_setting}",
            f"- **Lời bình (Narration):** {scene.narration}",
            ""
        ])

        if scene.dialogues:
            md_lines.append("**Hội thoại (Dialogues):**")
            for d in scene.dialogues:
                tag = "[HƯ CẤU / KỊCH BẢN]" if d.is_fictional else "[CHÍNH SỬ]"
                md_lines.append(f"- **{d.speaker}** ({tag}): *\"{d.text}\"*")
            md_lines.append("")

        if scene.citations:
            md_lines.append("**Tư liệu chứng thực (Citations):**")
            for c in scene.citations:
                md_lines.append(f"- 📄 `{c.filename}` (Trang {c.page}, Đoạn `{c.chunk_id}`): *\"{c.quote}\"*")
            md_lines.append("")

        if scene.needs_review:
            md_lines.append(f"> ⚠️ **CẦN DUYỆT LẠI:** {scene.review_notes}")
            md_lines.append("")

        md_lines.append("---")

    md_lines.extend([
        "",
        "## Kết Luận",
        f"{script.conclusion}",
        "",
        "## Nguồn Tư Liệu Tham Khảo",
        *[f"- {src}" for src in script.sources_consulted]
    ])

    content = "\n".join(md_lines)
    return Response(
        content=content,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=chronicle_script.md"}
    )
