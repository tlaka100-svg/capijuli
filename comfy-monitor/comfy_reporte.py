#!/usr/bin/env python3
"""Reporte de las últimas corridas de ComfyUI, en Markdown.

Pensado para que Claude (o tú) lo corra en la Mac y vea qué pasó:
errores, parámetros clave y qué cambió entre una corrida y la anterior.

    python3 comfy_reporte.py            # últimas 3 corridas
    python3 comfy_reporte.py --n 5 --url http://127.0.0.1:8000
"""
import argparse
import json
import re
import sys
import urllib.request

KEY_CLASS = re.compile(r"KSampler|Sampler|Checkpoint|UNET|Lora|CLIPTextEncode|EmptyLatent|EmptySD3|LoadImage|LoadVideo|VHS|Upscale|ControlNet|IPAdapter|Wan|Hunyuan|LTX|Flux|Guider|Scheduler|Noise|Save|Video", re.I)
KEY_INPUT = re.compile(r"^(seed|noise_seed|steps|cfg|sampler_name|scheduler|denoise|width|height|length|batch_size|frame_rate|fps|text|ckpt_name|unet_name|lora_name|strength_model|strength_clip|image|video|guidance|shift|filename_prefix|upscale_method|strength|weight)$")


def get(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read() or b"{}")


def short(v, n=160):
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[: n - 1] + "…"


def params(prompt):
    out = {}
    for nid, node in prompt.items():
        for k, v in (node.get("inputs") or {}).items():
            if isinstance(v, list):  # conexión a otro nodo
                continue
            title = (node.get("_meta") or {}).get("title") or node.get("class_type")
            out[f"{nid}:{k}"] = dict(id=nid, k=k, v=v, title=title, cls=node.get("class_type", ""),
                                     key=bool(KEY_CLASS.search(node.get("class_type", "")) and KEY_INPUT.match(k)))
    return out


def parse(pid, h):
    msgs = (h.get("status") or {}).get("messages") or []
    ts = lambda k: next((m[1].get("timestamp") for m in msgs if m[0] == k), None)
    start = ts("execution_start")
    end = ts("execution_success") or ts("execution_error") or ts("execution_interrupted")
    err = next((m[1] for m in msgs if m[0] == "execution_error"), None)
    outs = [f["filename"] for o in (h.get("outputs") or {}).values() for v in o.values()
            if isinstance(v, list) for f in v if isinstance(f, dict) and f.get("filename")]
    p = h.get("prompt") or [0, pid, {}]
    return dict(pid=pid, num=p[0], prompt=p[2], ms=(end - start) if start and end else None,
                err=err, outs=outs, status=(h.get("status") or {}).get("status_str", "?"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8188")
    ap.add_argument("--n", type=int, default=3)
    a = ap.parse_args()
    base = a.url.rstrip("/")
    try:
        hist = get(f"{base}/history?max_items={a.n + 1}")
        sysinfo = get(f"{base}/system_stats")
        queue = get(f"{base}/queue")
    except Exception as e:  # noqa: BLE001
        sys.exit(f"No pude hablar con ComfyUI en {base}: {e}")

    runs = sorted((parse(k, v) for k, v in hist.items()), key=lambda r: r["num"], reverse=True)
    dev = (sysinfo.get("devices") or [{}])[0]
    gb = lambda b: f"{(b or 0) / 2**30:.1f} GB"
    print(f"# ComfyUI {sysinfo.get('system', {}).get('comfyui_version', '?')} · {dev.get('name', '?')} · "
          f"memoria libre {gb(dev.get('vram_free'))} de {gb(dev.get('vram_total'))}")
    print(f"Cola: {len(queue.get('queue_running', []))} corriendo, {len(queue.get('queue_pending', []))} esperando\n")

    for i, r in enumerate(runs[: a.n]):
        prev = runs[i + 1] if i + 1 < len(runs) else None
        dur = f"{r['ms'] / 1000:.1f} s" if r["ms"] else "—"
        print(f"## Corrida #{r['num']} ({r['pid'][:8]}) · {r['status']} · {dur}")
        print(f"Salidas: {', '.join(r['outs']) or 'ninguna'}")
        if r["err"]:
            e = r["err"]
            print(f"\n**Error** en nodo #{e.get('node_id')} {e.get('node_type')}: {e.get('exception_type')}: {e.get('exception_message')}")
            tb = "".join(e.get("traceback") or []).strip().splitlines()[-12:]
            if tb:
                print("```\n" + "\n".join(tb) + "\n```")
        pr = params(r["prompt"])
        print("\nParámetros clave:")
        for x in pr.values():
            if x["key"]:
                print(f"- {x['title']} (#{x['id']}) · {x['k']} = {short(x['v'])}")
        if prev:
            pp = params(prev["prompt"])
            changes = [k for k in set(pr) | set(pp) if json.dumps((pr.get(k) or {}).get("v")) != json.dumps((pp.get(k) or {}).get("v"))]
            print(f"\nCambios contra #{prev['num']}:" if changes else f"\nSin cambios de parámetros contra #{prev['num']}.")
            for k in sorted(changes):
                x = pr.get(k) or pp.get(k)
                before = short(pp[k]["v"]) if k in pp else "(no existía)"
                now = short(pr[k]["v"]) if k in pr else "(se quitó)"
                print(f"- {x['title']} → {x['k']}: {before} → {now}")
        print()


if __name__ == "__main__":
    main()
