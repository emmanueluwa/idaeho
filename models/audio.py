"""
audio models - sqlAlchemy orm models for database tables
"""

from database.db import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Interval
from sqlalchemy.sql import func
from datetime import datetime, timedelta


class AudioCategory(enum.Enum):
    QURAN = "quran"
    LECTURE = "lecture"
    REMINDER = "reminder"


class User(Base):
    """
    user model stores auth and profile data

    relationships:
        audio_files - one to many with AudioFile
        playlists = one to many with Playlist
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrememnt=True)


class Audios(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    file_url = Column(String)
    duration = Column(Interval)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
