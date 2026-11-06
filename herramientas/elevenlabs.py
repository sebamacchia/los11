"""Cliente mínimo de ElevenLabs (solo stdlib) con caché para no pagar dos veces el mismo audio."""
import hashlib
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CACHE = RAIZ / ".cache" / "elevenlabs"
API = "https://api.elevenlabs.io/v1"


def _clave():
    clave = os.environ.get("ELEVENLABS_API_KEY")
    env = RAIZ / ".env"
    if not clave and env.exists():
        for linea in env.read_text().splitlines():
            if linea.startswith("ELEVENLABS_API_KEY="):
                clave = linea.split("=", 1)[1].strip()
    if not clave:
        raise SystemExit("Falta ELEVENLABS_API_KEY (ponela en .env)")
    return clave


def _post(ruta, cuerpo, destino: Path):
    req = urllib.request.Request(
        API + ruta,
        data=json.dumps(cuerpo).encode(),
        headers={"xi-api-key": _clave(), "Content-Type": "application/json", "Accept": "audio/mpeg"},
        method="POST",
    )
    for intento in range(6):  # 429 = sistema ocupado: esperar y reintentar
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                datos = r.read()
            break
        except urllib.error.HTTPError as e:
            detalle = e.read().decode(errors='replace')
            if e.code == 429 and intento < 5:
                time.sleep(10 * (intento + 1))
                continue
            raise SystemExit(f"ElevenLabs {e.code}: {detalle}")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(datos)
    return destino


def _cache_path(tipo, payload):
    h = hashlib.sha1(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]
    return CACHE / f"{tipo}_{h}.mp3"


def voz(texto, voice_id, model_id="eleven_multilingual_v2", ajustes=None):
    """Texto -> mp3 narrado. Devuelve la ruta (cacheada)."""
    cuerpo = {"text": texto, "model_id": model_id}
    if ajustes:
        cuerpo["voice_settings"] = ajustes
    destino = _cache_path("voz", {"v": voice_id, **cuerpo})
    if destino.exists():
        return destino
    return _post(f"/text-to-speech/{voice_id}?output_format=mp3_44100_128", cuerpo, destino)


def efecto(descripcion, duracion=None, influencia=0.4):
    """Descripción (en inglés funciona mejor) -> mp3 de efecto de sonido."""
    cuerpo = {"text": descripcion, "prompt_influence": influencia}
    if duracion:
        cuerpo["duration_seconds"] = max(0.5, min(22, float(duracion)))
    destino = _cache_path("sfx", cuerpo)
    if destino.exists():
        return destino
    return _post("/sound-generation", cuerpo, destino)


def musica(descripcion, segundos=120, destino=None):
    """Descripción -> mp3 instrumental con ElevenLabs Music (uso comercial incluido en el plan).
    Si se pasa `destino`, además lo copia ahí (por ejemplo musica/tension.mp3)."""
    cuerpo = {"prompt": descripcion, "music_length_ms": int(max(10, min(300, segundos)) * 1000),
              "force_instrumental": True}
    cache = _cache_path("musica", cuerpo)
    if not cache.exists():
        _post("/music?output_format=mp3_44100_128", cuerpo, cache)
    if destino:
        destino = Path(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(cache.read_bytes())
        return destino
    return cache


def listar_voces():
    req = urllib.request.Request(API + "/voices", headers={"xi-api-key": _clave()})
    with urllib.request.urlopen(req, timeout=60) as r:
        for v in json.load(r)["voices"]:
            etiquetas = ", ".join(f"{k}={x}" for k, x in (v.get("labels") or {}).items())
            print(f"{v['voice_id']}  {v['name']:<28} {etiquetas}")


if __name__ == "__main__":
    listar_voces()
