from core.enrich import enrich_text

text = """
Terrible!!
Atentos con estos delincuentes, roban todos los días a lo largo de la av Quito aprovechando el tráfico de las horas pico.
Tengan cuidado, no se apeguen al vehículo de adelante ni anden con el celular en la mano.
Toda la vida esa calle ha sido peligrosa, sin embargo la policía jamás ha hecho.
"""

result = enrich_text(text)
print(result)
