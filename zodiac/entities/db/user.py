import datetime
from beanie import Document
from pydantic import Field

from zodiac.entities.enums.roles import Role


class User(Document):
    email: str = Field(..., min_length=3, max_length=320)
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=128)
    
    created_at: datetime.datetime
    updated_at: datetime.datetime
