# Comfy en vivo

Panel para ver qué está haciendo ComfyUI y pedirle ayuda a Claude con datos concretos.

**Qué muestra**
- **Ahora:** qué nodo está corriendo, paso X de Y, cuánto falta, vista previa en vivo, qué nodos salieron de caché y cuánto tardó cada uno.
- **Errores en español claro:** en qué nodo falló y el mensaje; el detalle técnico queda plegado.
- **Historial:** las últimas 30 corridas con miniatura, duración y estado; imágenes y videos de salida.
- **Qué cambió contra la corrida anterior:** seed, steps, cfg, prompt, modelo, LoRA, tamaño… resaltado.
- **Copiar reporte para Claude:** arma un resumen (error, parámetros, cambios, nodos lentos y tu nota de "qué veo / qué quiero") listo para pegar en el chat.
- Botones para **Interrumpir** y **Liberar memoria**.

## Instalar (Mac)

1. Copia la carpeta `comfy-monitor` dentro de `ComfyUI/custom_nodes/`.
2. Reinicia ComfyUI.
3. Abre en otra pestaña: `http://127.0.0.1:8188/extensions/comfy-monitor/monitor.html`
   (con ComfyUI Desktop el puerto suele ser `8000`).
4. Deja abierta también la pestaña normal de ComfyUI: de ahí sale el detalle nodo por nodo y la vista previa.
   ComfyUI solo le manda esos eventos a la pestaña que lanzó el trabajo; `web/relay.js` los pasa al panel.

## Para Claude en la Mac

```bash
python3 ComfyUI/custom_nodes/comfy-monitor/comfy_reporte.py --n 3
```

Imprime en Markdown las últimas corridas con error, parámetros clave y cambios contra la anterior,
para que Claude vea lo mismo que tú sin abrir el navegador.
