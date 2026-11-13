# Archivos grandes (Google Drive)

GitHub tiene el código, los guiones, el árbol de carpetas y las referencias. Los archivos pesados no entran:
videos, fotos, música, voz ya generada y piezas renderizadas. Están en **Google Drive > LOS11/repo/**, con las
**mismas rutas** que en el repo. La lista completa, con el tamaño de cada uno, está en
[`archivos_grandes.txt`](archivos_grandes.txt).

| Ruta | Qué es |
| --- | --- |
| `proyectos/*/material/` | fotos, videos fuente (`fuentes/`), retratos, `creditos.txt` |
| `proyectos/*/salida/` | video final, `.fcproj` de FilmCraft, subtítulos, capítulos, `graficos/` |
| `proyectos/*/tmp_guion_*/` | piezas ya renderizadas de la última versión (para `--reusar`) |
| `musica/` | música de ElevenLabs Music |
| `.cache/` | voz y efectos de ElevenLabs ya pagados (sin esto se vuelven a cobrar) |
| `animaciones/**/assets/*.mp4, *.webm` | clips usados por las animaciones HyperFrames |
| `herramientas/filmcraft-cli/` | CLI de FilmCraft |

No están en ningún lado y hay que crearlos a mano: `.env` (`ELEVENLABS_API_KEY=...`) y las fuentes DIN, que
ya vienen con macOS.

## En otra compu

```bash
git clone https://github.com/sebamacchia/los11.git   # o: git pull
cd los11
python3 herramientas/archivos_grandes.py bajar     # con Google Drive para escritorio instalado
python3 herramientas/archivos_grandes.py faltan    # verifica que no falte nada
```

Sin Drive para escritorio: bajar `LOS11/repo` desde drive.google.com y copiar su contenido encima del repo.

## Al terminar de trabajar

```bash
python3 herramientas/archivos_grandes.py subir     # copia lo nuevo a Drive y rehace archivos_grandes.txt
git add -A && git commit -m "..." && git push
```
