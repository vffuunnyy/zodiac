from datetime import datetime

from pydantic import EmailStr, Field

from zodiac.entities.dto.base import BaseDto
from zodiac.entities.dto.location import Location


class TeamCreate(BaseDto):
    name: str
    description: str


class EmployeeCreate(BaseDto):
    full_name: str = Field(..., min_length=1, max_length=128, alias="fullName")
    birth_date: datetime = Field(..., alias="birthDate")
    birth_place: Location = Field(..., alias="birthPlace")
    email: EmailStr
    phone: str
    position: str


class ApplicantCreate(EmployeeCreate):
    pass
