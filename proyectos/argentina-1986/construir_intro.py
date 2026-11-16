"""Arma guion_intro.json: SOLO la intro de Argentina 86, con el guion técnico y literario que escribieron los del canal
(15/11, nueva metodología: se trabaja por partes). Piezas animadas: herramientas/intro_pop.py -> salida/graficos/intro_*.mp4

Cambios al texto original (avisados): "decimotercera" (no "décimo tercera"), "desenmarañar", y el pase de Maradona:
7,5 millones de dólares (la cifra más citada; los 9 millones no aparecen en las fuentes).

  /usr/bin/python3 proyectos/argentina-1986/construir_intro.py [--sin-sfx]   (sin-sfx: para probar sin clave de ElevenLabs)
  /usr/bin/python3 herramientas/armar.py proyectos/argentina-1986 --guion guion_intro.json [--borrador] [--voz-provisoria]
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).parent
MUSICA = AQUI.parent.parent / "musica"
G = "salida/graficos/"
CAM0 = [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}]


def clip(archivo, desde=0.0, hasta=None, vel=1.0, **k):
    v = {"archivo": archivo, "desde": desde, "velocidad": vel, **k}
    if hasta:
        v["hasta"] = hasta
    return v


def fx(prompt, en, dur=None, vol=0.6):
    d = {"prompt": prompt, "en": en, "volumen": vol}
    if dur:
        d["duracion"] = dur
    return d


def foto(archivo, x=960, y=540, alto=900, rot=0.0, **k):
    return {"archivo": archivo, "x": x, "y": y, "alto": alto, "rot": rot, "borde": 10, **k}


escenas = [
    {  # batería sola + íconos del 86 y recién ahí entra la voz
        "capitulo": "Intro",
        "retardo": 2.2,
        "texto": "Mil novecientos ochenta y seis. El mundo estaba completamente loco... y el fútbol no se quedaba atrás.",
        "visual": [clip(G + "intro_iconos.mp4", hasta="@y el fútbol"),
                   clip("material/fuentes/belgica.mp4", 264.5, vel=0.8)],
        "sfx": [fx("VHS tape inserted into a VCR, mechanical clunk, then tape whirring and glitchy rewind chirps", 0, 3, 0.5)],
    },
    {
        "texto": "Se jugaba la decimotercera edición de la Copa del Mundo.",
        "pausa": 1.4,
        "visual": [clip(G + "intro_afiches.mp4")],
        "sfx": [fx("rapid succession of paper posters slapping down onto a wooden table, accelerating", 0, 2.1, 0.55),
                fx("heavy rubber stamp thud on paper, single hit", 2.05, 1, 0.8)],
    },
    {
        "retardo": 1.5,
        "texto": "La sede: México.",
        "pausa": 0.7,
        "visual": [clip(G + "intro_satelital.mp4")],
        "sfx": [fx("fast cinematic descent whoosh from space through the atmosphere, wind rushing", 0, 3, 0.55)],
    },
    {
        "texto": ("Veinticuatro selecciones buscando la gloria eterna. Y entre ellas, Argentina... un equipo que llegaba "
                  "al límite, sufriendo, cuestionado por todos, pero que guardaba un as bajo la manga."),
        "pausa": 0.5,
        "visual": [clip(G + "intro_banderas.mp4", hasta="@un equipo"),
                   clip("material/fuentes/peru1985.mp4", 211.0, vel=0.6, hasta="@sufriendo", golpe="2-2",
                        golpe_sub="ARGENTINA-PERÚ · 1985 · AL MUNDIAL POR LA VENTANA", golpe_en=0.3,
                        golpe_estilo="fantasma", foco=[0.5, 0.5]),
                   {"tipo": "doc", "hasta": "@pero que guardaba", "planos": [
                       {"en": 0, "mesa": "papel", "capas": [foto("material/eg_bilardo86.jpg", x=640, alto=860, rot=-1.5)],
                        "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}, {"t": 2.5, "x": 760, "y": 480, "zoom": 1.08}],
                        "rotulos": [{"tipo": "titulo", "texto": "Cuestionado\npor todos.", "x": 1100, "y": 400,
                                     "en": 0.05, "tam": 84}]}]},
                   {"tipo": "doc", "planos": [
                       {"en": 0, "mesa": "negro", "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0},
                                                            {"t": "@bajo la manga", "x": 960, "y": 540, "zoom": 1.08}],
                        "rotulos": [{"tipo": "titulo", "texto": "Un as bajo\nla manga.", "x": 160, "y": 330,
                                     "en": "@un as", "tam": 150, "claro": True}]}]}],
        "sfx": [fx("quick succession of small cartoon pops, playful, like bubbles popping", 0, 2, 0.45),
                fx("magical bright shimmer swell, glowing sparkle", 2.0, 1.5, 0.5),
                fx("old camera shutter click", "@sufriendo", 1, 0.6),
                fx("playing card snapped down on a table, crisp", "@un as", 1, 0.8)],
    },
    {  # respiro: un silencio y entra la voz sola; la batería vuelve en escobillas
        "retardo": 0.9,
        "texto": ("Tenía a Diego Armando Maradona. El pibe de Fiorito, la estrella absoluta del Napoli, que venía de "
                  "romper el mercado siendo el fichaje más caro de la historia: siete millones y medio de dólares. "
                  "Una verdadera locura para la época."),
        "pausa": 0.4,
        "visual": [clip("material/fuentes/napoli1984.mp4", 84.5, vel=0.5, hasta="@la estrella"),
                   clip("material/fuentes/napoli1984.mp4", 93.5, vel=0.5, hasta="@que venía"),
                   {"tipo": "doc", "hasta": "@Una verdadera", "planos": [
                       {"en": 0, "mesa": "papel",
                        "capas": [foto("material/maradona_napoli_fotografos.jpg", x=1420, y=470, alto=640, rot=1.5,
                                       trama=5),
                                  foto("material/intro/dolar.jpg", x=900, y=640, alto=520, rot=-9,
                                       en="@siete millones")],
                        "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0},
                                   {"t": "@siete millones", "x": 900, "y": 600, "zoom": 1.15}],
                        "rotulos": [{"tipo": "maquina", "texto": "BARCELONA → NÁPOLES · JULIO DE 1984", "x": 130,
                                     "y": 150, "en": 0.1, "tam": 28, "fondo_tira": True},
                                    {"tipo": "titulo", "texto": "El pase más\ncaro de la historia.", "x": 120,
                                     "y": 230, "en": "@el fichaje", "tam": 92},
                                    {"tipo": "titulo", "texto": "US$ 7.500.000", "x": 140, "y": 880,
                                     "en": "@siete millones", "tam": 110, "rojo": True, "fondo_tira": True}]}]},
                   clip("material/fuentes/napoli1984.mp4", 126.0, vel=0.5)],
        "sfx": [fx("press photographers camera flashes and shutter clicks", "@la estrella", 2.5, 0.5),
                fx("paper banknote flutter whoosh landing on table", "@siete millones", 1.2, 0.7)],
    },
    {  # vuelve la batería con todo: montaje y remate de la peluca
        "texto": ("En este video vamos a desenmarañar el camino de la Selección dirigida por Bilardo y el gran Diego "
                  "hasta tocar el cielo con las manos: los partidos, el lado B de las anécdotas, los pormenores que "
                  "nadie te contó... y unos datos que literalmente te van a volar la peluca."),
        "pausa": 0.7,
        "visual": [clip("material/fuentes/corea.mp4", 195.5, vel=0.6, hasta="@dirigida"),
                   clip("material/fuentes/italia.mp4", 266.0, vel=0.8, hasta="@hasta tocar"),
                   clip("material/fuentes/inglaterra.mp4", 287.5, vel=0.6, hasta="@los partidos"),
                   clip("material/fuentes/belgica.mp4", 266.5, vel=0.8, hasta="@el lado B"),
                   {"tipo": "doc", "hasta": "@los pormenores", "planos": [
                       {"en": 0, "mesa": "papel", "capas": [foto("material/eg_comedor.jpg", alto=880, rot=1)],
                        "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0},
                                   {"t": "@los pormenores", "x": 960, "y": 540, "zoom": 1.1}],
                        "rotulos": [{"tipo": "maquina", "texto": "EL LADO B", "x": 140, "y": 900, "en": 0.1,
                                     "tam": 34, "fondo_tira": True}]}]},
                   clip("material/fuentes/uruguay.mp4", 94.0, vel=0.6, hasta="@y unos datos"),
                   clip(G + "intro_peluca.mp4")],
        "sfx": [fx("hard kick of a leather football", 0, 1, 0.6),
                fx("photograph slapped down on a wooden table", "@el lado B", 1, 0.6),
                fx("strong comedic wind gust blowing", "@literalmente", 2, 0.7),
                fx("single loud crash cymbal hit, dry, then silence", "@la peluca", 1.5, 0.8)],
    },
]

if "--sin-sfx" in sys.argv:
    for e in escenas:
        e.pop("sfx", None)

# Música: un solo tema de batería de jazz, continuo (musica_intro.py, ElevenLabs Music; la b fluye mejor que la a).
# Sigue sin cortes salvo el respiro de Maradona: se calla, entra la voz sola y vuelve baja; el montaje la sube.
JAZZ = "../../musica/intro86_jazz_b.mp3"
musica = []
if (MUSICA / "intro86_jazz_b.mp3").exists():
    musica = [{"archivo": JAZZ, "desde": 1, "hasta": 4, "volumen": 0.34, "fade_in": 0.05, "fade_out": 0.5},
              {"archivo": JAZZ, "desde": 5, "hasta": 5, "volumen": 0.17, "continua": True, "retardo": 2.6,
               "fade_in": 2.0, "fade_out": 0.3},
              {"archivo": JAZZ, "desde": 6, "hasta": 6, "volumen": 0.4, "continua": True, "fade_in": 0.3,
               "fade_out": 0.25}]

g = {"archivo": "argentina-1986_intro", "formato": "horizontal", "pausa": 0.35, "sfx_volumen": 1.0,
     "musica": musica, "escenas": escenas}
(AQUI / "guion_intro.json").write_text(json.dumps(g, ensure_ascii=False, indent=1))
palabras = sum(len(e["texto"].split()) for e in escenas)
print(f"guion_intro.json: {len(escenas)} escenas, {palabras} palabras, música: {len(musica)} tramos")
