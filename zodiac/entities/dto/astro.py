from enum import StrEnum

from pydantic import BaseModel

from zodiac.entities.dto.base import BaseDto


class PlanetPosition(BaseModel):
    name: str
    degree: float
    sign: str
    house: int


class HousePosition(BaseModel):
    name: str
    degree: float
    sign: str


class AspectName(StrEnum):
    SOEDINENIE = "Соединение"
    POLUSEXTIL = "Полусекстиль"
    POLUKVADRAT = "Полуквадрат"
    SEPTIL = "Септиль"
    KVADRATURA = "Квадратура"
    TRIN = "Трин"
    BI_KVINTIL = "Би-квинтиль"
    KVINTIL = "Квинтиль"
    KVINKUNKS = "Квинкункс"
    OPPOZICIYA = "Оппозиция"


ASPECTS = [
    {'name': AspectName.SOEDINENIE, 'angle': 0, 'orb': 8, 'score': 100.0},
    {'name': AspectName.POLUSEXTIL, 'angle': 30, 'orb': 2, 'score': 20.0},
    {'name': AspectName.POLUKVADRAT, 'angle': 45, 'orb': 2, 'score': 10.0},
    {'name': AspectName.SEPTIL, 'angle': 51.43, 'orb': 1, 'score': 5.0},
    {'name': AspectName.KVINTIL, 'angle': 72, 'orb': 2, 'score': 25.0},
    {'name': AspectName.KVADRATURA, 'angle': 90, 'orb': 8, 'score': 50.0},
    {'name': AspectName.TRIN, 'angle': 120, 'orb': 8, 'score': 80.0},
    {'name': AspectName.BI_KVINTIL, 'angle': 144, 'orb': 2, 'score': 15.0},
    {'name': AspectName.KVINKUNKS, 'angle': 150, 'orb': 2, 'score': 35.0},
    {'name': AspectName.OPPOZICIYA, 'angle': 180, 'orb': 8, 'score': 70.0},
]



class Aspect(BaseModel):
    planet1: str
    planet2: str
    aspect: AspectName
    angle: float
    house1: int
    house2: int


class LunarNode(BaseModel):
    degree: float
    element: str


class PersonalTraits(BaseDto):
    leadership: float  # Лидерство
    stress_resilience: float  # Стрессоустойчивость
    communication: float  # Коммуникабельность
    responsibility: float  # Ответственность
    ambition: float  # Амбициозность


class CompatibilityTraits(BaseDto):
    emotional_compatibility: float  # Эмоциональная совместимость
    intellectual_compatibility: float  # Интеллектуальная совместимость
    goals_compatibility: float  # Совместимость целей
    problem_solving_compatibility: float  # Совместимость в решении проблем
    decision_making_compatibility: float  # Совместимость в принятии решений


class AstroData(BaseDto):
    personal_traits: PersonalTraits
    compatibility: CompatibilityTraits
