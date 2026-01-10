from database.db import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Interval
from sqlalchemy.sql import func
from datetime import datetime, timedelta


class Audios(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    file_url = Column(String)
    duration = Column(Interval)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
