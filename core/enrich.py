from core.location_inference import infer_location
from core.geocoding import geocode_place
from core.validation import calculate_confidence
from core.keyphrases import extract_search_phrases
from core.similarity import search_similar_news


def build_queries(candidate: dict) -> list[str]:
    """
    Queries clásicas basadas en ubicación explícita
    """
    name = candidate["name"]
    city = candidate["city"]
    country = "Ecuador"

    queries = []

    if candidate["place_type"] == "barrio":
        queries.append(f"barrio {name}, {city}, {country}")
        queries.append(f"{name}, {city}, {country}")

    elif candidate["place_type"] in ("calle", "avenida"):
        queries.append(f"{candidate['place_type']} {name}, {city}, {country}")
        queries.append(f"{name}, {city}, {country}")

    else:
        queries.append(f"{name}, {city}, {country}")

    queries.append(f"{city}, {country}")

    return queries


def enrich_text(text: str) -> dict:
    # 1️⃣ Inferencia inicial con IA
    inference = infer_location(text)

    if not inference["location_candidates"]:
        return {"error": "Sin candidatos de ubicación", "confidence": 0.0}

    # 2️⃣ Frases clave SEMÁNTICAS (nuevo)
    search_phrases = extract_search_phrases(text)

    # 3️⃣ Buscar noticias similares (scraping / API / mock)
    similar_news = search_similar_news(search_phrases)

    # 4️⃣ Re-analizar ubicaciones de noticias similares
    triangulation_hits = []

    for news in similar_news:
        try:
            sim_inference = infer_location(news)
            triangulation_hits.extend(sim_inference["location_candidates"])
        except Exception:
            continue

    # 5️⃣ Evaluar cada candidato original
    for candidate in inference["location_candidates"]:
        queries = build_queries(candidate)

        for query in queries:
            geo = geocode_place(query)
            if not geo:
                continue

            # 6️⃣ Calcular confianza base (tu lógica)
            base_confidence = calculate_confidence(candidate, geo)

            # 7️⃣ Ajuste por triangulación semántica (nuevo)
            corroborations = sum(
                1 for loc in triangulation_hits
                if loc["name"].lower() == candidate["name"].lower()
            )

            # Heurística simple y defendible
            triangulation_boost = min(0.3, corroborations * 0.1)
            final_confidence = round(min(1.0, base_confidence + triangulation_boost), 2)

            return {
                "incident_types": inference["incident_types"],
                "location_name": candidate["name"],
                "city": candidate["city"],
                "latitude": geo["latitude"],
                "longitude": geo["longitude"],
                "precision": candidate["precision"],
                "place_type": candidate["place_type"],
                "search_phrases": search_phrases,
                "similar_news_found": len(similar_news),
                "triangulation_hits": corroborations,
                "confidence": final_confidence,
                "reasoning": candidate["reasoning"]
            }

    return {
        "error": "No se pudo geolocalizar ningún candidato",
        "confidence": 0.0
    }
