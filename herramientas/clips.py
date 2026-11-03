"""Videos de partidos: buscar, bajar, mirar y cortar.

  python3 herramientas/clips.py buscar "Liverpool Milan 2005 final highlights" [n]
  python3 herramientas/clips.py bajar <url> proyectos/<p>/material/fuentes [nombre]
  python3 herramientas/clips.py hoja <video> [cada_seg] [desde] [hasta]   -> hoja de contacto con tiempos
  python3 herramientas/clips.py cortes <video>                           -> tiempos de cambio de plano
  python3 herramientas/clips.py cortar <video> <inicio> <fin> <destino.mp4>

En el guion se usan así:
  {"archivo": "material/fuentes/final.mp4", "desde": 312.5, "velocidad": 0.6}
(sin audio original; "velocidad" < 1 = cámara lenta)
"""
import json
import subprocess
import sys
from pathlib import Path


def buscar(q, n=10):
    r = subprocess.run(["yt-dlp", f"ytsearch{n}:{q}", "--flat-playlist", "-J", "--cookies-from-browser", "chrome"],
                       capture_output=True, text=True)
    for e in json.loads(r.stdout).get("entries", []):
        d = e.get("duration") or 0
        print(f"{e.get('url') or e['id']}  [{int(d)//60}:{int(d)%60:02}]  {e.get('channel', '?')[:24]:<24} {e.get('title', '')[:80]}")


def bajar(url, carpeta, nombre=None):
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    plantilla = f"{nombre}.%(ext)s" if nombre else "%(title).60s.%(ext)s"
    subprocess.run(["yt-dlp", url, "-f", "bv*[height<=1080]+ba/b[height<=1080]",
                    "--merge-output-format", "mp4", "-o", str(carpeta / plantilla),
                    "--no-playlist", "--restrict-filenames", "--cookies-from-browser", "chrome"], check=True)
    with open(carpeta / "fuentes.txt", "a") as f:
        f.write(f"{nombre or '?'}: {url}\n")


def hoja(video, cada=5.0, desde=0.0, hasta=None, salida=None):
    """Una imagen con un cuadro cada `cada` segundos y el tiempo escrito en cada uno."""
    from PIL import Image, ImageDraw, ImageFont
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                video], capture_output=True, text=True).stdout)
    hasta = min(float(hasta or dur), dur)
    tiempos = []
    t = float(desde)
    while t < hasta and len(tiempos) < 60:
        tiempos.append(t)
        t += float(cada)
    tw, th, cols = 384, 216, 6
    hojaimg = Image.new("RGB", (tw * cols, th * ((len(tiempos) + cols - 1) // cols)), "black")
    f = ImageFont.truetype("/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf", 26)
    for k, t in enumerate(tiempos):
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                            "-vf", f"scale={tw}:{th}", "-f", "image2pipe", "-vcodec", "png", "-"],
                           capture_output=True)
        if not r.stdout:
            continue
        import io
        im = Image.open(io.BytesIO(r.stdout)).convert("RGB")
        d = ImageDraw.Draw(im)
        etiqueta = f"{int(t)//60}:{t%60:04.1f}"
        d.rectangle([0, 0, 110, 34], fill="black")
        d.text((6, 3), etiqueta, font=f, fill=(232, 179, 58))
        hojaimg.paste(im, ((k % cols) * tw, (k // cols) * th))
    salida = salida or str(Path(video).with_suffix("")) + f"_hoja_{int(desde)}.jpg"
    hojaimg.save(salida, quality=85)
    print(salida)


def cortes(video, umbral=0.35):
    r = subprocess.run(["ffmpeg", "-i", video, "-vf", f"select='gt(scene,{umbral})',showinfo", "-an",
                        "-f", "null", "-"], capture_output=True, text=True)
    ts = [float(l.split("pts_time:")[1].split()[0]) for l in r.stderr.splitlines() if "pts_time:" in l]
    print(" ".join(f"{t:.1f}" for t in ts))


def cortar(video, ini, fin, destino):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ini), "-i", video, "-t", str(float(fin) - float(ini)),
                    "-c:v", "libx264", "-crf", "18", "-an", destino], check=True)
    print(destino)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    {"buscar": lambda: buscar(a[1], int(a[2]) if len(a) > 2 else 10),
     "bajar": lambda: bajar(a[1], a[2], a[3] if len(a) > 3 else None),
     "hoja": lambda: hoja(a[1], *(a[2:5])),
     "cortes": lambda: cortes(a[1]),
     "cortar": lambda: cortar(*a[1:5])}[a[0]]()
