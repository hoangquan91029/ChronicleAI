#!/usr/bin/env python3
"""
Generate the canonical ChronicleAI demonstration video:
Emperor Lê Thánh Tông of Đại Việt (1460–1497).
Exports to demo_output/chronicle_demo_video.mp4 with visual cards, synchronized subtitles, and audio.
"""
import os
import sys
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.models.script import ScriptGenerationRequest, ScriptFormat
from app.services.scriptwriter import ScriptwriterService
from app.services.storyboard_generator import StoryboardGeneratorService
from app.services.video_renderer import global_video_renderer, DEMO_OUTPUT_DIR, ROOT_DEMO_DIR


async def main():
    print("[ChronicleAI] Generating canonical demo video for Emperor Lê Thánh Tông...")
    sw = ScriptwriterService()
    script = await sw.generate_script(ScriptGenerationRequest(
        subject="Hoàng đế Lê Thánh Tông",
        format=ScriptFormat.SHORTS
    ))
    print(f"[ChronicleAI] Script generated: {script.title} ({len(script.scenes)} scenes)")

    sb_service = StoryboardGeneratorService()
    storyboard = await sb_service.generate_storyboard(script, aspect_ratio="16:9")
    print(f"[ChronicleAI] Storyboard generated: {storyboard.total_scenes} scenes")

    status = global_video_renderer.render_storyboard_to_video(
        storyboard=storyboard,
        video_id="demo_le_thanh_tong",
        aspect_ratio="16:9",
        enable_tts=False  # Deterministic offline ambient audio for CI hermeticity
    )
    print(f"[ChronicleAI] Video rendered successfully:")
    print(f"  - File: {status.file_path}")
    print(f"  - Size: {status.file_size_bytes:,} bytes")
    print(f"  - Duration: {status.duration_seconds}s")
    print(f"  - Audio track: {status.audio_track_type}")

    demo_target = DEMO_OUTPUT_DIR / "chronicle_demo_video.mp4"
    if demo_target.exists():
        print(f"[ChronicleAI] Demo video verified at {demo_target}")
    else:
        print(f"[ChronicleAI] Warning: {demo_target} not found")


if __name__ == "__main__":
    asyncio.run(main())
