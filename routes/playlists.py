from typing import Annotated
from database.db import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.audio import AudioFile, Playlist, PlaylistItem
from schemas.playlist import (
    AudioInPlaylist,
    PlaylistCreate,
    PlaylistDetailResponse,
    PlaylistItemAdd,
    PlaylistListResponse,
    PlaylistResponse,
    PlaylistUpdate,
)
from sqlalchemy.orm import Session
from sqlalchemy import func
from utils.dependencies import CurrentUser

router = APIRouter()


@router.post(
    "/",
    response_model=PlaylistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="create playlist",
    description="create a new custom playlist",
)
def create_playlist(
    playlist_data: PlaylistCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    new_playlist = Playlist(
        user_id=current_user.id,
        name=playlist_data.name,
    )

    try:
        db.add(new_playlist)
        db.commit()
        db.refresh(new_playlist)
    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to create playlist: {str(e)}",
        )

    return PlaylistResponse(
        id=new_playlist.id,
        user_id=new_playlist.user_id,
        name=new_playlist.name,
        audio_count=0,
        created_at=new_playlist.created_at,
        updated_at=new_playlist.updated_at,
    )


@router.get(
    "/",
    response_model=PlaylistListResponse,
    summary="get users playlists",
    description="get all playlists for authenticated user",
)
def get_playlists(current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    # returns list of tuples (Playlist object, audio_count number)
    playlists = (
        db.query(Playlist, func.count(PlaylistItem.id).label("audio_count"))
        .outerjoin(PlaylistItem, Playlist.id == PlaylistItem.playlist_id)
        .filter(Playlist.user_id == current_user.id)
        .group_by(Playlist.id)
        .order_by(Playlist.created_at.desc())
        .all()
    )

    # tuple unpacking
    playlist_responses = [
        PlaylistResponse(
            id=playlist.id,
            user_id=playlist.user_id,
            name=playlist.name,
            audio_count=count,
            created_at=playlist.created_at,
            updated_at=playlist.updated_at,
        )
        for playlist, count in playlists
    ]

    return PlaylistListResponse(
        playlists=playlist_responses, total=len(playlist_responses)
    )


@router.get(
    "/{playlist_id}",
    response_model=PlaylistDetailResponse,
    summary="get playlist details",
    description="get playlist with all audio items",
)
def get_playlist(
    playlist_id: int, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
):
    playlist = (
        db.query(Playlist)
        .filter(Playlist.id == playlist_id, Playlist.user_id == current_user.id)
        .first()
    )
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="playlist not found"
        )

    items = (
        db.query(PlaylistItem, AudioFile)
        .join(AudioFile, PlaylistItem.audio_id == AudioFile.id)
        .filter(PlaylistItem.playlist_id == playlist_id)
        .order_by(PlaylistItem.order)
        .all()
    )

    audio_items = [
        AudioInPlaylist(
            id=audio.id,
            title=audio.title,
            author=audio.author,
            duration=audio.duration,
            file_size=audio.file_size,
            position=item.order,
            added_at=item.added_at,
        )
        for item, audio in items
    ]

    return PlaylistDetailResponse(
        id=playlist.id,
        user_id=playlist.user_id,
        name=playlist.name,
        audio_items=audio_items,
        created_at=playlist.created_at,
        updated_at=playlist.updated_at,
    )


@router.put(
    "/{playlist_id}",
    response_model=PlaylistResponse,
    summary="update playlist",
    description="update playlist name",
)
def update_playlist(
    playlist_id: int,
    playlist_data: PlaylistUpdate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    playlist = (
        db.query(Playlist)
        .filter(
            Playlist.id == playlist_id,
            Playlist.user_id == current_user.id,
        )
        .first()
    )
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="playlist not found"
        )

    update_data = playlist_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(playlist, field, value)

    try:
        db.commit()
        db.refresh(playlist)
    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to update playlist: {str(e)}",
        )

    audio_count = (
        db.query(func.count(PlaylistItem.id))
        .filter(PlaylistItem.playlist_id == playlist_id)
        .scalar()
    )

    return PlaylistResponse(
        id=playlist.id,
        user_id=playlist.user_id,
        name=playlist.name,
        audio_count=audio_count,
        created_at=playlist.created_at,
        updated_at=playlist.updated_at,
    )


@router.post(
    "/{playlist_id}/items",
    status_code=status.HTTP_201_CREATED,
    summary="add audio to playlist",
    description="add an audio file to playlist",
)
def add_audio_to_playlist(
    playlist_id: int,
    item_data: PlaylistItemAdd,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    playlist = (
        db.query(Playlist)
        .filter(Playlist.id == playlist_id, Playlist.user_id == current_user.id)
        .first()
    )
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="playlist not found"
        )

    # verify audio ownership
    audio = (
        db.query(AudioFile)
        .filter(
            AudioFile.id == item_data.audio_id, AudioFile.user_id == current_user.id
        )
        .first()
    )
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="audio file not found"
        )

    existing = (
        db.query(PlaylistItem)
        .filter(
            PlaylistItem.playlist_id == playlist_id,
            PlaylistItem.audio_id == item_data.audio_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="audio already in playlist"
        )

    # determine position
    if item_data.position is not None:
        position = item_data.position

    else:
        max_position = (
            db.query(func.max(PlaylistItem.order))
            .filter(PlaylistItem.playlist_id == playlist_id)
            .scalar()
        )
        position = (max_position + 1) if max_position is not None else 0

    new_item = PlaylistItem(
        playlist_id=playlist_id, audio_id=item_data.audio_id, order=position
    )

    try:
        db.add(new_item)
        db.commit()

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to add audio to playlist: {str(e)}",
        )

    return {
        "message": "Audio added to playlist",
        "playlist_id": playlist_id,
        "audio_id": item_data.audio_id,
    }


@router.delete(
    "/{playlist_id}/items/{audio_id}",
    summary="remove audio from playlist",
    description="remove an audio file from playlist",
)
def remove_audio_from_playlist(
    playlist_id: int,
    audio_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    playlist = (
        db.query(Playlist)
        .filter(Playlist.id == playlist_id, Playlist.user_id == current_user.id)
        .first()
    )
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="playlist not found"
        )

    item = (
        db.query(PlaylistItem)
        .filter(
            PlaylistItem.playlist_id == playlist_id, PlaylistItem.audio_id == audio_id
        )
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="audio not in playlist"
        )

    try:
        db.delete(item)
        db.commit()
    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to remove audio from playlist: {str(e)}",
        )

    return {"message": "audio removed from playlist"}


@router.delete(
    "/{playlist_id}",
    summary="delete playlist",
    description="delete playlist and all its items",
)
def delete_playlist(
    playlist_id: int, current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]
):
    playlist = (
        db.query(Playlist)
        .filter(Playlist.id == playlist_id, Playlist.user_id == current_user.id)
        .first()
    )
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="playlist not found"
        )

    try:
        db.delete(playlist)
        db.commit()
    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to delete playlist: {str(e)}",
        )

    return {"message": "playlist deleted successfully", "playlist_id": playlist_id}
