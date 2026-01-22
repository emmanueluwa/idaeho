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


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="user email address")

    password: str = Field(..., description="user password")


class TokenResponse(BaseModel):
    """
    response after successful login
    """

    access_token: str = Field(..., description="jwt access token")

    token_type: str = Field(default="bearer", description="token type always bearer")

    expires_in: int = Field(..., description="token expiration time in seconds")


class UserResponse(BaseModel):
    """
    user data response never includes password
    """

    id: int = Field(..., description="user id")

    email: str = Field(..., description="user email")

    created_at: datetime = Field(..., description="account creation time")

    updated_at: datetime = Field(..., description="last update time")

    class Config:
        # allows db_user.id, db_user.name
        from_attributes = True


class UserWithTokenResponse(BaseModel):
    """
    reseponse after registration, user and token
    """

    user: UserResponse
    access_token: str
    token_type: str = "bearer"
    expires_in: int
