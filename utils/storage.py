"""
local file storage for now
TODO: S3 storage
"""

import os
import shutil
import boto3
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
import uuid
from mutagen.mp3 import MP3

# AWS Configuration
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "eu-north-1")
AWS_S3_BUCKET = os.environ.get("AWS_S3_BUCKET")

# validate aws config
if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET]):
    raise RuntimeError("aws credentials not configured. check .env file")

s3_client = boto3.client(
    "s3",
    aws_access_key=AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

UPLOAD_DIR = Path("uploads/audio")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp3"}


def validate_audio_file(file: UploadFile) -> None:
    """
    checking file extension is .mp3 and content type is audio/mpeg
    """
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"invalid file type. only mp3 files are allowed. got: {file_ext}",
        )

    if file.content_type not in ["audio/mpeg", "audio/mp3"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"invalid content type. expected audio/mpeg, got: {file.content_type}",
        )


def save_audio_file(file: UploadFile, user_id: int) -> tuple[str, int, int]:
    try:
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # make directory for the user
        user_dir = UPLOAD_DIR / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        file_path = user_dir / unique_filename

        # save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_path.stat().st_size

        # get audio duration from mp3 metadata
        duration = None
        try:
            audio = MP3(file_path)
            duration = int(audio.info.length)
        except Exception as e:
            print(f"warning: could not extract duration: {e}")

        file_url = str(file_path)

        return file_url, duration, file_size

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to save file: {str(e)}",
        )


def delete_audio_file(file_url: str) -> None:
    try:
        file_path = Path(file_url)
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"warning: failed to delete file {file_url}: {e}")
