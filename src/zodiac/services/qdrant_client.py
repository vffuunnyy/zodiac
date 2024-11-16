# import numpy as np

# from qdrant_client import QdrantClient
# from qdrant_client.models import Distance, PointStruct, VectorParams


# client = QdrantClient(host="localhost", port=6333)

# # Создание коллекции, если она не существует
# collection_name = "astro_profiles"

# if collection_name not in client.get_collections().collections:
#     client.create_collection(
#         collection_name=collection_name,
#         vectors_config=VectorParams(size=128, distance=Distance.COSINE),
#     )


# # Функция для создания вектора профиля
# def create_profile_vector(profile):
#     vector = []

#     planet_positions = {planet: position.degree for planet, position in profile.planets.items()}
#     vector.extend(list(planet_positions.values()))

#     aspect_scores = [aspect.score for aspect in profile.aspects]
#     vector.extend(aspect_scores)

#     lunar_node_position = profile.lunar_node.degree
#     vector.append(lunar_node_position)

#     vector = np.array(vector)
#     vector = vector / np.linalg.norm(vector)

#     return vector


# # Пример использования
# profile1_vector = create_profile_vector(profile1)
# profile2_vector = create_profile_vector(profile2)


# # Добавляем вектор в Qdrant
# def upsert_profile_to_qdrant(client, collection_name, profile_id, vector):
#     point = PointStruct(id=profile_id, vector=vector.tolist())  # Преобразуем вектор в список
#     client.upsert(collection_name=collection_name, points=[point])


# # Добавляем профили в Qdrant
# upsert_profile_to_qdrant(client, collection_name, profile_id=1, vector=profile1_vector)
# upsert_profile_to_qdrant(client, collection_name, profile_id=2, vector=profile2_vector)
