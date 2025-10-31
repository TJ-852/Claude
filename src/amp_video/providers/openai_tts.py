"""OpenAI TTS API client (alternative provider)."""

import logging
from pathlib import Path
from typing import Optional, Literal

import httpx
import tenacity

from .errors import ProviderError, RateLimitError, AuthenticationError

logger = logging.getLogger(__name__)

VoiceType = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


class OpenAITTS:
    """
    Async client for OpenAI Text-to-Speech API.

    Alternative TTS provider with HD quality options.
    """

    def __init__(
        self,
        api_key: str,
        voice: VoiceType = "nova",
        model: str = "tts-1",
        base_url: str = "https://api.openai.com/v1"
    ):
        """
        Initialize OpenAI TTS client.

        Args:
            api_key: OpenAI API key
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)
            model: Model name (tts-1 or tts-1-hd)
            base_url: API base URL
        """
        self.api_key = api_key
        self.voice = voice
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
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
        voice: Optional[VoiceType] = None,
        speed: float = 1.0
    ) -> Path:
        """
        Synthesize text to speech.

        Args:
            text: Text to synthesize (max 4096 chars)
            language: Language code (not used by OpenAI, included for compatibility)
            name: Job name for output filename
            output_dir: Directory to save audio file
            voice: Voice name (overrides default)
            speed: Speed from 0.25 to 4.0

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

        # OpenAI has 4096 character limit
        if len(text) > 4096:
            logger.warning(f"Text length {len(text)} exceeds OpenAI limit, truncating to 4096")
            text = text[:4096]

        payload = {
            "model": self.model,
            "input": text,
            "voice": voice_id,
            "response_format": "mp3",
            "speed": speed
        }

        try:
            response = await self._client.post(
                "/audio/speech",
                json=payload
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

            # Save audio content
            output_path.write_bytes(response.content)
            logger.info(f"Generated OpenAI TTS audio: {output_path}")
            return output_path

        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            raise ProviderError(
                f"OpenAI API error: {error_text}",
                provider="openai",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            raise ProviderError(
                f"OpenAI request failed: {str(e)}",
                provider="openai"
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
