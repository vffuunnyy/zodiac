from zodiac.entities.dto.base import BaseDto
from zodiac.entities.dto.member import MemberDto

class TeamDto(BaseDto):
    id: str
    name: str
    description: str
    employees: list[MemberDto]
    applicants: list[MemberDto]