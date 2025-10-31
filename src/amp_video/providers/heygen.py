"""HeyGen API client for avatar video generation."""

import asyncio
import logging
from typing import Optional

import httpx
import tenacity

from .errors import ProviderError, RateLimitError, AuthenticationError

logger = logging.getLogger(__name__)


class HeyGenClient:
    """
    Async client for HeyGen API.

    Handles video creation with AI avatars and text-to-speech.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.heygen.com/v2"):
        """
        Initialize HeyGen client.

        Args:
            api_key: HeyGen API key
            base_url: API base URL
        """
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "X-Api-Key": api_key,
                "Content-Type": "application/json"
            },
            timeout=60.0
        )

    async def create_video(
        self,
        *,
        voice_url: str,
        avatar: str,
        script: str,
        language: str
    ) -> str:
        """
        Create a new avatar video.

        Args:
            voice_url: URL to TTS audio file
            avatar: Avatar ID (e.g., "SantaFe_v2")
            script: Script text for video
            language: Language code

        Returns:
            Video ID for polling

        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit exceeded
            ProviderError: For other API errors
        """
        payload = {
            "avatar": avatar,
            "voice": {
                "type": "audio",
                "audio_url": voice_url
            },
            "script": {
                "type": "text",
                "input_text": script,
                "language": language
            }
        }

        try:
            response = await self._client.post("/video/generate", json=payload)

            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid HeyGen API key",
                    provider="heygen",
                    status_code=401
                )
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise RateLimitError(
                    "HeyGen rate limit exceeded",
                    retry_after=retry_after,
                    provider="heygen",
                    status_code=429
                )

            response.raise_for_status()
            data = response.json()

            if "data" not in data or "video_id" not in data["data"]:
                raise ProviderError(
                    f"Unexpected response format: {data}",
                    provider="heygen"
                )

            video_id = data["data"]["video_id"]
            logger.info(f"Created HeyGen video: {video_id}")
            return video_id

        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"HeyGen API error: {e.response.text}",
                provider="heygen",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            raise ProviderError(
                f"HeyGen request failed: {str(e)}",
                provider="heygen"
            )

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=2, min=2, max=30),
        stop=tenacity.stop_after_delay(300),
        retry=tenacity.retry_if_exception_type(tenacity.TryAgain),
        reraise=True
    )
    async def poll_video(self, video_id: str) -> str:
        """
        Poll video generation status until complete.

        Args:
            video_id: Video ID from create_video()

        Returns:
            URL to completed video

        Raises:
            ProviderError: If video generation fails
            tenacity.RetryError: If polling times out (5 minutes)
        """
        try:
            response = await self._client.get(f"/video/status/{video_id}")
            response.raise_for_status()
            data = response.json()

            if "data" not in data:
                raise ProviderError(
                    f"Unexpected response format: {data}",
                    provider="heygen"
                )

            status_data = data["data"]
            status = status_data.get("status", "").lower()

            if status == "completed":
                video_url = status_data.get("video_url")
                if not video_url:
                    raise ProviderError(
                        "Video completed but no URL provided",
                        provider="heygen"
                    )
                logger.info(f"HeyGen video {video_id} completed: {video_url}")
                return video_url

            elif status == "failed":
                error_msg = status_data.get("error", "Unknown error")
                raise ProviderError(
                    f"HeyGen video generation failed: {error_msg}",
                    provider="heygen"
                )

            elif status in ("pending", "processing"):
                logger.debug(f"HeyGen video {video_id} still processing...")
                raise tenacity.TryAgain()

            else:
                raise ProviderError(
                    f"Unknown status: {status}",
                    provider="heygen"
                )

        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"HeyGen polling error: {e.response.text}",
                provider="heygen",
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
