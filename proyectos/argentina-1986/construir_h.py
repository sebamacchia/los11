"""Arma guion_h.json desde guion_g.json: reemplaza las animaciones por collages estilo Vox (herramientas/collage.py).
Quedan: intro, capítulos y cierre. Correr: /usr/bin/python3 proyectos/argentina-1986/construir_h.py
"""
import json
from pathlib import Path

AQUI = Path(__file__).parent
g = json.loads((AQUI / "guion_g.json").read_text())
g["archivo"] = "argentina-1986_h"
E = g["escenas"]
FIN = [0, 150, 1920, 960]     # cuadros de final.mp4 / inglaterra.mp4 sin marcador ni marca de agua


def tag(t, x, y, en, color="tinta", tam=30, rot=0, sale=None):
    d = {"tipo": "etiqueta", "texto": t, "x": x, "y": y, "en": en, "color": color, "tam": tam, "rot": rot}
    if sale is not None:
        d["sale"] = sale
    return d


def foto(a, celda, en, sale=None, centro=None, recorte=None, tipo="foto"):
    d = {"tipo": tipo, "celda": celda, "en": en}
    if a:
        d["archivo"] = a if a.startswith("material/") else "material/" + a
    if sale is not None:
        d["sale"] = sale
    if centro:
        d["centro"] = centro
    if recorte:
        d["recorte"] = recorte
    return d


def tit(t, x, y, en, tam=110, marcar=None, sale=None, dibujo=None):
    d = {"tipo": "titulo", "texto": t, "x": x, "y": y, "en": en, "tam": tam}
    if marcar is not None:
        d["marcar"] = marcar
    if sale is not None:
        d["sale"] = sale
    if dibujo:
        d["dibujo"] = dibujo
    return d


def circ(x, y, w, h, en, sale=None):
    d = {"tipo": "circulo", "x": x, "y": y, "ancho": w, "alto": h, "en": en, "dibujo": 0.5}
    if sale is not None:
        d["sale"] = sale
    return d


def flecha(a, b, en, sale=None):
    d = {"tipo": "flecha", "desde": a, "hasta": b, "en": en, "dibujo": 0.35}
    if sale is not None:
        d["sale"] = sale
    return d


def col(piezas, fondos=None, **extra):
    d = {"tipo": "collage", "piezas": piezas, **extra}
    if fondos:
        d["fondos"] = fondos
    return d


def poner(i, j, visual, conservar=("hasta", "duracion")):
    """Reemplaza el visual j de la escena i, conservando su "hasta"/"duracion"."""
    vs = E[i]["visual"] if isinstance(E[i]["visual"], list) else [E[i]["visual"]]
    viejo = vs[j]
    for k in conservar:
        if isinstance(viejo, dict) and k in viejo and k not in visual:
            visual[k] = viejo[k]
    vs[j] = visual
    E[i]["visual"] = vs


def quitar(i, j):
    vs = E[i]["visual"]
    del vs[j]


# ── 3: hook nuevo (pedido del usuario, 14/11): estilo documental ─────────────────────────────────────────────
E[3]["texto"] = ("Esta es la historia de una selección que llegó cuestionada... y terminó campeona del mundo. "
                 "De un equipo que lo dejó todo. Y de un diez imparable. "
                 "Argentina. Maradona. México ochenta y seis. ¿Cómo hicieron para ganar esa Copa?")
E[3]["pausa"] = 0.9
E[3]["visual"] = [{"tipo": "doc", "planos": [
    {"en": 0, "mesa": "papel",
     "capas": [{"archivo": "material/eg_bilardo86.jpg", "x": 560, "y": 540, "alto": 860, "rot": -1.5, "borde": 10}],
     "camara": [{"t": 0, "x": 900, "y": 540, "zoom": 1.0}, {"t": "@y terminó", "x": 1000, "y": 520, "zoom": 1.07}],
     "rotulos": [
         {"tipo": "maquina", "texto": "«Un enano mental.»", "x": 1040, "y": 350, "en": "@una selección", "tam": 46},
         {"tipo": "maquina", "texto": "— César L. Menotti, campeón en 1978", "x": 1044, "y": 425, "en": "@una selección",
          "tam": 22, "mudo": True},
         {"tipo": "maquina", "texto": "«Argentina está diez\n años atrasada.»", "x": 1040, "y": 580, "en": "@llegó", "tam": 40},
         {"tipo": "maquina", "texto": "— L'Équipe, París, 1986", "x": 1044, "y": 705, "en": "@llegó", "tam": 22, "mudo": True},
         {"tipo": "subrayado", "x": 1040, "y": 520, "ancho": 560, "en": "@cuestionada", "dibujo": 0.5}]},
    {"en": "@y terminó", "mesa": "negro",
     "capas": [{"archivo": "material/eg_levanta_copa.jpg", "x": 960, "y": 540, "alto": 1080, "sombra": False}],
     "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}, {"t": "@De un equipo", "x": 900, "y": 460, "zoom": 1.16}],
     "rotulos": [{"tipo": "maquina", "texto": "ESTADIO AZTECA · 29 DE JUNIO DE 1986", "x": 1300, "y": 980,
                  "en": "@campeona", "tam": 20, "claro": True, "mudo": True}]},
    {"en": "@De un equipo", "mesa": "papel",
     "capas": [{"archivo": "material/eg_festejo_tres.jpg", "x": 960, "y": 540, "alto": 940, "rot": 1, "borde": 10}],
     "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}, {"t": "@Y de un diez", "x": 920, "y": 640, "zoom": 1.32}]},
    {"en": "@Y de un diez", "mesa": "papel",
     "capas": [{"archivo": "material/eg_festejo_yako.jpg", "x": 960, "y": 540, "alto": 760, "rot": -1, "borde": 10}],
     "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}, {"t": "@Argentina.", "x": 1120, "y": 450, "zoom": 1.6}]},
    {"en": "@Argentina.", "mesa": "negro",
     "rotulos": [
         {"tipo": "titulo", "texto": "Argentina.", "x": 160, "y": 210, "en": "@Argentina.", "tam": 150, "claro": True,
          "sale": "@¿Cómo"},
         {"tipo": "titulo", "texto": "Maradona.", "x": 160, "y": 380, "en": "@Maradona.", "tam": 150, "claro": True,
          "sale": "@¿Cómo"},
         {"tipo": "titulo", "texto": "México 86.", "x": 160, "y": 550, "en": "@México", "tam": 150, "rojo": True,
          "sale": "@¿Cómo"},
         {"tipo": "maquina", "texto": "¿Cómo hicieron para ganar esa Copa?", "x": 500, "y": 510, "en": "@¿Cómo",
          "tam": 44, "claro": True}]}]}]

# ── 7: Argentina-Perú 1985 ─────────────────────────────────────────────────────────────────────────────────────
poner(7, 3, col([
    tag("Argentina-Perú · Monumental · 30/6/1985", 120, 90, 0.05),
    tit("Perú 2\nArgentina 1", 120, 200, 0.2, 140, [0]),
    tag("1-0 · Pasculli 12'", 140, 600, 0.5, "verde", 32),
    tag("1-1 · Velásquez 23'", 140, 665, 0.75, "rojo", 32),
    tag("1-2 · Barbadillo 39'", 140, 730, 1.0, "rojo", 32),
    foto("eg_passarella_peru.jpg", [1180, 150, 560, 740], 0.3, recorte=[0, 150, 350, 380]),
    tit("A 10 minutos\nde quedar afuera", 120, 820, "@el país", 84, [0]),
]))

# ── 9: Bilardo y sus críticos ──────────────────────────────────────────────────────────────────────────────────
CARD = [140, 180, 520, 700]
poner(9, 0, col([
    foto("eg_bilardo86.jpg", CARD, 0.1, "@Menotti", centro=[0.5, 0.25]),
    tag("Carlos Bilardo · DT", 120, 900, 0.3, "verde", 34, -2, "@Menotti"),
    tit("Lo criticaban\ntodos.", 760, 330, "@lo criticaban", 120, [1], "@Menotti"),
    foto("menotti_fumando.jpg", CARD, "@Menotti", "@Los diarios", centro=[0.5, 0.3]),
    tag("Menotti · campeón 1978", 120, 900, "@Menotti", "tinta", 32, -2, "@Los diarios"),
    tit("«Cobarde y\nenano mental»", 760, 330, "@cobarde", 110, [1], "@Los diarios"),
    tag("L'Équipe · París, 1/4/1986", 760, 260, "@Los diarios", "rojo", 34, 0, "@A Giusti"),
    tit("«Argentina está\ndiez años\natrasada»", 760, 340, "@Los diarios", 100, [1], "@A Giusti"),
    foto("retratos/caras/giusti.png", CARD, "@A Giusti", "@Y el presidente"),
    tag("Ricardo Giusti · Independiente", 120, 900, "@A Giusti", "tinta", 30, -2, "@Y el presidente"),
    tit("«Me silban porque\njuego en la\nselección»", 760, 330, "@A Giusti", 96, [2], "@Y el presidente"),
    foto("alfonsin.jpg", CARD, "@Y el presidente", "@Faltaban", centro=[0.5, 0.3]),
    tag("Raúl Alfonsín · presidente", 120, 900, "@Y el presidente", "tinta", 32, -2, "@Faltaban"),
    tit("«¿Qué estás\nesperando para\necharlo?»", 760, 330, "@qué estás", 104, [2], "@Faltaban"),
    foto("eg_bilardo86.jpg", CARD, "@Faltaban", centro=[0.5, 0.25]),
    tit("Faltaban\n50 días", 760, 300, "@Faltaban", 150, [1]),
    tag("para el Mundial", 780, 680, "@cincuenta", "rojo", 40, -3),
]), conservar=())
E[9]["visual"] = [E[9]["visual"][0]]

# ── 10: "Si lo tocan a Bilardo, nos vamos todos" ───────────────────────────────────────────────────────────────
poner(10, 0, col([
    foto("eg_besa_camiseta.jpg", [120, 150, 900, 600], 0.1, centro=[0.5, 0.35]),
    tag("Maradona · abril de 1986", 120, 780, 0.3, "verde", 32, -2),
    tit("«Si lo tocan\na Bilardo, nos\nvamos todos»", 1080, 220, 0.4, 92, [2]),
]))

# estilo documental (aprobado 14/11): la prueba de la cinta reemplaza el collage y los dos clips (sin el golpe "10")
E[10]["visual"] = [json.loads((AQUI / "prueba_doc.json").read_text())["escenas"][0]["visual"][0]]

# ── 11: España 82 ──────────────────────────────────────────────────────────────────────────────────────────────
poner(11, 2, col([
    tag("La cuenta pendiente", 120, 120, 0.05, "tinta", 30),
    tit("España 82", 120, 220, 0.2, 170, [0]),
    tag("Expulsado contra Brasil", 140, 520, "@expulsado", "rojo", 44, -2),
    tag("Argentina, afuera en segunda fase", 140, 610, "@expulsado", "tinta", 34, 1),
    foto("retratos/caras/maradona.png", [1360, 260, 400, 520], 0.3),
]))

# ── 15: Argentina 3 · Corea 1 ──────────────────────────────────────────────────────────────────────────────────
poner(15, 1, col([
    tag("Grupo A · Olímpico Universitario", 120, 110, 0.05),
    tit("Argentina 3\nCorea del Sur 1", 120, 210, 0.15, 120, [0]),
    tag("Valdano ×2", 140, 560, "@Dos goles", "verde", 40, -2),
    tag("Ruggeri", 140, 640, "@y uno de", "verde", 40, 2),
    tag("Los 3, con pase de Diego", 140, 740, "@Los tres", "rojo", 44, -3),
    foto("eg_valdano.jpg", [1240, 140, 540, 660], "@Dos goles", centro=[0.5, 0.3]),
    foto("eg_ruggeri.jpg", [1100, 640, 420, 310], "@y uno de"),
]))

# ── 17: tabla del grupo ────────────────────────────────────────────────────────────────────────────────────────
filas = [("1 · Argentina · 5 pts", "verde"), ("2 · Italia · 4 pts", "tinta"), ("3 · Bulgaria · 2 pts", "tinta"),
         ("4 · Corea del Sur · 1 pt", "tinta")]
poner(17, 2, col([
    tag("Grupo A · tabla final · 2 puntos por victoria", 120, 110, 0.05),
    tit("Grupo A", 120, 190, 0.1, 120, [0]),
] + [tag(t, 140, 420 + 95 * k, 0.3 + 0.25 * k, c, 46) for k, (t, c) in enumerate(filas)] + [
    circ(100, 385, 640, 130, "@Primera"),
    tit("Sin perder.", 1060, 300, "@Sin perder", 110, [0]),
    tit("Nadie se asustaba\nde Argentina.", 1060, 520, "@Y sin que", 72, [1]),
]))

# ── 21: la búsqueda de la camiseta (la prueba aprobada) ────────────────────────────────────────────────────────
M = "material/"
ING = "collage/ing_323.png"
poner(21, 0, col([
    tag("México 86 · Cuartos de final", 80, 60, 0.05, sale="@A tres días"),
    foto(ING, [120, 160, 720, 700], 0.15, "@A tres días", [0.5, 0.4], [700, 140, 1600, 960]),
    tag("Inglaterra", 90, 820, "@Inglaterra", "rojo", 36, -3, "@A tres días"),
    tit("Se vestía\nde blanco.", 920, 380, "@que se vestía", 120, [1], "@A tres días"),
    tit("19 de junio\nde 1986", 110, 250, "@A tres días", 130, [0], "@Bilardo mandó"),
    tag("Faltan 3 días para Inglaterra", 120, 620, "@del partido", "rojo", 34, -2, "@Bilardo mandó"),
    foto("bilardo.jpg", [1100, 150, 600, 720], "@Bilardo mandó", "@a recorrer", [0.5, 0.3]),
    tag("Carlos Bilardo · DT", 1080, 820, "@Bilardo mandó", "tinta", 32, 2, "@a recorrer"),
    flecha([1080, 420], [860, 440], "@a un colaborador", "@a recorrer"),
    foto(None, [300, 150, 520, 720], "@Rubén", "@a recorrer", tipo="silueta"),
    tag("Rubén Moschella", 270, 820, "@Rubén", "verde", 36, -2, "@a recorrer"),
    tag("Colaborador de la AFA", 280, 890, "@Rubén", "tinta", 24, -2, "@a recorrer"),
    foto("df86_calle3.jpg", [90, 90, 760, 480], "@a recorrer", "@A buscar"),
    tag("CDMX · 1986", 110, 520, "@a recorrer", "tinta", 24, 0, "@A buscar"),
    foto("df86_calle1.jpg", [700, 300, 420, 560], "@los negocios", "@A buscar"),
    tag("CDMX · 1986", 830, 790, "@los negocios", "tinta", 24, 0, "@A buscar"),
    foto("mercado_lagunilla_ropa.jpg", [1150, 110, 680, 440], "@de la Ciudad", "@A buscar"),
    tag("La Lagunilla · hoy", 1170, 500, "@de la Ciudad", "tinta", 24, 0, "@A buscar"),
    foto("tepito_puestos.jpg", [180, 600, 620, 400], "@de México", "@A buscar"),
    tag("Tepito · hoy", 200, 950, "@de México", "tinta", 24, 0, "@A buscar"),
    foto("df86_calle2.jpg", [1180, 560, 640, 420], "@México.", "@A buscar"),
    tag("CDMX · 1986", 1200, 930, "@México.", "tinta", 24, 0, "@A buscar"),
    foto("mercado_merced_vendedor.jpg", [200, 110, 1520, 860], "@A buscar"),
    tit("A buscar\ncamisetas...", 240, 700, "@A buscar", 96, [0, 1], dibujo=0.5),
    circ(930, 330, 300, 380, "@en una tienda"),
    tag("En una tienda", 1200, 660, "@en una tienda", "rojo", 40, -4),
], fondos=[
    {"en": 0, "archivo": M + "fuentes/inglaterra.mp4", "desde": 300},
    {"en": "@Bilardo mandó", "archivo": M + "fuentes/uruguay.mp4", "desde": 34},
    {"en": "@a recorrer", "archivo": M + "df86_zocalo1.jpg"},
    {"en": "@A buscar", "archivo": M + "mercado_merced.jpg"},
]))

# ── 22: los dos modelos, el escudo, los números ────────────────────────────────────────────────────────────────
poner(22, 0, col([
    tit("Volvió con\ndos modelos.", 120, 200, "@Volvió", 120, [1], "@Maradona eligió"),
    tag("Le Coq Sportif · lisas", 140, 560, "@Volvió", "tinta", 36, -2, "@Maradona eligió"),
    foto("collage/ing_331.5.png", [1060, 120, 720, 840], "@Maradona eligió", "@Compraron", [0.55, 0.4],
         [300, 110, 1500, 960]),
    tag("Maradona", 1040, 900, "@Maradona eligió", "verde", 36, -2, "@Compraron"),
    tit("«Con esta le\nganamos a\nInglaterra»", 120, 260, "@y dijo", 100, [2], "@Compraron"),
    tit("38\ncamisetas", 120, 200, "@Compraron", 150, [0], "@les plancharon"),
    foto("collage/ing_229.5.png", [960, 120, 840, 520], "@les cosieron", "@les plancharon", [0.5, 0.3],
         [400, 110, 1500, 780]),
    circ(1340, 160, 300, 300, "@el escudo", "@les plancharon"),
    tag("Escudo de la AFA · cosido a mano", 980, 680, "@el escudo", "rojo", 34, -2, "@les plancharon"),
    foto("collage/ing_365.5.png", [120, 120, 1680, 640], "@les plancharon", centro=[0.3, 0.3],
         recorte=[0, 110, 1920, 780]),
    circ(150, 120, 700, 500, "@números plateados"),
    tag("Números plateados · planchados", 140, 800, "@números plateados", "rojo", 40, -2),
    tag("Como los del fútbol americano", 160, 880, "@de los que", "tinta", 32, 1),
]))

# ── 24: Malvinas, el porqué ────────────────────────────────────────────────────────────────────────────────────
poner(24, 1, col([
    tit("¿Por qué?", 120, 160, 0.05, 130, [0], "@unas islas"),
    foto("malv_satelite.png", [120, 120, 1120, 640], "@unas islas"),
    tag("Puerto Argentino · satélite, 13/6/1982", 120, 790, "@unas islas", "tinta", 28),
    tit("Malvinas", 1300, 160, "@unas islas", 120, [0]),
    tag("Atlántico Sur", 1320, 330, "@en el Atlántico", "tinta", 34),
    tit("500 km\nde la Patagonia", 1300, 430, "@a unos quinientos", 78, [0]),
    tag("Ocupadas por Inglaterra · 1833", 1280, 700, "@Inglaterra las", "rojo", 28, -2),
    tag("Reclamadas por Argentina", 1300, 780, "@y Argentina siempre", "verde", 34, 2),
]))

# ── 25: la guerra en números ───────────────────────────────────────────────────────────────────────────────────
poner(25, 3, col([
    foto("malv_tumbas.jpg", [1080, 160, 720, 520], 0.1),
    tag("Tumbas británicas · Malvinas, 1982", 1080, 710, 0.2, "tinta", 26),
    tit("74 días\nde guerra", 120, 120, 0.15, 84, [0]),
    tit("649 soldados\nargentinos", 120, 420, "@seiscientos", 84, [0]),
    tit("255\nbritánicos", 120, 720, "@doscientos", 84, [0]),
], sfx_volumen=0.25))

# ── 32: la mano de Dios, explicada ─────────────────────────────────────────────────────────────────────────────
poner(32, 0, col([
    tag("Argentina-Inglaterra · 51'", 120, 80, 0.05),
    tit("Hodge la levanta\nhacia atrás.", 120, 360, "@Hodge", 110, [0], "@Shilton sale"),
    foto("eg_mano_shilton.jpg", [120, 110, 1120, 860], "@Shilton sale", centro=[0.45, 0.35]),
    tag("Shilton · 1,83 m · dos manos", 700, 900, "@Shilton sale", "rojo", 34, 2),
    tag("Maradona · 1,65 m", 150, 900, "@Y Diego", "verde", 38, -3),
    tit("Llega\nprimero.", 1320, 300, "@llega primero", 110, [1]),
    circ(300, 110, 420, 360, "@con el puño"),
    tag("El puño", 600, 420, "@con el puño", "rojo", 44, -5),
]))

# ── 34: "la mano de Dios" ──────────────────────────────────────────────────────────────────────────────────────
poner(34, 1, col([
    tag("Maradona, después del partido", 120, 180, 0.05, "verde", 32, -2),
    tit("«Un poco con la cabeza\nde Maradona y otro\npoco con la mano\nde Dios»", 120, 270, 0.15, 92, [3]),
]))

# ── 38: el gol del siglo, cuadro por cuadro ────────────────────────────────────────────────────────────────────
celdas = [(80, 110), (680, 110), (1280, 110), (80, 560), (680, 560), (1280, 560)]
pasos = [("collage/fifa_266.png", "@Arranca", "En su campo"), ("collage/fifa_270.png", "@Beardsley", "Beardsley"),
         ("collage/fifa_271.png", "@Reid", "Reid"), ("collage/fifa_274.png", "@Butcher. Fenwick", "Butcher"),
         ("collage/fifa_275.png", "@Fenwick. Entra", "Fenwick"), ("eludiendo_shilton.jpg", "@Shilton...", "Shilton")]
pzs = [tag("Argentina-Inglaterra · 55'", 80, 40, 0.05, sale="@Sesenta")]
for (x, y), (a, en, nombre) in zip(celdas, pasos):
    pzs += [foto(a, [x, y, 560, 340], en, "@Sesenta"), tag(nombre, x + 10, y + 290, en, "rojo", 30, -2, "@Sesenta")]
pzs += [tag("Butcher, otra vez", 1290, 920, "@y Butcher", "rojo", 30, 2, "@Sesenta"),
        tit("60 metros", 120, 160, "@Sesenta", 130, [0]),
        tit("10,8 segundos", 120, 420, "@Diez segundos", 130, [0]),
        tit("0 toques con\nla derecha", 120, 680, "@Y ni un", 100, [0]),
        foto("eg_fenwick.jpg", [1240, 160, 560, 760], "@Sesenta", centro=[0.3, 0.5])]
poner(38, 0, col(pzs))

# ── 40: Enrique ────────────────────────────────────────────────────────────────────────────────────────────────
poner(40, 1, col([
    foto("retratos/caras/enrique.png", [200, 260, 380, 500], 0.05),
    tag("Héctor Enrique · el del pase", 120, 850, 0.2, "verde", 32, -2),
    tit("«Con el pase\nque le di, no era\npara menos»", 720, 280, 0.3, 100, [2]),
]))

# ── 43: 2-1 ────────────────────────────────────────────────────────────────────────────────────────────────────
poner(43, 0, col([
    tag("Cuartos de final · Estadio Azteca", 120, 110, 0.05),
    tit("Argentina 2\nInglaterra 1", 120, 210, 0.15, 130, [0]),
    tag("Lineker 81'", 140, 600, "@Lineker", "rojo", 40, -2),
    tag("A semifinales", 140, 690, "@A semifinales", "verde", 52, 2),
    foto("eg_festejo_yako.jpg", [1160, 140, 640, 780], 0.3, centro=[0.62, 0.4]),
    tag("Foto: Dani Yako", 1180, 880, 0.4, "tinta", 22),
]))

# ── 44: suscribite ─────────────────────────────────────────────────────────────────────────────────────────────
poner(44, 0, col([
    tit("Y todavía faltaba\nuna final.", 120, 200, 0.05, 100, [1], "@Si te gustan"),
    foto("eg_telefono.jpg", [1160, 150, 620, 760], "@Si te gustan", centro=[0.35, 0.4]),
    tag("México, 1986", 1180, 860, "@Si te gustan", "tinta", 26),
    tit("Suscribite\na LOS 11", 120, 250, "@suscribite", 140, [1]),
    tag("Todo el fútbol, como merece ser contado", 140, 640, "@acá contamos", "verde", 34, -2),
]))

# ── 48: el camino y los diarios ────────────────────────────────────────────────────────────────────────────────
ruta = [("Grupo A · Corea 3-1 · Italia 1-1 · Bulgaria 2-0", "tinta"), ("Octavos · Uruguay 1-0", "tinta"),
        ("Cuartos · Inglaterra 2-1", "tinta"), ("Semifinal · Bélgica 2-0", "verde")]
poner(48, 1, col([
    tit("Invicta.", 120, 150, 0.05, 130, [0], "@Y un solo"),
] + [tag(t, 140, 400 + 90 * k, 0.25 + 0.3 * k, c, 38, 0, "@Y un solo") for k, (t, c) in enumerate(ruta)] + [
    tag("5 victorias · 1 empate", 140, 790, "@cinco victorias", "rojo", 44, -2, "@Y un solo"),
    foto("eg_tapa_3481.jpg", [1180, 110, 560, 860], "@Y un solo", recorte=[690, 780, 1250, 1560]),
    tag("El Gráfico · 24/6/1986", 1160, 920, "@Y un solo", "tinta", 28, -2),
    tit("«No llores\npor mí,\nInglaterra»", 120, 280, "@Y un solo", 120, [2]),
]))

# ── 50: Beckenbauer y Matthäus ─────────────────────────────────────────────────────────────────────────────────
poner(50, 1, col([
    foto("retratos/caras/beckenbauer.png", [200, 260, 380, 500], 0.05),
    tag("Franz Beckenbauer · DT", 120, 850, 0.2, "tinta", 34, -2),
    tit("Campeón como\njugador en 1974", 720, 300, 0.3, 96, [1]),
    tag("Eliminó a la Francia de Platini", 740, 600, "@que en semifinales", "rojo", 34, 2),
]))
poner(50, 3, col([
    foto("retratos/caras/matthaus.png", [200, 260, 380, 500], 0.05),
    tag("Lothar Matthäus · Nº 8", 120, 850, 0.2, "tinta", 34, -2),
    tit("Misión:\nperseguir\na Diego", 720, 260, 0.3, 120, [2]),
]))

# ── 51: la formación ───────────────────────────────────────────────────────────────────────────────────────────
pos = {"Pumpido": (110, 430), "Cuciuffo": (470, 150), "Brown": (470, 430), "Ruggeri": (470, 710),
       "Giusti": (850, 60), "Batista": (850, 310), "Enrique": (850, 560), "Olarticoechea": (850, 810),
       "Burruchaga": (1230, 280), "Valdano": (1230, 600), "Diego": (1580, 400)}
pzs = [tag("Final · 3-5-2", 1560, 60, 0.05, "verde", 34)]
for n, (x, y) in pos.items():
    a = "maradona" if n == "Diego" else n.lower()
    t = 220 if n == "Diego" else 180
    pzs += [foto(f"retratos/caras/{a}.png", [x, y, t, t], "@" + n),
            tag(n, x, y + t - 10, "@" + n, "rojo" if n == "Diego" else "tinta", 24 if n != "Diego" else 32)]
pzs[1]["en"] = pzs[2]["en"] = "@Pumpido"
poner(51, 0, col(pzs))

# ── 52: el gol de Brown ────────────────────────────────────────────────────────────────────────────────────────
poner(52, 0, col([
    tag("Argentina-Alemania · 23'", 120, 60, 0.05),
    foto("collage/fin_116.5.png", [120, 140, 840, 390], "@tiro libre", recorte=FIN),
    tag("Tiro libre · Burruchaga", 130, 490, "@tiro libre", "tinta", 30, -2),
    foto("collage/fin_119.5.png", [1000, 140, 800, 390], "@sale a buscarla", recorte=FIN),
    tag("Schumacher sale", 1010, 490, "@sale a buscarla", "rojo", 30, 2),
    tit("...y se queda.", 1000, 590, "@se queda", 90, [0]),
    foto("retratos/caras/brown.png", [120, 600, 380, 380], "@Y José Luis"),
    tag("José Luis Brown", 120, 940, "@Y José Luis", "verde", 32, -2),
    tit("Su primer gol\ncon la selección", 540, 760, "@que nunca", 70, [0]),
], hasta="@la cabecea"))

# ── 57: el pase ────────────────────────────────────────────────────────────────────────────────────────────────
poner(57, 0, col([
    tag("Argentina-Alemania · 84'", 120, 60, 0.05),
    foto("collage/fin_465.5.png", [120, 140, 840, 400], "@Mirá el pase", recorte=FIN),
    tag("3 alemanes encima", 130, 500, "@tres alemanes", "rojo", 32, -2),
    foto("collage/fin_467.png", [1000, 140, 800, 400], "@Levanta", recorte=FIN),
    tag("Levanta la cabeza · una vez", 1010, 500, "@Levanta", "tinta", 30, 2),
    foto("collage/fin_469.png", [120, 600, 840, 400], "@cuarenta metros", recorte=FIN),
    tag("40 metros · un toque", 130, 960, "@cuarenta metros", "verde", 32, -2),
    tag("Briegel no llega", 680, 640, "@Briegel", "rojo", 30, 3),
    tit("Lo más\nsimple.", 1060, 640, "@hizo lo más", 130, [1]),
]))

# ── 61: 5 y 5 ──────────────────────────────────────────────────────────────────────────────────────────────────
poner(61, 1, col([
    tag("Maradona en México 86", 120, 130, 0.05, "tinta", 32),
    tit("5 goles\n5 asistencias", 120, 230, 0.15, 130, [0, 1]),
    tag("Balón de Oro del Mundial", 140, 620, "@y el Balón", "verde", 44, -2),
    foto("eg_levanta_copa.jpg", [1240, 120, 520, 860], 0.3, centro=[0.5, 0.3]),
]))

# ── 64: la subasta ─────────────────────────────────────────────────────────────────────────────────────────────
poner(64, 1, col([
    foto("hodge_camiseta.jpg", [140, 160, 560, 700], "@Después del partido", "@En dos mil"),
    tag("Steve Hodge", 120, 880, "@Steve Hodge", "rojo", 36, -2, "@En dos mil"),
    tit("La cambió con\nun inglés.", 780, 240, "@Después del partido", 100, [1], "@Hodge la guardó"),
    foto("nfm_manchester.jpg", [780, 200, 1000, 620], "@Hodge la guardó", "@En dos mil"),
    tag("National Football Museum · Manchester", 790, 850, "@Hodge la guardó", "tinta", 28, 0, "@En dos mil"),
    tit("36 años", 800, 80, "@treinta y seis", 100, [0], "@En dos mil"),
    foto("sothebys.jpg", [140, 120, 600, 820], "@En dos mil"),
    tag("Sotheby's · Londres · 4/5/2022", 120, 900, "@En dos mil", "tinta", 30, -2),
    tit("US$ 9,3\nmillones", 820, 250, "@por más de", 160, [0, 1]),
    tag("£7.142.500", 840, 650, "@por más de", "verde", 44, -2),
    tag("Récord para un objeto deportivo (2022)", 840, 740, "@La camiseta", "rojo", 34, 2),
]))

# ── 65: las tres copas ─────────────────────────────────────────────────────────────────────────────────────────
poner(65, 0, col([
    tit("Pasaron\n40 años.", 120, 160, "@Pasaron", 120, [1]),
    tag("1978 · Argentina", 140, 520, "@Pasaron", "tinta", 40),
    tag("1986 · México", 140, 600, "@Argentina volvió", "verde", 52, -2),
    tag("2022 · Qatar · Messi", 140, 700, "@en Qatar", "tinta", 40),
    foto("eg_tapa_3482.jpg", [1160, 110, 600, 860], 0.3, recorte=[600, 980, 1465, 1914], centro=[0.4, 0.5]),
    tag("El Gráfico · 1/7/1986", 1140, 920, 0.4, "tinta", 28, -2),
]))

(AQUI / "guion_h.json").write_text(json.dumps(g, ensure_ascii=False, indent=1))
n = sum(1 for e in E for v in (e["visual"] if isinstance(e["visual"], list) else [e["visual"]])
        if isinstance(v, dict) and v.get("tipo") == "collage")
quedan = sorted({v.get("tipo") for e in E for v in (e["visual"] if isinstance(e["visual"], list) else [e["visual"]])
                 if isinstance(v, dict) and v.get("tipo")})
print(f"guion_h.json: {n} collages; tipos que quedan: {quedan}")
