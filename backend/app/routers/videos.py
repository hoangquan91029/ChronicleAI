import os
import hashlib
from typing import List, Dict, Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from app.models.video import VideoRenderRequest, VideoRenderStatus
from app.services.video_renderer import global_video_renderer, EXPORTS_DIR, DEMO_OUTPUT_DIR, ROOT_DEMO_DIR
from app.routers.storyboards import cached_storyboards
from app.routers.scripts import cached_scripts
from app.services.scriptwriter import ScriptwriterService
from app.services.storyboard_generator import StoryboardGeneratorService
from app.models.script import ScriptGenerationRequest, ScriptFormat
from app.models.storyboard import StoryboardGenerationRequest

router = APIRouter(prefix="/api/videos", tags=["Video Production Engine"])

# In-memory registry of rendered videos (also checks disk for pre-rendered videos)
video_registry: Dict[str, VideoRenderStatus] = {}


def _find_demo_file() -> Optional[Path]:
    for d in (ROOT_DEMO_DIR, DEMO_OUTPUT_DIR):
        p = d / "chronicle_demo_video.mp4"
        if p.exists():
            return p
    return None



def _discover_existing_videos():
    """Discover existing exported MP4 videos on disk upon initialization."""
    if EXPORTS_DIR.exists():
        for p in EXPORTS_DIR.glob("*.mp4"):
            vid_id = p.stem
            if vid_id not in video_registry:
                size = p.stat().st_size
                video_registry[vid_id] = VideoRenderStatus(
                    video_id=vid_id,
                    status="completed",
                    title=f"Video: {vid_id}",
                    subject="Lê Thánh Tông",
                    progress_percent=100,
                    duration_seconds=60.0,
                    aspect_ratio="16:9",
                    file_path=str(p),
                    file_size_bytes=size,
                    download_url=f"/api/videos/{vid_id}/download",
                    stream_url=f"/api/videos/{vid_id}/stream",
                    created_at="2026-11-23T00:00:00",
                    total_scenes=3
                )


_discover_existing_videos()


@router.post("/render", response_model=VideoRenderStatus)
async def render_video(req: VideoRenderRequest):
    """
    Produce a complete, playable MP4 video from a storyboard.
    Generates high-resolution 2D visual scene cards, acoustic ambient narration audio,
    and timed subtitles, assembling them into a broadcast-ready MP4 using FFmpeg.
    """
    storyboard = req.storyboard

    if not storyboard:
        # Check cached storyboard
        storyboard = cached_storyboards.get("latest")

    if not storyboard:
        # Generate on the fly
        sw = ScriptwriterService()
        fmt_enum = ScriptFormat.SHORTS if req.format.upper() == "SHORTS" else (
            ScriptFormat.EXPLAINER if req.format.upper() == "EXPLAINER" else ScriptFormat.DOCUMENTARY
        )
        script = await sw.generate_script(ScriptGenerationRequest(
            subject=req.subject,
            format=fmt_enum
        ))
        cached_scripts["latest"] = script

        sb_service = StoryboardGeneratorService()
        storyboard = await sb_service.generate_storyboard(script, aspect_ratio=req.aspect_ratio)
        cached_storyboards["latest"] = storyboard

    # Generate unique stable video id
    video_hash = hashlib.md5(f"{storyboard.subject}_{req.format}_{req.aspect_ratio}_{len(storyboard.scenes)}".encode("utf-8")).hexdigest()[:8]
    video_id = f"chronicle_{video_hash}"

    try:
        status = global_video_renderer.render_storyboard_to_video(
            storyboard=storyboard,
            video_id=video_id,
            aspect_ratio=req.aspect_ratio,
            enable_tts=req.enable_tts,
            audio_mode=req.audio_mode
        )
        video_registry[video_id] = status
        video_registry["latest"] = status
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed rendering video: {str(e)}")


@router.get("", response_model=List[VideoRenderStatus])
async def list_rendered_videos():
    """List all completed and available video exports."""
    # Exclude the 'latest' alias key from list
    return [v for k, v in video_registry.items() if k != "latest"]


@router.get("/latest", response_model=VideoRenderStatus)
async def get_latest_video():
    """Retrieve the latest rendered video status."""
    latest = video_registry.get("latest")
    if not latest:
        # Try demo video if exists
        demo_p = _find_demo_file()
        if demo_p:
            return VideoRenderStatus(
                video_id="demo_le_thanh_tong",
                status="completed",
                title="Đại Việt Thời Hồng Đức (Demo)",
                subject="Hoàng đế Lê Thánh Tông (1460–1497)",
                progress_percent=100,
                duration_seconds=60.0,
                aspect_ratio="16:9",
                file_path=str(demo_p),
                file_size_bytes=demo_p.stat().st_size,
                download_url="/api/videos/demo_le_thanh_tong/download",
                stream_url="/api/videos/demo_le_thanh_tong/stream",
                created_at="2026-11-23T00:00:00",
                total_scenes=3
            )
        raise HTTPException(status_code=404, detail="No rendered video available yet. Trigger /api/videos/render first.")
    return latest


@router.get("/{video_id}/status", response_model=VideoRenderStatus)
async def get_video_status(video_id: str):
    """Check the status and metadata of a specific video export."""
    if video_id == "demo_le_thanh_tong":
        demo_p = _find_demo_file()
        if demo_p:
            return VideoRenderStatus(
                video_id="demo_le_thanh_tong",
                status="completed",
                title="Đại Việt Thời Hồng Đức (Demo)",
                subject="Hoàng đế Lê Thánh Tông (1460–1497)",
                progress_percent=100,
                duration_seconds=60.0,
                aspect_ratio="16:9",
                file_path=str(demo_p),
                file_size_bytes=demo_p.stat().st_size,
                download_url="/api/videos/demo_le_thanh_tong/download",
                stream_url="/api/videos/demo_le_thanh_tong/stream",
                created_at="2026-11-23T00:00:00",
                total_scenes=3
            )

    if video_id not in video_registry:
        # Check disk directly
        disk_p = EXPORTS_DIR / f"{video_id}.mp4"
        if disk_p.exists():
            status = VideoRenderStatus(
                video_id=video_id,
                status="completed",
                title=f"Video: {video_id}",
                subject="Lê Thánh Tông",
                progress_percent=100,
                duration_seconds=60.0,
                aspect_ratio="16:9",
                file_path=str(disk_p),
                file_size_bytes=disk_p.stat().st_size,
                download_url=f"/api/videos/{video_id}/download",
                stream_url=f"/api/videos/{video_id}/stream",
                created_at="2026-11-23T00:00:00",
                total_scenes=3
            )
            video_registry[video_id] = status
            return status
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found.")
    return video_registry[video_id]


@router.get("/{video_id}/download")
async def download_video(video_id: str):
    """Download the completed MP4 video file."""
    # Check demo alias
    if video_id == "demo_le_thanh_tong":
        target = _find_demo_file()
        if target:
            return FileResponse(
                path=str(target),
                media_type="video/mp4",
                filename="chronicle_demo_video.mp4"
            )

    status = video_registry.get(video_id)
    file_path = status.file_path if status else str(EXPORTS_DIR / f"{video_id}.mp4")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Video file '{video_id}.mp4' not found on disk.")

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=f"{video_id}.mp4"
    )


@router.get("/{video_id}/stream")
async def stream_video(video_id: str):
    """Stream MP4 video directly for HTML5 inline video players."""
    if video_id == "demo_le_thanh_tong":
        target = _find_demo_file()
        if target:
            return FileResponse(path=str(target), media_type="video/mp4")

    status = video_registry.get(video_id)
    file_path = status.file_path if status else str(EXPORTS_DIR / f"{video_id}.mp4")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Video file '{video_id}.mp4' not found on disk.")

    return FileResponse(
        path=file_path,
        media_type="video/mp4"
    )

