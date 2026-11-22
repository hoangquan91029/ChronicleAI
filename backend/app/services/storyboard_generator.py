from typing import Optional
from app.models.script import VideoScript
from app.models.storyboard import Storyboard
from app.services.llm_provider import get_llm_provider


class StoryboardGeneratorService:
    def __init__(self):
        self.llm = get_llm_provider()

    async def generate_storyboard(self, script: VideoScript) -> Storyboard:
        """
        Convert a VideoScript into an actionable animation storyboard.
        Produces minimalist 2D Vietnamese historical stick-figure character animation
        scenes with character dialogues, camera movements, and AI image prompts.
        """
        return await self.llm.generate_storyboard(script)
