from pydantic import EmailStr

from zodiac.entities.dto.astro import AstroData
from zodiac.entities.dto.base import BaseDto
from zodiac.entities.dto.location import Location

class MemberDto(BaseDto):
    id: int
    full_name: str
    birth_date: str
    birth_place: Location
    email: EmailStr
    phone: str
    position: str
    astro: AstroData