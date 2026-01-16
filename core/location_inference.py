import json
from gpt4all import GPT4All

MODEL_NAME = "mistral-7b-instruct-v0.1.Q4_0.gguf"


model = GPT4All(MODEL_NAME)

LOCATION_PROMPT = """
Analiza cuidadosamente la siguiente noticia de inseguridad ciudadana.

Lee TODO el texto antes de responder.

OBJETIVO:
Extraer los tipos de incidentes y determinar la ubicación MÁS ESPECÍFICA posible donde ocurrió el hecho.

PROCESO OBLIGATORIO:
1. Identifica TODAS las referencias geográficas mencionadas en el texto.
2. Clasifica cada referencia por nivel espacial:
   - Macro: ciudad, parroquia, sector grande
   - Meso: barrios, zonas urbanas
   - Micro: calles, avenidas, intersecciones, puntos de referencia
3. Si existe una ubicación MÁS ESPECÍFICA que otra (por ejemplo un barrio dentro de un sector),
   DEBES priorizar la más específica.
4. Usa ubicaciones generales SOLO como contexto, no como ubicación final si existe una más precisa.
5. Si se menciona un barrio dentro de un sector o parroquia, el barrio tiene mayor prioridad.
6. NO te quedes con la primera ubicación mencionada; analiza todo el texto.

REGLAS DE CLASIFICACIÓN:
- "sector", "barrio", "zona" → barrio (a menos que el texto indique parroquia)
- "parroquia" → parroquia
- "calle", "avenida", "av." → calle o avenida
- Barrios históricos de Quito como La Marín, San Roque, La Tola, San José de Morán
  deben clasificarse como barrio.
- NO confundas parroquias con barrios.
- NO inventes ubicaciones que no estén en el texto.

PRECISIÓN:
- "alta": barrio o punto específico claramente identificado
- "media": sector o parroquia sin barrio específico
- "baja": solo ciudad o referencia vaga

Devuelve EXCLUSIVAMENTE JSON válido con la siguiente estructura:

{
  "incident_types": ["string"],
  "location_candidates": [
    {
      "name": "string",
      "city": "Quito",
      "country": "Ecuador",
      "place_type": "barrio | parroquia | calle | avenida | punto_de_referencia | zona_general",
      "precision": "alta | media | baja",
      "reasoning": "Explica por qué esta ubicación fue priorizada sobre otras"
    }
  ]
}

NO agregues texto fuera del JSON.

"""
def clean_json(text: str) -> str:
    # Elimina escapes inválidos como \_
    text = text.replace("\\_", "_")

    # Recorta todo antes del primer {
    start = text.find("{")
    if start != -1:
        text = text[start:]

    return text


def infer_location(text: str) -> dict:
    prompt = LOCATION_PROMPT + "\n\nNOTICIA:\n" + text

    with model.chat_session():
        response = model.generate(
            prompt=prompt,
            max_tokens=700,
            temp=0.2
        )

    try:
        cleaned = clean_json(response)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"GPT4All devolvió JSON inválido:\n{response}"
        ) from e
