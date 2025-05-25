"""
Pydantic models for request/response validation
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """Request model for translation"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to translate")
    source_language: str = Field(..., min_length=2, max_length=5, description="Source language code")
    target_language: str = Field(..., min_length=2, max_length=5, description="Target language code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "नमस्ते, आज का समाचार क्या है?",
                "source_language": "hi",
                "target_language": "kn"
            }
        }


class TranslationResponse(BaseModel):
    """Response model for translation"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence_score: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_text": "नमस्ते, आज का समाचार क्या है?",
                "translated_text": "ನಮಸ್ಕಾರ, ಇಂದಿನ ಸುದ್ದಿ ಏನು?",
                "source_language": "hi",
                "target_language": "kn",
                "confidence_score": 0.95
            }
        }


class VoiceToTextRequest(BaseModel):
    """Request model for voice to text conversion"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    language: str = Field(..., min_length=2, max_length=5, description="Language code for recognition")
    
    class Config:
        json_schema_extra = {
            "example": {
                "audio_data": "base64_encoded_audio_string",
                "language": "hi"
            }
        }


class VoiceToTextResponse(BaseModel):
    """Response model for voice to text conversion"""
    text: str
    language: str
    confidence_score: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "नमस्ते, आज का समाचार क्या है?",
                "language": "hi",
                "confidence_score": 0.92
            }
        }


class TextToSpeechRequest(BaseModel):
    """Request model for text to speech conversion"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert to speech")
    language: str = Field(..., min_length=2, max_length=5, description="Language code for speech")
    voice_speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "ನಮಸ್ಕಾರ, ಇಂದಿನ ಸುದ್ದಿ ಏನು?",
                "language": "kn",
                "voice_speed": 1.0
            }
        }


class TextToSpeechResponse(BaseModel):
    """Response model for text to speech conversion"""
    audio_url: str
    text: str
    language: str
    duration: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "audio_url": "/api/v1/audio/generated_audio_id.mp3",
                "text": "ನಮಸ್ಕಾರ, ಇಂದಿನ ಸುದ್ದಿ ಏನು?",
                "language": "kn",
                "duration": 3.5
            }
        }


class LanguageInfo(BaseModel):
    """Language information model"""
    code: str
    name: str
    native_name: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "kn",
                "name": "Kannada",
                "native_name": "ಕನ್ನಡ"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "TRANSLATION_ERROR",
                "message": "Failed to translate text",
                "details": {"source_language": "hi", "target_language": "kn"}
            }
        }
