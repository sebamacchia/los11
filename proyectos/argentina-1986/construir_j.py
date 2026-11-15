"""Arma guion_j.json desde guion_i.json con las notas del usuario del 15/11 (docs de Drive "Guion Argentina 1986
(versión g)" e "Ideas argentina 86"):

1. Nuevo inicio: "Siete partidos separaban a Argentina de la gloria..." (sale el hook de los cuatro minutos).
2. Primer acto sin énfasis en la altura de Diego (se iba con el hook viejo).
3. Passarella: la foto de Diego y Passarella con sombreros mexicanos para su liderazgo (escena 13).
4. Sale la frase de Enrique ("con el pase que le di..."); entra la foto del festejo ante Inglaterra.
5. La llamada de Diego con Doña Tota después de la final: solo ellos dos (sin el periodista), con la "animación"
   Diego en México / la mamá en Buenos Aires unidos por la línea del teléfono.
6. Final: el récord de Passarella (único argentino con dos medallas) y la frase de las 44 medallas para 43 jugadores.
7. La foto de Diego de espaldas con la copa en "nunca un jugador había ganado un Mundial tan solo".

Correr: /usr/bin/python3 proyectos/argentina-1986/construir_j.py
"""
import json
from pathlib import Path

AQUI = Path(__file__).parent
g = json.loads((AQUI / "guion_i.json").read_text())
g["archivo"] = "argentina-1986_j"
E = g["escenas"]
orig = list(E)  # para remapear la música (va por número de escena)


def doc(planos, hasta=None):
    v = {"tipo": "doc", "planos": planos}
    if hasta:
        v["hasta"] = hasta
    return v


def foto(archivo, x=960, y=540, alto=900, rot=0.0, **k):
    return {"archivo": archivo, "x": x, "y": y, "alto": alto, "rot": rot, "borde": 10, **k}


CAM0 = [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}]

# ── 1. inicio nuevo (reemplaza las escenas 1-4) ──────────────────────────────────────────────────────────────────
hook = {
    "capitulo": "Siete partidos",
    "retardo": 0.3,
    "pausa": 0.9,
    "texto": ("Siete partidos separaban a Argentina de la gloria. En el camino la esperaban el campeón del mundo, "
              "un duelo con Inglaterra que iba mucho más allá del fútbol... y una final que se le escapaba de las "
              "manos. Para levantar esa copa, necesitaba a Maradona. Pero también necesitaba un equipo capaz de "
              "llegar hasta el final."),
    "visual": [
        doc([{"en": 0, "mesa": {"archivo": "material/fuentes/final.mp4", "desde": 44.5},
              "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}, {"t": "@de la gloria", "x": 960, "y": 540,
                                                                      "zoom": 1.08}],
              "rotulos": [{"tipo": "titulo", "texto": "7 partidos.", "x": 160, "y": 380, "en": 0.2, "tam": 170,
                           "claro": True},
                          {"tipo": "maquina", "texto": "MÉXICO · 31 DE MAYO – 29 DE JUNIO DE 1986", "x": 168,
                           "y": 610, "en": "@separaban", "tam": 30, "claro": True}]}],
            hasta="@En el camino"),
        {"archivo": "material/fuentes/italia.mp4", "desde": 58.0, "velocidad": 0.6, "hasta": "@un duelo",
         "zocalo": "Italia", "sub": "campeón del mundo en 1982"},
        {"archivo": "material/limpias/inglaterra_fifa.mp4", "desde": 140.0, "velocidad": 0.6, "hasta": "@y una final"},
        {"archivo": "material/fuentes/final.mp4", "desde": 447.0, "velocidad": 0.5, "hasta": "@Para levantar",
         "golpe": "2-2", "golpe_en": "@se le escapaba", "golpe_estilo": "fantasma", "foco": [0.5, 0.5]},
        {"archivo": "material/limpias/inglaterra_fifa.mp4", "desde": 270.0, "velocidad": 0.7, "hasta": "@Pero también"},
        doc([{"en": 0, "mesa": "papel",
              "capas": [foto("material/eg_festejo_tres.jpg", alto=940, rot=1)],
              "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}, {"t": "@hasta el final", "x": 960, "y": 520,
                                                                      "zoom": 1.12}]}]),
    ],
    "sfx": E[0].get("sfx", [])[:1],
}
E[0:4] = [hook]

# ── 3. Passarella: la foto de los sombreros para el liderazgo ────────────────────────────────────────────────────
pas = next(e for e in E if "Daniel Passarella, se enfermó" in e.get("texto", ""))
# foto cuadrada de 1920: a alto 940 ocupa x 490-1430; Passarella (derecha) queda en ~x 1180, cara en ~y 330
pas["visual"] = [
    doc([{"en": 0, "mesa": "papel",
          "capas": [foto("material/diego_passarella_sombreros.jpg", alto=940, rot=-0.8)],
          "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0},
                     {"t": "@Daniel Passarella", "x": 1150, "y": 420, "zoom": 1.7}],
          "rotulos": [{"tipo": "maquina", "texto": "DANIEL PASSARELLA · CAPITÁN CAMPEÓN EN 1978", "x": 900, "y": 760,
                       "en": "@Daniel Passarella", "tam": 22, "fondo_tira": True, "mundo": True}]}],
        hasta="@El equipo era"),
    pas["visual"][-1],  # entrenamiento.jpg
]

# ── 4. sin la frase de Enrique; foto del festejo ante Inglaterra ─────────────────────────────────────────────────
vh = next(e for e in E if e.get("texto", "").startswith("Eso que escuchaste"))
vh["texto"] = ("Eso que escuchaste es Víctor Hugo Morales, en la radio. Barrilete cósmico... ¿de qué planeta "
               "viniste? Y Gary Lineker, el delantero inglés, confesó que fue la única vez en su carrera que tuvo "
               "ganas de aplaudir un gol del rival.")
clip_vh, clip_lineker = vh["visual"][0], vh["visual"][-1]
clip_vh["hasta"] = "@¿de qué planeta"
vh["visual"] = [
    clip_vh,
    doc([{"en": 0, "mesa": "papel",
          "capas": [foto("material/diego_festejo_inglaterra.png", alto=760, rot=1.2)],
          "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}, {"t": "@Y Gary", "x": 1120, "y": 420, "zoom": 1.35}]}],
        hasta="@Y Gary"),
    clip_lineker,
]

# ── 7. la copa de espaldas para "tan solo" ───────────────────────────────────────────────────────────────────────
copa = next(e for e in E if e.get("texto", "").startswith("Diego levanta la copa"))
copa["visual"][-1] = doc([{"en": 0, "mesa": "papel",
                           "capas": [foto("material/diego_copa_espalda.png", alto=880, rot=-1, trama=5)],
                           "camara": [{"t": 0, "x": 960, "y": 560, "zoom": 1.0},
                                      {"t": "@Y nunca volvió", "x": 960, "y": 470, "zoom": 1.25}]}])

# ── 5. la llamada con Doña Tota (después de la copa, antes del regreso a Buenos Aires) ──────────────────────────
# Audio: material/fuentes/llamada_tota.mp4 (radio de José María Muñoz, 29/06/1986), Diego y la mamá desde 86.4 s.
#  0.0 Hola, mamita / 2.3 ¿Cómo estás, mamá? / 3.5 Mi vida / 6.4 Te quiero mucho, mamá / 8.0 También, mi amor...
#  la madre más feliz del mundo hoy (13.9) / 16.2 Yo juego para vos, mamá / 18.3 Sí, mi amor (20.6)
DIEGO = foto("material/maradona_copa2.jpg", x=540, y=430, alto=660, rot=-1.5, recorte=[60, 0, 660, 760])
TOTA = foto("material/tota_diario.jpg", x=1380, y=430, alto=660, rot=1.5, recorte=[700, 0, 1200, 675])
LINEA = {"tipo": "linea", "desde": [790, 260], "hasta": [1130, 260], "rojo": True, "en": "@Del otro lado", "dibujo": 1.2,
         "mundo": True}
LUGARES = [{"tipo": "maquina", "texto": "ESTADIO AZTECA · MÉXICO", "x": 330, "y": 790, "en": 0.3, "tam": 24,
            "fondo_tira": True, "mundo": True},
           {"tipo": "maquina", "texto": "BUENOS AIRES", "x": 1290, "y": 790, "en": "@en Buenos Aires", "tam": 24,
            "fondo_tira": True, "mundo": True}]
llamada_intro = {
    "texto": ("Unos minutos después, todavía en el Azteca, Diego salió al aire en una radio argentina. "
              "Del otro lado de la línea, en Buenos Aires, estaba su mamá: doña Tota."),
    "pausa": 0.3,
    "visual": [doc([{"en": 0, "mesa": "papel", "capas": [DIEGO, TOTA],
                     "camara": [{"t": 0, "x": 640, "y": 480, "zoom": 1.35},
                                {"t": "@Del otro lado", "x": 960, "y": 540, "zoom": 1.0},
                                {"t": "@doña Tota", "x": 1200, "y": 500, "zoom": 1.2}],
                     "rotulos": LUGARES + [LINEA]}])],
    "sfx": [{"prompt": "old telephone line hiss and click, analog radio static, 1980s", "en": "@Del otro lado",
             "duracion": 3, "volumen": 0.25, "fade_out": 1.0}],
}


def dice(quien, texto, en, n):
    x = 150 if quien == "diego" else 1030
    return {"tipo": "maquina", "texto": texto, "x": x, "y": 900, "en": en, "tam": 34, "fondo_tira": True,
            "sale": None}


DIALOGO = [("diego", "—Hola, mamita. ¿Cómo estás, mamá?", 0.1, 3.3),
           ("tota", "—Mi vida.", 3.4, 6.2),
           ("diego", "—Te quiero mucho, mamá.", 6.3, 7.9),
           ("tota", "—También, mi amor. Andá, descansá,\n mi hijo, que me hiciste la madre\n más feliz del mundo hoy.",
            8.0, 16.0),
           ("diego", "—Yo juego para vos, mamá.", 16.1, 18.2),
           ("tota", "—Sí, mi amor.", 18.3, 20.8)]
rot_dialogo = []
for i, (q, t, en, sale) in enumerate(DIALOGO):
    r = dice(q, t, en, i)
    r["sale"] = sale
    rot_dialogo.append(r)
LUG_FIJOS = [dict(r, en=0) for r in LUGARES]
cam = [{"t": 0, "x": 800, "y": 500, "zoom": 1.12}]
for q, _, en, _ in DIALOGO[1:]:
    x = 800 if q == "diego" else 1120
    cam += [{"t": round(en - 0.6, 2), "x": cam[-1]["x"], "y": 500, "zoom": 1.12},
            {"t": en, "x": x, "y": 500, "zoom": 1.12}]
cam += [{"t": 19.5, "x": 1120, "y": 500, "zoom": 1.12}, {"t": 20.8, "x": 960, "y": 540, "zoom": 1.0}]
llamada = {
    "texto": "",
    "duracion": 21.0,
    "sfx": [{"archivo": "material/fuentes/llamada_tota.mp4", "desde": 86.4, "duracion": 20.8, "en": 0,
             "volumen": 1.0, "fade_in": 0.2, "fade_out": 0.6}],
    "visual": [doc([{"en": 0, "mesa": "papel", "capas": [DIEGO, TOTA], "camara": cam,
                     "rotulos": LUG_FIJOS + [dict(LINEA, en=0, dibujo=0.01)] + rot_dialogo}])],
}
i_copa = E.index(copa)
E[i_copa + 1:i_copa + 1] = [llamada_intro, llamada]

# ── 6. Passarella, el único con dos medallas (antes de "Pasaron cuarenta años") ─────────────────────────────────
medallas = {
    "texto": ("Y un dato más. Daniel Passarella, el capitán del setenta y ocho, el que no pudo jugar ni un minuto en "
              "México, también era parte de ese plantel. Así se convirtió en el único argentino con dos medallas de "
              "campeón del mundo. Por eso, durante treinta y seis años, en la Argentina se repitió una frase: hay "
              "cuarenta y cuatro medallas de campeón del mundo... para cuarenta y tres jugadores."),
    "pausa": 0.9,
    "visual": [doc([{"en": 0, "mesa": "papel",
                     "capas": [foto("material/diego_passarella_sombreros.jpg", x=1380, y=520, alto=900, rot=1.2, trama=5,
                                    recorte=[1060, 240, 1760, 1500])],
                     "camara": CAM0,
                     "rotulos": [{"tipo": "maquina", "texto": "1978 · CAMPEÓN, CAPITÁN", "x": 140, "y": 330,
                                  "en": "@el capitán", "tam": 34, "fondo_tira": True},
                                 {"tipo": "maquina", "texto": "1986 · CAMPEÓN, SIN JUGAR", "x": 140, "y": 420,
                                  "en": "@ni un minuto", "tam": 34, "fondo_tira": True},
                                 {"tipo": "titulo", "texto": "2 medallas.", "x": 130, "y": 560,
                                  "en": "@dos medallas", "tam": 120, "rojo": True}]}],
               hasta="@Por eso"),
               doc([{"en": 0, "mesa": "negro",
                     "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}, {"t": "@para cuarenta", "x": 960,
                                                                             "y": 540, "zoom": 1.06}],
                     "rotulos": [{"tipo": "maquina", "texto": "1978 + 1986", "x": 170, "y": 250, "en": "@una frase",
                                  "tam": 36, "claro": True},
                                 {"tipo": "titulo", "texto": "44 medallas", "x": 160, "y": 340, "en": "@hay cuarenta",
                                  "tam": 150, "claro": True},
                                 {"tipo": "titulo", "texto": "para 43 jugadores.", "x": 160, "y": 520,
                                  "en": "@para cuarenta", "tam": 150, "rojo": True}]}])],
}
i_cam = next(i for i, e in enumerate(E) if e.get("texto", "").startswith("¿Y la camiseta azul"))
E[i_cam + 1:i_cam + 1] = [medallas]

# ── música: remapear rangos (números de escena desde 1) ─────────────────────────────────────────────────────────
pos = {id(e): i + 1 for i, e in enumerate(E)}


def nuevo(n_viejo, lado):
    """Escena vieja -> nueva; si ya no existe (hook viejo), la más cercana hacia adentro del rango."""
    rango = range(n_viejo, 0, -1) if lado == "hasta" else range(n_viejo, len(orig) + 1)
    for n in rango:
        if id(orig[n - 1]) in pos:
            return pos[id(orig[n - 1])]
    return 1


mus = []
for m in g["musica"]:
    m = dict(m, desde=1 if m["desde"] <= 4 else nuevo(m["desde"], "desde"), hasta=nuevo(m["hasta"], "hasta"))
    if m["desde"] <= pos[id(copa)] < m["hasta"]:  # la llamada va sin música: se corta en la copa y sigue después
        resto = dict(m, desde=pos[id(llamada)] + 1)
        mus += [dict(m, hasta=pos[id(copa)], fade_out=2.0), resto]
    else:
        mus.append(m)
g["musica"] = mus

(AQUI / "guion_j.json").write_text(json.dumps(g, ensure_ascii=False, indent=1))
print(f"guion_j.json: {len(E)} escenas")
for m in g["musica"]:
    print("  música", m["archivo"].split("/")[-1], m["desde"], "→", m["hasta"])
