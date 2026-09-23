"""Verificación medida de la paleta de *Ecos de la Tierra*.

La regla del juego es que ningún color va suelto y que el verde tiene un solo
significado. Eso no se comprueba mirando una captura: se comprueba aquí.

    python tools/verify_palette.py tokens
        Coteja la paleta de `tools/pixel.py` con `src/ui/design_tokens.gd`.
        Un token que existe en un lado y no en el otro es deriva.

    python tools/verify_palette.py image <png> [--world]
        Todo píxel opaco debe ser un token exacto. Con --world, además, todo
        color que no sea brasa ni verde debe quedar bajo el techo de
        saturación 0,22 del contrato «Vereda».

    python tools/verify_palette.py cvd
        Simula deuteranopía, protanopía y tritanopía (Machado et al. 2009,
        severidad 1,0) sobre los pares de acento y dice cuánto se separan.

    python tools/verify_palette.py value <png_enfermo> <png_purificado>
        Compara la luminancia media de dos renders del mismo tile o zona, en
        visión normal y simulada. El contrato dice «enfermo = valor bajo,
        purificado = valor alto»: si el cociente no llega a 1,5 en las cuatro
        visiones, la diferencia la está cargando solo el matiz, y el matiz
        desaparece para uno de cada doce jugadores varones.

Sale con código 1 si algo falla, para poder encadenarlo en otras pruebas.
"""

from __future__ import annotations

import colorsys
import math
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TOKENS_GD = ROOT / "src" / "ui" / "design_tokens.gd"

WORLD_SATURATION_CEILING = 0.22
VALUE_RATIO_FLOOR = 1.5

## Matrices de Machado, Oliveira y Fernandes (2009), severidad 1,0, en RGB
## lineal. https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html
CVD = {
    "deuteranopía": [[0.367322, 0.860646, -0.227968],
                     [0.280085, 0.672501, 0.047413],
                     [-0.011820, 0.042940, 0.968881]],
    "protanopía": [[0.152286, 1.052583, -0.204868],
                   [0.114503, 0.786281, 0.099216],
                   [-0.003882, -0.048116, 1.051998]],
    "tritanopía": [[1.255528, -0.076749, -0.178779],
                   [-0.078411, 0.930809, 0.147602],
                   [0.004733, 0.691367, 0.303900]],
}


# --- Color ---------------------------------------------------------------------


def to_linear(rgb: tuple[int, int, int]) -> list[float]:
    out = []
    for c in rgb:
        c = c / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return out


def simulate(lin: list[float], kind: str | None) -> list[float]:
    if kind is None:
        return lin
    m = CVD[kind]
    return [max(0.0, min(1.0, sum(m[i][j] * lin[j] for j in range(3)))) for i in range(3)]


def luminance(lin: list[float]) -> float:
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: list[float], b: list[float]) -> float:
    lo, hi = sorted([luminance(a), luminance(b)])
    return (hi + 0.05) / (lo + 0.05)


def lab(lin: list[float]) -> tuple[float, float, float]:
    x = (0.4124 * lin[0] + 0.3576 * lin[1] + 0.1805 * lin[2]) / 0.95047
    y = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    z = (0.0193 * lin[0] + 0.1192 * lin[1] + 0.9505 * lin[2]) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    return (116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z)))


def delta_e(a: list[float], b: list[float]) -> float:
    return math.dist(lab(a), lab(b))


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# --- Fuentes de tokens -----------------------------------------------------------


def gd_tokens() -> dict[str, tuple[int, int, int]]:
    """Tokens crudos de design_tokens.gd. Los papeles semánticos (alias) no
    llevan hex propio y no cuentan."""
    pattern = re.compile(r'^const\s+([A-Z0-9_]+)\s*:=\s*Color\("(#[0-9a-fA-F]{6})"\)', re.M)
    text = TOKENS_GD.read_text(encoding="utf-8")
    return {name.lower(): hex_rgb(h) for name, h in pattern.findall(text)}


def py_tokens() -> dict[str, tuple[int, int, int]]:
    sys.path.insert(0, str(ROOT / "tools"))
    from pixel import PALETTE  # noqa: E402

    return {k: v[:3] for k, v in PALETTE.items() if v[3] == 255}


def is_accent(name: str) -> bool:
    return name.startswith(("ember_", "vital_"))


# --- Órdenes -----------------------------------------------------------------------


def cmd_tokens() -> bool:
    gd, py = gd_tokens(), py_tokens()
    ok = True
    for name in sorted(set(gd) | set(py)):
        if name not in py:
            print(f"  FALLA  {name} está en design_tokens.gd y no en pixel.py")
            ok = False
        elif name not in gd:
            print(f"  FALLA  {name} está en pixel.py y no en design_tokens.gd")
            ok = False
        elif gd[name] != py[name]:
            print(f"  FALLA  {name} difiere: gd {gd[name]} / py {py[name]}")
            ok = False
    print(f"\n{len(set(gd) & set(py))} tokens coinciden. " + ("Sin deriva." if ok else "Hay deriva."))
    return ok


def cmd_image(path: str, world: bool) -> bool:
    tokens = {**py_tokens(), **gd_tokens()}
    by_rgb = {v: k for k, v in tokens.items()}
    img = Image.open(path).convert("RGBA")
    loose: dict[tuple[int, int, int], int] = {}
    over: dict[str, int] = {}
    for r, g, b, a in getattr(img, "get_flattened_data", img.getdata)():
        if a == 0:
            continue
        name = by_rgb.get((r, g, b))
        if name is None:
            loose[(r, g, b)] = loose.get((r, g, b), 0) + 1
            continue
        if world and not is_accent(name):
            s = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)[1]
            if s > WORLD_SATURATION_CEILING + 1e-3:
                over[name] = over.get(name, 0) + 1
    for rgb, n in sorted(loose.items(), key=lambda kv: -kv[1])[:12]:
        print(f"  FALLA  color suelto #{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x} en {n} px")
    for name, n in over.items():
        print(f"  FALLA  {name} supera la saturación 0,22 del mundo en {n} px")
    ok = not loose and not over
    print(f"\n{path}: " + ("todo píxel es un token." if ok else "hay colores fuera del contrato."))
    return ok


def cmd_cvd() -> bool:
    t = gd_tokens()
    pairs = [("vital_500", "ember_500"), ("vital_500", "ember_400"),
             ("vital_500", "ember_300"), ("vital_500", "flora_300"),
             ("vital_500", "water_300"), ("vital_500", "soil_300")]
    print(f"{'par':28} {'visión':14} {'dE':>6} {'contraste':>10}")
    for a, b in pairs:
        la, lb = to_linear(t[a]), to_linear(t[b])
        for kind in [None, *CVD]:
            sa, sb = simulate(la, kind), simulate(lb, kind)
            print(f"{a + ' / ' + b:28} {kind or 'normal':14} {delta_e(sa, sb):6.1f} {contrast(sa, sb):10.2f}")
    print("\nLectura: con dE alto y contraste bajo, el par se separa solo por matiz.")
    print("Ese par no puede cargar solo un significado: necesita forma o valor.")
    return True


def mean_linear(path: str) -> list[float]:
    img = Image.open(path).convert("RGBA")
    acc, n = [0.0, 0.0, 0.0], 0
    for r, g, b, a in getattr(img, "get_flattened_data", img.getdata)():
        if a == 0:
            continue
        lin = to_linear((r, g, b))
        for i in range(3):
            acc[i] += lin[i]
        n += 1
    return [c / max(n, 1) for c in acc]


def cmd_value(sick: str, pure: str) -> bool:
    ls, lp = mean_linear(sick), mean_linear(pure)
    ok = True
    for kind in [None, *CVD]:
        ss, sp = simulate(ls, kind), simulate(lp, kind)
        ratio = (luminance(sp) + 0.05) / (luminance(ss) + 0.05)
        mark = "OK   " if ratio >= VALUE_RATIO_FLOOR else "FALLA"
        ok &= ratio >= VALUE_RATIO_FLOOR
        print(f"  {mark} {kind or 'normal':14} purificado / enfermo = {ratio:.2f} (piso {VALUE_RATIO_FLOOR})")
    return ok


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    if cmd == "tokens":
        ok = cmd_tokens()
    elif cmd == "image" and len(argv) >= 2:
        ok = cmd_image(argv[1], "--world" in argv)
    elif cmd == "cvd":
        ok = cmd_cvd()
    elif cmd == "value" and len(argv) == 3:
        ok = cmd_value(argv[1], argv[2])
    else:
        print(__doc__)
        return 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
