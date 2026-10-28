"""Prueba de entrecerrar (contrato «Rastro», fuente 4: Rogers, «squint test»).

    python tools/verify_squint.py <zona> [--purified all|none|<parte>,...]

Entrecerrando los ojos, lo más luminoso de una zona tiene que marcar el camino
o lo purificado, nunca un decorado. Se mide así, sobre el render de la zona
entera que da `zone_preview.py` (el mismo terreno y los mismos sprites que el
motor, sin Ilan):

1. La imagen se desenfoca con una caja de 24 px (tile y medio): es el
   entrecerrar.
2. Se toma el 1 % de píxeles más luminosos del desenfoque.
3. En cada uno se mira cuánto de lo que lo rodea (la misma caja) es
   decorado: los píxeles donde el render completo difiere del de solo terreno.
4. FALLA si, de media, en ese 1 % más luminoso manda el decorado (> 50 %).

Se mide en el estado de inicio (por defecto) y con todo purificado.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zone_preview import load_parts, load_zone, render  # noqa: E402

BLUR = 12          # radio de la caja: 24 px de lado
TOP = 0.01         # el 1 % más luminoso
DECOR_LIMIT = 0.5  # por encima, manda el decorado


def luminance(img: Image.Image) -> Image.Image:
    return img.convert("RGB").convert("L")


def measure(zone_id: str, parts: set[str], label: str) -> bool:
    full = render(zone_id, parts)
    terrain = render(zone_id, parts, terrain_only=True)
    decor = ImageChops.difference(full.convert("RGB"), terrain.convert("RGB")).convert("L")
    decor = decor.point(lambda v: 255 if v > 0 else 0)
    blurred = luminance(full).filter(ImageFilter.BoxBlur(BLUR))
    share = decor.filter(ImageFilter.BoxBlur(BLUR))
    lum = list(getattr(blurred, "get_flattened_data", blurred.getdata)())
    dec = list(getattr(share, "get_flattened_data", share.getdata)())
    order = sorted(range(len(lum)), key=lambda i: -lum[i])[: max(1, int(len(lum) * TOP))]
    mean = sum(dec[i] for i in order) / len(order) / 255
    ok = mean <= DECOR_LIMIT
    w = full.width
    top = order[0]
    tile = ((top % w) // 16, (top // w) // 16)
    lines = load_zone(zone_id)
    material = {".": "suelo", "=": "camino", "~": "agua", "#": "follaje", ":": "arena"}[lines[tile[1]][tile[0]]]
    # Qué material domina el 1 % más luminoso: lo dice, para leerlo con Rogers.
    counts: dict[str, int] = {}
    for i in order:
        ch = lines[(i // w) // 16][(i % w) // 16]
        counts[ch] = counts.get(ch, 0) + 1
    names = {".": "suelo", "=": "camino", "~": "agua", "#": "follaje", ":": "arena"}
    mix = ", ".join(f"{names[k]} {v * 100 // len(order)} %" for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))
    print(f"  {'OK   ' if ok else 'FALLA'} {label}: en el 1 % más luminoso, el decorado ocupa "
          f"un {mean * 100:.0f} % (límite {DECOR_LIMIT * 100:.0f} %); "
          f"lo más luminoso está en el tile {tile} ({material}); por material: {mix}")
    return ok


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    zone_id = sys.argv[1]
    parts = set(load_parts(zone_id))
    # Una zona sin partes se purifica entera («all», como en zone_preview).
    states = [("al empezar", {"yara_garden"} & parts), ("todo purificado", parts or {"all"})]
    if "--purified" in sys.argv:
        value = sys.argv[sys.argv.index("--purified") + 1]
        chosen = (parts or {"all"}) if value == "all" else set() if value == "none" else set(value.split(","))
        states = [(value, chosen)]
    print(f"Prueba de entrecerrar: {zone_id}")
    ok = all([measure(zone_id, p, label) for label, p in states])
    print("\nEntrecerrando, manda el terreno." if ok else "\nHay fallos: se informan, no se maquillan.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
