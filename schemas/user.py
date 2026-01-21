from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(
        ..., description="user email address", examples=["me@mail.com"]
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="password min 8 characters",
        examples=["passwording!"],
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters long")

        return v

    class Config:
        json_schema_extra = {
            "example": {"email": "me@mail.com", "passoword": "passwording!"}
        }


class TokenResponse(BaseModel):
    """
    response after successful login
    """

    access_token: str = Field(..., description="jwt access token")

    token_type: str = Field(default="bearer", description="token type always bearer")

    expires_in: int = Field(..., description="token expiration time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }


class UserResponse(BaseModel):
    """
    user data response should never include password
    """

    id: int = Field(..., description="user id")

    email: str = Field(..., description="user email")

    created_at: datetime = Field(..., description="account creation time")

    updated_at: datetime = Field(..., description="last update time")

    class Config:
        from_attributes = True
        # allows db_user.id, db_user.name
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "me@email.com",
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z",
            }
        }


class UserWithTokenResponse:
    """
    reseponse after registration, user and token
    """

    useer: UserResponse
    access_token: str
    token_type: str = "bearer"
    expires_in: int

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": 1,
                    "email": "me@mail.com",
                    "created_at": "2025-01-15T10:30:00Z",
                    "updated_at": "2025-01-15T10:30:00Z",
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }
