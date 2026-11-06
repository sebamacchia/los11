"""Arma un video a partir de proyectos/<nombre>/guion.json.

Uso:  python3 herramientas/armar.py proyectos/<nombre> [--solo-audio] [--borrador] [--reusar] [--filmcraft] [--guion otro.json]
      --reusar: no vuelve a dibujar las escenas que ya están en tmp/ con la misma duración
      --filmcraft: además arma salida/<archivo>.fcproj (FilmCraft) con cada pieza como clip, para editar a mano
                   (no pisa un .fcproj que ya existe; --forzar lo rehace)

Tipos de visual (cada escena tiene una lista "visual"):
  "material/foto.jpg"                                  foto fija, entera, con negro a los costados
  {"archivo": "...", "zocalo": "NOMBRE", "sub": "..."} foto + zócalo con nombre
  {"archivo": "clip.mp4", "desde": 12.5}              video (sin audio original)
  {"tipo": "intro", "sub": "El milagro de Estambul"}  animación del canal
  {"tipo": "placa", "texto": "6 MINUTOS", "sub": "...", "etiqueta": "..."}
  {"tipo": "marcador", "local": "MILAN", "visitante": "LIVERPOOL", "goles": [3, 0],
   "etiqueta": "ENTRETIEMPO", "cambios": [[1.0, 3, 1, "Gerrard 54'"]]}
Cualquier visual acepta "duracion"; el resto de la escena se reparte en partes iguales.
Música: "musica": [{"archivo": "...", "desde": <n° escena>, "hasta": <n° escena>, "volumen": 0.2}]
(escenas numeradas desde 1; "hasta" incluida).
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import elevenlabs  # noqa: E402
import graficos  # noqa: E402

FPS = 30
FORMATOS = {"horizontal": (1920, 1080), "vertical": (1080, 1920)}
IMAGENES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
VOZ_POR_DEFECTO = {"voice_id": "3bwJ6wzKqreWHSoA0x43", "model_id": "eleven_v4",
                   "ajustes": {"stability": 0.5, "similarity_boost": 0.75}}


def run(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("ffmpeg falló:\n" + " ".join(map(str, cmd)) + "\n" + r.stderr[-3000:])


def duracion(archivo):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(archivo)], capture_output=True, text=True)
    return float(r.stdout.strip())


def _enc(calidad):
    return ["-c:v", "libx264", "-preset", "veryfast" if calidad == "borrador" else "medium",
            "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]


def render_imagen(src, dest, dur, W, H, calidad, zocalo=None):
    """Foto fija, entera (sin recortar), con negro donde sobre."""
    base = (f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,setsar=1")
    cmd = ["ffmpeg", "-y", "-loop", "1", "-t", f"{dur:.3f}", "-i", src]
    if zocalo:
        cmd += ["-loop", "1", "-t", f"{dur:.3f}", "-i", zocalo, "-filter_complex",
                f"[0:v]{base}[b];[1:v]format=rgba,fade=t=in:st=0.4:d=0.4:alpha=1,"
                f"fade=t=out:st={max(0.5, dur - 0.5):.2f}:d=0.4:alpha=1[z];[b][z]overlay=0:0,format=yuv420p"]
    else:
        cmd += ["-vf", base + ",format=yuv420p"]
    run(cmd + ["-t", f"{dur:.3f}"] + _enc(calidad) + [dest])


def render_video(src, dest, dur, W, H, desde, calidad, vel=1.0, zocalo=None, zoom=None, centro=(0.5, 0.45)):
    """Clip de video entero (con negro si no es 16:9), sin audio. vel < 1 = cámara lenta.
    zoom: número (primer plano fijo) o [inicio, fin] (la cámara se acerca de a poco); centro = punto a acercar (0-1)."""
    vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,setsar=1"
    if vel != 1.0:
        vf = f"setpts=PTS/{vel}," + vf + f",minterpolate=fps={FPS}:mi_mode=blend"
    else:
        vf += f",fps={FPS}"
    if zoom:
        z0, z1 = (zoom, zoom) if isinstance(zoom, (int, float)) else zoom
        n = max(1, round(dur * FPS))
        cx, cy = centro
        vf += (f",scale={W*2}:{H*2}:flags=lanczos,zoompan=z='{z0}+({z1}-{z0})*min(on/{n},1)'"
               f":x='(iw-iw/zoom)*{cx}':y='(ih-ih/zoom)*{cy}':d=1:s={W}x{H}:fps={FPS}")
    cmd = ["ffmpeg", "-y", "-ss", str(desde), "-t", f"{dur * vel + 0.1:.3f}", "-i", src]
    if zocalo:
        cmd += ["-loop", "1", "-t", f"{dur:.3f}", "-i", zocalo, "-filter_complex",
                f"[0:v]{vf}[b];[1:v]format=rgba,fade=t=in:st={min(0.3, dur*0.1):.2f}:d={min(0.4, dur*0.2):.2f}:alpha=1,"
                f"fade=t=out:st={max(0.2, dur - min(0.5, dur*0.25)):.2f}:d={min(0.4, dur*0.2):.2f}:alpha=1[z];[b][z]overlay=0:0,format=yuv420p"]
    else:
        cmd += ["-vf", vf + ",format=yuv420p"]
    run(cmd + ["-t", f"{dur:.3f}"] + _enc(calidad) + [dest])


def srt_tiempo(t):
    h, m = int(t // 3600), int(t % 3600 // 60)
    s = t % 60
    ms = min(999, int(round((s % 1) * 1000)))
    return f"{h:02}:{m:02}:{int(s):02},{ms:03}"


def frases(texto, max_chars=84):
    import re
    partes = re.split(r"(?<=[.!?…;:])\s+", texto.strip())
    out = []
    for p in partes:
        while len(p) > max_chars:
            corte = p.rfind(",", 0, max_chars)
            corte = corte if corte > 20 else p.rfind(" ", 0, max_chars)
            out.append(p[:corte + 1].strip())
            p = p[corte + 1:].strip()
        if p:
            out.append(p)
    return out


def momento(esc, valor, info):
    """Segundos desde el inicio de la escena. Acepta un número o "@frase" (cuando el narrador dice esa frase)."""
    if isinstance(valor, str) and valor.startswith("@"):
        texto = esc.get("texto", "")
        pos = texto.find(valor[1:])
        if pos < 0:
            raise SystemExit(f"No encuentro '{valor[1:]}' en el texto de la escena")
        retardo, d_voz = info
        return retardo + d_voz * pos / max(1, len(texto))
    return float(valor)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    proyecto = Path(sys.argv[1]).resolve()
    calidad = "borrador" if "--borrador" in sys.argv else "final"
    archivo_guion = sys.argv[sys.argv.index("--guion") + 1] if "--guion" in sys.argv else "guion.json"
    guion = json.loads((proyecto / archivo_guion).read_text())
    W, H = FORMATOS[guion.get("formato", "horizontal")]
    vozcfg = {**VOZ_POR_DEFECTO, **guion.get("voz", {})}
    tmp = proyecto / ("tmp" if archivo_guion == "guion.json" else "tmp_" + Path(archivo_guion).stem)
    tmp.mkdir(exist_ok=True)
    salida = proyecto / "salida"
    salida.mkdir(exist_ok=True)
    escenas = guion["escenas"]

    # 1) audio: narración y efectos, y la línea de tiempo
    t = float(guion.get("intro", 0.2))
    voces, efectos, srt, tiempos, info = [], [], [], [], []
    for i, esc in enumerate(escenas):
        pausa = float(esc.get("pausa", guion.get("pausa", 0.45)))
        retardo = float(esc.get("retardo", 0))  # silencio antes de que hable
        d_voz = 0
        if esc.get("texto"):
            mp3 = elevenlabs.voz(esc["texto"], vozcfg["voice_id"], vozcfg["model_id"], vozcfg.get("ajustes"))
            d_voz = duracion(mp3)
            voces.append((mp3, t + retardo))
            fr = frases(esc.get("subtitulo", esc["texto"]))
            total = sum(len(f) for f in fr)
            tt = t + retardo
            for f in fr:
                df = d_voz * len(f) / total
                srt.append((tt, tt + df, f))
                tt += df
        d_esc = float(esc.get("duracion", retardo + d_voz + pausa))
        info.append((retardo, d_voz))
        for s in esc.get("sfx", []):
            mp3 = elevenlabs.efecto(s["prompt"], s.get("duracion"))
            en = momento(esc, s.get("en", 0), info[-1])
            efectos.append((mp3, t + en, float(s.get("volumen", 0.5))))
        tiempos.append((t, d_esc))
        t += d_esc
    outro = float(guion.get("outro", 1.0))
    total = t + outro
    print(f"Duración total: {total:.1f}s ({total/60:.1f} min, {len(escenas)} escenas)")

    with open(salida / "subtitulos.srt", "w") as f:
        for n, (a, b, txt) in enumerate(srt, 1):
            f.write(f"{n}\n{srt_tiempo(a)} --> {srt_tiempo(b)}\n{txt}\n\n")
    with open(salida / "capitulos.txt", "w") as f:
        for i, esc in enumerate(escenas):
            if esc.get("capitulo"):
                s = 0 if not f.tell() else int(tiempos[i][0])
                f.write(f"{s // 60}:{s % 60:02} {esc['capitulo']}\n")

    if "--solo-audio" in sys.argv:
        return

    # 2) video
    piezas = []
    linea = {"piezas": [], "voces": [{"archivo": str(m), "inicio": a} for m, a in voces],
             "efectos": [{"archivo": str(m), "inicio": a, "volumen": v * float(guion.get("sfx_volumen", 1.0))}
                         for m, a, v in efectos],
             "musica": [], "total": total, "subtitulos": str(salida / "subtitulos.srt"),
             "fps": FPS, "ancho": W, "alto": H}
    t_pieza = 0.0
    for i, esc in enumerate(escenas):
        inicio, d_esc = tiempos[i]
        if i == 0:
            d_esc += inicio
        if i == len(escenas) - 1:
            d_esc += outro
        visuales = esc.get("visual") or []
        if isinstance(visuales, (str, dict)):
            visuales = [visuales]
        if not visuales:
            raise SystemExit(f"La escena {i+1} no tiene 'visual'")
        visuales = [{"archivo": v} if isinstance(v, str) else dict(v) for v in visuales]
        pos = -inicio if i == 0 else 0.0
        for v in visuales:  # "hasta": "@frase" -> el visual termina cuando el narrador dice esa frase
            if "hasta" in v:
                v["duracion"] = round(momento(esc, v["hasta"], info[i]) - pos, 3)
                if v["duracion"] < 0.5:
                    raise SystemExit(f"Escena {i+1}: el visual que termina en '{v['hasta']}' queda de "
                                     f"{v['duracion']}s (los visuales de antes ya ocupan ese tiempo)")
            if "duracion" not in v:
                break
            pos += float(v["duracion"])
        fijos = sum(float(v["duracion"]) for v in visuales if "duracion" in v)
        libres = [v for v in visuales if "duracion" not in v]
        d_libre = (d_esc - fijos) / len(libres) if libres else 0
        if libres and d_libre < 0.5:
            raise SystemExit(f"Escena {i+1}: las duraciones fijas no entran en {d_esc:.1f}s")
        if not libres and abs(fijos - d_esc) > 0.05:  # ajusta la última para que cierre justo
            visuales[-1] = {**visuales[-1], "duracion": float(visuales[-1]["duracion"]) + d_esc - fijos}
        offset = -inicio if i == 0 else 0.0  # dónde arranca cada visual, en tiempo de escena
        for j, v in enumerate(visuales):
            d = float(v.get("duracion", d_libre))
            v_ini = offset
            offset += d
            dest = tmp / f"p{i:03}_{j:02}.mp4"
            tipo = v.get("tipo", "archivo")
            firma = tmp / f"p{i:03}_{j:02}.json"
            sello = json.dumps({**v, "_d": round(d, 3)}, sort_keys=True)
            linea["piezas"].append({"archivo": str(dest), "inicio": round(t_pieza, 4), "duracion": round(d, 4),
                                    "escena": i + 1, "nombre": f"{i+1:02}.{j+1} {v.get('tipo', '') or Path(v.get('archivo', '')).stem}"
                                    + (f" · {v['zocalo']}" if v.get('zocalo') else "")
                                    + (f" · {v['texto']}" if v.get('texto') else "")})
            t_pieza += d
            if "--reusar" in sys.argv and dest.exists() and firma.exists() and firma.read_text() == sello:
                piezas.append(dest)
                continue
            firma.write_text(sello)
            if tipo == "intro":
                graficos.intro(dest, W, H, d, v.get("sub", ""))
                etiqueta = "intro"
            elif tipo == "placa":
                graficos.placa(dest, W, H, d, v["texto"], v.get("sub", ""), v.get("etiqueta", ""))
                etiqueta = f"placa '{v['texto']}'"
            elif tipo == "marcador":
                cambios = [[momento(esc, c[0], info[i]) - v_ini] + list(c[1:]) for c in v.get("cambios", [])]
                graficos.marcador(dest, W, H, d, v["local"], v["visitante"], v["goles"],
                                  v.get("etiqueta", ""), cambios)
                etiqueta = f"marcador {v['goles']}"
            else:
                src = (proyecto / v["archivo"]).resolve()
                if not src.exists():
                    raise SystemExit(f"No existe {src}")
                zoc = None
                if v.get("zocalo"):
                    zoc = tmp / f"z{i:03}_{j:02}.png"
                    graficos.zocalo(zoc, W, H, v["zocalo"], v.get("sub", ""))
                if src.suffix.lower() in IMAGENES:
                    render_imagen(src, dest, d, W, H, calidad, zoc)
                else:
                    render_video(src, dest, d, W, H, v.get("desde", 0), calidad,
                                 float(v.get("velocidad", 1.0)), zoc, v.get("zoom"), v.get("centro", (0.5, 0.45)))
                etiqueta = src.name
            piezas.append(dest)
            print(f"  {i+1:>2}.{j+1} {etiqueta} ({d:.1f}s)")

    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in piezas))
    mudo = tmp / "mudo.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", mudo])

    # 3) mezcla: voz + efectos + música (la música baja sola cuando habla la voz)
    # (en dos pasos: mezclar audio y video en un solo ffmpeg con ~50 entradas se cuelga)
    cmd = ["ffmpeg", "-y"]
    filtros, n = [], 0

    def entrada(archivo, inicio, vol, etiqueta, loop=False):
        nonlocal n
        if loop:
            cmd.extend(["-stream_loop", "-1"])
        cmd.extend(["-i", archivo])
        ms = int(inicio * 1000)
        filtros.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=stereo,"
                       f"volume={vol},adelay={ms}|{ms}[{etiqueta}]")
        n += 1

    for k, (mp3, inicio) in enumerate(voces):
        entrada(mp3, inicio, 1.0, f"v{k}")
    sfx_vol = float(guion.get("sfx_volumen", 1.0))
    for k, (mp3, inicio, vol) in enumerate(efectos):
        entrada(mp3, inicio, vol * sfx_vol, f"s{k}")
        d = duracion(mp3)  # entra y sale suave, nada de golpes
        fi, fo = min(0.8, d / 4), min(1.5, d / 3)
        filtros[-1] = filtros[-1].replace(f"volume={vol * sfx_vol}",
                                          f"volume={vol * sfx_vol},afade=t=in:d={fi:.2f},afade=t=out:st={d - fo:.2f}:d={fo:.2f}")
    filtros.append("".join(f"[v{k}]" for k in range(len(voces))) +
                   f"amix=inputs={len(voces)}:normalize=0,asplit=2[voz][vozsc]")
    mezcla = ["[voz]"] + [f"[s{k}]" for k in range(len(efectos))]
    musicas = guion.get("musica") or []
    if isinstance(musicas, dict):
        musicas = [{**musicas, "desde": 1, "hasta": len(escenas)}]
    if musicas:
        for k, m in enumerate(musicas):
            a = tiempos[m.get("desde", 1) - 1][0] if m.get("desde", 1) > 1 else 0
            hasta = m.get("hasta", len(escenas))
            b = (tiempos[hasta - 1][0] + tiempos[hasta - 1][1]) if hasta < len(escenas) else total
            largo = b - a
            pista = (proyecto / m["archivo"]).resolve()
            vueltas = int(largo // duracion(pista))  # loops finitos: con -1 ffmpeg queda girando para siempre
            cmd.extend(["-stream_loop", str(vueltas), "-i", pista])
            fi = float(m.get("fade_in", 1.0))
            fo = float(m.get("fade_out", 1.5))
            ms = int(a * 1000)
            filtros.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=stereo,atrim=0:{largo:.3f},"
                           f"volume={m.get('volumen', 0.2)},afade=t=in:d={fi},"
                           f"afade=t=out:st={max(0, largo - fo):.2f}:d={fo},adelay={ms}|{ms}[m{k}]")
            n += 1
            linea["musica"].append({"archivo": str(pista), "inicio": a, "largo": largo, "volumen": float(m.get("volumen", 0.2)),
                                    "fade_in": fi, "fade_out": fo})
        filtros.append("".join(f"[m{k}]" for k in range(len(musicas))) +
                       f"amix=inputs={len(musicas)}:normalize=0[mus]")
        filtros.append("[mus][vozsc]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=500[musd]")
        mezcla.append("[musd]")
    else:
        filtros.append("[vozsc]anullsink")
    filtros.append("".join(mezcla) + f"amix=inputs={len(mezcla)}:normalize=0,"
                   f"apad,atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
    audio = tmp / "audio.wav"
    run(cmd + ["-filter_complex", ";".join(filtros), "-map", "[aout]", "-t", f"{total:.3f}",
               "-c:a", "pcm_s16le", audio])
    nombre = guion.get("archivo", proyecto.name) + (".borrador" if calidad == "borrador" else "") + ".mp4"
    run(["ffmpeg", "-y", "-i", mudo, "-i", audio, "-vf", f"fade=t=out:st={total-0.8:.2f}:d=0.8",
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
         "-t", f"{total:.3f}", salida / nombre])
    print(f"Listo: {salida / nombre}\nSubtítulos: {salida / 'subtitulos.srt'}")
    (tmp / "linea.json").write_text(json.dumps(linea, ensure_ascii=False, indent=1))
    if "--filmcraft" in sys.argv:
        import filmcraft
        print("FilmCraft:", filmcraft.exportar(tmp / "linea.json", salida / (guion.get("archivo", proyecto.name) + ".fcproj"),
                                                     forzar="--forzar" in sys.argv))


if __name__ == "__main__":
    main()
