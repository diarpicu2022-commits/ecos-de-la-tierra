"""Retratos de diálogo del sistema de diseño (`components/DialogBox`).

    python tools/gen_tierra_viva_portraits.py

En el sistema, el retrato es el sprite de PixelLab de frente, recortado sin
repintar a 40 × 44 (`assets/img/portrait_coral.png`). Escribe en
`assets/sprites/portraits/tierra_viva/<quien>.png` los de quien tiene original en
`assets/source/pixellab/`. Yara y Rasgo no lo tienen: siguen con su retrato de
`tools/gen_portraits.py` hasta que se generen (guía del equipo §3.1, fila 20).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "source" / "pixellab"
OUT = ROOT / "assets" / "sprites" / "portraits" / "tierra_viva"
CAST = ("ilan", "bruma", "coral", "nix", "suri")
W, H = 40, 44


def crop(path: Path) -> Image.Image:
    img = Image.open(path).convert("RGBA")
    alpha = np.array(img)[..., 3]
    rows, cols = np.where(alpha > 0)
    top = int(rows.min())
    cx = (int(cols.min()) + int(cols.max()) + 1) // 2
    left = cx - W // 2
    out = Image.new("RGBA", (W, H))
    out.paste(img.crop((left, top, left + W, top + H)), (0, 0))
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for who in CAST:
        path = OUT / f"{who}.png"
        crop(SOURCE / who / "south.png").save(path)
        print(f"  {path.relative_to(ROOT)}: {W}×{H}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
