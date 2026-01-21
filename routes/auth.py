"""
auth routes for registration, login and user management
"""

from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from schemas.user import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserWithTokenResponse,
)
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.db import get_db
from models.audio import User
from utils.auth import hash_password, verify_password
from utils.dependencies import CurrentUser
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


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="login user",
    description="authenticate user and return access token",
)
def login(credentials: UserLoginRequest, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="get current user",
    description="get the currently authenticated user profile",
)
def get_current_user_profile(current_user: CurrentUser):
    return UserResponse.model_validate(current_user)


def logout(current_user: CurrentUser):
    """
    jwt tokens are stateless, logout hapens client-side by deleting token
    this endpoint exists for consistencey and to verify the token is valid before logging out
    """

    return {
        "message": "successfully logged out",
        "detail": "please delete the access token from client storage",
    }
