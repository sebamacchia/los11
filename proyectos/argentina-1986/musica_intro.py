"""Música de la intro de Argentina 86 (ElevenLabs Music) -> musica/intro86_jazz_*.mp3
Un solo tema de batería de jazz, continuo y fluido, con la forma de la intro (escenas medidas en el render del 15/11):
  0-30 s swing con palillos (1986, afiches, satélite, banderas) · 30-45 s escobillas, suave (Maradona)
  · 45-63 s vuelve con todo (montaje) · corte seco (el platillo de la peluca lo pone el sfx).
  /usr/bin/python3 proyectos/argentina-1986/musica_intro.py
No vuelve a generar las que ya existen.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "herramientas"))
import elevenlabs  # noqa: E402

BASE = ("Solo jazz drum kit, no other instruments. Fluid, musical bebop drumming in the style of a live jazz club "
        "recording, warm vintage room sound, ride cymbal swing pattern, ghost notes on the snare, melodic tom fills, "
        "feathered bass drum. ")
PISTAS = [
    ("intro86_jazz_a.mp3", 70, BASE +
     "Starts immediately with sticks at a fast swing tempo, around 250 bpm, energetic and playful for the first 30 "
     "seconds. Then switches to brushes on the snare, soft, sparse and intimate for about 15 seconds, leaving room for "
     "a narrator. Then builds back with sticks into an exciting full swing with rolling tom fills until the end."),
    ("intro86_jazz_b.mp3", 70, BASE +
     "Uptempo hard bop drum solo, constantly flowing, never stopping: driving ride cymbal, snare comping, "
     "conversational fills. Dynamics: lively for the first half, a quieter brushes passage in the middle, "
     "then a big crescendo at the end."),
]

for nombre, seg, prompt in PISTAS:
    destino = RAIZ / "musica" / nombre
    if destino.exists():
        print("ya está:", nombre)
        continue
    elevenlabs.musica(prompt, seg, destino)
    print("listo:", nombre)
