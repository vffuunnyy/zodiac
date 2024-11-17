from typing import Optional

from zodiac.entities.dto.base import BaseDto
from zodiac.entities.dto.member import MemberDto


class TeamDto(BaseDto):
    id: str
    name: str
    description: str
    employees: Optional[list[MemberDto]] = None
    applicants: Optional[list[MemberDto]] = None


class TeamGetResponse(BaseDto):
    success: bool
    team: Optional[TeamDto] = None


class TeamCreateRequest(BaseDto):
    name: str
    description: str


class TeamCreateResponse(BaseDto):
    success: bool
    id: Optional[str] = None
    message: Optional[str] = None
