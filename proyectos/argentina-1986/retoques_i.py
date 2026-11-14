# Retoques a mano de guion_i (lo ejecuta construir_i.py después de la conversión automática). Usa E, g.

# ── 11: Nápoles (1986, camiseta Buitoni; fotos libres de Commons) ──────────────────────────────────────────────
E[11]["visual"][1] = {"tipo": "doc", "hasta": "@Pero en los", "planos": [
    {"en": 0, "mesa": "papel",
     "capas": [{"archivo": "material/maradona_napoli_fotografos.jpg", "x": 700, "y": 500, "alto": 620, "rot": -1.4,
                "borde": 10},
               {"archivo": "material/maradona_companeros_napoli.jpg", "recorte": [735, 0, 1140, 761], "x": 1440,
                "y": 590, "alto": 760, "rot": 1.6, "borde": 10, "en": "@y su pase"}],
     "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}],
     "rotulos": [{"tipo": "maquina", "texto": "NÁPOLES · ESTADIO SAN PAOLO", "x": 260, "y": 900, "en": "@el Nápoles",
                  "tam": 26, "fondo_tira": True},
                 {"tipo": "maquina", "texto": "BARCELONA → NÁPOLES, 1984\nEL PASE MÁS CARO DEL MUNDO", "x": 1120,
                  "y": 80, "en": "@el más caro", "tam": 26, "fondo_tira": True}]}]}

# ── música del final: orquestal que crece (musica_i.py, hace falta la clave de ElevenLabs) ─────────────────────
_mus = AQUI.parent.parent / "musica"
if (_mus / "m86_final_orquestal.mp3").exists():
    g["musica"] = [m for m in g["musica"] if m["desde"] < 50] + [
        {"archivo": "../../musica/m86_final_orquestal.mp3", "desde": 50, "hasta": 64, "volumen": 0.3,
         "fade_in": 1.5, "fade_out": 2.5}]
    if (_mus / "m86_epilogo_orquestal.mp3").exists():
        g["musica"].append({"archivo": "../../musica/m86_epilogo_orquestal.mp3", "desde": 65, "hasta": 67,
                            "volumen": 0.26, "fade_in": 1.5, "fade_out": 3})

# ── 51: la formación de la final, sobre una cancha dibujada en tinta ─────────────────────────────────────────────
for _v in E[51]["visual"]:
    if _v.get("tipo") == "doc":
        _v["planos"][0]["cancha"] = True
for _v in E[51]["visual"]:
    if _v.get("tipo") == "doc":
        _v["planos"][0]["camara"] = [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}]  # la cancha entera, quieta (simetría)

# cámara fija en los planos hechos a mano (solo queda el zoom con intención a la cinta de capitán, escena 10 plano 3)
def _fijar(esc, salvo=()):
    for _v in E[esc]["visual"]:
        if _v.get("tipo") == "doc":
            for _k, _pl in enumerate(_v["planos"]):
                if _k not in salvo:
                    _pl["camara"] = [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}]
_fijar(3)
_fijar(10, salvo=(2,))
for _v in E[10]["visual"]:
    if _v.get("tipo") == "doc":
        _c = _v["planos"][2]["camara"]
        _c[0].update(x=960, y=540, zoom=1.0)
        _c[1].update(x=960, y=540, zoom=1.0)   # quieta hasta "le dio", y de ahí el zoom a la cinta
