"""Arma guion_i.json desde guion_h.json: TODO el video al estilo documental aprobado el 14/11
(herramientas/documental.py: fotos impresas sobre una mesa de papel, cámara con zoom con intención, textos a máquina,
títulos contundentes, marcador rojo a mano, grano de película).

- Cada collage Vox se convierte automáticamente (convertir_collage) y después se retocan a mano las escenas clave.
- Cada foto fija suelta pasa a un plano "doc" con la foto impresa y un acercamiento lento.
- Los clips de partido quedan como están (son el documento).
Correr: /usr/bin/python3 proyectos/argentina-1986/construir_i.py
"""
import json
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).parent
g = json.loads((AQUI / "guion_h.json").read_text())
g["archivo"] = "argentina-1986_i"
E = g["escenas"]
FOTOS = {".jpg", ".jpeg", ".png", ".webp"}


def _tam(archivo):
    return Image.open(AQUI / archivo).size


def recorte_celda(archivo, celda, recorte=None, centro=None):
    """Caja de recorte de la fuente equivalente a ImageOps.fit(celda, centro) del collage."""
    sw, sh = _tam(archivo)
    x0, y0, x1, y1 = recorte or (0, 0, sw, sh)
    w, h = x1 - x0, y1 - y0
    cw, ch = celda[2], celda[3]
    cx, cy = centro or (0.5, 0.5)
    if w / h > cw / ch:  # sobra ancho
        nw = h * cw / ch
        ox = (w - nw) * cx
        return [int(x0 + ox), y0, int(x0 + ox + nw), y1]
    nh = w * ch / cw
    oy = (h - nh) * cy
    return [x0, int(y0 + oy), x1, int(y0 + oy + nh)]


def cuadro_de(archivo, desde):
    """Cuadro congelado de un clip (para usar el fondo de contexto del collage como foto impresa)."""
    import subprocess
    dest = AQUI / "material" / "collage" / f"fondo_{Path(archivo).stem}_{desde}.png"
    if not dest.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(desde), "-i", str(AQUI / archivo),
                        "-frames:v", "1", str(dest)], check=True)
    return str(dest.relative_to(AQUI))


def fondos_a_capas(fondos):
    """Los fondos de contexto del collage pasan a ser fotos grandes impresas, debajo de todo."""
    capas = []
    for k, f in enumerate(fondos or []):
        a = f["archivo"]
        if Path(a).suffix.lower() not in FOTOS:
            a = cuadro_de(a, f.get("desde", 0))
        sw, sh = _tam(a)
        alto = min(940, int(1680 * sh / sw))
        c = {"archivo": a, "x": 960, "y": 540, "alto": alto, "rot": [0.6, -0.5][k % 2], "borde": 12,
             "en": f.get("en", 0)}
        if a.endswith(".png") and "fuentes" not in a and "collage/fondo_" in a:
            c["recorte"] = [0, int(sh * 0.14), sw, int(sh * 0.89)]  # sin marcador ni marca de agua de la TV
            c["alto"] = min(940, int(1680 * (c["recorte"][3] - c["recorte"][1]) / sw))
        if k + 1 < len(fondos):
            c["sale"] = fondos[k + 1].get("en", 0)
        capas.append(c)
    return capas


def convertir_collage(v, k_esc=0):
    capas, rotulos, camara = fondos_a_capas(v.get("fondos")), [], [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}]
    pose = (960, 540, 1.0)
    n_fotos = 0
    for p in v["piezas"]:
        t = p.get("en", 0)
        tipo = p["tipo"]
        if tipo in ("foto", "silueta") and p.get("archivo"):
            x, y, w, h = p["celda"]
            rec = p.get("recorte")
            if "collage/ing_" in p["archivo"] or "collage/fin_" in p["archivo"]:  # sin marcador ni logo de la TV
                sw, sh = _tam(p["archivo"])
                rec = rec or [0, 0, sw, sh]
                rec = [rec[0], max(rec[1], 150), rec[2], min(rec[3], 960)]
                p = dict(p, recorte=rec)
            c = {"archivo": p["archivo"], "x": x + w / 2, "y": y + h / 2, "alto": h,
                 "recorte": recorte_celda(p["archivo"], p["celda"], p.get("recorte"), p.get("centro")),
                 "rot": [-1.2, 0.9, -0.6, 1.4][(n_fotos + k_esc) % 4], "borde": 9, "en": t}
            if p.get("sale") is not None:
                c["sale"] = p["sale"]
            if p.get("bn"):
                c["bn"] = True
            if min(_tam(p["archivo"])) < 420:   # foto chica: que se note la trama de imprenta, no los píxeles
                c["trama"] = 5
            capas.append(c)
            # la cámara se inclina un poco hacia la foto nueva
            if False:  # 14/11: el usuario pidió cámara fija (los paneos marean); solo zoom con intención
                nueva = (960 + (x + w / 2 - 960) * 0.22, 540 + (y + h / 2 - 540) * 0.22, min(1.12, 1.04 + 0.02 * n_fotos))
                camara += [{"t": [t, 0], "x": pose[0], "y": pose[1], "zoom": pose[2]},
                           {"t": [t, 1.4], "x": nueva[0], "y": nueva[1], "zoom": nueva[2]}]
                pose = nueva
            n_fotos += 1
        elif tipo == "silueta":
            x, y, w, h = p["celda"]
            r = {"tipo": "titulo", "texto": "?", "x": x + w / 2 - 60, "y": y + h / 2 - 160, "tam": 300, "rojo": True,
                 "en": t}
            if p.get("sale") is not None:
                r["sale"] = p["sale"]
            rotulos.append(r)
        elif tipo == "etiqueta":
            r = {"tipo": "maquina", "texto": p["texto"].upper() if len(p["texto"]) < 40 else p["texto"],
                 "x": p["x"], "y": p["y"], "en": t, "tam": max(20, int(p.get("tam", 30) * 0.78)), "fondo_tira": True}
            if p.get("color") == "rojo":
                r["rojo"] = True
            if p.get("sale") is not None:
                r["sale"] = p["sale"]
            rotulos.append(r)
        elif tipo == "titulo":
            cita = p["texto"].lstrip().startswith("«")
            tam = int(p.get("tam", 110) * (0.5 if cita else 0.8))
            r = {"tipo": "maquina" if cita else "titulo", "texto": p["texto"], "x": p["x"], "y": p["y"], "en": t,
                 "tam": tam, "fondo_tira": True}
            if p.get("sale") is not None:
                r["sale"] = p["sale"]
            rotulos.append(r)
            lh = tam * (1.45 if cita else 1.02)
            cw = tam * (0.6 if cita else 0.53)
            for i in []:  # 14/11: sin subrayado rojo en los títulos (al usuario no le gusta: "tachado con el rojo pedorro")
                lineas = p["texto"].split("\n")
                if i < len(lineas):
                    s = {"tipo": "subrayado", "x": p["x"], "y": int(p["y"] + (i + 1) * lh - tam * 0.12),
                         "ancho": int(len(lineas[i]) * cw), "en": t, "dibujo": 0.5}
                    if p.get("sale") is not None:
                        s["sale"] = p["sale"]
                    rotulos.append(s)
        elif tipo == "circulo":
            cx, cy = p["x"] + p["ancho"] / 2, p["y"] + p["alto"] / 2
            r = {"tipo": "circulo", "x": cx, "y": cy, "ancho": p["ancho"], "alto": p["alto"], "en": t, "dibujo": 0.6}
            if p.get("sale") is not None:
                r["sale"] = p["sale"]
            rotulos.append(r)
            # zoom con intención: la cámara va hacia lo que se marca
            z = max(1.25, min(1.9, 0.42 * 1920 / max(p["ancho"], p["alto"] * 1.78)))
            camara += [{"t": [t, 0], "x": pose[0], "y": pose[1], "zoom": pose[2]},
                       {"t": [t, 1.3], "x": cx, "y": cy, "zoom": z}]
            pose = (cx, cy, z)
            if p.get("sale") is not None:
                camara += [{"t": [p["sale"], -0.01], "x": cx, "y": cy, "zoom": z},
                           {"t": [p["sale"], 0], "x": 960, "y": 540, "zoom": 1.0}]  # vuelve en corte, no en paneo
                pose = (960, 540, 1.0)
        elif tipo == "flecha":
            r = {"tipo": "flecha", "desde": p["desde"], "hasta": p["hasta"], "en": t}
            if p.get("sale") is not None:
                r["sale"] = p["sale"]
            rotulos.append(r)
    for r in rotulos:
        r["mundo"] = True
    d = {"tipo": "doc", "planos": [{"en": 0, "mesa": "papel", "capas": capas, "camara": camara, "rotulos": rotulos}]}
    for k in ("hasta", "duracion", "fin"):
        if k in v:
            d[k] = v[k]
    return d


def foto_doc(v, k):
    """Foto fija suelta -> foto impresa sobre la mesa con acercamiento lento."""
    a = v["archivo"]
    sw, sh = _tam(a)
    alto = 900 if sw / sh < 1.75 else int(1500 * sh / sw)
    c = {"archivo": a, "x": 960, "y": 540, "alto": alto, "rot": [-1, 0.8, -0.5][k % 3], "borde": 10}
    if min(sw, sh) < 420:
        c["trama"] = 5
    foco = v.get("foco", [0.5, 0.42])
    ancho = alto * sw / sh
    fx, fy = 960 + (foco[0] - 0.5) * ancho, 540 + (foco[1] - 0.5) * alto
    d = {"tipo": "doc", "planos": [{"en": 0, "mesa": "papel", "capas": [c],
                                    "camara": [{"t": 0, "x": 960, "y": 540, "zoom": 1.0}]}]}
    for key in ("hasta", "duracion", "fin"):
        if key in v:
            d[key] = v[key]
    return d


n_col = n_fot = 0
for i, e in enumerate(E):
    vs = e.get("visual")
    if not vs:
        continue
    vs = vs if isinstance(vs, list) else [vs]
    nuevos = []
    for j, v in enumerate(vs):
        if isinstance(v, str):
            v = {"archivo": v}
        if v.get("tipo") == "collage":
            v = convertir_collage(v, i)
            n_col += 1
        elif not v.get("tipo") and Path(v.get("archivo", "")).suffix.lower() in FOTOS and not v.get("golpe"):
            v = foto_doc(v, i + j)
            n_fot += 1
        nuevos.append(v)
    e["visual"] = nuevos

# ── retoques a mano ─────────────────────────────────────────────────────────────────────────────────────────────
exec((AQUI / "retoques_i.py").read_text()) if (AQUI / "retoques_i.py").exists() else None

(AQUI / "guion_i.json").write_text(json.dumps(g, ensure_ascii=False, indent=1))
print(f"guion_i.json: {n_col} collages y {n_fot} fotos pasados a estilo documental")
