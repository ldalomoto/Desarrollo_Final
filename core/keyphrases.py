import os
import json
import re
from google import genai
from dotenv import load_dotenv
from core.location_inference import clean_json

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_NAME = "gemini-2.5-flash-lite"

# 📐 Schema SOLO para keyphrases
KEYPHRASE_SCHEMA = {
    "type": "object",
    "properties": {
        "search_phrases": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 5
        }
    },
    "required": ["search_phrases"]
}

KEYPHRASE_PROMPT = """
Analiza cuidadosamente la siguiente noticia de inseguridad ciudadana.

LEE TODO EL TEXTO ANTES DE RESPONDER.

OBJETIVO:
Generar FRASES DE BÚSQUEDA SEMÁNTICAS para encontrar NOTICIAS SIMILARES.

REGLAS OBLIGATORIAS:
- NO palabras sueltas
- NO listas de keywords
- FRASES completas, naturales y buscables
- 3 a 5 frases
- Deben servir para buscar en Google News
- Prioriza lugar + tipo de hecho

EJEMPLOS VÁLIDOS:
- "Hallazgo de cuerpos en Ruta del Spondylus en Puerto López"
- "Violencia armada en cantón Puerto López Manabí"

Devuelve EXCLUSIVAMENTE JSON válido que cumpla el schema.
"""

def extract_search_phrases(text: str) -> list[str]:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=KEYPHRASE_PROMPT + "\n\nNOTICIA:\n" + text,
        config={
            "response_mime_type": "application/json",
            "response_schema": KEYPHRASE_SCHEMA,
            "temperature": 0.3
        }
    )

    raw_text = response.text

    with open("gemini_keyphrases.txt", "w", encoding="utf-8") as f:
        f.write(raw_text)

    try:
        cleaned = clean_json(raw_text)
        data = json.loads(cleaned)
        return data.get("search_phrases", [])

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Gemini devolvió keyphrases inválidas:\n{raw_text}"
        ) from e
