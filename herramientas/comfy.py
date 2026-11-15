"""ANIME IA (pedido 14/11): un clip pasado a dibujo animado con Stable Diffusion en ComfyUI (local, GPU del Mac).

Flujo: ffmpeg saca cuadros a N dibujos/s -> ComfyUI (AnyLoRA + ControlNet lineart + AnimateDiff para que no tiemble,
img2img con denoise) -> cuadros repetidos a 30 fps (animación "en dos/tres/cuatro") -> suciedad VHS de efecto_anime.Cinta.

  # 1) servidor (dejarlo corriendo):
  herramientas/comfyui/.venv/bin/python herramientas/comfyui/main.py --port 8188 --force-fp16
  # 2) clip:
  herramientas/.venv/bin/python herramientas/comfy.py <video> <desde> <dur> <salida.mp4>
      [--dibujos 8] [--denoise 0.6] [--control 0.8] [--ancho 768] [--pasos 20] [--semilla 7] [--suciedad 1]
      [--sin-ad] (cuadro por cuadro, sin AnimateDiff: tiembla más) [--prompt "..."]
      [--seguir X,Y] cámara que sigue al jugador de camiseta azul que está en (X,Y) del cuadro 1920x1080 inicial
      [--encuadre 720] ancho del recorte en px del original (más chico = más cerca)
      [--cara retrato.png] [--peso-cara 0.6] la cara de referencia (IPAdapter) para el jugador seguido
  # primer plano de anime (cara grande) a partir de un retrato, 4 variantes:
  herramientas/.venv/bin/python herramientas/comfy.py primerplano <retrato.png> <carpeta_salida> [--prompt "..."]

Los cuadros generados quedan en caché en .cache/comfy/<hash>/ (si no cambia nada, no se vuelve a generar).
"""
import hashlib
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from efecto_anime import Cinta, W, H, FPS  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SERVIDOR = "http://127.0.0.1:8188"
PROMPT = ("1980s anime screencap, retro tv anime, cel animation, soccer match on a bright green pitch, "
          "argentina player with curly black hair, dark blue shirt, black shorts, "
          "england players in white shirts and light blue shorts, short brown hair, "
          "bold black ink outlines, flat cel shading, hand painted background, vibrant saturated colors, dynamic")
PROMPT_PP = ("1980s anime screencap, retro tv anime, extreme close-up of a young football player's face, curly black hair, "
             "dark brown eyes, intense determined eyes, thick eyebrows, gritted teeth, sweat drops, dark blue shirt, dramatic speed lines background, "
             "bold black ink outlines, flat cel shading, vibrant colors")
NEGATIVO = ("blue eyes, red hair, orange hair, blonde hair, green shirt, photo, photorealistic, realistic, 3d render, blurry, lowres, jpeg artifacts, text, watermark, logo, "
            "deformed, extra limbs, bad anatomy, nsfw")


def args():
    a = sys.argv[1:]
    op = {"dibujos": "8", "denoise": "0.6", "control": "0.8", "ancho": "768", "pasos": "20", "semilla": "7",
          "suciedad": "1", "prompt": PROMPT, "cfg": "7", "encuadre": "720", "peso-cara": "0.6"}
    flags, pos, i = set(), [], 0
    while i < len(a):
        if a[i] in ("--sin-ad",):
            flags.add(a[i][2:])
            i += 1
        elif a[i].startswith("--"):
            op[a[i][2:]] = a[i + 1]
            i += 2
        else:
            pos.append(a[i])
            i += 1
    return pos, op, flags


def flujo(carpeta, op, flags, prefijo, alto):
    ancho = int(op["ancho"])
    g = {
        "img": {"class_type": "VHS_LoadImagesPath", "inputs": {"directory": str(carpeta), "image_load_cap": 0,
                                                                "skip_first_images": 0, "select_every_nth": 1}},
        "ckpt": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "AnyLoRA_noVae_fp16-pruned.safetensors"}},
        "vae": {"class_type": "VAELoader", "inputs": {"vae_name": "vae-ft-mse-840000-ema-pruned.safetensors"}},
        "pos": {"class_type": "CLIPTextEncode", "inputs": {"text": op["prompt"], "clip": ["ckpt", 1]}},
        "neg": {"class_type": "CLIPTextEncode", "inputs": {"text": NEGATIVO, "clip": ["ckpt", 1]}},
        "lin": {"class_type": "LineArtPreprocessor", "inputs": {"image": ["img", 0], "coarse": "disable",
                                                               "resolution": alto}},
        "cnl": {"class_type": "ControlNetLoader", "inputs": {"control_net_name": "control_v11p_sd15_lineart_fp16.safetensors"}},
        "cn": {"class_type": "ControlNetApplyAdvanced", "inputs": {
            "positive": ["pos", 0], "negative": ["neg", 0], "control_net": ["cnl", 0], "image": ["lin", 0],
            "strength": float(op["control"]), "start_percent": 0.0, "end_percent": 1.0}},
        "esc": {"class_type": "ImageScale", "inputs": {"image": ["img", 0], "upscale_method": "lanczos",
                                                       "width": ancho, "height": alto, "crop": "disabled"}},
        "lat": {"class_type": "VAEEncode", "inputs": {"pixels": ["esc", 0], "vae": ["vae", 0]}},
        "ks": {"class_type": "KSampler", "inputs": {
            "model": ["ad", 0] if "sin-ad" not in flags else ["ckpt", 0],
            "seed": int(op["semilla"]), "steps": int(op["pasos"]), "cfg": float(op["cfg"]),
            "sampler_name": "dpmpp_2m", "scheduler": "karras", "positive": ["cn", 0], "negative": ["cn", 1],
            "latent_image": ["lat", 0], "denoise": float(op["denoise"])}},
        "dec": {"class_type": "VAEDecode", "inputs": {"samples": ["ks", 0], "vae": ["vae", 0]}},
        "out": {"class_type": "SaveImage", "inputs": {"images": ["dec", 0], "filename_prefix": prefijo}},
    }
    modelo = ["ckpt", 0]
    if op.get("cara"):
        g["cv"] = {"class_type": "CLIPVisionLoader", "inputs": {"clip_name": "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"}}
        g["ipm"] = {"class_type": "IPAdapterModelLoader", "inputs": {"ipadapter_file": "ip-adapter-plus-face_sd15.safetensors"}}
        g["ref"] = {"class_type": "LoadImage", "inputs": {"image": subir(op["cara"])}}
        g["ipa"] = {"class_type": "IPAdapterAdvanced", "inputs": {
            "model": modelo, "ipadapter": ["ipm", 0], "image": ["ref", 0], "weight": float(op["peso-cara"]),
            "weight_type": "linear", "combine_embeds": "concat", "start_at": 0.0, "end_at": 1.0,
            "embeds_scaling": "V only", "clip_vision": ["cv", 0]}}
        if op.get("mascara"):
            g["msk"] = {"class_type": "LoadImageMask", "inputs": {"image": subir(op["mascara"]), "channel": "red"}}
            g["ipa"]["inputs"]["attn_mask"] = ["msk", 0]
        modelo = ["ipa", 0]
    g["ks"]["inputs"]["model"] = modelo
    if "sin-ad" not in flags:
        g["ctx"] = {"class_type": "ADE_StandardUniformContextOptions", "inputs": {
            "context_length": 16, "context_stride": 1, "context_overlap": 4, "fuse_method": "pyramid",
            "use_on_equal_length": False, "start_percent": 0.0, "guarantee_steps": 1}}
        g["ad"] = {"class_type": "ADE_AnimateDiffLoaderGen1", "inputs": {
            "model": modelo, "model_name": "v3_sd15_mm.ckpt", "beta_schedule": "autoselect",
            "context_options": ["ctx", 0]}}
        g["ks"]["inputs"]["model"] = ["ad", 0]
    return g


def subir(ruta):
    """Copia una imagen a herramientas/comfyui/input (LoadImage solo lee de ahí) y devuelve su nombre."""
    import shutil
    ruta = Path(ruta)
    dest = RAIZ / "herramientas/comfyui/input" / f"los11_{hashlib.sha1(ruta.read_bytes()).hexdigest()[:10]}{ruta.suffix}"
    dest.parent.mkdir(exist_ok=True)
    if not dest.exists():
        shutil.copy(ruta, dest)
    return dest.name


def seguir(video, desde, dur, dib, x0, y0, encuadre, ancho, alto, carpeta):
    """Recorte que sigue al jugador de camiseta azul (mancha azul más cercana a la posición anterior)."""
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(desde), "-t", str(dur), "-i", video, "-vf", f"fps={dib}",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(b, np.uint8).reshape(-1, H, W, 3)
    pos, (x, y) = [], (x0, y0)
    for f in fr:
        hsv = cv2.cvtColor(f, cv2.COLOR_RGB2HSV)
        m = ((hsv[..., 0] > 100) & (hsv[..., 0] < 125) & (hsv[..., 1] > 90) & (hsv[..., 2] > 60)).astype(np.uint8)
        n, _, st, c = cv2.connectedComponentsWithStats(cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)))
        cand = [(np.hypot(c[i][0] - x, c[i][1] - y), c[i]) for i in range(1, n)
                if st[i][4] > 600 and st[i][3] < 500 and np.hypot(c[i][0] - x, c[i][1] - y) < 260]
        if cand:
            x, y = min(cand, key=lambda t: t[0])[1]
        pos.append((x, y))
    pos = np.array(pos, np.float32)
    from scipy.ndimage import gaussian_filter1d
    pos = gaussian_filter1d(pos, 1.2, axis=0, mode="nearest")
    cw, chh = encuadre, int(encuadre * 9 / 16)
    for k, (f, (x, y)) in enumerate(zip(fr, pos)):
        cx = int(np.clip(x - cw / 2, 0, W - cw))
        cy = int(np.clip(y + chh * 0.08 - chh / 2, 0, H - chh))  # la camiseta un poco arriba del centro
        rec = cv2.resize(f[cy:cy + chh, cx:cx + cw], (ancho, alto), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(carpeta / f"f{k + 1:04d}.png"), cv2.cvtColor(rec, cv2.COLOR_RGB2BGR))
    print("seguimiento:", " ".join(f"{int(a)},{int(b)}" for a, b in pos[::4]))


def mascara_centro(ancho, alto, ruta):
    """Elipse blanda en el centro (donde queda el jugador seguido): solo ahí actúa la cara de referencia."""
    m = np.zeros((alto, ancho), np.float32)
    cv2.ellipse(m, (ancho // 2, int(alto * 0.45)), (int(ancho * 0.16), int(alto * 0.46)), 0, 0, 360, 1, -1)
    m = cv2.GaussianBlur(m, (0, 0), ancho * 0.03)
    cv2.imwrite(str(ruta), (np.dstack([m, m, m]) * 255).astype(np.uint8))


def pedir(ruta, datos=None):
    req = urllib.request.Request(SERVIDOR + ruta, data=json.dumps(datos).encode() if datos else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def generar(carpeta, op, flags, alto):
    prefijo = "los11_" + carpeta.parent.name[:10]
    r = pedir("/prompt", {"prompt": flujo(carpeta, op, flags, prefijo, alto)})
    return esperar(r["prompt_id"])


def esperar(pid):
    t0 = time.time()
    while True:
        h = pedir(f"/history/{pid}")
        if pid in h:
            est = h[pid].get("status", {})
            if est.get("status_str") == "error":
                raise SystemExit("ComfyUI dio error: " + json.dumps(est.get("messages", []))[-1500:])
            imgs = h[pid]["outputs"]["out"]["images"]
            break
        time.sleep(5)
        print(f"  generando... {time.time() - t0:.0f}s", flush=True)
    salida = RAIZ / "herramientas/comfyui/output"
    return [salida / i["subfolder"] / i["filename"] for i in imgs]


def primerplano(retrato, carpeta, op):
    """Cara de anime grande a partir de un retrato: img2img + lineart + IPAdapter cara, 4 semillas."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    prompt = op["prompt"] if op["prompt"] != PROMPT else PROMPT_PP
    r = cv2.imread(str(retrato))
    h, w = r.shape[:2]
    lado = int(h * 0.25)
    r = cv2.copyMakeBorder(r, lado, lado, 0, 0, cv2.BORDER_REPLICATE)
    h = r.shape[0]
    extra = (int(h * 16 / 9) - w) // 2
    lienzo = cv2.copyMakeBorder(r, 0, 0, extra, extra, cv2.BORDER_REPLICATE)
    borroso = cv2.GaussianBlur(lienzo, (0, 0), 25)
    m = np.zeros(lienzo.shape[:2], np.float32)
    m[lado:h - lado, extra:extra + w] = 1
    m = cv2.GaussianBlur(m, (0, 0), 12)[..., None]
    lienzo = (lienzo * m + borroso * (1 - m)).astype(np.uint8)
    ancho_r = carpeta / "_retrato_16x9.png"
    cv2.imwrite(str(ancho_r), lienzo)
    retrato_ref = retrato
    retrato = ancho_r
    g = {
        "ckpt": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "AnyLoRA_noVae_fp16-pruned.safetensors"}},
        "vae": {"class_type": "VAELoader", "inputs": {"vae_name": "vae-ft-mse-840000-ema-pruned.safetensors"}},
        "img": {"class_type": "LoadImage", "inputs": {"image": subir(retrato)}},
        "ref": {"class_type": "LoadImage", "inputs": {"image": subir(retrato_ref)}},
        "esc": {"class_type": "ImageScale", "inputs": {"image": ["img", 0], "upscale_method": "lanczos",
                                                       "width": 768, "height": 432, "crop": "center"}},
        "pos": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["ckpt", 1]}},
        "neg": {"class_type": "CLIPTextEncode", "inputs": {"text": NEGATIVO, "clip": ["ckpt", 1]}},
        "lin": {"class_type": "LineArtPreprocessor", "inputs": {"image": ["esc", 0], "coarse": "enable", "resolution": 432}},
        "cnl": {"class_type": "ControlNetLoader", "inputs": {"control_net_name": "control_v11p_sd15_lineart_fp16.safetensors"}},
        "cn": {"class_type": "ControlNetApplyAdvanced", "inputs": {
            "positive": ["pos", 0], "negative": ["neg", 0], "control_net": ["cnl", 0], "image": ["lin", 0],
            "strength": 0.55, "start_percent": 0.0, "end_percent": 0.7}},
        "cv": {"class_type": "CLIPVisionLoader", "inputs": {"clip_name": "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"}},
        "ipm": {"class_type": "IPAdapterModelLoader", "inputs": {"ipadapter_file": "ip-adapter-plus-face_sd15.safetensors"}},
        "ipa": {"class_type": "IPAdapterAdvanced", "inputs": {
            "model": ["ckpt", 0], "ipadapter": ["ipm", 0], "image": ["ref", 0], "weight": 0.7, "weight_type": "linear",
            "combine_embeds": "concat", "start_at": 0.0, "end_at": 1.0, "embeds_scaling": "V only", "clip_vision": ["cv", 0]}},
        "enc": {"class_type": "VAEEncode", "inputs": {"pixels": ["esc", 0], "vae": ["vae", 0]}},
        "rep": {"class_type": "RepeatLatentBatch", "inputs": {"samples": ["enc", 0], "amount": 4}},
        "ks": {"class_type": "KSampler", "inputs": {
            "model": ["ipa", 0], "seed": int(op["semilla"]), "steps": 25, "cfg": 7.5, "sampler_name": "dpmpp_2m",
            "scheduler": "karras", "positive": ["cn", 0], "negative": ["cn", 1], "latent_image": ["rep", 0],
            "denoise": float(op.get("denoise-pp", 0.78))}},
        "dec": {"class_type": "VAEDecode", "inputs": {"samples": ["ks", 0], "vae": ["vae", 0]}},
        "out": {"class_type": "SaveImage", "inputs": {"images": ["dec", 0], "filename_prefix": "los11_pp"}},
    }
    archivos = esperar(pedir("/prompt", {"prompt": g})["prompt_id"])
    for i, a in enumerate(sorted(archivos)):
        a.rename(carpeta / f"pp{i + 1}.png")
    print("listo:", carpeta)


def main():
    pos, op, flags = args()
    if pos and pos[0] == "primerplano":
        return primerplano(pos[1], pos[2], op)
    video, desde, dur, salida = pos[0], float(pos[1]), float(pos[2]), pos[3]
    dib = int(op["dibujos"])
    ancho = int(op["ancho"])
    alto = round(ancho * 9 / 16 / 8) * 8

    clave = hashlib.sha1(json.dumps([str(Path(video).resolve()), desde, dur, op, sorted(flags)]).encode()).hexdigest()[:12]
    cache = RAIZ / ".cache/comfy" / clave
    hechos = cache / "hechos"
    if not (hechos.exists() and any(hechos.iterdir())):
        fuente = cache / "fuente"
        fuente.mkdir(parents=True, exist_ok=True)
        if op.get("seguir"):
            x0, y0 = map(float, op["seguir"].split(","))
            seguir(video, desde, dur, dib, x0, y0, int(op["encuadre"]), ancho, alto, fuente)
            if op.get("cara"):
                mascara_centro(ancho, alto, cache / "mascara.png")
                op["mascara"] = str(cache / "mascara.png")
        else:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(desde), "-t", str(dur), "-i", video, "-vf",
                            f"fps={dib},scale={ancho}:{alto}", str(fuente / "f%04d.png")], check=True)
        n = len(list(fuente.glob("*.png")))
        print(f"{n} cuadros a ComfyUI ({ancho}x{alto}, {'cuadro por cuadro' if 'sin-ad' in flags else 'AnimateDiff'})")
        archivos = generar(fuente, op, flags, alto)
        hechos.mkdir(exist_ok=True)
        for i, a in enumerate(sorted(archivos)):
            a.rename(hechos / f"d{i:04d}.png")
        (cache / "parametros.json").write_text(json.dumps({"video": video, "desde": desde, "dur": dur, **op,
                                                           "flags": sorted(flags)}, ensure_ascii=False, indent=1))
    dibujos = sorted(hechos.glob("*.png"))
    print(f"{len(dibujos)} dibujos -> {salida}")

    cinta = Cinta(int(op["semilla"]), float(op["suciedad"]))
    rng = np.random.default_rng(int(op["semilla"]))
    esc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                            "-pix_fmt", "yuv420p", "-an", salida], stdin=subprocess.PIPE)
    total = int(round(dur * FPS))
    actual, cuadro = -1, None
    s = float(op["suciedad"])
    for k in range(total):
        j = min(len(dibujos) - 1, int(k * dib / FPS))
        if j != actual:
            actual = j
            img = cv2.cvtColor(cv2.imread(str(dibujos[j])), cv2.COLOR_BGR2RGB)
            base = cv2.resize(img, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
            dx, dy = rng.normal(0, 2.2 * s), rng.normal(0, 1.6 * s)
            cuadro = cv2.warpAffine(base, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
        esc.stdin.write(cinta.aplicar(cuadro, k).tobytes())
    esc.stdin.close()
    esc.wait()
    print("listo:", salida)


if __name__ == "__main__":
    main()
