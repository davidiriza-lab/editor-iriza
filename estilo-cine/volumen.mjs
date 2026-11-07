// Volumen lineal: ganancia fija + limitador. Reemplaza al loudnorm de una pasada, que actúa como control automático
// de ganancia y en cada pausa sube el ruido de fondo casi al nivel de la voz.
import { spawnSync } from 'node:child_process';

const lufs = args => {
  const r = spawnSync('ffmpeg', ['-hide_banner', '-nostats', ...args, '-f', 'null', '-'], { encoding: 'utf8', maxBuffer: 1 << 28 });
  const m = [...r.stderr.matchAll(/^\s*I:\s+(-?[\d.]+) LUFS/gm)].pop();
  if (!m) throw new Error(`no pude medir el volumen:\n${r.stderr.slice(-500)}`);
  return +m[1];
};
export const medirArchivo = f => lufs(['-i', f, '-vn', '-af', 'ebur128=framelog=quiet']);
export const medirGrafo = (entradas, fc, etiqueta) => lufs([...entradas, '-filter_complex', `${fc};[${etiqueta}]ebur128=framelog=quiet[medido]`, '-map', '[medido]']);
// medido ≤ −69 = silencio: no se le aplica ganancia
export const nivelar = (medido, objetivo, techoDb) => {
  const g = medido <= -69 ? 0 : Math.max(-30, Math.min(36, objetivo - medido));
  return `volume=${g.toFixed(2)}dB,alimiter=limit=${(10 ** (techoDb / 20)).toFixed(4)}:level=false:latency=true`;
};
