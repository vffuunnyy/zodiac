from datetime import datetime

import astropy.units as u

from astropy.coordinates import (
    AltAz,
    EarthLocation,
    GeocentricTrueEcliptic,
    SkyCoord,
    get_body,
    solar_system_ephemeris,
)
from astropy.time import Time

from zodiac.entities.astro import (
    ASPECT_RANGES,
    Aspect,
    CompatibilityAspect,
    HousePosition,
    LunarNode,
    PlanetPosition,
)


solar_system_ephemeris.set("jpl")


class AstroChart:
    def __init__(self, birth_date: str, birth_time: str, latitude: float, longitude: float):
        self.birth_time = datetime.strptime(
            f"{self.birth_date} {self.birth_time} +0000", "%Y-%m-%d %H:%M %z"
        )
        self.time = Time(self.birth_time)
        self.latitude = latitude
        self.longitude = longitude
        self.location = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg, height=0 * u.m)
        self.ascendant = self.calculate_ascendant()
        self.houses = self.calculate_houses()
        self.planets = self.calculate_planet_positions()
        self.assign_planets_to_houses()
        self.aspects = self.calculate_aspects()
        self.lunar_node = self.calculate_lunar_nodes()

    def get_zodiac_sign(self, degree: float) -> str:
        signs = [
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
        index = int(degree // 30)
        return signs[index]

    def get_house(self, degree: float) -> int:
        for i in range(12):
            start = (self.ascendant + i * 30) % 360
            end = (start + 30) % 360
            if start < end:
                if start <= degree < end:
                    return i + 1
            elif degree >= start or degree < end:
                return i + 1
        return 12

    def calculate_planet_positions(self) -> list[PlanetPosition]:
        planet_names = [
            "sun",
            "moon",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "uranus",
            "neptune",
        ]
        planets_positions = []
        for planet in planet_names:
            body = get_body(planet, self.time, self.location)
            ecliptic = body.transform_to(GeocentricTrueEcliptic(equinox=self.time))
            degree = ecliptic.lon.degree % 360
            sign = self.get_zodiac_sign(degree)
            planets_positions.append(
                PlanetPosition(
                    name=planet.capitalize(),
                    degree=degree,
                    sign=sign,
                    house=0,  # Будет назначен позже
                )
            )
        return planets_positions

    def calculate_ascendant(self) -> float:
        altaz_frame = AltAz(obstime=self.time, location=self.location)
        east = SkyCoord(az=90 * u.deg, alt=0 * u.deg, frame=altaz_frame)
        equatorial = east.transform_to("icrs")
        ecliptic = equatorial.transform_to(GeocentricTrueEcliptic(equinox=self.time))
        return ecliptic.lon.degree % 360

    def calculate_houses(self) -> list[HousePosition]:
        houses = []
        for i in range(1, 13):
            house_degree = (self.ascendant + (i - 1) * 30) % 360
            sign = self.get_zodiac_sign(house_degree)
            houses.append(HousePosition(name=f"House {i}", degree=house_degree, sign=sign))
        return houses

    def assign_planets_to_houses(self):
        for planet in self.planets:
            planet.house = self.get_house(planet.degree)

    def calculate_aspects(self) -> list[Aspect]:
        aspects = []
        for i, p1 in enumerate(self.planets):
            for p2 in self.planets[i + 1 :]:
                angle = abs(p1.degree - p2.degree)
                angle = angle if angle <= 180 else 360 - angle
                aspect = self.determine_aspect(angle)
                if aspect:
                    aspects.append(
                        Aspect(
                            planet1=p1.name,
                            planet2=p2.name,
                            aspect=aspect,
                            angle=angle,
                            house1=p1.house,
                            house2=p2.house,
                        )
                    )
        return aspects

    def determine_aspect(self, angle: float) -> str:
        for (low, high), aspect, _ in ASPECT_RANGES:
            if low <= angle <= high:
                return aspect
        return None

    def calculate_lunar_nodes(self) -> LunarNode:
        sun = get_body("sun", self.time, self.location).transform_to(
            GeocentricTrueEcliptic(equinox=self.time)
        )
        moon = get_body("moon", self.time, self.location).transform_to(
            GeocentricTrueEcliptic(equinox=self.time)
        )
        node_pos = (moon.lon.degree - sun.lon.degree + 180) % 360
        element = self.get_zodiac_element(node_pos)
        return LunarNode(degree=node_pos, element=element)

    def get_zodiac_element(self, longitude: float) -> str:
        elements = ["Огонь", "Земля", "Воздух", "Вода"]
        index = int(longitude // 30) % 4
        return elements[index]

    def calculate_houses(self) -> list[HousePosition]:
        return [
            HousePosition(
                name=f"House {i}",
                degree=(self.ascendant + (i - 1) * 30) % 360,
                sign=self.get_zodiac_sign((self.ascendant + (i - 1) * 30) % 360),
            )
            for i in range(1, 13)
        ]

    def calculate_compatibility_score(self, aspects: list[CompatibilityAspect]) -> float:
        if not aspects:
            return 0

        # Суммируем баллы аспектов с их влиянием
        total_score = sum(aspect.score for aspect in aspects)

        # Для расчёта максимального возможного балла можно использовать количество аспектов,
        # каждый из которых имеет максимальный вес.
        max_possible_score = sum(aspect[2] for aspect in ASPECT_RANGES)

        # Нормализуем общий балл к шкале [0, 100] (в процентах)
        return (total_score / max_possible_score) * 100

    def calculate_compatibility(self, other: "AstroChart") -> list[CompatibilityAspect]:
        compatibility_aspects = []

        emotional_score = self.calculate_aspect_score("moon", "venus", other)
        compatibility_aspects.append(
            CompatibilityAspect(
                name="Эмоциональная совместимость",
                score=emotional_score,
                description="Оценка способности работать вместе, удовлетворяя эмоциональные потребности.",
            )
        )

        intellectual_score = self.calculate_aspect_score("mercury", "saturn", other)
        compatibility_aspects.append(
            CompatibilityAspect(
                name="Интеллектуальная совместимость",
                score=intellectual_score,
                description="Способность решать задачи, обмениваться идеями и работать над проектами.",
            )
        )

        goals_compatibility_score = self.calculate_aspect_score("jupiter", "saturn", other)
        compatibility_aspects.append(
            CompatibilityAspect(
                name="Совместимость в целях и амбициях",
                score=goals_compatibility_score,
                description="Способность работать над долгосрочными целями и амбициозными проектами.",
            )
        )

        problem_solving_score = self.calculate_aspect_score("mars", "saturn", other)
        compatibility_aspects.append(
            CompatibilityAspect(
                name="Совместимость в решении проблем",
                score=problem_solving_score,
                description="Способность справляться с трудностями и решать сложные задачи.",
            )
        )

        decision_making_score = self.calculate_aspect_score("neptune", "saturn", other)
        compatibility_aspects.append(
            CompatibilityAspect(
                name="Совместимость в принятии решений",
                score=decision_making_score,
                description="Оценка того, насколько оба человека склонны к аналогичному подходу в решении вопросов.",
            )
        )

        return compatibility_aspects

    def calculate_aspect_score(self, planet1: str, planet2: str, other: "AstroChart") -> float:
        def get_planet_position(chart, planet):
            return next((p for p in chart.planets if p.name.lower() == planet), None)

        p1 = get_planet_position(self, planet1)
        p2 = get_planet_position(other, planet2)

        if not p1 or not p2:
            return 0.0

        angle = abs(p1.degree - p2.degree)
        angle = angle if angle <= 180 else 360 - angle

        aspect = self.determine_aspect(angle)
        if not aspect:
            return 0.0

        # Плавная шкала для аспекта, степень близости
        max_angle = 180  # максимальное значение угла для аспектов
        distance_factor = 1 - (
            angle / max_angle
        )  # Нормируем на диапазон [0, 1], где 1 - идеально совпадающий аспект

        # Влияние аспекта на совместимость
        for (low, high), aspect_name, score in ASPECT_RANGES:
            if aspect == aspect_name and low <= angle <= high:
                # Возвращаем плавный результат, учитывая степень близости аспекта
                return score * distance_factor  # Умножаем на фактор близости

        return 0.0


if __name__ == "__main__":
    astro_chart_1 = AstroChart("1990-01-01", "12:00", 40.7128, -74.0060)
    astro_chart_2 = AstroChart("1990-01-01", "12:00", 40.7128, -74.0060)
    # astro_chart_2 = AstroChart("1992-05-03", "15:00", 34.0522, -118.2437)

    compatibility = astro_chart_1.calculate_compatibility(astro_chart_2)
    for aspect in compatibility:
        print(aspect)

    score = astro_chart_1.calculate_compatibility_score(compatibility)
    print(f"Total compatibility score: {score}")
