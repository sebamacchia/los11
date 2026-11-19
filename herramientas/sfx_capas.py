"""<pieza>.sonidos.json -> <pieza>_capas/sonidos/ (un wav por efecto + sfx_clips.json para filmcraft.py capas)."""
import json, subprocess, sys
from pathlib import Path
v = Path(sys.argv[1]); c = v.with_name(v.stem + "_capas") / "sonidos"; c.mkdir(parents=True, exist_ok=True)
cues = json.load(open(v.with_suffix(".sonidos.json")))
fin, out = {}, []
for n, q in enumerate(sorted(cues, key=lambda q: q["en"])):
    lane = next(l for l in range(50) if fin.get(l, 0) <= q["en"])
    nom = Path(q["archivo"]).stem; f = f"sfx_{n:03d}_{nom}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(q["desde"]), "-t", str(q["dur"]), "-i", q["archivo"],
                    "-af", f"volume={q['vol']},afade=t=out:st={max(0, q['dur'] - 0.3)}:d=0.3", "-ar", "48000", "-ac", "2", str(c / f)], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(c / f)], capture_output=True, text=True).stdout)
    out.append({"id": f"sfx-{n:03d}", "file": f, "start": q["en"], "duration": round(dur, 3), "t_moment": q["en"], "role": "foley",
                "label": nom, "lane": lane, "source_file": q["archivo"], "bed": False, "texture": False, "layer": False})
    fin[lane] = q["en"] + dur
json.dump(out, open(c / "sfx_clips.json", "w"), indent=1); print(v.name, len(out), "efectos")
