
from zodiac.entities.dto.base import BaseDto


class Location(BaseDto):
    name: str
    latitude: float
    longitude: float