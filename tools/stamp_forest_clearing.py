"""El claro del Bosque de las Cenizas, como en la referencia del sistema.

    python tools/stamp_forest_clearing.py

La referencia `docs/ux/sistema-de-diseno/project/assets/img/bosque_enfermo.png`
sale del prototipo (`tools/tierra_viva/maps2.bosque()`, 40 × 23 casillas, y
`scene2.forest_objects`). Este script pone esa escena dentro del mapa del juego,
`data/world/zones/ashen_forest.txt` y su `.deco.txt`, desplazada para que su río
caiga sobre el río del mapa y su camino sobre la entrada desde Valdehoja.

- Se conservan las salidas, el monstruo, el hito, el paso cerrado y todas las
  piezas que no son árboles de relleno (viñetas, semillero, rocas, hierba).
- El mapa del repo no tiene cotas, así que la meseta y su escalera de la
  referencia no se pintan: el camino de la escalera queda como camino.
- Los árboles de la escena van como árbol enfermo en pie (`T`, `U`): el árbol
  quemado (`c`) es el gradiente hacia la fuente y no se usa lejos de ella.

Es idempotente: se puede volver a correr y deja el mismo resultado.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONE = ROOT / "data" / "world" / "zones" / "ashen_forest.txt"
DECO = ROOT / "data" / "world" / "zones" / "ashen_forest.deco.txt"
PROTO = ROOT / "tools" / "tierra_viva"

# La referencia empieza en esta casilla del mapa: su río (columnas 29 a 35)
# queda sobre el del mapa (47 a 50) y su camino del este sobre el puente de la fila 15.
DX, DY = 17, 1
T = 16
GROUND = {".": ".", "t": ".", "f": ".", "p": "=", "S": "=", "w": "~", "B": "="}
FILLER = set("TUc")
# Caracteres nuevos de la leyenda del decorado.
NEW_LEGEND = {
    "k": "; k = decor, bush, sólido                     arbusto seco del claro",
    "L": "; L = decor, felled_log, sólido, 2x1          tronco caído del claro",
}


def split(path: Path) -> tuple[list[str], list[list[str]]]:
    """Cabecera (comentarios y, en el decorado, la línea `---`) y filas."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if "---" in lines:
        cut = lines.index("---") + 1
        return lines[:cut], [list(r) for r in lines[cut:]]
    head = [l for l in lines if l.startswith(";")]
    return head, [list(l) for l in lines if not l.startswith(";")]


def main() -> int:
    sys.path.insert(0, str(PROTO))
    cwd = os.getcwd()
    os.chdir(PROTO)
    import maps2
    os.chdir(cwd)
    ref = maps2.bosque()["ground"]

    ghead, ground = split(ZONE)
    dhead, deco = split(DECO)
    H, W = len(ground), len(ground[0])
    assert len(deco) <= H, (len(deco), H)
    deco.extend([] for _ in range(H - len(deco)))
    for r in deco:
        r.extend(" " * (W - len(r)))

    def inside(x: int, y: int) -> bool:
        return DX <= x < DX + 40 and DY <= y < DY + 23 and 0 < y < H - 1

    # 1. Suelo de la referencia.
    for ry, row in enumerate(ref):
        for rx, ch in enumerate(row):
            x, y = rx + DX, ry + DY
            if inside(x, y):
                ground[y][x] = GROUND.get(ch, ".")
                # El generador solo reconoce un puente de una fila, con agua
                # arriba y abajo: de un cruce de dos filas, la de abajo es río.
                if ch == "B" and ry > 0 and ref[ry - 1][rx] == "B":
                    ground[y][x] = "~"

    # El camino de la referencia entra dos filas más arriba que la llegada
    # desde Valdehoja (filas 16 y 17): se unen por un tramo vertical.
    for y in range(DY + 13, 18):
        for x in (DX, DX + 1):
            ground[y][x] = "="

    # Fuera el relleno de árboles del claro, cada árbol entero: un 2 × 2 que el
    # borde del claro cortara quedaría a medias. Los árboles se leen en orden,
    # fila a fila, como en `WorldDecor`.
    claimed = set()
    for y in range(H):
        for x in range(W):
            c = deco[y][x]
            if (x, y) in claimed or not (c in FILLER or c in NEW_LEGEND):
                continue
            w, h = (2, 1) if c == "L" else ((1, 1) if c == "k" else (2, 2))
            cells = [(x + i, y + j) for i in range(w) for j in range(h)
                     if x + i < W and y + j < H and deco[y + j][x + i] == c]
            claimed.update(cells)
            if any(inside(cx, cy) for cx, cy in cells):
                for cx, cy in cells:
                    deco[cy][cx] = " "

    problems = []
    for y in range(H):
        for x in range(W):
            c = deco[y][x]
            # Lo que se pisa (ceniza, hierba) puede quedar sobre el camino.
            if inside(x, y) and c not in " eg" and ground[y][x] in "~=":
                problems.append(f"pieza «{c}» en ({x}, {y}) sobre «{ground[y][x]}»")

    def free(x: int, y: int, w: int, h: int) -> bool:
        return all(inside(x + i, y + j) and ground[y + j][x + i] == "." and deco[y + j][x + i] == " "
                   for i in range(w) for j in range(h))

    def put(ch: str, x: int, y: int, w: int = 1, h: int = 1) -> bool:
        if not free(x, y, w, h):
            return False
        for i in range(w):
            for j in range(h):
                deco[y + j][x + i] = ch
        return True

    # 2. Las piezas de la escena, de píxeles a casillas (y es la base del sprite).
    def cell(px: int, py: int) -> tuple[int, int]:
        return px // T + DX, py // T - 1 + DY

    spots = [(40, 30), (150, 40), (250, 30), (300, 66), (380, 40), (150, 420), (230, 432),
             (560, 64), (590, 10), (604, 128), (590, 220), (604, 320), (560, 430)]
    for i, (px_, py_) in enumerate(spots):
        x, y = cell(px_, py_)
        put("T" if i % 2 else "U", x, y - 1, 2, 2)
    for px_, py_ in [(118, 190), (300, 182), (420, 238), (196, 256), (420, 120), (30, 250), (560, 340)]:
        put("k", *cell(px_, py_))
    for px_, py_ in [(170, 100), (380, 196), (470, 262), (276, 310), (110, 352)]:
        put("R", *cell(px_, py_))
    for px_, py_ in [(196, 124), (470, 304)]:
        put("t", *cell(px_, py_))
    x, y = cell(76, 100)
    put("L", x, y, 2, 1)
    # Matas de hierba seca donde la referencia tiene hierba alta.
    for ry, row in enumerate(ref):
        for rx, ch in enumerate(row):
            if ch == "t":
                put("g", rx + DX, ry + DY)

    # 3. Leyenda: añade lo nuevo antes de la línea de la aparición.
    legend = [l for l in dhead]
    for ch, line in NEW_LEGEND.items():
        if not any(l.startswith(f"; {ch} = ") for l in legend):
            at = next(i for i, l in enumerate(legend) if l.startswith("; @ = "))
            legend.insert(at, line)
    assert legend[-1] == "---" or "---" not in legend

    ZONE.write_text("\n".join(ghead + ["".join(r) for r in ground]) + "\n", encoding="utf-8")
    DECO.write_text("\n".join(legend + ["".join(r).rstrip() for r in deco]) + "\n", encoding="utf-8")
    for p in problems:
        print("  AVISO", p)
    print(f"  claro de 40 × 23 en ({DX}, {DY}); {len(problems)} avisos")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
