from typing import Optional, Dict
from fastapi import APIRouter, Response, HTTPException
from app.models.script import VideoScript, ScriptGenerationRequest, SceneUpdateRequest
from app.services.scriptwriter import ScriptwriterService

router = APIRouter(prefix="/api/scripts", tags=["Scriptwriting Agent"])
scriptwriter = ScriptwriterService()

# In-memory cached script for export
cached_scripts: Dict[str, VideoScript] = {}


@router.post("/generate", response_model=VideoScript)
async def generate_video_script(req: ScriptGenerationRequest):
    """
    Generate an educational video script (Shorts, Explainer, or Documentary)
    grounded in historical documents with citations, scene structure,
    and clearly demarcated fictional dramatizations.
    """
    script = await scriptwriter.generate_script(req)
    cached_scripts["latest"] = script
    return script


@router.get("/latest", response_model=Optional[VideoScript])
async def get_latest_script():
    return cached_scripts.get("latest")


@router.put("/scenes/{scene_number}", response_model=VideoScript)
async def update_script_scene(scene_number: int, update: SceneUpdateRequest):
    """Update details of a specific scene in the active script."""
    script = cached_scripts.get("latest")
    if not script:
        raise HTTPException(status_code=404, detail="No active script found. Generate a script first.")
    scene = next((s for s in script.scenes if s.scene_number == scene_number), None)
    if not scene:
        raise HTTPException(status_code=404, detail=f"Scene {scene_number} not found.")

    if update.title is not None:
        scene.title = update.title
    if update.scene_type is not None:
        scene.scene_type = update.scene_type
    if update.estimated_duration_seconds is not None:
        scene.estimated_duration_seconds = update.estimated_duration_seconds
    if update.historical_setting is not None:
        scene.historical_setting = update.historical_setting
    if update.narration is not None:
        scene.narration = update.narration
    if update.dialogues is not None:
        scene.dialogues = update.dialogues
    if update.key_historical_facts is not None:
        scene.key_historical_facts = update.key_historical_facts
    if update.needs_review is not None:
        scene.needs_review = update.needs_review
    if update.review_notes is not None:
        scene.review_notes = update.review_notes

    script.total_estimated_duration_seconds = sum(s.estimated_duration_seconds for s in script.scenes)
    script.flagged_for_review_count = sum(1 for s in script.scenes if s.needs_review)
    return script



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
