"""
API routes for the multilingual voice translation application
"""
import logging
import os
import base64
from typing import List
from fastapi import APIRouter, HTTPException, status, File, UploadFile, Form
from fastapi.responses import FileResponse
from app.models.schemas import (
    TranslationRequest, TranslationResponse,
    VoiceToTextRequest, VoiceToTextResponse,
    TextToSpeechRequest, TextToSpeechResponse,
    LanguageInfo, ErrorResponse
)
from app.services.gemini_service import gemini_service
from app.services.speech_service import speech_service
from app.config import settings

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1", tags=["translation"])


@router.get("/health", summary="Health check endpoint")
async def health_check():
    """Health check endpoint to verify API is running"""
    return {
        "status": "healthy",
        "version": settings.version,
        "app_name": settings.app_name
    }


@router.get(
    "/languages",
    response_model=List[LanguageInfo],
    summary="Get supported languages"
)
async def get_supported_languages():
    """Get list of all supported languages"""
    try:
        languages = []
        for code, name in settings.supported_languages.items():
            languages.append(LanguageInfo(code=code, name=name))

        return languages

    except Exception as e:
        logger.error(f"Failed to get supported languages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve supported languages"
        )


@router.post(
    "/translate",
    response_model=TranslationResponse,
    summary="Translate text between languages"
)
async def translate_text(request: TranslationRequest):
    """Translate text from source language to target language"""
    try:
        # Validate language codes
        if request.source_language not in settings.supported_languages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported source language: {request.source_language}"
            )

        if request.target_language not in settings.supported_languages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported target language: {request.target_language}"
            )

        # Perform translation
        translated_text, confidence = await gemini_service.translate_text(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language
        )

        return TranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            source_language=request.source_language,
            target_language=request.target_language,
            confidence_score=confidence
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


@router.post(
    "/voice-to-text",
    response_model=VoiceToTextResponse,
    summary="Convert voice audio to text"
)
async def voice_to_text(request: VoiceToTextRequest):
    """Convert voice audio to text using speech recognition"""
    try:
        # Validate language code
        if request.language not in settings.supported_languages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language: {request.language}"
            )

        # Perform voice to text conversion
        recognized_text, confidence = await speech_service.voice_to_text(
            audio_data=request.audio_data,
            language=request.language
        )

        return VoiceToTextResponse(
            text=recognized_text,
            language=request.language,
            confidence_score=confidence
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice to text conversion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice to text conversion failed: {str(e)}"
        )


@router.post(
    "/speech-to-text",
    summary="Convert uploaded audio file to text"
)
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = Form(default="en")
):
    """Convert uploaded audio file to text using speech recognition"""
    try:
        # Validate language code
        if language not in settings.supported_languages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language: {language}"
            )

        # Validate file type
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an audio file"
            )

        # Read audio file content
        audio_content = await audio.read()

        # Convert to base64 for processing
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')

        # Perform voice to text conversion
        recognized_text, confidence = await speech_service.voice_to_text(
            audio_data=audio_base64,
            language=language
        )

        return {
            "text": recognized_text,
            "transcription": recognized_text,  # Alternative field name
            "language": language,
            "confidence_score": confidence,
            "filename": audio.filename
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech to text conversion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech to text conversion failed: {str(e)}"
        )


@router.post(
    "/text-to-speech",
    response_model=TextToSpeechResponse,
    summary="Convert text to speech audio"
)
async def text_to_speech(request: TextToSpeechRequest):
    """Convert text to speech audio"""
    try:
        # Validate language code
        if request.language not in settings.supported_languages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language: {request.language}"
            )

        # Perform text to speech conversion
        audio_url, duration = await speech_service.text_to_speech(
            text=request.text,
            language=request.language,
            voice_speed=request.voice_speed
        )

        return TextToSpeechResponse(
            audio_url=audio_url,
            text=request.text,
            language=request.language,
            duration=duration
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text to speech conversion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text to speech conversion failed: {str(e)}"
        )


@router.get(
    "/audio/{filename}",
    summary="Serve generated audio files"
)
async def get_audio_file(filename: str):
    """Serve generated audio files"""
    try:
        audio_path = os.path.join("app/static/audio", filename)

        if not os.path.exists(audio_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio file not found"
            )

        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve audio file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to serve audio file"
        )


@router.post(
    "/detect-language",
    summary="Detect language of given text"
)
async def detect_language(text: str):
    """Detect the language of the given text"""
    try:
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )

        detected_language = await gemini_service.detect_language(text)

        return {
            "text": text,
            "detected_language": detected_language,
            "language_name": settings.supported_languages.get(detected_language, "Unknown")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Language detection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Language detection failed: {str(e)}"
        )
