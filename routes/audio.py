from http.client import HTTPException
from typing import Annotated, Optional

from database.db import get_db
from fastapi import APIRouter, status, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from models.audio import AudioFile, UploadFile
from schemas.audio import AudioLibraryResponse, AudioResponse
from utils.dependencies import CurrentUser
from utils.storage import delete_audio_file, save_audio_file, validate_audio_file

router = APIRouter()


@router.post(
    "/upload",
    response_model=AudioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="upload audio file",
    description="upload mp3 file with metadata",
)
async def upload_audio(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(..., description="MP3 audio file"),
    title: str = Form(..., description="audio title"),
    author: str = Form(..., description="author name"),
    category: str = Form(default="quran", description="audio category"),
):
    validate_audio_file(file)

    file_url, duration, file_size = save_audio_file(file, current_user.id)

    # create db record
    new_audio = AudioFile(
        user_id=current_user.id,
        title=title,
        author=author,
        category=category,
        file_url=file_url,
        duration=duration,
        file_size=file_size,
    )

    try:
        db.add(new_audio)
        db.commit()
        db.refresh(new_audio)
    except Exception as e:
        db.rollback()
        # clean file if db insert fails
        delete_audio_file(file_url)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to save audio metadata: {str(e)}",
        )

    return AudioResponse.model_validate(new_audio)


@router.get(
    "/library",
    response_model=AudioLibraryResponse,
    summary="get users audio library",
    description="get all audio files for authenticated user",
)
def get_library(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    category: Optional[str] = None,
):
    query = db.query(AudioFile).filter(AudioFile.user_id == current_user.id)

    if category:
        query = query.filter(AudioFile.category == category)

    # alphabetical order based on author name
    query = query.ordery_by(AudioFile.author)

    audios = query.all()

    return AudioLibraryResponse(
        audios=[AudioResponse.model_validate(audio) for audio in audios],
        total=len(audios),
    )
