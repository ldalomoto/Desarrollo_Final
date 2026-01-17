import os
import json
from google import genai
from dotenv import load_dotenv
import re

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_NAME = "gemini-2.5-flash-lite"

LOCATION_SCHEMA = {
    "type": "object",
    "properties": {
        "incident_types": {
            "type": "array",
            "items": {"type": "string"}
        },
        "location_candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "city": {"type": "string"},
                    "country": {"type": "string"},

                    "place_type": {
                        "type": "string",
                        "enum": [
                            "barrio",
                            "parroquia",
                            "calle",
                            "avenida",
                            "punto_de_referencia",
                            "zona_general"
                        ]
                    },

                    "precision": {
                        "type": "string",
                        "enum": ["alta", "media", "baja"]
                    },

                    "reasoning": {"type": "string"}
                },
                "required": [
                    "name",
                    "city",
                    "country",
                    "place_type",
                    "precision",
                    "reasoning"
                ]
            }
        }
    },
    "required": ["incident_types", "location_candidates"]
}


LOCATION_PROMPT = """
Analiza cuidadosamente la siguiente noticia de inseguridad ciudadana.

LEE TODO EL TEXTO ANTES DE RESPONDER.

OBJETIVO:
1. Identificar los tipos de incidentes ocurridos.
2. Detectar TODAS las ubicaciones mencionadas.
3. Determinar cuál es la ubicación MÁS ESPECÍFICA posible donde ocurrió el hecho.

PROCESO OBLIGATORIO:
- Identifica todas las referencias geográficas del texto.
- Clasifica cada una por nivel espacial:
  * Macro: ciudad, cantón, parroquia
  * Meso: barrio, sector, zona urbana
  * Micro: calles, avenidas, intersecciones, puntos de referencia
- Si existe una ubicación más específica dentro de otra (ej. barrio dentro de sector),
  DEBES priorizar la más específica.
- NO te quedes con la primera ubicación mencionada.
- Usa ubicaciones generales solo como contexto si existe una más precisa.

REGLAS DE CLASIFICACIÓN:
- "sector", "barrio", "zona" → BARRIO
- "parroquia" → PARROQUIA
- "calle", "avenida", "av." → CALLE o AVENIDA
- Barrios históricos de Quito (La Marín, San Roque, La Tola, San José de Morán)
  deben clasificarse como BARRIO.
- NO confundas barrios con parroquias.
- NO inventes ubicaciones.

PRECISIÓN:
- alta → calle, punto de referencia o barrio claramente identificado
- media → parroquia o sector sin barrio
- baja → solo ciudad o referencia vaga

IMPORTANTE:
- Devuelve TODAS las ubicaciones relevantes, pero
  la MÁS ESPECÍFICA debe aparecer PRIMERO en la lista.
- País: Ecuador.

Responde EXCLUSIVAMENTE con JSON válido que cumpla el schema.
"""


def clean_json(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No se encontró JSON en la respuesta del modelo")

    text = text[start:end + 1]

    text = text.replace("\\_", "_")
    text = text.replace("\\-", "-")
    text = text.replace("\\'", "'")

    text = re.sub(r"[\x00-\x1F\x7F]", "", text)

    return text


def infer_location(text: str) -> dict:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=LOCATION_PROMPT + "\n\nNOTICIA:\n" + text,
        config={
            "response_mime_type": "application/json",
            "response_schema": LOCATION_SCHEMA,
            "temperature": 0.2
        }
    )

    raw_text = response.text

    with open("gemini_response.txt", "w", encoding="utf-8") as f:
        f.write(raw_text)

    try:
        cleaned = clean_json(raw_text)
        return json.loads(cleaned)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Gemini devolvió JSON inválido:\n{raw_text}"
        ) from e

