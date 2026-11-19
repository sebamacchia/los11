"""Segunda parte de Argentina 86 (17/11): el capítulo 1 "Nadie creía" (Perú 85 y el 2-2 de Gareca, Bilardo criticado,
Maradona capitán, Nápoles y España 82, Passarella enfermo). Pedido del usuario: "mezcla, como venimos pero bajemos el
ritmo a algo más documental": arranca en carpeta (carpeta.py capitulo: una hoja limpia tapa el collage de la intro)
y sigue con las escenas documentales del guion j (4-10), con más aire entre frases y una música ochentosa más calma
(musica/m86_parte2_80s.mp3, sigue a la de la intro).

  /usr/bin/python3 proyectos/argentina-1986/construir_parte2.py
  /usr/bin/python3 herramientas/armar.py proyectos/argentina-1986 --guion guion_parte2.json [--borrador]
"""
import copy
import json
from pathlib import Path

AQUI = Path(__file__).parent
j = json.load(open(AQUI / "guion_j.json"))
G = "salida/graficos/"

placa = {
    "capitulo": "Nadie creía",
    "visual": [{"archivo": G + "capitulo1_1986.mp4", "desde": 0}],
    "duracion": 3.6,
    "sfx": [{"archivo": G + "capitulo1_1986_con_sonido.mp4", "desde": 0, "duracion": 3.6, "en": 0, "volumen": 0.8}],
}
escenas = [placa] + [copy.deepcopy(e) for e in j["escenas"][3:10]]
# notas del 17/11: "falta el datazo de cuánto costó el pase" y "Passarella enfermo: qué enfermedad"
# (UPI 1/7/1984: US$ 7,5 millones, récord mundial; enterocolitis / "mal de Moctezuma", diarrea y deshidratación)
escenas[6]["texto"] = ("Llegó a México como la gran estrella del mundo. Jugaba en el Nápoles, en Italia. Dos años antes, "
                       "el Nápoles se lo había comprado al Barcelona por siete millones y medio de dólares: el pase más "
                       "caro de la historia. Pero en los Mundiales le debía una al fútbol: en España ochenta y dos lo "
                       "habían pateado de todos lados... y se fue expulsado.")
escenas[7]["texto"] = ("Y había un problema más. El otro gran líder del plantel, el capitán campeón del setenta y ocho, "
                       "Daniel Passarella, se enfermó en México: una infección intestinal, la famosa venganza de "
                       "Moctezuma. Diarrea, deshidratación... y no jugó ni un minuto. El equipo era de Diego. "
                       "Para bien o para mal.")
for e in escenas[1:]:
    e["retardo"] = max(float(e.get("retardo", 0)), 0.35)       # más aire: respira antes de cada escena
    e["pausa"] = max(float(e.get("pausa", 0.45)), 0.75)
guion = {
    "archivo": "argentina-1986_parte2",
    "formato": "horizontal",
    "pausa": 0.75,
    "sfx_volumen": 0.5,
    "musica": [{"archivo": "../../musica/m86_parte2_80s.mp3", "desde": 1, "hasta": len(escenas), "volumen": 0.17,
                "fade_in": 1.5, "fade_out": 2.0}],
    "escenas": escenas,
}
json.dump(guion, open(AQUI / "guion_parte2.json", "w"), ensure_ascii=False, indent=1)
pal = sum(len(e.get("texto", "").split()) for e in escenas)
print(f"guion_parte2.json: {len(escenas)} escenas, {pal} palabras")
