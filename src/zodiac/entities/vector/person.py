from datetime import datetime
from uuid import UUID, uuid4

import numpy as np

from pydantic import BaseModel, Field

from zodiac.entities.astro import ASPECT_RANGES, Aspect, LunarNode, PlanetPosition


class Profile(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    birth_time: datetime
    latitude: float
    longitude: float
    planets: list[PlanetPosition]
    aspects: list[Aspect]
    lunar_node: LunarNode

    def generate_vector(self) -> list[float]:
        """
        Генерируем вектор для данного профиля на основе планет, аспектов и лунного узла.
        """
        vector = []

        for planet in self.planets:
            sign_index = self.get_sign_index(planet.sign)
            vector.extend([planet.degree, sign_index, planet.house])

        for aspect in self.aspects:
            aspect_score = self.get_aspect_score(aspect)
            vector.extend([aspect_score, aspect.angle])

        lunar_node_score = self.get_lunar_node_score(self.lunar_node.element)
        vector.extend([self.lunar_node.degree, lunar_node_score])

        vector = np.array(vector)
        normalized_vector = np.pad(vector, (0, 50 - len(vector)), mode="constant")

        return normalized_vector.tolist()

    def get_sign_index(self, sign: str) -> int:
        """
        Получаем индекс знака зодиака
        """
        zodiac_signs = [
            "Овен",
            "Телец",
            "Близнецы",
            "Рак",
            "Лев",
            "Дева",
            "Весы",
            "Скорпион",
            "Стрелец",
            "Козерог",
            "Водолей",
            "Рыбы",
        ]
        return zodiac_signs.index(sign)

    def get_aspect_score(self, aspect: Aspect) -> float:
        """
        Получаем балл аспекта на основе его типа и угла.
        """
        for (low, high), aspect_name, score in ASPECT_RANGES:
            if aspect.aspect == aspect_name and low <= aspect.angle <= high:
                return score
        return 0.0

    def get_lunar_node_score(self, element: str) -> float:
        """
        Получаем значение элемента для лунного узла
        """
        elements = {"Огонь": 0, "Земля": 1, "Воздух": 2, "Вода": 3}
        return elements.get(element, 0)
