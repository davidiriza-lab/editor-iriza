"""Mide la fluidez de un video: % de tiempo quieto y pausas sin movimiento (cuadro a cuadro, 0.05 s).
Uso: python3 fluidez.py video.mp4 [inicio fin]   -> lista las pausas > 0.3 s
Meta: < 5% quieto y ninguna pausa > 0.3 s."""
import sys, subprocess, numpy as np
v = sys.argv[1]; a = sys.argv[2:3]; b = sys.argv[3:4]
cmd = ["ffmpeg", "-v", "error"] + (["-ss", a[0]] if a else []) + ["-i", v] + (["-t", str(float(b[0]) - float(a[0]))] if b else []) + ["-vf", "fps=20,scale=180:320,format=gray", "-f", "rawvideo", "-"]
raw = subprocess.run(cmd, capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 320, 180).astype(np.int16)
still = np.array([(np.abs(fr[i] - fr[i - 1]) > 10).sum() < 8 for i in range(1, len(fr))])
t0 = float(a[0]) if a else 0; pausas, c = [], 0
for i, s in enumerate(still):
    if s: c += 1
    else:
        if c * 0.05 > 0.3: pausas.append((t0 + (i - c) * 0.05, c * 0.05))
        c = 0
if c * 0.05 > 0.3: pausas.append((t0 + (len(still) - c) * 0.05, c * 0.05))
print(f"quieto {still.mean() * 100:.1f}% · pausas > 0.3 s: {len(pausas)}")
for s, d in pausas: print(f"  {s:7.2f}s  dura {d:.2f}s")
