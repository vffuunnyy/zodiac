from datetime import UTC, datetime

from beanie import Document, Link
from pydantic import Field

from zodiac.entities.db.team import Team
from zodiac.entities.dto.astro import PersonalTraits
from zodiac.entities.dto.location import Location
from zodiac.entities.enums.roles import Role


class Employee(Document):
    # id: UUID = Field(default_factory=uuid4)
    full_name: str
    birth_date: datetime
    birth_place: Location
    email: str
    phone: str
    position: str
    personal_traits: PersonalTraits
    team: Link[Team] | None = None
    role: Role = Role.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
