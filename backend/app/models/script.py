from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.rag import Citation


class DialogueType(str, Enum):
    HISTORICAL_QUOTE = "HISTORICAL_QUOTE"
    FICTIONAL_DRAMATIZATION = "FICTIONAL_DRAMATIZATION"
    NARRATION = "NARRATION"


class DialogueLine(BaseModel):
    speaker: str = Field(..., description="Speaker name, e.g. 'Người dẫn chuyện', 'Vua Lê Thánh Tông', 'Nguyễn Trãi'")
    text: str = Field(..., description="Spoken line or dialogue")
    dialogue_type: DialogueType = Field(default=DialogueType.NARRATION, description="HISTORICAL_QUOTE | FICTIONAL_DRAMATIZATION | NARRATION")
    is_fictional: bool = Field(default=False, description="Flag indicating if dialogue is a creative reconstruction")
    citation: Optional[Citation] = Field(None, description="Direct citation if this is an authentic historical quote")


class SceneType(str, Enum):
    HOOK = "HOOK"
    BACKGROUND = "BACKGROUND"
    NARRATIVE = "NARRATIVE"
    KEY_ACHIEVEMENT = "KEY_ACHIEVEMENT"
    HISTORICAL_CONFLICT = "HISTORICAL_CONFLICT"
    CONCLUSION = "CONCLUSION"


class ScriptScene(BaseModel):
    scene_number: int = Field(..., description="Sequential scene index (1, 2, ...)")
    title: str = Field(..., description="Scene title / chapter header")
    scene_type: SceneType = Field(..., description="Scene dramatic purpose")
    estimated_duration_seconds: int = Field(..., description="Duration in seconds (e.g. 90-150s)")
    historical_setting: str = Field(..., description="Time, location, historical environment")
    narration: str = Field(..., description="Main narrator voiceover text")
    dialogues: List[DialogueLine] = Field(default_factory=list, description="List of character dialogues")
    key_historical_facts: List[str] = Field(default_factory=list, description="Historical claims and achievements in this scene")
    citations: List[Citation] = Field(default_factory=list, description="Traceable citations linking facts to sources")
    needs_review: bool = Field(default=False, description="Flagged true if unverified claims need historian review")
    review_notes: Optional[str] = Field(None, description="Reason for review if claim lacks evidence")


class VideoScript(BaseModel):
    title: str
    subject: str = Field(default="Lê Thánh Tông", description="Historical figure or topic")
    target_duration_minutes: float = Field(default=16.0, description="Target total duration in minutes (15-20 min)")
    total_estimated_duration_seconds: int = Field(default=960, description="Sum of scene durations")
    hook: str = Field(..., description="Engaging opening hook to capture viewers")
    background_summary: str = Field(..., description="Historical context & geopolitical background")
    scenes: List[ScriptScene] = Field(default_factory=list)
    conclusion: str = Field(..., description="Engaging closing remarks & historical legacy")
    total_scenes: int = 0
    verified_claims_count: int = 0
    flagged_for_review_count: int = 0
    sources_consulted: List[str] = Field(default_factory=list)


class ScriptGenerationRequest(BaseModel):
    subject: str = Field(default="Emperor Lê Thánh Tông (1460–1497)", description="Topic / Figure to script")
    target_minutes: int = Field(default=16, ge=10, le=25, description="Target duration in minutes (15-20 min recommended)")
    document_ids: Optional[List[str]] = Field(None, description="Scope to specific uploaded document IDs")
