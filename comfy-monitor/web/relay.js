// Corre dentro de la pestaña de ComfyUI y reenvía sus eventos en vivo
// (nodo actual, progreso, vista previa, errores) al panel monitor.html.
// ComfyUI solo manda esos eventos a la pestaña que encoló el trabajo,
// por eso hace falta este puente.
import { api } from "../../scripts/api.js";

const ch = new BroadcastChannel("comfy-monitor");
const EVENTS = [
  "status", "execution_start", "execution_cached", "executing", "progress",
  "executed", "execution_error", "execution_interrupted", "execution_success",
];

for (const type of EVENTS) {
  api.addEventListener(type, (e) => {
    try { ch.postMessage({ type, data: e.detail }); } catch (_) { /* dato no clonable */ }
  });
}

api.addEventListener("b_preview", (e) => {
  try { ch.postMessage({ type: "preview", blob: e.detail }); } catch (_) {}
});
api.addEventListener("b_preview_with_metadata", (e) => {
  try { ch.postMessage({ type: "preview", blob: e.detail?.blob }); } catch (_) {}
});

setInterval(() => ch.postMessage({ type: "hello" }), 2000);
console.log("[comfy-monitor] puente activo → abre /extensions/comfy-monitor/monitor.html");
