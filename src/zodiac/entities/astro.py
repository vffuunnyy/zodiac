from enum import StrEnum

from pydantic import BaseModel


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


ASPECT_RANGES = [
    # ((min_degree, max_degree), aspect_name, aspect_score)
    ((0, 8), AspectName.SOEDINENIE, 100.0),
    ((28, 32), AspectName.POLUSEXTIL, 20.0),
    ((43, 47), AspectName.POLUKVADRAT, 10.0),
    ((58, 62), AspectName.SEPTIL, 5.0),
    ((80, 100), AspectName.KVADRATURA, 50.0),
    ((115, 125), AspectName.TRIN, 80.0),
    ((134, 136), AspectName.BI_KVINTIL, 15.0),
    ((143, 147), AspectName.KVINTIL, 25.0),
    ((150, 154), AspectName.KVINKUNKS, 35.0),
    ((170, 190), AspectName.OPPOZICIYA, 70.0),
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


class CompatibilityAspect(BaseModel):
    name: str
    score: float
    description: str
    
class PersonalTraits(BaseModel):
    leadership: float  # Лидерство
    stress_resilience: float  # Стрессоустойчивость
    communication: float  # Коммуникабельность
    responsibility: float  # Ответственность
    ambition: float  # Амбициозность
    

class AstroData(BaseModel):
    planet_positions: list[PlanetPosition]
    house_positions: list[HousePosition]
    aspects: list[Aspect]
    lunar_node: LunarNode
    compatibility_aspects: list[CompatibilityAspect] | None = None
    personal_traits: PersonalTraits