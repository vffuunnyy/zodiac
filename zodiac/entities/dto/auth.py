from pydantic import EmailStr, Field

from zodiac.entities.dto.base import BaseDto


class AuthRequest(BaseDto):
    email: EmailStr
    password: str


class AuthResponse(BaseDto):
    success: bool
    access_token: str | None = None


class UserCreateRequest(BaseDto):
    email: EmailStr
    password: str
    full_name: str = Field(..., min_length=1, max_length=128, alias="fullName")


class UserCreateResponse(BaseDto):
    success: bool
    message: str | None = None
