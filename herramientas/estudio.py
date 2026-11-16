"""ESTUDIO — app local para trabajar los estilos animados (catálogo identidad/estilos-lemo) con el material
de un proyecto, los colores de la marca y exportar la pieza a .mp4 para usarla en guion.json.

  /usr/bin/python3 herramientas/estudio.py [--puerto 8770]      → abre http://localhost:8770
  /usr/bin/python3 herramientas/estudio.py exportar <proyecto> <pieza>   → .mp4 sin abrir nada (Chrome headless)
  http://localhost:8770/mesa → MESA DE GUION (conversación por escena con Claude, ver herramientas/mesa.py)

Cada pieza se guarda en proyectos/<p>/estudio/<pieza>.json (estilo, textos, imágenes, encuadres, marca,
tiempos y "pedidos" para Claude). Claude puede editar ese JSON a mano: la app lo recarga sola.
Exportar deja proyectos/<p>/material/animaciones/<pieza>.mp4 (1920×1080, 30 fps, sin audio) →
en guion.json: {"archivo": "material/animaciones/<pieza>.mp4"}.
Recortes (sacar el fondo de una foto) con rembg del venv → proyectos/<p>/estudio/recortes/.
"""
import argparse
import json
import mimetypes
import re
import shutil
import subprocess
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import mesa

RAIZ = Path(__file__).resolve().parent.parent
PROY = RAIZ / "proyectos"
LEMO = RAIZ / "identidad" / "estilos-lemo"
APP = Path(__file__).resolve().parent / "estudio"
FUENTES = RAIZ / "animaciones" / "futbol" / "assets" / "fonts"
VENV_PY = RAIZ / "herramientas" / ".venv" / "bin" / "python"
IMAGENES = {".jpg", ".jpeg", ".png", ".webp"}
NO_LISTAR = {"candidatas", "fuentes", "audio", "limpias"}
EXPORTS = {}  # id -> carpeta temporal de cuadros
TERMINADO = {"evento": threading.Event(), "resultado": None}


def nombre_ok(s):
    return re.fullmatch(r"[\w\-]{1,80}", s or "") is not None


def dentro(base, ruta):
    p = (base / ruta).resolve()
    if base.resolve() not in p.parents and p != base.resolve():
        raise PermissionError(ruta)
    return p


def pagina():
    S = LEMO / "src"
    cab = (S / "cabecera.html").read_text()
    fuentes_g = next(l for l in cab.splitlines() if "fonts.googleapis.com/css2" in l)
    js = "\n".join(p.read_text() for p in [S / "base.js", S / "ayudas.js", *sorted(S.glob("lote*.js")), *sorted((APP / "estilos").glob("*.js"))])
    app = ((APP / "app.js").read_text() + "\n" + (APP / "capas.js").read_text()).replace("/*CATS*/{}", (S / "categorias.json").read_text().strip())
    html = (APP / "app.html").read_text()
    return (html.replace("<!--FUENTES-->", fuentes_g).replace("/*ESTILOS*/", js).replace("/*APP*/", app))


def recortar(proyecto, ruta):
    src = dentro(PROY / proyecto, ruta)
    out_dir = PROY / proyecto / "estudio" / "recortes"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (src.stem + ".png")
    if not out.exists():
        codigo = (
            "import sys\nfrom PIL import Image\nfrom rembg import new_session, remove\n"
            "im = Image.open(sys.argv[1]).convert('RGB')\n"
            "r = remove(im, session=new_session('u2net'))\n"
            "bb = r.getbbox()\nr = r.crop(bb) if bb else r\nr.save(sys.argv[2])\n")
        subprocess.run([str(VENV_PY), "-c", codigo, str(src), str(out)], check=True, capture_output=True, timeout=600)
    return str(out.relative_to(PROY / proyecto))


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def responder(self, cuerpo, tipo="application/json", codigo=200):
        if isinstance(cuerpo, (dict, list)):
            cuerpo = json.dumps(cuerpo, ensure_ascii=False)
        if isinstance(cuerpo, str):
            cuerpo = cuerpo.encode()
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def archivo(self, p):
        if not p.is_file():
            return self.responder({"error": "no existe"}, codigo=404)
        tipo = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        rango = self.headers.get("Range")
        if not rango:
            return self.responder(p.read_bytes(), tipo)
        total = p.stat().st_size  # Range: para que <video> pueda saltar a cualquier segundo
        a, _, b = rango.replace("bytes=", "").partition("-")
        a = int(a or 0)
        b = min(int(b) if b else a + 4_000_000, total - 1)
        with open(p, "rb") as f:
            f.seek(a)
            datos = f.read(b - a + 1)
        self.send_response(206)
        self.send_header("Content-Type", tipo)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {a}-{b}/{total}")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def cuerpo(self):
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n) if n else b""

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        ruta = unquote(u.path)
        try:
            if ruta in ("/", "/index.html"):
                return self.responder(pagina(), "text/html; charset=utf-8")
            if ruta == "/mesa":
                cab = (LEMO / "src" / "cabecera.html").read_text()
                fuentes_g = next(l for l in cab.splitlines() if "fonts.googleapis.com/css2" in l)
                return self.responder((APP / "mesa.html").read_text().replace("<!--FUENTES-->", fuentes_g), "text/html; charset=utf-8")
            if ruta == "/api/guiones":
                return self.responder(mesa.guiones(q["p"]))
            if ruta == "/api/mesa":
                if not re.fullmatch(r"guion[\w\-]*", q.get("g", "")):
                    return self.responder({"error": "guion"}, codigo=400)
                return self.responder(mesa.estado(q["p"], q["g"]))
            if ruta == "/api/cuadro":
                return self.archivo(mesa.cuadro(q["p"], q["ruta"], q.get("t", 0)))
            if ruta.startswith("/lemo/"):
                return self.archivo(dentro(LEMO, ruta[6:]))
            if ruta.startswith("/fuentes/"):
                return self.archivo(dentro(FUENTES, ruta[9:]))
            if ruta.startswith("/p/"):  # /p/<proyecto>/<ruta>
                _, _, pr, resto = ruta.split("/", 3)
                return self.archivo(dentro(PROY / pr, resto))
            if ruta == "/api/proyectos":
                return self.responder(sorted(p.name for p in PROY.iterdir() if (p / "material").is_dir()))
            if ruta == "/api/material":
                base = PROY / q["p"]
                lista = []
                for f in sorted((base / "material").rglob("*")):
                    rel = f.relative_to(base)
                    if f.suffix.lower() in IMAGENES and not (set(rel.parts) & NO_LISTAR):
                        lista.append(str(rel))
                for f in sorted((base / "estudio" / "recortes").glob("*.png")):
                    lista.append(str(f.relative_to(base)))
                return self.responder(lista)
            if ruta == "/api/piezas":
                d = PROY / q["p"] / "estudio"
                return self.responder(sorted(f.stem for f in d.glob("*.json")) if d.is_dir() else [])
            if ruta == "/api/pieza":
                if not nombre_ok(q.get("n")):
                    return self.responder({"error": "nombre"}, codigo=400)
                f = PROY / q["p"] / "estudio" / f"{q['n']}.json"
                if not f.exists():
                    return self.responder({"error": "no existe"}, codigo=404)
                video = PROY / q["p"] / "material" / "animaciones" / f"{q['n']}.mp4"
                return self.responder({"datos": json.loads(f.read_text()), "mtime": f.stat().st_mtime,
                                       "video": video.exists()})
            return self.responder({"error": "?"}, codigo=404)
        except (PermissionError, KeyError, ValueError) as e:
            return self.responder({"error": str(e)}, codigo=400)

    def do_POST(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if u.path == "/api/pieza":
                if not nombre_ok(q.get("n")):
                    return self.responder({"error": "nombre: letras, números, - y _"}, codigo=400)
                d = PROY / q["p"] / "estudio"
                d.mkdir(parents=True, exist_ok=True)
                f = d / f"{q['n']}.json"
                f.write_text(json.dumps(json.loads(self.cuerpo()), ensure_ascii=False, indent=2) + "\n")
                return self.responder({"ok": True, "mtime": f.stat().st_mtime})
            if u.path == "/api/mesa/mensaje":
                if not re.fullmatch(r"guion[\w\-]*", q.get("g", "")):
                    return self.responder({"error": "guion"}, codigo=400)
                d = json.loads(self.cuerpo())
                m = mesa.mensaje(q["p"], q["g"], d.get("escena", "general"), "humano", d["texto"], d.get("columna", "general"),
                                 d.get("tipo", "nota"), {k: d[k] for k in ("antes", "despues", "t") if k in d})
                return self.responder(m)
            if u.path == "/api/recorte":
                return self.responder({"ruta": recortar(q["p"], json.loads(self.cuerpo())["ruta"])})
            if u.path == "/api/exportar/inicio":
                i = str(len(EXPORTS) + 1)
                EXPORTS[i] = Path(tempfile.mkdtemp(prefix="estudio_"))
                return self.responder({"id": i})
            if u.path == "/api/exportar/cuadro":
                (EXPORTS[q["id"]] / f"{int(q['k']):05d}.jpg").write_bytes(self.cuerpo())
                return self.responder({"ok": True})
            if u.path == "/api/exportar/fin":
                if not nombre_ok(q.get("n")):
                    return self.responder({"error": "nombre"}, codigo=400)
                tmp = EXPORTS.pop(q["id"])
                out = PROY / q["p"] / "material" / "animaciones" / f"{q['n']}.mp4"
                out.parent.mkdir(parents=True, exist_ok=True)
                r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", q.get("fps", "30"), "-i", str(tmp / "%05d.jpg"),
                                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium", str(out)],
                                   capture_output=True, text=True)
                shutil.rmtree(tmp, ignore_errors=True)
                TERMINADO["resultado"] = r.stderr[-800:] if r.returncode else str(out)
                TERMINADO["evento"].set()
                if r.returncode:
                    return self.responder({"error": r.stderr[-800:]}, codigo=500)
                return self.responder({"ruta": str(out.relative_to(PROY / q["p"]))})
            return self.responder({"error": "?"}, codigo=404)
        except subprocess.CalledProcessError as e:
            return self.responder({"error": (e.stderr or b"").decode()[-800:]}, codigo=500)
        except (PermissionError, KeyError, ValueError) as e:
            return self.responder({"error": str(e)}, codigo=400)


CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def exportar_cli(proyecto, pieza, limite=900):
    """Exporta una pieza sin abrir ventanas: servidor en un puerto libre + Chrome headless."""
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://localhost:{srv.server_port}/?p={proyecto}&n={pieza}&exportar=1"
    perfil = tempfile.mkdtemp(prefix="estudio_chrome_")
    ch = subprocess.Popen([CHROME, "--headless=new", f"--user-data-dir={perfil}", "--disable-gpu", "--window-size=1280,800",
                           "--remote-debugging-port=0", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ok = TERMINADO["evento"].wait(limite)
    finally:
        ch.terminate()
        shutil.rmtree(perfil, ignore_errors=True)
        srv.shutdown()
    if not ok:
        raise SystemExit("no terminó a tiempo")
    print(TERMINADO["resultado"])


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "exportar":  # estudio.py exportar <proyecto> <pieza>
        exportar_cli(sys.argv[2], sys.argv[3])
        raise SystemExit
    if len(sys.argv) > 1 and sys.argv[1] == "responder":  # estudio.py responder <proyecto> <guion> <escena|general> "texto"
        mesa.mensaje(sys.argv[2], sys.argv[3], sys.argv[4], "claude", sys.argv[5])
        print("respondido")
        raise SystemExit
    if len(sys.argv) > 1 and sys.argv[1] == "pendientes":  # estudio.py pendientes [<proyecto>]
        for m in mesa.pendientes(sys.argv[2] if len(sys.argv) > 2 else None):
            print(json.dumps(m, ensure_ascii=False))
        raise SystemExit
    ap = argparse.ArgumentParser()
    ap.add_argument("--puerto", type=int, default=8770)
    ap.add_argument("--sin-abrir", action="store_true")
    a = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", a.puerto), H)
    url = f"http://localhost:{a.puerto}/"
    print("ESTUDIO en", url)
    if not a.sin_abrir:
        threading.Timer(.6, lambda: webbrowser.open(url)).start()
    srv.serve_forever()
