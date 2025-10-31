"""Video translation module for AMP Video Automation Toolkit.

This module provides functionality to:
- Extract audio from video files
- Transcribe audio using Whisper
- Translate transcriptions with style adaptation using GPT-4
- Generate new avatar videos in target language
"""

from .pipeline import translate_video
from .styles import TranslationStyle

__all__ = ["translate_video", "TranslationStyle"]
