from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.models.storyboard import Storyboard


class VideoRenderRequest(BaseModel):
    subject: str = Field(default="Emperor Lê Thánh Tông (1460–1497)", description="Topic of video")
    format: str = Field(default="SHORTS", description="'SHORTS' (45-60s), 'EXPLAINER' (3-4m), or 'DOCUMENTARY' (15m)")
    aspect_ratio: str = Field(default="16:9", description="'16:9' (horizontal) or '9:16' (vertical mobile)")
    include_subtitles: bool = Field(default=True, description="Embed synchronized timed subtitles")
    storyboard: Optional[Storyboard] = Field(None, description="Optional custom storyboard to render")
    enable_tts: bool = Field(default=False, description="Enable spoken TTS voiceover narration if available (falls back to ambient background audio if offline)")
    audio_mode: str = Field(default="ambient", description="Audio track mode: 'tts' (spoken narration), 'ambient' (pentatonic chime background audio)")


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
    audio_track_type: str = Field(default="background_ambient_chime", description="Actual audio track rendered: 'spoken_narration_tts' or 'background_ambient_chime'")
    subtitles_synchronized: bool = Field(default=True, description="Whether subtitles are precisely synchronized with audio timeline")
