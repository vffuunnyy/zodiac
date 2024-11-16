from pydantic import BaseModel

from zodiac.entities.dto.member import MemberDto

class TeamDto(BaseModel):
    id: str
    name: str
    description: str
    employees: list[MemberDto]
    applicants: list[MemberDto]