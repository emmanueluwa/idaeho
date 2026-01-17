import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "JWT_SECRET_KEY_PROD")
ALOGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    args:
        data to encode in token e.g {"sub": user_id}
        expires_delta is optional for custom expiration time

    returns:
        encoded jwt token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.now(datetime.timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALOGORITHM)

    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    args:
        jwt token string

    returns:
        decoded token payload
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALOGORITHM])

        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="could not validate credentials",
                headers={"WWW=Authenticate": "Bearer"},
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
