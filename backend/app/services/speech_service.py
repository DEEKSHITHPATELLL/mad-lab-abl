"""
Speech recognition and text-to-speech services
"""
import logging
import base64
import io
import os
import tempfile
import uuid
from typing import Optional, Tuple
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from app.config import settings

logger = logging.getLogger(__name__)


class SpeechService:
    """Service for handling speech recognition and text-to-speech"""

    def __init__(self):
        """Initialize the speech service"""
        self.recognizer = sr.Recognizer()
        self.audio_output_dir = "app/static/audio"
        os.makedirs(self.audio_output_dir, exist_ok=True)

    async def voice_to_text(
        self,
        audio_data: str,
        language: str = "en"
    ) -> Tuple[str, Optional[float]]:
        """
        Convert voice audio to text

        Args:
            audio_data: Base64 encoded audio data
            language: Language code for recognition

        Returns:
            Tuple of (recognized_text, confidence_score)
        """
        try:
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)

            # Create temporary file for audio processing
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file_path = temp_file.name

            try:
                # Try to convert audio to WAV format using pydub for better compatibility
                try:
                    # First, save the raw audio data
                    with open(temp_file_path.replace('.wav', '.raw'), 'wb') as raw_file:
                        raw_file.write(audio_bytes)

                    # Try to load as different formats and convert to WAV
                    audio_segment = None
                    for format_type in ['m4a', 'mp3', 'wav', 'ogg', 'webm']:
                        try:
                            if format_type == 'm4a':
                                audio_segment = AudioSegment.from_file(
                                    temp_file_path.replace('.wav', '.raw'),
                                    format='m4a'
                                )
                            elif format_type == 'mp3':
                                audio_segment = AudioSegment.from_mp3(temp_file_path.replace('.wav', '.raw'))
                            elif format_type == 'wav':
                                audio_segment = AudioSegment.from_wav(temp_file_path.replace('.wav', '.raw'))
                            elif format_type == 'ogg':
                                audio_segment = AudioSegment.from_ogg(temp_file_path.replace('.wav', '.raw'))
                            elif format_type == 'webm':
                                audio_segment = AudioSegment.from_file(
                                    temp_file_path.replace('.wav', '.raw'),
                                    format='webm'
                                )
                            break
                        except Exception:
                            continue

                    if audio_segment:
                        # Convert to WAV format for speech recognition
                        audio_segment.export(temp_file_path, format="wav")
                    else:
                        # Fallback: write raw bytes as WAV
                        with open(temp_file_path, 'wb') as wav_file:
                            wav_file.write(audio_bytes)

                except Exception as conversion_error:
                    logger.warning(f"Audio conversion failed, using raw data: {conversion_error}")
                    # Fallback: write raw bytes
                    with open(temp_file_path, 'wb') as wav_file:
                        wav_file.write(audio_bytes)

                # Load audio file for speech recognition
                with sr.AudioFile(temp_file_path) as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    # Record the audio
                    audio = self.recognizer.record(source)

                # Convert language code to format expected by speech_recognition
                recognition_language = self._get_recognition_language_code(language)

                # Perform speech recognition
                try:
                    # Try Google Speech Recognition first
                    text = self.recognizer.recognize_google(
                        audio,
                        language=recognition_language
                    )
                    confidence = 0.85  # Google API doesn't provide confidence, estimate

                except sr.RequestError:
                    # Fallback to offline recognition if available
                    try:
                        text = self.recognizer.recognize_sphinx(audio)
                        confidence = 0.7  # Lower confidence for offline recognition
                    except sr.RequestError:
                        raise Exception("Speech recognition service unavailable")

                logger.info(f"Speech recognition successful: {text[:50]}...")
                return text, confidence

            finally:
                # Clean up temporary files
                for temp_path in [temp_file_path, temp_file_path.replace('.wav', '.raw')]:
                    if os.path.exists(temp_path):
                        try:
                            os.unlink(temp_path)
                        except Exception:
                            pass  # Ignore cleanup errors

        except sr.UnknownValueError:
            raise Exception("Could not understand the audio")
        except sr.RequestError as e:
            raise Exception(f"Speech recognition service error: {str(e)}")
        except Exception as e:
            logger.error(f"Voice to text conversion failed: {str(e)}")
            raise Exception(f"Voice to text conversion failed: {str(e)}")

    async def text_to_speech(
        self,
        text: str,
        language: str = "en",
        voice_speed: float = 1.0
    ) -> Tuple[str, Optional[float]]:
        """
        Convert text to speech audio

        Args:
            text: Text to convert to speech
            language: Language code for speech synthesis
            voice_speed: Speed multiplier for speech

        Returns:
            Tuple of (audio_file_path, duration)
        """
        try:
            # Generate unique filename
            audio_id = str(uuid.uuid4())
            audio_filename = f"{audio_id}.mp3"
            audio_path = os.path.join(self.audio_output_dir, audio_filename)

            # Convert language code to format expected by gTTS
            tts_language = self._get_tts_language_code(language)

            # Create gTTS object
            tts = gTTS(
                text=text,
                lang=tts_language,
                slow=(voice_speed < 0.8)  # Use slow speech for speeds below 0.8
            )

            # Save to temporary file first
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                tts.save(temp_file.name)
                temp_audio_path = temp_file.name

            try:
                # Load audio for speed adjustment if needed
                if voice_speed != 1.0:
                    audio = AudioSegment.from_mp3(temp_audio_path)

                    # Adjust speed
                    if voice_speed > 1.0:
                        # Speed up
                        audio = audio.speedup(playback_speed=voice_speed)
                    elif voice_speed < 1.0:
                        # Slow down (already handled by gTTS slow parameter for very slow speeds)
                        if voice_speed >= 0.8:
                            audio = audio.speedup(playback_speed=voice_speed)

                    # Export adjusted audio
                    audio.export(audio_path, format="mp3")
                    duration = len(audio) / 1000.0  # Duration in seconds
                else:
                    # No speed adjustment needed, just copy the file
                    audio = AudioSegment.from_mp3(temp_audio_path)
                    audio.export(audio_path, format="mp3")
                    duration = len(audio) / 1000.0

            finally:
                # Clean up temporary file
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)

            # Return relative path for API response
            relative_path = f"/api/v1/audio/{audio_filename}"

            logger.info(f"Text to speech conversion successful: {relative_path}")
            return relative_path, duration

        except Exception as e:
            logger.error(f"Text to speech conversion failed: {str(e)}")
            raise Exception(f"Text to speech conversion failed: {str(e)}")

    def _get_recognition_language_code(self, language: str) -> str:
        """
        Convert language code to format expected by speech recognition

        Args:
            language: ISO 639-1 language code

        Returns:
            Language code for speech recognition
        """
        # Mapping for speech recognition language codes
        recognition_mapping = {
            "en": "en-US",
            "hi": "hi-IN",
            "kn": "kn-IN",
            "ta": "ta-IN",
            "te": "te-IN",
            "ml": "ml-IN",
            "bn": "bn-IN",
            "gu": "gu-IN",
            "mr": "mr-IN",
            "pa": "pa-IN",
            "ur": "ur-PK",
            "es": "es-ES",
            "fr": "fr-FR",
            "de": "de-DE",
            "it": "it-IT",
            "pt": "pt-PT",
            "ru": "ru-RU",
            "ja": "ja-JP",
            "ko": "ko-KR",
            "zh": "zh-CN",
            "ar": "ar-SA"
        }

        return recognition_mapping.get(language, "en-US")

    def _get_tts_language_code(self, language: str) -> str:
        """
        Convert language code to format expected by gTTS

        Args:
            language: ISO 639-1 language code

        Returns:
            Language code for text-to-speech
        """
        # gTTS uses standard ISO 639-1 codes for most languages
        # Some adjustments for specific languages
        tts_mapping = {
            "kn": "kn",  # Kannada
            "ta": "ta",  # Tamil
            "te": "te",  # Telugu
            "ml": "ml",  # Malayalam
            "bn": "bn",  # Bengali
            "gu": "gu",  # Gujarati
            "mr": "mr",  # Marathi
            "pa": "pa",  # Punjabi
            "ur": "ur",  # Urdu
            "zh": "zh-cn"  # Chinese (Simplified)
        }

        return tts_mapping.get(language, language)


# Global service instance
speech_service = SpeechService()
