"""Audio transcription using OpenAI Whisper."""

import logging
from pathlib import Path
from typing import Optional

import httpx
import tenacity

from ..providers.errors import ProviderError, AuthenticationError, RateLimitError

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    """
    Transcriber using OpenAI Whisper API.

    Supports automatic language detection and optional translation to English.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1"
    ):
        """
        Initialize Whisper transcriber.

        Args:
            api_key: OpenAI API key
            base_url: API base URL
        """
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}"
            },
            timeout=300.0  # Transcription can take a while for long videos
        )

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=2, min=2, max=30),
        stop=tenacity.stop_after_attempt(3),
        retry=tenacity.retry_if_exception_type(RateLimitError),
        reraise=True
    )
    async def transcribe(
        self,
        audio_path: Path,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json"
    ) -> dict:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file (mp3, mp4, wav, etc.)
            language: ISO-639-1 language code (e.g., 'en', 'th', 'es')
                     If None, language is auto-detected
            prompt: Optional text to guide the model's style
            response_format: Response format (json, text, srt, vtt)

        Returns:
            Transcription result dict with 'text' and optional 'language'

        Raises:
            FileNotFoundError: If audio file doesn't exist
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit exceeded
            ProviderError: For other API errors
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Check file size (Whisper has 25MB limit)
        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 25:
            logger.warning(
                f"Audio file {audio_path} is {file_size_mb:.1f}MB. "
                "Whisper API has a 25MB limit. Consider compressing the audio."
            )

        logger.info(f"Transcribing {audio_path} (size: {file_size_mb:.1f}MB)")

        # Prepare multipart form data
        files = {
            "file": (audio_path.name, audio_path.open("rb"), "audio/mpeg")
        }

        data = {
            "model": "whisper-1",
            "response_format": response_format
        }

        if language:
            data["language"] = language

        if prompt:
            data["prompt"] = prompt

        try:
            response = await self._client.post(
                "/audio/transcriptions",
                files=files,
                data=data
            )

            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid OpenAI API key",
                    provider="openai",
                    status_code=401
                )
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise RateLimitError(
                    "OpenAI rate limit exceeded",
                    retry_after=retry_after,
                    provider="openai",
                    status_code=429
                )

            response.raise_for_status()

            if response_format == "json":
                result = response.json()
                logger.info(
                    f"Transcription complete. Length: {len(result.get('text', ''))} chars"
                )
                return result
            else:
                # For text, srt, vtt formats, return as dict
                return {"text": response.text}

        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"Whisper API error: {e.response.text}",
                provider="openai",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            raise ProviderError(
                f"Whisper request failed: {str(e)}",
                provider="openai"
            )
        finally:
            # Make sure to close the file
            if "file" in files:
                files["file"][1].close()

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=2, min=2, max=30),
        stop=tenacity.stop_after_attempt(3),
        retry=tenacity.retry_if_exception_type(RateLimitError),
        reraise=True
    )
    async def transcribe_with_timestamps(
        self,
        audio_path: Path,
        language: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio with word-level timestamps.

        Args:
            audio_path: Path to audio file
            language: ISO-639-1 language code (optional)

        Returns:
            Dict with 'text' and 'segments' (timestamped segments)
        """
        return await self.transcribe(
            audio_path=audio_path,
            language=language,
            response_format="verbose_json"
        )

    async def detect_language(self, audio_path: Path) -> str:
        """
        Detect the language of an audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Detected language code (e.g., 'en', 'th', 'es')

        Raises:
            ProviderError: If detection fails
        """
        logger.info(f"Detecting language for {audio_path}")

        result = await self.transcribe(
            audio_path=audio_path,
            response_format="verbose_json"
        )

        detected_language = result.get("language", "unknown")
        logger.info(f"Detected language: {detected_language}")

        return detected_language

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
