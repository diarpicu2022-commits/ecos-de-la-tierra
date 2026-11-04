"""Iconos de 12 × 12 del HUD del combate de acción (`components/ActionHUD`).

    python tools/gen_tierra_viva_icons.py

Salen tal cual del prototipo aprobado (`tools/tierra_viva/hud.py`, `icon`), con
la misma paleta, y se escriben en `assets/ui/iconos/<nombre>.png`. No se
redibuja nada: si un icono cambia, cambia en el prototipo.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTO = ROOT / "tools" / "tierra_viva"
OUT = ROOT / "assets" / "ui" / "iconos"
NAMES = ("espada", "bota", "hoja", "hierba", "agua", "antidoto", "racion")


def main() -> int:
    sys.path.insert(0, str(PROTO))
    os.chdir(PROTO)  # el prototipo abre sus recursos con rutas relativas
    import numpy as np
    from PIL import Image
    import hud

    OUT.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        img = hud.icon(name)
        path = OUT / f"{name}.png"
        Image.fromarray(np.asarray(img, dtype=np.uint8), "RGBA").save(path)
        print(f"  {path.relative_to(ROOT)}: {img.shape[1]}×{img.shape[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
