"""Translation style definitions and prompts."""

from enum import Enum
from typing import Dict


class TranslationStyle(str, Enum):
    """Supported translation styles."""

    CASUAL = "casual"
    CONVERSATIONAL = "conversational"
    BUSINESS = "business"
    EXPLAINER = "explainer"
    FORMAL = "formal"
    TECHNICAL = "technical"


# Style-specific prompts for GPT-4 translation
STYLE_PROMPTS: Dict[TranslationStyle, str] = {
    TranslationStyle.CASUAL: """
You are translating a video script into {target_language}.

Style Guidelines:
- Use casual, relaxed language
- Include colloquialisms and informal expressions appropriate to the target language
- Keep sentences short and punchy
- Use contractions where natural
- Aim for a friendly, approachable tone
- Preserve humor and personality from the original

Translate the following transcript while maintaining a casual, friendly style:
""",

    TranslationStyle.CONVERSATIONAL: """
You are translating a video script into {target_language}.

Style Guidelines:
- Use natural, conversational language as if speaking to a friend
- Include rhetorical questions and direct address ("you", "we")
- Maintain a warm, engaging tone
- Use transitional phrases that flow naturally in speech
- Keep the pacing conversational, not too formal or stiff
- Preserve the speaker's personality and enthusiasm

Translate the following transcript while maintaining a conversational, engaging style:
""",

    TranslationStyle.BUSINESS: """
You are translating a video script into {target_language}.

Style Guidelines:
- Use professional, business-appropriate language
- Maintain clarity and precision
- Use industry-standard terminology
- Keep a confident, authoritative tone
- Avoid overly casual expressions
- Ensure cultural appropriateness for business contexts
- Focus on value propositions and key messages

Translate the following transcript while maintaining a professional business style:
""",

    TranslationStyle.EXPLAINER: """
You are translating a video script into {target_language}.

Style Guidelines:
- Use clear, educational language
- Break down complex concepts into simple terms
- Use analogies and examples where appropriate
- Maintain a helpful, patient tone
- Include transitional phrases for logical flow
- Avoid jargon unless necessary (then explain it)
- Focus on making content accessible and easy to understand

Translate the following transcript while maintaining a clear explainer style:
""",

    TranslationStyle.FORMAL: """
You are translating a video script into {target_language}.

Style Guidelines:
- Use formal, sophisticated language
- Maintain grammatical precision
- Avoid contractions and colloquialisms
- Use complete sentences with proper structure
- Employ respectful, dignified tone
- Use appropriate honorifics for the target language
- Ensure high register appropriate for official communications

Translate the following transcript while maintaining a formal, dignified style:
""",

    TranslationStyle.TECHNICAL: """
You are translating a video script into {target_language}.

Style Guidelines:
- Use precise technical terminology
- Maintain accuracy of technical concepts
- Use industry-standard terms in the target language
- Keep explanations clear but technically accurate
- Preserve acronyms and technical abbreviations where appropriate
- Focus on precision over simplicity
- Ensure technical concepts are not oversimplified

Translate the following transcript while maintaining technical accuracy:
"""
}


def get_style_prompt(style: TranslationStyle, target_language: str) -> str:
    """
    Get the translation prompt for a specific style.

    Args:
        style: Translation style to use
        target_language: Target language name

    Returns:
        Formatted prompt string
    """
    return STYLE_PROMPTS[style].format(target_language=target_language)


def get_available_styles() -> list[str]:
    """
    Get list of available translation styles.

    Returns:
        List of style names
    """
    return [style.value for style in TranslationStyle]
