def calculate_confidence(candidate: dict, geo: dict) -> float:
    score = 0.0

    if geo:
        score += 0.4

    precision_weight = {
        "punto_de_referencia": 0.35,
        "calle": 0.3,
        "barrio": 0.2,
        "ciudad": 0.1
    }

    score += precision_weight.get(candidate["precision"], 0.1)

    # Penalizar si devuelve centro de ciudad
    address = geo.get("raw", {}).get("address", {})
    if "city" in address and address.get("suburb") is None:
        score -= 0.2

    return round(max(min(score, 1.0), 0.0), 2)
