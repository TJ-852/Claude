"""Translation service using GPT-4 with style adaptation."""

import logging
from typing import Optional

import httpx
import tenacity

from ..providers.errors import ProviderError, AuthenticationError, RateLimitError
from .styles import TranslationStyle, get_style_prompt

logger = logging.getLogger(__name__)


class GPT4Translator:
    """
    Translator using GPT-4 with style-aware prompts.

    Translates text while adapting to specified communication styles.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        base_url: str = "https://api.openai.com/v1"
    ):
        """
        Initialize GPT-4 translator.

        Args:
            api_key: OpenAI API key
            model: GPT model to use (gpt-4o, gpt-4-turbo, gpt-4, etc.)
            base_url: API base URL
        """
        self.api_key = api_key
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=120.0
        )

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=2, min=2, max=30),
        stop=tenacity.stop_after_attempt(3),
        retry=tenacity.retry_if_exception_type(RateLimitError),
        reraise=True
    )
    async def translate(
        self,
        text: str,
        target_language: str,
        style: TranslationStyle = TranslationStyle.CONVERSATIONAL,
        source_language: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> str:
        """
        Translate text with style adaptation.

        Args:
            text: Text to translate
            target_language: Target language (e.g., "Thai", "Spanish")
            style: Translation style to apply
            source_language: Source language (optional, for context)
            additional_context: Additional context or instructions

        Returns:
            Translated text

        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit exceeded
            ProviderError: For other API errors
        """
        logger.info(
            f"Translating {len(text)} chars to {target_language} "
            f"with style: {style.value}"
        )

        # Build system prompt
        system_prompt = get_style_prompt(style, target_language)

        if source_language:
            system_prompt += f"\n\nSource language: {source_language}"

        if additional_context:
            system_prompt += f"\n\nAdditional context: {additional_context}"

        system_prompt += "\n\nProvide ONLY the translated text, no explanations or notes."

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,  # Some creativity for natural style
            "max_tokens": len(text) * 3  # Allow for expansion in translation
        }

        try:
            response = await self._client.post(
                "/chat/completions",
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
            data = response.json()

            translated_text = data["choices"][0]["message"]["content"].strip()

            logger.info(
                f"Translation complete. Output length: {len(translated_text)} chars"
            )

            return translated_text

        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"GPT-4 API error: {e.response.text}",
                provider="openai",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            raise ProviderError(
                f"GPT-4 request failed: {str(e)}",
                provider="openai"
            )
        except (KeyError, IndexError) as e:
            raise ProviderError(
                f"Unexpected response format from GPT-4: {e}",
                provider="openai"
            )

    async def translate_segments(
        self,
        segments: list[dict],
        target_language: str,
        style: TranslationStyle = TranslationStyle.CONVERSATIONAL
    ) -> list[dict]:
        """
        Translate multiple segments while preserving structure.

        Args:
            segments: List of segment dicts with 'text' and 'start'/'end' times
            target_language: Target language
            style: Translation style

        Returns:
            List of translated segments with preserved timestamps
        """
        logger.info(f"Translating {len(segments)} segments")

        # Combine all text for context-aware translation
        combined_text = "\n\n".join(
            f"[Segment {i+1}]\n{seg['text']}"
            for i, seg in enumerate(segments)
        )

        # Translate combined text
        translated_combined = await self.translate(
            text=combined_text,
            target_language=target_language,
            style=style,
            additional_context="Preserve segment markers [Segment N] in translation"
        )

        # Split back into segments
        translated_segments = []
        parts = translated_combined.split("[Segment ")

        for i, seg in enumerate(segments):
            if i + 1 < len(parts):
                # Extract translated text for this segment
                segment_text = parts[i + 1]
                # Remove the segment number and marker
                if "]" in segment_text:
                    segment_text = segment_text.split("]", 1)[1].strip()

                translated_segments.append({
                    "text": segment_text,
                    "start": seg.get("start"),
                    "end": seg.get("end")
                })
            else:
                # Fallback: translate individually
                translated_text = await self.translate(
                    text=seg["text"],
                    target_language=target_language,
                    style=style
                )
                translated_segments.append({
                    "text": translated_text,
                    "start": seg.get("start"),
                    "end": seg.get("end")
                })

        return translated_segments

    async def detect_language(self, text: str) -> str:
        """
        Detect the language of text.

        Args:
            text: Text to analyze

        Returns:
            Detected language name
        """
        messages = [
            {
                "role": "system",
                "content": "Identify the language of the following text. "
                          "Respond with ONLY the language name (e.g., 'English', 'Thai', 'Spanish')."
            },
            {"role": "user", "content": text[:500]}  # Use first 500 chars
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 20
        }

        try:
            response = await self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "Unknown"

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
