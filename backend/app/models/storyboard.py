from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.rag import Citation


class StoryboardScene(BaseModel):
    scene_number: int = Field(..., description="Scene index")
    title: str = Field(..., description="Scene Title")
    estimated_duration_seconds: int = Field(..., description="Duration in seconds")
    narration: str = Field(..., description="Voiceover narration for this frame")
    character_dialogue: str = Field(default="", description="Key dialogue spoken by characters")
    historical_setting: str = Field(..., description="Setting (e.g., Điện Kính Thiên, Văn Miếu, Chiêm Thành border)")
    visual_description: str = Field(..., description="Description of the 2D minimalist animation scene composition")
    camera_direction: str = Field(..., description="Camera movement: wide angle, pan, slow zoom, character focus")
    character_poses: List[str] = Field(default_factory=list, description="Minimalist stick-figure character stances and gestures")
    ai_image_prompt: str = Field(..., description="Production-ready AI image generation prompt (minimalist 2D Vietnamese historical stick-figure style)")
    evidence_references: List[Citation] = Field(default_factory=list, description="Citations grounding the historical accuracy of this scene")


class Storyboard(BaseModel):
    script_title: str
    subject: str
    total_scenes: int
    total_duration_seconds: int
    visual_theme: str = Field(
        default="Minimalist 2D Vietnamese historical animation, clean vector stick-figure style, authentic 15th-century Đại Việt costumes (áo giao lĩnh, khăn đóng), subtle muted watercolor backgrounds",
        description="Overarching visual art direction"
    )
    scenes: List[StoryboardScene] = Field(default_factory=list)


class StoryboardGenerationRequest(BaseModel):
    script_id: Optional[str] = None
    subject: Optional[str] = "Emperor Lê Thánh Tông (1460–1497)"
    visual_style_preference: Optional[str] = "minimalist_2d_stick_figure"
