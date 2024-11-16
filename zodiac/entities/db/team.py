from datetime import datetime
from beanie import Link, Document

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zodiac.entities.db.employee import Employee


class Team(Document):
    name: str
    description: str
    employees: list[Link["Employee"]]
    created_at: datetime
    updated_at: datetime