from datetime import datetime
from typing import Optional

from pydantic import EmailStr

from zodiac.entities.dto.astro import AstroShit
from zodiac.entities.dto.base import BaseDto
from zodiac.entities.dto.location import Location
from zodiac.entities.enums.roles import Role


class MemberDto(BaseDto):
    id: str
    full_name: str
    birth_date: datetime
    birth_place: Location
    email: EmailStr
    phone: str
    position: str
    astro: AstroShit


class AddMemberRequest(BaseDto):
    full_name: str
    birth_date: datetime
    birth_place: Location
    email: EmailStr
    phone: str
    position: str
    role: Role


class AddMemberResponse(BaseDto):
    success: bool
    message: str


class GetMemberResponse(BaseDto):
    success: bool
    member: Optional[MemberDto] = None
