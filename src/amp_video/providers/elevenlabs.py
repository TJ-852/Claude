"""ElevenLabs TTS API client."""

import logging
from pathlib import Path
from typing import Optional

import httpx
import tenacity

from .errors import ProviderError, RateLimitError, AuthenticationError

logger = logging.getLogger(__name__)


class ElevenLabsTTS:
    """
    Async client for ElevenLabs Text-to-Speech API.

    Converts text scripts to high-quality audio files.
    """

    def __init__(
        self,
        api_key: str,
        voice: str = "Rachel",
        base_url: str = "https://api.elevenlabs.io/v1"
    ):
        """
        Initialize ElevenLabs TTS client.

        Args:
            api_key: ElevenLabs API key
            voice: Default voice ID or name
            base_url: API base URL
        """
        self.api_key = api_key
        self.voice = voice
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            },
            timeout=60.0
        )

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=2, min=1, max=10),
        stop=tenacity.stop_after_attempt(3),
        retry=tenacity.retry_if_exception_type(RateLimitError),
        reraise=True
    )
    async def synth(
        self,
        text: str,
        language: str,
        name: str,
        output_dir: Path,
        voice: Optional[str] = None
    ) -> Path:
        """
        Synthesize text to speech.

        Args:
            text: Text to synthesize
            language: Language code (e.g., "en", "es", "zh")
            name: Job name for output filename
            output_dir: Directory to save audio file
            voice: Voice ID (overrides default)

        Returns:
            Path to generated audio file

        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit exceeded
            ProviderError: For other API errors
        """
        voice_id = voice or self.voice
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{name}_tts.mp3"

        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        try:
            # First, resolve voice name to ID if needed
            voice_endpoint = f"/text-to-speech/{voice_id}"

            response = await self._client.post(
                voice_endpoint,
                json=payload
            )

            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid ElevenLabs API key",
                    provider="elevenlabs",
                    status_code=401
                )
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise RateLimitError(
                    "ElevenLabs rate limit exceeded",
                    retry_after=retry_after,
                    provider="elevenlabs",
                    status_code=429
                )

            response.raise_for_status()

            # Save audio content
            output_path.write_bytes(response.content)
            logger.info(f"Generated TTS audio: {output_path}")
            return output_path

        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"ElevenLabs API error: {e.response.text}",
                provider="elevenlabs",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            raise ProviderError(
                f"ElevenLabs request failed: {str(e)}",
                provider="elevenlabs"
            )

    async def list_voices(self) -> list[dict]:
        """
        List available voices.

        Returns:
            List of voice dictionaries with id, name, and metadata

        Raises:
            ProviderError: If request fails
        """
        try:
            response = await self._client.get("/voices")
            response.raise_for_status()
            data = response.json()
            return data.get("voices", [])
        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"Failed to list voices: {e.response.text}",
                provider="elevenlabs",
                status_code=e.response.status_code
            )

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
