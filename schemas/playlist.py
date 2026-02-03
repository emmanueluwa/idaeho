from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PlaylistCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="playlist name")


class PlaylistUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class PlaylistItemAdd(BaseModel):
    audio_id: int = Field(..., description="audio file id to add")


class AudioInPlaylist(BaseModel):
    id: int
    title: str
    author: str
    duration: Optional[int]
    file_size: Optional[int]
    position: int
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlaylistResponse(BaseModel):
    id: int
    user_id: int
    name: str
    audio_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlaylistDetailResponse(BaseModel):
    id: int
    user_id: int
    name: str
    audio_items: List[AudioInPlaylist]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlaylistListResponse(BaseModel):
    playlists: List[PlaylistResponse]
    total: int
