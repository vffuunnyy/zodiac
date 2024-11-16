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

from zodiac.entities.dto.astro import (
    ASPECTS,
    Aspect,
    AspectName,
    CompatibilityTraits,
    HousePosition,
    LunarNode,
    PersonalTraits,
    PlanetPosition,
)

solar_system_ephemeris.set("jpl")

SIGNS = [
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

ELEMENTS = ["Огонь", "Земля", "Воздух", "Вода"]

PLANET_NAMES = [
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
]


class AstroChart:
    def __init__(self, birth_time: datetime, latitude: float, longitude: float):
        self.birth_time = birth_time
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
        degree = degree % 360
        index = int(degree // 30)
        return SIGNS[index]


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
        planets_positions = []
        for planet in PLANET_NAMES:
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
        return [
            HousePosition(
                name=f"House {i}",
                degree=(self.ascendant + (i - 1) * 30) % 360,
                sign=self.get_zodiac_sign((self.ascendant + (i - 1) * 30) % 360),
            )
            for i in range(1, 13)
        ]

    def assign_planets_to_houses(self):
        for planet in self.planets:
            planet.house = self.get_house(planet.degree)

    def calculate_aspects(self) -> list[Aspect]:
        aspects = []
        for i, p1 in enumerate(self.planets):
            for p2 in self.planets[i + 1 :]:
                angle = abs(p1.degree - p2.degree)
                angle = angle if angle <= 180 else 360 - angle
                aspect, base_score, orb = self.determine_aspect(angle)

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

    def determine_aspect(self, angle: float) -> tuple[str, float, float]:
        for aspect in ASPECTS:
            exact_angle = aspect['angle']
            max_orb = aspect['orb']
            orb = abs(angle - exact_angle)
            if orb <= max_orb:
                return aspect['name'], aspect['score'], orb
        return None, 0, None


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
        index = int(longitude // 30) % 4
        return ELEMENTS[index]

    def calculate_compatibility(self, other: "AstroChart") -> "CompatibilityTraits":
        def normalize_score(score):
            return max(0, min(score, 100))

        emotional_score = normalize_score(
            self.calculate_aspect_score("moon", "venus", other)
        )
        intellectual_score = normalize_score(
            self.calculate_aspect_score("mercury", "saturn", other)
        )
        goals_compatibility_score = normalize_score(
            self.calculate_aspect_score("jupiter", "saturn", other)
        )
        problem_solving_score = normalize_score(
            self.calculate_aspect_score("mars", "saturn", other)
        )
        decision_making_score = normalize_score(
            self.calculate_aspect_score("neptune", "saturn", other)
        )

        return CompatibilityTraits(
            emotional_compatibility=emotional_score,
            intellectual_compatibility=intellectual_score,
            goals_compatibility=goals_compatibility_score,
            problem_solving_compatibility=problem_solving_score,
            decision_making_compatibility=decision_making_score,
        )

    def calculate_aspect_score(self, planet1: str, planet2: str, other: "AstroChart") -> float:
        def get_planet_position(chart, planet):
            return next((p for p in chart.planets if p.name.lower() == planet.lower()), None)

        p1 = get_planet_position(self, planet1)
        p2 = get_planet_position(other, planet2)

        if not p1 or not p2:
            return 0.0

        angle = abs(p1.degree - p2.degree)
        angle = angle if angle <= 180 else 360 - angle

        aspect, base_score, orb = self.determine_aspect(angle)
        if not aspect:
            return 0.0

        max_orb = next(a['orb'] for a in ASPECTS if a['name'] == aspect)
        adjusted_score = base_score * ((max_orb - orb) / max_orb)
        adjusted_score = max(0, adjusted_score)
        return adjusted_score



    def calculate_personal_traits(self) -> PersonalTraits:
        traits = {
            "leadership": 0,
            "stress_resilience": 0,
            "communication": 0,
            "responsibility": 0,
            "ambition": 0,
        }

        sun = next((p for p in self.planets if p.name.lower() == "sun"), None)
        mars = next((p for p in self.planets if p.name.lower() == "mars"), None)
        if sun:
            traits["leadership"] += self.influence_score(
                sun.degree, ["Овен", "Лев", "Стрелец"], [1, 10]
            )
        if mars:
            traits["leadership"] += self.influence_score(
                mars.degree, ["Овен", "Скорпион"], [1, 11]
            )

        saturn = next((p for p in self.planets if p.name.lower() == "saturn"), None)
        if saturn:
            traits["stress_resilience"] += self.influence_score(
                saturn.degree, ["Телец", "Дева", "Козерог"], [6, 10]
            )

        mercury = next((p for p in self.planets if p.name.lower() == "mercury"), None)
        venus = next((p for p in self.planets if p.name.lower() == "venus"), None)
        if mercury:
            traits["communication"] += self.influence_score(
                mercury.degree, ["Близнецы", "Весы", "Водолей"], [3, 7]
            )
        if venus:
            traits["communication"] += self.influence_score(
                venus.degree, ["Близнецы", "Весы"], [3, 7]
            )

        if saturn:
            traits["responsibility"] += self.influence_score(
                saturn.degree, ["Козерог", "Дева"], [6, 10]
            )

        jupiter = next((p for p in self.planets if p.name.lower() == "jupiter"), None)
        pluto = next((p for p in self.planets if p.name.lower() == "pluto"), None)
        if jupiter:
            traits["ambition"] += self.influence_score(
                jupiter.degree, ["Стрелец", "Лев"], [9, 10]
            )
        if pluto:
            traits["ambition"] += self.influence_score(
                pluto.degree, ["Скорпион", "Козерог"], [8, 10]
            )

        for aspect in self.aspects:
            if aspect.aspect in {AspectName.TRIN, AspectName.SOEDINENIE}:
                traits["leadership"] += (
                    5 if "sun" in {aspect.planet1.lower(), aspect.planet2.lower()} else 0
                )
                traits["communication"] += (
                    5 if "mercury" in {aspect.planet1.lower(), aspect.planet2.lower()} else 0
                )
                traits["ambition"] += (
                    5 if "mars" in {aspect.planet1.lower(), aspect.planet2.lower()} else 0
                )
            if aspect.aspect == AspectName.KVADRATURA:
                traits["stress_resilience"] = max(0, traits["stress_resilience"] - 5)  # Минимум 0

        traits = {k: max(0, v) for k, v in traits.items()}  # Не меньше 0

        total = sum(traits.values())
        if total > 0:
            traits = {k: (v / total) * 100 for k, v in traits.items()}

        return PersonalTraits(
            leadership=traits["leadership"],
            stress_resilience=traits["stress_resilience"],
            communication=traits["communication"],
            responsibility=traits["responsibility"],
            ambition=traits["ambition"],
        )

    def influence_score(
        self, degree: float, relevant_signs: list[str], houses: list[int], orb: float = 5.0
    ) -> float:
        """
        Рассчитывает влияние планеты на основе положения в знаке, доме и аспектах.

        :param degree: Положение планеты в градусах (0–360).
        :param relevant_signs: Знаки, которые усиливают влияние.
        :param houses: Дома, которые усиливают влияние.
        :param orb: Допустимая погрешность (орбис) для аспектов.
        :return: Итоговый балл влияния.
        """
        score = 0

        sign = self.get_zodiac_sign(degree)
        house = self.get_house(degree)

        if sign in relevant_signs:
            score += 10

        if house in houses:
            score += 10

        planet_name = next((p.name for p in self.planets if p.degree == degree), None)
        if not planet_name:
            return score

        for aspect in self.aspects:
            if planet_name.lower() not in {aspect.planet1.lower(), aspect.planet2.lower()}:
                continue

            aspect_def = next((a for a in ASPECTS if a['name'] == aspect.aspect), None)
            if not aspect_def:
                continue

            base_score = aspect_def['score']
            max_orb = aspect_def['orb']

            orb = abs(aspect.angle - aspect_def['angle'])
            if orb > max_orb:
                continue

            adjusted_score = base_score * ((max_orb - orb) / max_orb)
            adjusted_score = max(0, adjusted_score)

            score += adjusted_score / 10

        elements_score = {"Огонь": 5, "Земля": 3, "Воздух": 4, "Вода": 2}
        element = self.get_zodiac_element(degree)
        if element in elements_score:
            score += elements_score[element]

        return score
    
    def calculate_group_compatibility(
        self, others: list["AstroChart"]
    ) -> CompatibilityTraits:
        total_compatibility = CompatibilityTraits(
            emotional_compatibility=0.0,
            intellectual_compatibility=0.0,
            goals_compatibility=0.0,
            problem_solving_compatibility=0.0,
            decision_making_compatibility=0.0,
        )
        num_others = len(others)
        if num_others == 0:
            return total_compatibility  # Return zeroed traits if no others

        for other in others:
            compatibility = self.calculate_compatibility(other)
            total_compatibility.emotional_compatibility += compatibility.emotional_compatibility
            total_compatibility.intellectual_compatibility += compatibility.intellectual_compatibility
            total_compatibility.goals_compatibility += compatibility.goals_compatibility
            total_compatibility.problem_solving_compatibility += compatibility.problem_solving_compatibility
            total_compatibility.decision_making_compatibility += compatibility.decision_making_compatibility

        # Calculate average
        average_compatibility = CompatibilityTraits(
            emotional_compatibility=total_compatibility.emotional_compatibility / num_others,
            intellectual_compatibility=total_compatibility.intellectual_compatibility / num_others,
            goals_compatibility=total_compatibility.goals_compatibility / num_others,
            problem_solving_compatibility=total_compatibility.problem_solving_compatibility / num_others,
            decision_making_compatibility=total_compatibility.decision_making_compatibility / num_others,
        )

        return average_compatibility

    def calculate_individual_compatibilities(
        self, others: list["AstroChart"]
    ) -> list[CompatibilityTraits]:
        compatibilities = []
        for other in others:
            compatibility = self.calculate_compatibility(other)
            compatibilities.append(compatibility)
        return compatibilities
    
    @staticmethod
    def calculate_compatibility_score(compatibility: CompatibilityTraits) -> float:
        """
        Рассчитывает общую совместимость на основе пяти критериев по 100-балльной шкале.
        """
        scores = [
            compatibility.emotional_compatibility,
            compatibility.intellectual_compatibility,
            compatibility.goals_compatibility,
            compatibility.problem_solving_compatibility,
            compatibility.decision_making_compatibility,
        ]
        return sum(scores) / 5



if __name__ == "__main__":
    birth_time = datetime(2002, 5, 25, 13, 0, 0)
    latitude, longitude = 56.484645, 84.947649
    chart = AstroChart(birth_time, latitude, longitude)

    print("Ascendant:", chart.get_zodiac_sign(chart.ascendant))
    for planet in chart.planets:
        print(f"{planet.name}: {planet.sign} {planet.degree:.2f}° in house {planet.house}")
    for house in chart.houses:
        print(f"{house.name}: {house.sign} {house.degree:.2f}°")
    for aspect in chart.aspects:
        print(
            f"{aspect.planet1} {aspect.aspect.value} {aspect.planet2} ({aspect.angle:.2f}°) in houses {aspect.house1} and {aspect.house2}"
        )
    print(f"Lunar node: {chart.lunar_node.element} {chart.lunar_node.degree:.2f}°")

    other_birth_time = datetime(2002, 3, 24, 0, 0, 0)
    other_latitude, other_longitude = 56.484645, 84.947649
    other_chart = AstroChart(other_birth_time, other_latitude, other_longitude)

    compatibility = chart.calculate_compatibility(other_chart)
    print("Emotional compatibility:", compatibility.emotional_compatibility)
    print("Intellectual compatibility:", compatibility.intellectual_compatibility)
    print("Goals compatibility:", compatibility.goals_compatibility)
    print("Problem solving compatibility:", compatibility.problem_solving_compatibility)
    print("Decision making compatibility:", compatibility.decision_making_compatibility)

    print("Compatibility score:", AstroChart.calculate_compatibility_score(compatibility))

    traits = chart.calculate_personal_traits()
    print("Leadership:", traits.leadership)
    print("Stress resilience:", traits.stress_resilience)
    print("Communication:", traits.communication)
    print("Responsibility:", traits.responsibility)
    print("Ambition:", traits.ambition)