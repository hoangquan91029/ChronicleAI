from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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


class ScriptFormat(str, Enum):
    SHORTS = "SHORTS"              # 30-60s, fast-paced, high hook, punchy visual cues
    EXPLAINER = "EXPLAINER"        # 3-5m, clear pedagogical overview
    DOCUMENTARY = "DOCUMENTARY"    # 10-20m, deep archival breakdown


class ScriptScene(BaseModel):
    scene_number: int = Field(..., description="Sequential scene index (1, 2, ...)")
    title: str = Field(..., description="Scene title / chapter header")
    scene_type: SceneType = Field(..., description="Scene dramatic purpose")
    estimated_duration_seconds: int = Field(..., description="Duration in seconds (e.g. 15-180s)")
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
    format: ScriptFormat = Field(default=ScriptFormat.DOCUMENTARY, description="Target video format")
    target_duration_minutes: float = Field(default=16.0, description="Target total duration in minutes")
    total_estimated_duration_seconds: int = Field(default=960, description="Sum of scene durations")
    hook: str = Field(..., description="Engaging opening hook to capture viewers")
    background_summary: str = Field(..., description="Historical context & geopolitical background")
    scenes: List[ScriptScene] = Field(default_factory=list)
    conclusion: str = Field(..., description="Engaging closing remarks & historical legacy")
    total_scenes: int = 0
    verified_claims_count: int = 0
    flagged_for_review_count: int = 0
    sources_consulted: List[str] = Field(default_factory=list)
    provider_diagnostics: Optional[Dict[str, Any]] = None


class ScriptGenerationRequest(BaseModel):
    subject: str = Field(default="Emperor Lê Thánh Tông (1460–1497)", description="Topic / Figure to script")
    target_minutes: Optional[float] = Field(default=None, description="Target duration in minutes (e.g. 1.0 for Shorts, 4.0 for Explainer, 16.0 for Documentary)")
    format: Optional[ScriptFormat] = Field(default=None, description="Target format (defaults to DOCUMENTARY if target_minutes >= 10, EXPLAINER if >= 2, SHORTS if < 2)")
    document_ids: Optional[List[str]] = Field(None, description="Scope to specific uploaded document IDs")


class SceneUpdateRequest(BaseModel):
    title: Optional[str] = None
    scene_type: Optional[SceneType] = None
    estimated_duration_seconds: Optional[int] = None
    historical_setting: Optional[str] = None
    narration: Optional[str] = None
    dialogues: Optional[List[DialogueLine]] = None
    key_historical_facts: Optional[List[str]] = None
    needs_review: Optional[bool] = None
    review_notes: Optional[str] = None
