"""
auth routes for registration, login and user management
"""

from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from schemas.user import UserRegisterRequest, UserResponse, UserWithTokenResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.db import get_db
from models.audio import User
from utils.auth import hash_password
from utils.jwt import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

router = APIRouter()


@router.post(
    "/register",
    response_model=UserWithTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="register new user",
    description="create new user account and return access token",
)
def register(user_data: UserRegisterRequest, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email already registered"
        )

    hashed_password = hash_password(user_data.password)

    new_user = User(email=user_data.email, password_hash=hashed_password)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            satus_code=status.HTTP_400_BAD_REQUEST, detail="email already registered"
        )

    access_token = create_access_token(data={"sub": str(new_user.id)})

    return UserWithTokenResponse(
        user=UserResponse.model_validate(new_user),
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # convert to seconds
    )
