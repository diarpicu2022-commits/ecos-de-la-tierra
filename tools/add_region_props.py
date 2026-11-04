"""Añade a los `.deco.txt` de las regiones las piezas que el sistema de diseño
les pone y la matriz no traía: balancines y tubería en la Cuenca, manglares y
pescadores en la Costa, espantapájaros y campesinos en la Llanura, apachetas y
la abuela del páramo en la Cumbre (`components/Regiones`, `z_*.png`).

Reparte con semilla fija, cerca del camino principal, sin tapar camino, sin
pisar otra pieza y dejando una casilla libre alrededor: no cierra ningún paso.
Se corre una vez; lo que queda es dato. No repite lo que ya está.
"""
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ZONES = ROOT / "data" / "world" / "zones"
POOL = "àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ"

# zona: [(id, ancho, alto, sólido, cuántas)]
PLAN = {
    "tar_basin": [("pumpjack", 3, 2, True, 6), ("pipe_run", 3, 1, False, 3), ("npc_petrolero", 1, 1, True, 1)],
    "broken_coast": [("mangrove", 3, 2, True, 5), ("npc_pescadora", 1, 1, True, 1), ("npc_nino_costa", 1, 1, True, 1)],
    "withered_plain": [("scarecrow", 1, 1, True, 6), ("npc_campesina", 1, 1, True, 1), ("npc_nina_llanura", 1, 1, True, 1)],
    "waning_peak": [("apacheta", 2, 1, True, 5), ("npc_abuela_paramo", 1, 1, True, 1)],
}


def add(zone: str, plan: list) -> None:
    rng = np.random.default_rng(sum(map(ord, zone)))
    rows = (ZONES / f"{zone}.txt").read_text(encoding="utf8").split()
    H, W = len(rows), len(rows[0])
    path = ZONES / f"{zone}.deco.txt"
    text = path.read_text(encoding="utf8").replace("\r", "")
    head, body = text.split("\n---\n")
    deco = [list(r.ljust(W)) for r in body.split("\n")[:H]]
    used = set(re.findall(r"^; (\S) =", head, re.M))
    pool = iter(c for c in POOL if c not in used)
    near_path = np.zeros((H, W), bool)
    grid = np.array([list(r) for r in rows])
    ys, xs = np.where(grid == "=")
    for y, x in zip(ys, xs):
        near_path[max(0, y - 6):y + 7, max(0, x - 8):x + 9] = True

    def free(c, r, w, h):
        for j in range(r - 1, r + h + 1):
            for i in range(c - 1, c + w + 1):
                if not (0 < i < W - 1 and 0 < j < H - 1):
                    return False
                if deco[j][i] != " " or grid[j, i] not in ".:,":
                    return False
        return True

    for sid, w, h, solid, n in plan:
        if re.search(rf"^; \S = decor, {sid},", head, re.M):
            continue
        cells = np.argwhere(near_path & np.isin(grid, list(".:,")))
        rng.shuffle(cells)
        placed = 0
        ch = None
        taken = []
        for r, c in cells:
            if placed == n:
                break
            if any(abs(r - a) + abs(c - b) < 30 for a, b in taken):
                continue
            if not free(c, r, w, h):
                continue
            if ch is None or (w, h) != (1, 1):
                ch = next(pool)
                head += f"\n; {ch} = decor, {sid}, {'sólido' if solid else 'pisable'}, {w}x{h}"
            for j in range(h):
                for i in range(w):
                    deco[r + j][c + i] = ch
            taken.append((r, c))
            placed += 1
        print(f"  {zone}: {sid} × {placed}")
    body = "\n".join("".join(r).rstrip() for r in deco)
    path.write_text(head + "\n---\n" + body + "\n", encoding="utf8", newline="\n")


if __name__ == "__main__":
    for z, p in PLAN.items():
        add(z, p)
    sys.exit(0)
