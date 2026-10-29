"""Las posturas del monstruo de mapa se leen sin color (contrato «Persiana»).

    python tools/verify_monster_poses.py

Por cada uno de los seis monstruos compara la máscara de su reposo con la de
alerta y la de persecución, alineadas por el pie:

- persecución: solape (intersección / unión) <= POSE_IOU_MAX con el reposo;
- alerta: la silueta es al menos 1 px más alta que el reposo;
- las tres comparten pie: la fila más baja es la misma (no flotan).

El color no cuenta: se mide solo dónde hay píxel. Sale con código 1 si algo
falla.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

DECOR = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "world" / "decor"
ZONES = ("ashen_forest", "tar_basin", "broken_coast", "withered_plain", "waning_peak", "greed_crypt")
## Por encima de esto, la persecución se confunde con el reposo de reojo.
POSE_IOU_MAX = 0.80


def mask(path: Path, pad: int) -> set[tuple[int, int]]:
    img = Image.open(path).convert("RGBA")
    return {(x + pad, y) for y in range(img.height) for x in range(img.width)
            if img.getpixel((x, y))[3] > 0}


def main() -> int:
    fails = 0

    def check(label: str, ok: bool, detail: str = "") -> None:
        nonlocal fails
        print(f"  {'OK   ' if ok else 'FALLA'} {label}" + (f"  ({detail})" if detail else ""))
        fails += 0 if ok else 1

    for zone in ZONES:
        print(zone)
        rest = mask(DECOR / f"monster_{zone}_sick.png", 2)
        alert = mask(DECOR / f"monster_{zone}_alert_sick.png", 0)
        chase = mask(DECOR / f"monster_{zone}_chase_sick.png", 0)
        iou = len(rest & chase) / len(rest | chase)
        check("persecución distinta del reposo por la silueta", iou <= POSE_IOU_MAX,
              f"solape {iou:.2f}, tope {POSE_IOU_MAX}")
        top = lambda m: min(y for _, y in m)
        check("alerta, más alta que el reposo", top(alert) < top(rest),
              f"arriba en y={top(alert)} frente a y={top(rest)}")
        feet = {name: max(y for _, y in m) for name, m in (("reposo", rest), ("alerta", alert), ("persecución", chase))}
        check("las tres posturas pisan la misma fila", len(set(feet.values())) == 1, str(feet))

    print(f"\n{'Todo en verde.' if fails == 0 else f'{fails} fallos.'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
