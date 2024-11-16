from datetime import datetime
from uuid import UUID, uuid4
from beanie import BackLink, Document, Indexed

from typing import TYPE_CHECKING, Optional

from pydantic import Field

from zodiac.entities.dto.astro import  PersonalTraits
from zodiac.entities.enums.roles import Role
from zodiac.entities.dto.location import Location

if TYPE_CHECKING:
    from zodiac.entities.db.team import Team


class Employee(Document):
    id: UUID = Field(default_factory=uuid4)
    full_name: str
    birth_date: datetime
    birth_place: Location
    email: str
    phone: str
    position: str
    personal_traits: PersonalTraits
    team: Optional[BackLink["Team"]]
    role: Role = Role.PENDING
    created_at: datetime
    updated_at: datetime
