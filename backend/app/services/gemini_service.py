"""
Google Gemini API service for text translation
"""
import logging
from typing import Optional, Tuple
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)


class GeminiTranslationService:
    """Service for handling text translation using Google Gemini API"""

    def __init__(self):
        """Initialize the Gemini service"""
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def translate_text(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> Tuple[str, Optional[float]]:
        """
        Translate text from source language to target language

        Args:
            text: Text to translate
            source_language: Source language code
            target_language: Target language code

        Returns:
            Tuple of (translated_text, confidence_score)
        """
        try:
            # Get language names for better context
            source_lang_name = settings.supported_languages.get(source_language, source_language)
            target_lang_name = settings.supported_languages.get(target_language, target_language)

            # Create a detailed prompt for better translation quality
            prompt = f"""
            You are a professional translator specializing in news and media content.

            Task: Translate the following text from {source_lang_name} to {target_lang_name}.

            Instructions:
            1. Maintain the original meaning and context
            2. Use appropriate formal language suitable for news content
            3. Preserve any proper nouns, names, and technical terms
            4. Ensure cultural sensitivity and accuracy
            5. Return ONLY the translated text, no explanations or additional content

            Text to translate:
            {text}

            Translation:
            """

            logger.info(f"Translating text from {source_language} to {target_language}")

            response = self.model.generate_content(prompt)

            if not response.text:
                raise Exception("Empty response from Gemini API")

            translated_text = response.text.strip()

            # Simple confidence estimation based on response quality
            confidence_score = self._estimate_confidence(text, translated_text)

            logger.info(f"Translation completed with confidence: {confidence_score}")

            return translated_text, confidence_score

        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            raise Exception(f"Translation failed: {str(e)}")

    def _estimate_confidence(self, original_text: str, translated_text: str) -> float:
        """
        Estimate translation confidence based on simple heuristics

        Args:
            original_text: Original text
            translated_text: Translated text

        Returns:
            Confidence score between 0 and 1
        """
        try:
            # Basic heuristics for confidence estimation
            original_length = len(original_text.split())
            translated_length = len(translated_text.split())

            # Length ratio check (reasonable translations should have similar word counts)
            length_ratio = min(original_length, translated_length) / max(original_length, translated_length)

            # Base confidence
            confidence = 0.8

            # Adjust based on length ratio
            if length_ratio > 0.7:
                confidence += 0.1
            elif length_ratio < 0.3:
                confidence -= 0.2

            # Check for empty or very short translations
            if translated_length < 2:
                confidence -= 0.3

            # Ensure confidence is between 0 and 1
            confidence = max(0.0, min(1.0, confidence))

            return round(confidence, 2)

        except Exception:
            return 0.7  # Default confidence if estimation fails

    async def detect_language(self, text: str) -> str:
        """
        Detect the language of the given text

        Args:
            text: Text to analyze

        Returns:
            Language code
        """
        try:
            prompt = f"""
            Detect the language of the following text and return ONLY the ISO 639-1 language code (2 letters).

            Supported languages: {', '.join(settings.supported_languages.keys())}

            Text: {text}

            Language code:
            """

            response = self.model.generate_content(prompt)
            detected_language = response.text.strip().lower()

            # Validate the detected language
            if detected_language in settings.supported_languages:
                return detected_language
            else:
                logger.warning(f"Detected language '{detected_language}' not supported, defaulting to 'en'")
                return "en"

        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return "en"  # Default to English if detection fails


# Global service instance
gemini_service = GeminiTranslationService()
