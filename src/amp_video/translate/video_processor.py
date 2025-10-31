"""Video processing utilities for audio extraction."""

import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Video processor for extracting audio and metadata.

    Uses ffmpeg for video/audio manipulation.
    """

    def __init__(self):
        """Initialize video processor."""
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """
        Check if ffmpeg is installed.

        Raises:
            RuntimeError: If ffmpeg is not found
        """
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "ffmpeg is not installed. Install with: apt-get install ffmpeg (Linux) "
                "or brew install ffmpeg (Mac) or download from https://ffmpeg.org/"
            )

    async def extract_audio(
        self,
        video_path: Path,
        output_path: Optional[Path] = None,
        audio_format: str = "mp3",
        sample_rate: int = 16000
    ) -> Path:
        """
        Extract audio from video file.

        Args:
            video_path: Path to input video file
            output_path: Path for output audio file (optional)
            audio_format: Output audio format (mp3, wav, etc.)
            sample_rate: Audio sample rate in Hz (16000 recommended for Whisper)

        Returns:
            Path to extracted audio file

        Raises:
            FileNotFoundError: If video file doesn't exist
            subprocess.CalledProcessError: If ffmpeg extraction fails
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Generate output path if not provided
        if output_path is None:
            output_path = video_path.parent / f"{video_path.stem}_audio.{audio_format}"

        logger.info(f"Extracting audio from {video_path} to {output_path}")

        # Build ffmpeg command
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",  # No video
            "-acodec", "libmp3lame" if audio_format == "mp3" else "pcm_s16le",
            "-ar", str(sample_rate),  # Sample rate
            "-ac", "1",  # Mono
            "-y",  # Overwrite output file
            str(output_path)
        ]

        # Run ffmpeg
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="ignore")
            raise subprocess.CalledProcessError(
                process.returncode,
                cmd,
                stderr=error_msg
            )

        logger.info(f"Audio extracted successfully: {output_path}")
        return output_path

    async def get_video_info(self, video_path: Path) -> dict:
        """
        Get video metadata using ffprobe.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video metadata (duration, resolution, etc.)

        Raises:
            FileNotFoundError: If video file doesn't exist
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(video_path)
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="ignore")
            raise subprocess.CalledProcessError(
                process.returncode,
                cmd,
                stderr=error_msg
            )

        import json
        return json.loads(stdout.decode("utf-8"))

    def get_duration(self, video_path: Path) -> float:
        """
        Get video duration in seconds.

        Args:
            video_path: Path to video file

        Returns:
            Duration in seconds

        Raises:
            FileNotFoundError: If video file doesn't exist
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        try:
            return float(result.stdout.strip())
        except ValueError:
            logger.warning(f"Could not parse duration for {video_path}")
            return 0.0

    async def replace_audio(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path
    ) -> Path:
        """
        Replace audio track in video with new audio.

        Args:
            video_path: Path to original video file
            audio_path: Path to new audio file
            output_path: Path for output video

        Returns:
            Path to output video

        Raises:
            FileNotFoundError: If input files don't exist
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Replacing audio in {video_path} with {audio_path}")

        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", "copy",  # Copy video codec
            "-map", "0:v:0",  # Use video from first input
            "-map", "1:a:0",  # Use audio from second input
            "-shortest",  # Match shortest stream
            "-y",  # Overwrite output
            str(output_path)
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="ignore")
            raise subprocess.CalledProcessError(
                process.returncode,
                cmd,
                stderr=error_msg
            )

        logger.info(f"Audio replaced successfully: {output_path}")
        return output_path
