"""Monta un GIF a partir de cuadros PNG capturados en Godot.

    python tools/frames_to_gif.py <carpeta_de_cuadros> <salida.gif> [ms_por_cuadro]

Lo usa la hoja de estados del mundo (`tools/world_states_sheet.tscn`) para
enseñar en movimiento lo que una captura fija no puede: si el follaje
purificado se delata como patrón al desplazarse la cámara. Los cuadros son los
del motor, a 480x270; el GIF solo los encadena, a 2x y con escalado Nearest.
Por defecto, 33 ms por cuadro: el GIF no baja de 20 ms en la mayoría de
visores, así que se enseña a la mitad de la velocidad real, y se dice.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    frames_dir, out = Path(sys.argv[1]), Path(sys.argv[2])
    ms = int(sys.argv[3]) if len(sys.argv) > 3 else 33
    paths = sorted(frames_dir.glob("*.png"))
    if not paths:
        print(f"no hay cuadros en {frames_dir}")
        return 1
    frames = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        frames.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=False)
    print(f"  gif: {out} ({len(frames)} cuadros, {ms} ms por cuadro)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
