# Comfy en vivo: panel para ver qué está pasando en ComfyUI.
# No agrega nodos; solo sirve la carpeta web/ en /extensions/comfy-monitor/
# Abre: http://127.0.0.1:8188/extensions/comfy-monitor/monitor.html

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
