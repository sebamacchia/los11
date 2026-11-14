"""Música nueva del final (pedido 14/11: "algo más Hans Zimmer, Time, orquestal"). Necesita ELEVENLABS_API_KEY en .env.
Correr: /usr/bin/python3 proyectos/argentina-1986/musica_i.py   (después volver a correr construir_i.py y armar.py)
El prompt describe el ESTILO (no nombra obras ni compositores: ElevenLabs los rechaza y no queremos una copia).
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "herramientas"))
import elevenlabs  # noqa: E402

PISTAS = {
    # final: de la final (escena 51) al epílogo; crece de a poco y explota en la copa
    "m86_final_orquestal.mp3": (
        "Modern cinematic orchestral score, slow and patient build. Starts with a soft, repeating four-chord piano "
        "ostinato in a minor key, warm sustained low strings underneath, very sparse. Gradually adds cellos, "
        "a deep pulsing synth bass and soft timpani, layering octave by octave. Middle section: full string section and "
        "French horns swell on the same chord progression, wide reverb, emotional and epic but restrained. Final third: "
        "massive emotional climax with full orchestra, organ-like sustained brass and choir pads, then a slow fade back "
        "to the lonely piano motif. Instrumental, 60 BPM, no drums kit, documentary film trailer feeling.", 240),
    # epílogo corto (escenas 65-67): el mismo motivo, solo piano y cuerdas
    "m86_epilogo_orquestal.mp3": (
        "Quiet cinematic epilogue: solo piano playing a simple, repeating four-chord minor progression, long sustained "
        "strings swelling softly underneath, intimate and nostalgic, slow 60 BPM, ends on an unresolved chord. "
        "Instrumental, film score.", 90),
}

for nombre, (prompt, seg) in PISTAS.items():
    destino = RAIZ / "musica" / nombre
    if destino.exists():
        print("ya está:", nombre)
        continue
    elevenlabs.musica(prompt, seg, destino)
    print("listo:", destino)
