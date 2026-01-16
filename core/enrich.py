from core.location_inference import infer_location
from core.geocoding import geocode_place
from core.validation import calculate_confidence

def build_queries(candidate: dict) -> list[str]:
    name = candidate["name"]
    city = candidate["city"]
    country = "Ecuador"

    queries = []

    if candidate["place_type"] == "barrio":
        queries.append(f"barrio {name}, {city}, {country}")
        queries.append(f"{name}, centro histórico, {city}, {country}")
        queries.append(f"centro histórico, {city}, {country}")

    elif candidate["place_type"] == "calle":
        queries.append(f"calle {name}, {city}, {country}")
        queries.append(f"{name}, {city}, {country}")

    else:
        queries.append(f"{name}, {city}, {country}")

    queries.append(f"{city}, {country}")

    return queries


def enrich_text(text: str) -> dict:
    inference = infer_location(text)

    for candidate in inference["location_candidates"]:
        queries = build_queries(candidate)

        for query in queries:
            geo = geocode_place(query)
            if not geo:
                continue

            confidence = calculate_confidence(candidate, geo)

            return {
                "incident_types": inference["incident_types"],
                "location_name": candidate["name"],
                "city": candidate["city"],
                "latitude": geo["latitude"],
                "longitude": geo["longitude"],
                "precision": candidate["precision"],
                "place_type": candidate["place_type"],
                "confidence": confidence,
                "reasoning": candidate["reasoning"]
            }

    return {"error": "No se pudo geolocalizar", "confidence": 0.0}
