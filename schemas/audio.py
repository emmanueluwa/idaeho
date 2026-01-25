"""
Audio Schemas - Pydantic models for request/response validation
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, field_validator
from enum import Enum


class AudioCategory(str, Enum):
    """Enum for audio catgories"""

    QURAN = "quran"
    LECTURE = "lecture"
    REMINDER = "reminder"


class AudioUploadRequest(BaseModel):
    """
    schema for audio upload metadata
    """

    title: str = Field(..., min_length=1, max_length=255, description="title")

    author: str = Field(..., min_length=1, max_length=255, description="name of author")

    category: AudioCategory = Field(
        default=AudioCategory.QURAN, description="audio category type"
    )

    @field_validator("title", "author")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure strings are not just whitespace"""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Surah Al-Baqarah",
                "author": "Sheikh Mustafa Al-Shaybani",
                "category": "quran",
            }
        }


class AudioUpdateRequest(BaseModel):
    """
    Schema for updating audio metadata
    """

    title: Optional[str] = Field(None, min_length=1, max_length=255)

    author: Optional[str] = Field(None, min_length=1, max_length=255)

    category: Optional[AudioCategory] = None

    @field_validator("title", "author")
    @classmethod
    def validate_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure strings are not just whitespace"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip() if v else None


class AudioResponse(BaseModel):
    """
    schema for audio response
    """

    id: int = Field(..., description="unique audio identifier")

    user_id: int = Field(..., description="owner user ID")

    title: str = Field(..., description="owner user ID")

    author: str = Field(..., description="name of author")

    category: str = Field(..., description="audio category")

    file_url: str = Field(..., description="cloud storage url for audio file")

    duration: Optional[int] = Field(None, description="duration in seconds", ge=0)

    file_size: Optional[int] = Field(None, description="file size in bytes", ge=0)

    created_at: datetime = Field(..., description="creation timestamps")

    updated_at: datetime = Field(..., description="last updated timestamp")

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123,
                "title": "Surah Al-Baqarah",
                "author": "Sheikh Mustafa Al-Shaybani",
                "category": "quran",
                "file_url": "https://storage.example.com/audio/abc123.mp3",
                "duration": 3600,
                "file_size": 52428800,
                "created_at": "2025-01-10T12:00:00Z",
                "updated_at": "2025-01-10T12:00:00Z",
            }
        }


class AudioLibraryResponse(BaseModel):
    """
    list of audio files on account
    """

    audios: List[AudioResponse] = Field(
        ..., description="complete list of user's audio files"
    )

    total: int = Field(..., description="total number of audio files", ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "audios": [
                    {
                        "id": 1,
                        "user_id": 123,
                        "title": "Surah Al-Baqarah",
                        "author": "Sheikh Mustafa Al-Shaybani",
                        "category": "quran",
                        "file_url": "https://storage.example.com/audio/abc123.mp3",
                        "duration": 3600,
                        "file_size": 52428800,
                        "created_at": "2025-01-10T12:00:00Z",
                        "updated_at": "2025-01-10T12:00:00Z",
                    },
                    {
                        "id": 2,
                        "user_id": 123,
                        "title": "Patience in Hardship",
                        "author": "Abdul Rahman Hassan - AMAU",
                        "category": "lecture",
                        "file_url": "https://storage.example.com/audio/def456.mp3",
                        "duration": 2700,
                        "file_size": 41943040,
                        "created_at": "2025-01-09T10:30:00Z",
                        "updated_at": "2025-01-09T10:30:00Z",
                    },
                ],
                "total": 2,
            }
        }


class AudioUploadResponse(BaseModel):
    """
    response after successful audio upload
    """

    id: int = Field(..., description="created audio ID")

    title: str = Field(..., description="audio title")

    file_url: str = Field(..., description="cloud storage url")

    message: str = Field(
        default="audio uploaded successfully", description="success response"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Surah Al-Baqarah",
                "file_url": "https://storage.example.com/audio/abc123.mp3",
                "message": "Audio uploaded successfully",
            }
        }


class AudioDeleteResponse(BaseModel):
    """
    response after successful audio deletion
    """

    id: int = Field(..., description="deleted audio ID")

    message: str = Field(
        default="audio deleted successfully", description="success message"
    )

    class Config:
        json_schema_extra = {
            "example": {"id": 1, "message": "audio deleted successfully"}
        }


class ErrorResponse(BaseModel):
    """
    standard error response format
    """

    error: str = Field(..., description="error type")
    message: str = Field(..., description="human readable error message")
    detail: Optional[str] = Field(None, description="additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "invalid audio file format",
                "detail": "only mp3 files are supported",
            }
        }


class Users(BaseModel):
    id: int
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime


class Playlists(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime


class PlaylistItems(BaseModel):
    playlist_id: int
    audio_id: int
