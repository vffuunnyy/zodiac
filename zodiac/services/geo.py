from fastapi import HTTPException
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="astro_api")


def get_coordinates_by_city_name(city_name: str):
    location = geolocator.geocode(city_name)
    if not location:
        raise HTTPException(status_code=404, detail=f"Coordinates for '{city_name}' not found.")
    return location.latitude, location.longitude
