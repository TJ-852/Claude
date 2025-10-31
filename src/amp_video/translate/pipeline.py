"""Video translation pipeline orchestrator."""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Optional

from rich.console import Console

from ..config import settings
from ..models import Artifact
from ..providers.heygen import HeyGenClient
from ..providers.elevenlabs import ElevenLabsTTS
from ..storage.local import LocalStore
from ..utils import get_timestamp, format_duration
from .styles import TranslationStyle
from .transcriber import WhisperTranscriber
from .translator import GPT4Translator
from .video_processor import VideoProcessor

logger = logging.getLogger(__name__)
console = Console()


class TranslationResult:
    """Result of video translation pipeline."""

    def __init__(
        self,
        video_id: str,
        original_video: Path,
        source_language: str,
        target_language: str,
        style: TranslationStyle,
        transcription: str,
        translated_script: str,
        audio_path: Optional[Path] = None,
        video_path: Optional[Path] = None,
        error: Optional[str] = None
    ):
        self.video_id = video_id
        self.original_video = original_video
        self.source_language = source_language
        self.target_language = target_language
        self.style = style
        self.transcription = transcription
        self.translated_script = translated_script
        self.audio_path = audio_path
        self.video_path = video_path
        self.error = error

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "video_id": self.video_id,
            "original_video": str(self.original_video),
            "source_language": self.source_language,
            "target_language": self.target_language,
            "style": self.style.value,
            "transcription": self.transcription,
            "translated_script": self.translated_script,
            "audio_path": str(self.audio_path) if self.audio_path else None,
            "video_path": str(self.video_path) if self.video_path else None,
            "error": self.error
        }


async def translate_video(
    video_path: Path,
    target_language: str,
    style: TranslationStyle = TranslationStyle.CONVERSATIONAL,
    avatar: Optional[str] = None,
    voice: Optional[str] = None,
    output_dir: Optional[Path] = None,
    detect_language: bool = True
) -> TranslationResult:
    """
    Translate a video to a new language with avatar.

    Pipeline:
    1. Extract audio from video
    2. Transcribe audio using Whisper
    3. Translate transcription with style using GPT-4
    4. Generate TTS audio in target language
    5. Create new avatar video with translated audio

    Args:
        video_path: Path to input video file
        target_language: Target language (e.g., "Thai", "Spanish")
        style: Translation style
        avatar: Avatar ID (uses default if not specified)
        voice: Voice ID (uses default if not specified)
        output_dir: Output directory (auto-generated if not specified)
        detect_language: Auto-detect source language

    Returns:
        TranslationResult with all outputs and metadata

    Raises:
        FileNotFoundError: If video file doesn't exist
        ProviderError: If any API call fails
    """
    start_time = time.time()

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Setup output directory
    if output_dir is None:
        timestamp = get_timestamp()
        output_dir = Path("output") / f"translate_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    video_id = video_path.stem
    avatar = avatar or settings.default_avatar
    voice = voice or settings.default_voice

    console.print(f"\n[bold cyan]Video Translation Pipeline[/bold cyan]")
    console.print(f"Video: {video_path.name}")
    console.print(f"Target: {target_language}")
    console.print(f"Style: {style.value}")
    console.print(f"Output: {output_dir}\n")

    try:
        # Step 1: Extract audio
        console.print("[cyan]→[/cyan] Extracting audio from video...")
        processor = VideoProcessor()
        audio_path = await processor.extract_audio(
            video_path=video_path,
            output_path=output_dir / f"{video_id}_original_audio.mp3"
        )
        console.print(f"[green]✓[/green] Audio extracted: {audio_path.name}\n")

        # Step 2: Transcribe audio
        console.print("[cyan]→[/cyan] Transcribing audio...")
        transcriber = WhisperTranscriber(api_key=settings.openai_api_key)

        # Detect language if requested
        source_language = None
        if detect_language:
            source_language = await transcriber.detect_language(audio_path)
            console.print(f"[green]✓[/green] Detected language: {source_language}")

        # Transcribe
        transcription_result = await transcriber.transcribe(
            audio_path=audio_path,
            language=source_language[:2] if source_language else None  # ISO code
        )
        transcription = transcription_result["text"]
        await transcriber.close()

        console.print(
            f"[green]✓[/green] Transcription complete "
            f"({len(transcription)} chars)\n"
        )

        # Save transcription
        (output_dir / f"{video_id}_transcription.txt").write_text(
            transcription,
            encoding="utf-8"
        )

        # Step 3: Translate with style
        console.print(
            f"[cyan]→[/cyan] Translating to {target_language} "
            f"with {style.value} style..."
        )
        translator = GPT4Translator(
            api_key=settings.openai_api_key,
            model=getattr(settings, "gpt_model", "gpt-4o")
        )

        translated_script = await translator.translate(
            text=transcription,
            target_language=target_language,
            style=style,
            source_language=source_language
        )
        await translator.close()

        console.print(
            f"[green]✓[/green] Translation complete "
            f"({len(translated_script)} chars)\n"
        )

        # Save translated script
        (output_dir / f"{video_id}_translated_{target_language.lower()}.txt").write_text(
            translated_script,
            encoding="utf-8"
        )

        # Step 4: Generate TTS audio
        console.print(f"[cyan]→[/cyan] Generating TTS audio with voice {voice}...")
        tts = ElevenLabsTTS(api_key=settings.elevenlabs_api_key, voice=voice)

        tts_path = await tts.synth(
            text=translated_script,
            language=target_language,
            name=f"{video_id}_translated",
            output_dir=output_dir
        )
        await tts.close()

        console.print(f"[green]✓[/green] TTS audio generated: {tts_path.name}\n")

        # Step 5: Create avatar video
        console.print(f"[cyan]→[/cyan] Creating avatar video with {avatar}...")
        heygen = HeyGenClient(api_key=settings.heygen_api_key)

        # Upload TTS audio or use file URL
        store = LocalStore(base=output_dir)
        voice_url = store.public_url(tts_path)

        # Create video
        video_id_heygen = await heygen.create_video(
            voice_url=voice_url,
            avatar=avatar,
            script=translated_script,
            language=target_language
        )

        console.print(f"[cyan]→[/cyan] Polling for video completion...")
        video_url = await heygen.poll_video(video_id_heygen)

        # Download video
        console.print(f"[cyan]→[/cyan] Downloading video...")
        video_path_final = await store.download(
            video_url,
            f"{video_id}_translated_{target_language.lower()}.mp4"
        )
        await heygen.close()

        console.print(f"[green]✓[/green] Video created: {video_path_final.name}\n")

        # Create result
        elapsed = time.time() - start_time
        console.print(f"[bold green]Translation Complete![/bold green]")
        console.print(f"Duration: {format_duration(elapsed)}")
        console.print(f"Output: {video_path_final}\n")

        result = TranslationResult(
            video_id=video_id,
            original_video=video_path,
            source_language=source_language or "Auto-detected",
            target_language=target_language,
            style=style,
            transcription=transcription,
            translated_script=translated_script,
            audio_path=tts_path,
            video_path=video_path_final
        )

        # Save manifest
        manifest_path = output_dir / "translation_manifest.json"
        manifest_path.write_text(
            json.dumps(result.to_dict(), indent=2),
            encoding="utf-8"
        )

        return result

    except Exception as e:
        logger.error(f"Translation failed: {e}", exc_info=True)
        console.print(f"[red]✗ Error: {e}[/red]\n")

        return TranslationResult(
            video_id=video_id,
            original_video=video_path,
            source_language="Unknown",
            target_language=target_language,
            style=style,
            transcription="",
            translated_script="",
            error=str(e)
        )


async def translate_batch(
    video_paths: list[Path],
    target_language: str,
    style: TranslationStyle = TranslationStyle.CONVERSATIONAL,
    avatar: Optional[str] = None,
    voice: Optional[str] = None,
    concurrency: int = 2
) -> list[TranslationResult]:
    """
    Translate multiple videos in batch.

    Args:
        video_paths: List of video file paths
        target_language: Target language
        style: Translation style
        avatar: Avatar ID
        voice: Voice ID
        concurrency: Max concurrent translations

    Returns:
        List of TranslationResult objects
    """
    console.print(f"\n[bold cyan]Batch Video Translation[/bold cyan]")
    console.print(f"Videos: {len(video_paths)}")
    console.print(f"Target: {target_language}")
    console.print(f"Concurrency: {concurrency}\n")

    sem = asyncio.Semaphore(concurrency)
    results = []

    async def worker(video_path: Path):
        async with sem:
            result = await translate_video(
                video_path=video_path,
                target_language=target_language,
                style=style,
                avatar=avatar,
                voice=voice
            )
            results.append(result)

    await asyncio.gather(*(worker(vp) for vp in video_paths))

    # Summary
    success_count = sum(1 for r in results if r.error is None)
    error_count = len(results) - success_count

    console.print(f"[bold green]Batch Complete![/bold green]")
    console.print(f"Success: {success_count} | Errors: {error_count}\n")

    return results
