# location_resolver.py

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
import time

geolocator = Nominatim(user_agent="urban_insecurity_observer")


def geocode_place(query: str) -> dict | None:
    """
    Geocodifica un lugar usando OpenStreetMap (Nominatim)
    """
    try:
        location = geolocator.geocode(query, timeout=10)

        # Evitar bloqueo por rate limit
        time.sleep(1)

        if location:
            return {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": location.address,
                "confidence": 0.8
            }

    except GeocoderServiceError:
        return None

    return None


def resolve_location(candidates: list) -> dict:
    """
    Intenta geocodificar múltiples candidatos
    de mayor a menor precisión
    """

    for candidate in candidates:
        query = f"{candidate['name']}, {candidate['city']}, {candidate['country']}"
        result = geocode_place(query)

        if result:
            return {
                **candidate,
                **result
            }

    return {
        "error": "No se pudo geolocalizar",
        "confidence": 0.0
    }
