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
    pass
