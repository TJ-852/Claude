"""Tests for video translation functionality."""

import pytest
from pathlib import Path

from amp_video.translate.styles import (
    TranslationStyle,
    get_style_prompt,
    get_available_styles
)


class TestTranslationStyles:
    """Test translation style utilities."""

    def test_translation_style_enum(self):
        """Test TranslationStyle enum values."""
        assert TranslationStyle.CASUAL.value == "casual"
        assert TranslationStyle.CONVERSATIONAL.value == "conversational"
        assert TranslationStyle.BUSINESS.value == "business"
        assert TranslationStyle.EXPLAINER.value == "explainer"
        assert TranslationStyle.FORMAL.value == "formal"
        assert TranslationStyle.TECHNICAL.value == "technical"

    def test_get_available_styles(self):
        """Test getting list of available styles."""
        styles = get_available_styles()

        assert "casual" in styles
        assert "conversational" in styles
        assert "business" in styles
        assert "explainer" in styles
        assert "formal" in styles
        assert "technical" in styles
        assert len(styles) == 6

    def test_get_style_prompt(self):
        """Test getting style-specific prompts."""
        prompt = get_style_prompt(TranslationStyle.BUSINESS, "Thai")

        assert "Thai" in prompt
        assert "business" in prompt.lower() or "professional" in prompt.lower()
        assert len(prompt) > 50  # Should be a detailed prompt

    def test_all_styles_have_prompts(self):
        """Test that all styles have associated prompts."""
        for style in TranslationStyle:
            prompt = get_style_prompt(style, "Spanish")
            assert len(prompt) > 0
            assert "Spanish" in prompt


class TestTranslationResult:
    """Test TranslationResult model."""

    def test_translation_result_to_dict(self):
        """Test converting TranslationResult to dictionary."""
        from amp_video.translate.pipeline import TranslationResult

        result = TranslationResult(
            video_id="test_video",
            original_video=Path("/path/to/video.mp4"),
            source_language="English",
            target_language="Thai",
            style=TranslationStyle.CONVERSATIONAL,
            transcription="Hello world",
            translated_script="สวัสดีชาวโลก",
            audio_path=Path("/path/to/audio.mp3"),
            video_path=Path("/path/to/output.mp4"),
            error=None
        )

        result_dict = result.to_dict()

        assert result_dict["video_id"] == "test_video"
        assert result_dict["source_language"] == "English"
        assert result_dict["target_language"] == "Thai"
        assert result_dict["style"] == "conversational"
        assert result_dict["transcription"] == "Hello world"
        assert result_dict["translated_script"] == "สวัสดีชาวโลก"
        assert result_dict["error"] is None

    def test_translation_result_with_error(self):
        """Test TranslationResult with error."""
        from amp_video.translate.pipeline import TranslationResult

        result = TranslationResult(
            video_id="test_video",
            original_video=Path("/path/to/video.mp4"),
            source_language="English",
            target_language="Thai",
            style=TranslationStyle.CASUAL,
            transcription="",
            translated_script="",
            error="API error occurred"
        )

        assert result.error == "API error occurred"
        assert result.transcription == ""
        assert result.translated_script == ""


class TestVideoProcessor:
    """Test VideoProcessor utilities."""

    def test_video_processor_init(self):
        """Test VideoProcessor initialization."""
        from amp_video.translate.video_processor import VideoProcessor

        # This will check for ffmpeg - may raise RuntimeError if not installed
        try:
            processor = VideoProcessor()
            assert processor is not None
        except RuntimeError as e:
            # ffmpeg not installed - this is expected in test environment
            assert "ffmpeg" in str(e).lower()


# Note: Integration tests requiring actual API calls are not included
# in the standard test suite to avoid API costs and rate limits.
# For full integration testing, use manual test scripts with real API keys.
