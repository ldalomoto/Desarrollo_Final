def triangulate(original, similar_locations: list[dict]) -> dict:
    score = {}

    for loc in similar_locations:
        name = loc["name"]
        score[name] = score.get(name, 0) + 1

    if not score:
        return {
            "final_location": original,
            "confidence": 0.6
        }

    best = max(score, key=score.get)
    confidence = min(0.9, 0.5 + score[best] * 0.15)

    return {
        "final_location": best,
        "confidence": round(confidence, 2)
    }
