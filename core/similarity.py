import os
import requests

SERPER_URL = "https://google.serper.dev/news"
SERPER_API_KEY = os.getenv("SERPER_API_KEY")


def search_similar_news(phrases: list[str], max_results: int = 5) -> list[str]:
    """
    Busca noticias similares usando Google News (Serper API)
    Devuelve SOLO textos de noticias
    """
    if not SERPER_API_KEY:
        raise RuntimeError("SERPER_API_KEY no configurada en variables de entorno")

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    results = []

    for phrase in phrases:
        payload = {
            "q": phrase,
            "gl": "ec",      # Ecuador
            "hl": "es",      # Español
            "num": max_results
        }

        try:
            response = requests.post(
                SERPER_URL,
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            for article in data.get("news", []):
                title = article.get("title")
                snippet = article.get("snippet")

                if title:
                    results.append(
                        f"{title}. {snippet}" if snippet else title
                    )

        except requests.RequestException:
            continue

    # eliminar duplicados manteniendo orden
    seen = set()
    unique_results = []
    for r in results:
        if r not in seen:
            seen.add(r)
            unique_results.append(r)

    return unique_results
