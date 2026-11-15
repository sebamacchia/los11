#!/usr/bin/env python3
"""Archivos grandes del repo (los que .gitignore deja afuera de GitHub) <-> Google Drive.

GitHub tiene el código, los guiones y el árbol; Drive (carpeta LOS11/repo) tiene los archivos pesados en las
MISMAS rutas que en el repo. `archivos_grandes.txt` (en el repo) lista cada archivo con su tamaño.

  python3 herramientas/archivos_grandes.py lista    # rehace archivos_grandes.txt con lo que hay local
  python3 herramientas/archivos_grandes.py subir    # copia lo local a Drive (LOS11/repo) y rehace la lista
  python3 herramientas/archivos_grandes.py bajar    # copia de Drive al repo lo que falte (pide Drive para escritorio)
  python3 herramientas/archivos_grandes.py faltan   # qué archivos de la lista no están en esta compu

Sin Drive para escritorio: bajar la carpeta LOS11/repo desde drive.google.com y copiar su contenido encima del repo.
"""
import glob
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTA = os.path.join(RAIZ, "archivos_grandes.txt")
# ignorados que NO van a Drive: secretos, entornos, temporales y fuentes DIN (licencia de Apple, ya están en macOS)
FUERA = (".env", ".venv/", "venv/", "__pycache__/", "node_modules/", ".DS_Store", "cookies", ".cookies",
         "/.hyperframes/", "/renders/", "fonts/din-", ".pyc")


def drive():
    rutas = glob.glob(os.path.expanduser("~/Library/CloudStorage/GoogleDrive-*/My Drive/LOS11"))
    if not rutas:
        sys.exit("No encuentro Google Drive para escritorio (~/Library/CloudStorage/GoogleDrive-*/My Drive/LOS11).")
    return os.path.join(rutas[0], "repo")


def ignorados():
    out = subprocess.run(["git", "ls-files", "--others", "--ignored", "--exclude-standard"],
                         cwd=RAIZ, capture_output=True, text=True, check=True).stdout.splitlines()
    return sorted(p for p in out if not any(f in "/" + p for f in FUERA))


def leer_lista():
    with open(LISTA, encoding="utf-8") as f:
        return [l.rstrip("\n").split("\t")[1] for l in f if l.strip() and not l.startswith("#")]


def mb(n):
    return f"{n / 1e6:,.1f} MB" if n < 1e9 else f"{n / 1e9:,.2f} GB"


def lista():
    archivos = ignorados()
    total = 0
    with open(LISTA, "w", encoding="utf-8") as f:
        f.write("# Archivos grandes: NO están en GitHub, están en Google Drive > LOS11/repo/ con la misma ruta.\n"
                "# Bajarlos con: python3 herramientas/archivos_grandes.py bajar   (ver ARCHIVOS_GRANDES.md)\n"
                "# bytes\truta\n")
        for p in archivos:
            n = os.path.getsize(os.path.join(RAIZ, p))
            total += n
            f.write(f"{n}\t{p}\n")
    print(f"{len(archivos)} archivos, {mb(total)} -> archivos_grandes.txt")
    return archivos


def rsync(origen, destino, archivos):
    tmp = os.path.join(RAIZ, ".cache", "_lista_rsync.txt")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(archivos) + "\n")
    subprocess.run(["rsync", "-a", "--ignore-existing" if destino == RAIZ else "--update",
                    f"--files-from={tmp}", origen + "/", destino + "/"], check=True)
    os.remove(tmp)


def faltan():
    falta = [p for p in leer_lista() if not os.path.exists(os.path.join(RAIZ, p))]
    for p in falta:
        print("  falta:", p)
    print(f"{len(falta)} de {len(leer_lista())} archivos faltan en esta compu.")
    return falta


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "faltan"
    if cmd == "lista":
        lista()
    elif cmd == "subir":
        d = drive()
        archivos = lista()
        os.makedirs(d, exist_ok=True)
        rsync(RAIZ, d, archivos)
        print("Copiado a", d, "(Drive lo sube en segundo plano).")
    elif cmd == "bajar":
        d = drive()
        archivos = [p for p in leer_lista() if os.path.exists(os.path.join(d, p))]
        rsync(d, RAIZ, archivos)
        faltan()
    elif cmd == "faltan":
        faltan()
    else:
        sys.exit(__doc__)
