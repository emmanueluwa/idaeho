"""
audio models - sqlAlchemy orm models for database tables
"""

from database.db import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    BigInteger,
    Text,
    ForeignKey,
    DateTime,
    Interval,
    CheckConstraint,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="user email address used for login",
    )

    password_hush = Column(
        String(255), nullable=False, comment="bcrypt hashed password"
    )

    # metadata
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="account created timestamp",
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="last update timestamp",
    )

    # relationships
    audio_files = relationship(
        "AudioFile", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )

    playlists = relationship(
        "Playlist", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )

    __table_args__ = (
        CheckConstraint(
            "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'",
            name="valid_email_format",
        ),
        Index("idx_users_email", "email"),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class AudioFile(Base):
    """
    audio file model stores audio file metadata and cloud storage references

    design principles:
        - store only metadata, not actual file data
        - cloud storage handles actual MP3 files
        - optimized for fast queries with proper indexing
    """

    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # foreign key
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="owner user id - cascades on delete",
    )

    # metadata
    title = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Audio title (e.g., Surah Al-Baqarah'')",
    )

    author = Column(String(255), nullable=False, index=True, comment="author name")

    category = Column(
        SQLEnum(AudioCategory),
        nullable=False,
        default=AudioCategory.QURAN,
        index=True,
        comment="audio category type",
    )

    description = Column(Text, nullable=True, comment="optinal audio descripton")

    # file information
    file_url = Column(Text, nullable=False, comment="S3 cloud storage url")

    duration = Column(Integer, nullable=True, comment="duration in seconds")

    file_size = Column(BigInteger, nullable=True, comment="file size in bytes")

    # metadata
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="upload timestamp",
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="last metadata update timestamp",
    )

    # relationships
    user = relationship("User", back_populates="audio_files")

    playlist_items = relationship(
        "PlaylistItem", back_populates="audio_file", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("duration > 0", name="positive_duration"),
        CheckConstraint("file_size > 0", name="positive_file_size"),
        # composite indexes
        Index("idx_audio_user_created", "user_id", "cerated_at"),
        Index("idx_audio_user_category", "user_id", "category"),
        Index("idx_audio_author", "author"),
        Index("idx_audio_title", "title"),
    )

    def __repr__(self):
        return (
            f"<AudioFile(id={self.id}, title='{self.title}', author='{self.author}')>"
        )


class Playlist(Base):
    """
    playlist model groups audio files into collections

    design principles:
        - many-to-Many relationship with AudioFile via PlaylistItem
        - supports ordering of audio files within playlist
    """

    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="owner user ID - cascades on delete",
    )

    # playlist information
    name = Column(String(255), nullable=False, comment="playlist name")

    # metadata
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="playlist creation timestamp",
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="last update timestamp",
    )

    # relationships
    user = relationship("User", back_populates="playlists")

    playlist_items = relationship(
        "PlaylistItem",
        back_populates="playlist",
        cascade="all, delete-orphan",
        order_by="PlaylistItem,order",
    )

    __table_args__ = (
        Index("idx_playlist_user", "user_id"),  # users playlists
        Index("idx_playlist_name", "name"),
    )

    def __repr__(self):
        return f"<Playlist(id={self.id}, name='{self.name}')>"


class PlaylistItem(Base):
    """
    playlist item model is a junction table for playlist and audiofile

    design principles:
        - implements Many-to-Many relationship
        - maintains order of audio files in playlist
        - prevents duplicate entries in same playlist
    """

    __tablename__ = "playlist_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    playlist_id = Column(
        Integer,
        ForeignKey("playlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="playlist id - cascades on delete",
    )

    audio_id = Column(
        Integer,
        ForeignKey("audio_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="audio file ID - cascades on delete",
    )

    order = Column(
        Integer, nullable=False, default=0, comment="position in playlist for sorting"
    )

    # metadata
    added_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="timestamp when added to playist",
    )

    # relationships
    playlist = relationship("Playlist", back_populates="playlist_items")
    audio_file = relationship("AudioFile", back_populates="playlist_items")


class Audios(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    file_url = Column(String)
    duration = Column(Interval)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
