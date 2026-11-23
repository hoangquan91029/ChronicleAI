from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.models.storyboard import Storyboard


class VideoRenderRequest(BaseModel):
    subject: str = Field(default="Emperor Lê Thánh Tông (1460–1497)", description="Topic of video")
    format: str = Field(default="SHORTS", description="'SHORTS' (45-60s), 'EXPLAINER' (3-4m), or 'DOCUMENTARY' (15m)")
    aspect_ratio: str = Field(default="16:9", description="'16:9' (horizontal) or '9:16' (vertical mobile)")
    include_subtitles: bool = Field(default=True, description="Embed synchronized timed subtitles")
    storyboard: Optional[Storyboard] = Field(None, description="Optional custom storyboard to render")


class VideoRenderStatus(BaseModel):
    video_id: str
    status: str = Field(..., description="'queued', 'rendering', 'completed', 'failed'")
    title: str
    subject: str
    progress_percent: int = 0
    duration_seconds: float = 0.0
    aspect_ratio: str = "16:9"
    file_path: Optional[str] = None
    file_size_bytes: int = 0
    download_url: str
    stream_url: str
    error_message: Optional[str] = None
    created_at: str
    total_scenes: int = 0
