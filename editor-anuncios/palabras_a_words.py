"""Convierte las palabras de whisper-cli (JSON -oj) al words.json que espera editor-anuncios/prepare.py."""
import json, sys
src, dst = sys.argv[1], sys.argv[2]
def seg(s):
    h, m, r = s.split(':'); sec, ms = r.split(',')
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
d = json.load(open(src))
ws = []
for w in d['transcription']:
    t = w['text'].strip()
    if not t: continue
    s, e = seg(w['timestamps']['from']), seg(w['timestamps']['to'])
    if e <= s: e = s + 0.05
    ws.append({"w": t, "s": round(s, 3), "e": round(e, 3), "p": 1.0, "blk": 0})
for i in range(len(ws) - 1):
    if ws[i]["e"] > ws[i + 1]["s"]: ws[i]["e"] = ws[i + 1]["s"]
json.dump(ws, open(dst, 'w'), ensure_ascii=False, indent=0)
print(len(ws), 'palabras')
