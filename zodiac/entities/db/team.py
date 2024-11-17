from datetime import UTC, datetime
from typing import TYPE_CHECKING

from beanie import BackLink, Document
from pydantic import Field


if TYPE_CHECKING:
    from zodiac.entities.db.employee import Employee


class Team(Document):
    name: str
    description: str
    employees: list[BackLink["Employee"]] = Field(default_factory=list, original_field="team") # type: ignore
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
