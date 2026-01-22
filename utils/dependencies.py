"""
fastapi dependencies for auth
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from database.db import get_db
from models.audio import User
from utils.jwt import verify_token


security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    get the current authenticated user from jwt token
    """
    token = credentials.credentials

    payload = verify_token(token)

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HttpException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invald auth credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found",
            headers={"WWW-Authenticate": "Bearee"},
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
