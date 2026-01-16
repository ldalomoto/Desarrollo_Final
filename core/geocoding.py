from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

geolocator = Nominatim(
    user_agent="urban-insecurity-observer/1.0 (academic)",
    timeout=10
)

geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1,
    max_retries=2,
    swallow_exceptions=True
)

def geocode_place(place: str) -> dict | None:
    location = geocode(
        place,
        addressdetails=True,
        exactly_one=True
    )

    if not location:
        return None

    return {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "address": location.address,
        "raw": location.raw
    }
