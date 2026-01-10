from typing import Annotated, List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class VersesHistory(BaseModel):
    user_query: str
    answer_summary: str
    verses_returned: str
    themes: str
    created_at: datetime
    id: int

    class Config:
        from_attributes = True


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
