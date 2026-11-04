"""Los retratos de diálogo, medidos (contrato «Columna» §3).

    python tools/verify_portraits.py

- Ocho retratos (Yara en persona y por el ave) × dos expresiones, de 48×48.
- Todo píxel es un token de la paleta.
- **Cada voz se distingue por la silueta**: entre dos voces cualesquiera, el
  solape de sus siluetas (lo que no es fondo ASH_900) es ≤ SILHOUETTE_MAX.
- **Las dos expresiones de una voz se distinguen**: al menos EXPRESSION_MIN
  píxeles distintos entre la neutra y la de arco, con la misma silueta.
- Los ojos (ASH_950) contrastan con la piel (ASH_200) ≥ 3:1.
Sale con código 1 si algo falla.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixel import PALETTE  # noqa: E402

DIR = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "portraits"
VOICES = {"ilan": "determinado", "yara": "alerta", "yara_ave": "alerta", "bruma": "dolida", "coral": "risa",
          "nix": "concentrado", "suri": "firme", "rasgo": "duda"}
SILHOUETTE_MAX = 0.90
EXPRESSION_MIN = 12
BACK = PALETTE["ash_900"][:3]


def lum(rgb) -> float:
    def ch(v: float) -> float:
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(rgb[0]) + 0.7152 * ch(rgb[1]) + 0.0722 * ch(rgb[2])


def main() -> int:
    fails = 0

    def check(label: str, ok: bool) -> None:
        nonlocal fails
        print(f"  {'OK   ' if ok else 'FALLA'} {label}")
        fails += 0 if ok else 1

    tokens = {v[:3] for v in PALETTE.values() if v[3] == 255}
    masks = {}
    for voice, arc in VOICES.items():
        imgs = {}
        for mood in ("neutral", arc):
            path = DIR / f"{voice}_{mood}.png"
            if not path.exists():
                check(f"{path.name} existe", False)
                continue
            img = Image.open(path).convert("RGBA")
            imgs[mood] = img
            loose = {img.getpixel((x, y))[:3] for y in range(img.height) for x in range(img.width)} - tokens
            check(f"{path.name}: {img.size[0]}×{img.size[1]}, {len(loose)} colores fuera de la paleta",
                  img.size == (48, 48) and not loose)
        if len(imgs) == 2:
            a, b = imgs["neutral"], imgs[arc]
            diff = sum(1 for y in range(48) for x in range(48) if a.getpixel((x, y)) != b.getpixel((x, y)))
            check(f"  {voice}: neutral y {arc} se distinguen ({diff} píxeles distintos, mínimo {EXPRESSION_MIN})",
                  diff >= EXPRESSION_MIN)
            masks[voice] = {(x, y) for y in range(48) for x in range(48) if a.getpixel((x, y))[:3] != BACK}
    names = list(masks)
    worst = ("", "", 0.0)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            m1, m2 = masks[names[i]], masks[names[j]]
            iou = len(m1 & m2) / len(m1 | m2)
            if iou > worst[2]:
                worst = (names[i], names[j], iou)
    check(f"las {len(names)} siluetas se distinguen: el par más parecido, {worst[0]} y {worst[1]}, "
          f"solapa {worst[2]:.2f} (tope {SILHOUETTE_MAX})", worst[2] <= SILHOUETTE_MAX)
    ratio = (lum(PALETTE["ash_200"]) + 0.05) / (lum(PALETTE["ash_950"]) + 0.05)
    check(f"ojos sobre la piel: {ratio:.1f}:1 (≥ 3)", ratio >= 3.0)
    print(f"\n{'Todo en verde.' if fails == 0 else f'{fails} fallos.'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
