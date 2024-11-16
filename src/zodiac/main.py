from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from zodiac.entities.astro import PlanetPosition
from zodiac.entities.person import Profile
from zodiac.services.astology import AstroChart


# Подключение к клиенту
client = QdrantClient(host="localhost", port=6333)

astro_chart = AstroChart("2002-05-25", "07:00", 40.7128, -74.0060)
profile = Profile(
    name="Vlad",
    birth_time=astro_chart.birth_time,
    latitude=40.7128,
    longitude=-74.0060,
    planets=astro_chart.planets,
    aspects=astro_chart.aspects,
    lunar_node=astro_chart.lunar_node,
)

collection_name = "astro_profiles"

if collection_name not in client.get_collections().collections:
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=50, distance=Distance.COSINE),
    )

# Генерация вектора для профиля
vector = profile.generate_vector()

# Создание объекта для добавления в Qdrant
vector_data = {
    "id": str(profile.id),  # Уникальный ID
    "payload": {"name": profile.name, "birth_date": profile.birth_date},  # Дополнительные данные
    "vector": vector,  # Вектор, который мы генерировали
}

# Добавление данных в коллекцию
client.upsert(collection_name="astro_profiles", points=[vector_data])
