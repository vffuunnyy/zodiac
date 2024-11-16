from datetime import datetime
from uuid import UUID, uuid4
from beanie import BackLink, Document, Indexed

from typing import TYPE_CHECKING, Optional

from pydantic import Field

from zodiac.entities.astro import AstroData
from zodiac.entities.enums.roles import Role
from zodiac.entities.location import Location

if TYPE_CHECKING:
    from zodiac.entities.team import Team


class Employee(Document):
    id: UUID = Field(default_factory=uuid4)
    full_name: str
    birth_date: datetime
    birth_place: Location
    email: str
    phone: str
    position: str
    astro: AstroData
    team: Optional[BackLink[Team]]
    role: Role = Role.PENDING
    created_at: datetime    
    updated_at: datetime