"""Agranda la matriz de una zona en un factor 4/3 (contrato «Piel nueva»,
decisión de Diego del 2026-10-30: con el viewport de 640x360 las zonas pensadas
para 480x270 enseñaban dos viñetas por pantalla).

    python tools/scale_zone.py <zona> [<zona> ...]

Orden, porque cada paso depende del anterior:

1. Terreno (`<zona>.txt`): vecino más próximo. Cada tres filas y columnas se
   duplica una; un camino de 1 tile puede pasar a 2, nunca a 0.
2. Salidas (`exits.json`): la casilla de borde se queda en el borde, sobre el
   camino más cercano a su posición escalada. La llegada (`to_cell`) se pone un
   tile dentro, junto a la salida de vuelta, como pide el contrato «Umbral».
3. Borde: el camino que ganó un tile de ancho en el borde se cierra, salvo la
   casilla de salida (ningún borde pisable que no sea salida).
4. Decorado (`<zona>.deco.txt`): cada pieza conserva su tamaño en tiles y se
   ancla junto a su esquina escalada, sobre el mismo suelo y a la misma
   distancia del camino que tenía. Los pasos cerrados tapan el camino entero de
   lado a lado. El hito sigue junto a la fuente y la aparición, en la llegada.

El orden de viñetas, hito y fuente no cambia; `verify_zone.tscn` lo mide.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZONES = ROOT / "data" / "world" / "zones"
EXITS = ROOT / "data" / "world" / "exits.json"
NUM, DEN = 4, 3
LEGEND = re.compile(r"^; (\S) = (\w+), (\w+), (sólido|pisable)(?:, (\d+)x(\d+))?")
NOT_WALKABLE = "#~% "


def split_header(lines: list[str]) -> tuple[list[str], list[str]]:
    if "---" in lines:
        i = lines.index("---")
        return lines[: i + 1], lines[i + 1:]
    head = []
    while lines and lines[0].startswith(";"):
        head.append(lines.pop(0))
    return head, lines


def scale_grid(rows: list[str]) -> list[str]:
    w = max(len(r) for r in rows)
    rows = [r.ljust(w) for r in rows]
    nw, nh = math.ceil(w * NUM / DEN), math.ceil(len(rows) * NUM / DEN)
    return ["".join(rows[y * DEN // NUM][x * DEN // NUM] for x in range(nw)) for y in range(nh)]


def walkable(rows: list[str], x: int, y: int) -> bool:
    return 0 <= y < len(rows) and 0 <= x < len(rows[y]) and rows[y][x] not in NOT_WALKABLE


def cheb_to(rows: list[str], cells: list[tuple[int, int]], target: str = "=", radius: int = 10) -> int:
    best = radius + 1
    for x, y in cells:
        for yy in range(y - radius, y + radius + 1):
            for xx in range(x - radius, x + radius + 1):
                if 0 <= yy < len(rows) and 0 <= xx < len(rows[yy]) and rows[yy][xx] == target:
                    best = min(best, max(abs(xx - x), abs(yy - y)))
    return best


def route(rows: list[str], start, source) -> set:
    """Camino principal como lo mide verify_zone: el recorrido más corto sobre
    «=» desde la aparición hasta 2 tiles de la fuente."""
    from collections import deque
    if not start or not source:
        return set()
    par = {tuple(start): None}
    q = deque([tuple(start)])
    goal = None
    while q:
        c = q.popleft()
        if max(abs(c[0] - source[0]), abs(c[1] - source[1])) <= 2:
            goal = c
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if n in par or not (0 <= n[1] < len(rows) and 0 <= n[0] < len(rows[0])) or rows[n[1]][n[0]] != "=":
                continue
            par[n] = c
            q.append(n)
    out = set()
    while goal is not None:
        out.add(goal)
        goal = par[goal]
    return out


def route_dist(rt: set, cells) -> int:
    return max(min(max(abs(a - x), abs(b - y)) for a, b in rt) for x, y in cells) if rt else 99


def border_cell(rows: list[str], cell: list[int], old: tuple[int, int]) -> list[int]:
    ow, oh = old
    nw, nh = len(rows[0]), len(rows)
    x, y = cell
    tx = nw - 1 if x == ow - 1 else 0 if x == 0 else round(x * NUM / DEN)
    ty = nh - 1 if y == oh - 1 else 0 if y == 0 else round(y * NUM / DEN)
    on_v = x in (0, ow - 1)
    cands = [(tx, ty + d) if on_v else (tx + d, ty) for d in sorted(range(-5, 6), key=abs)]
    for cx, cy in cands:
        if walkable(rows, cx, cy) and rows[cy][cx] == "=":
            return [cx, cy]
    for cx, cy in cands:
        if walkable(rows, cx, cy):
            return [cx, cy]
    return [tx, ty]


def inward(cell: list[int], size: tuple[int, int]) -> list[int]:
    x, y = cell
    w, h = size
    if x == 0:
        return [1, y]
    if x == w - 1:
        return [w - 2, y]
    if y == 0:
        return [x, 1]
    return [x, h - 2]


def close_border(rows: list[str], exit_cells: set) -> list[str]:
    g = [list(r) for r in rows]
    h, w = len(g), len(g[0])
    border = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)] + \
             [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    for x, y in border:
        if g[y][x] not in NOT_WALKABLE and (x, y) not in exit_cells:
            # se cierra con el material no pisable vecino del borde
            fill = "#"
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and g[yy][xx] in NOT_WALKABLE and g[yy][xx] != " ":
                    fill = g[yy][xx]
                    break
            g[y][x] = fill
    return ["".join(r) for r in g]


def parse_deco(lines: list[str]):
    head, rows = split_header(lines)
    legend = {}
    for ln in head:
        m = LEGEND.match(ln)
        if m:
            size = (int(m.group(5)), int(m.group(6))) if m.group(5) else (1, 1)
            legend[m.group(1)] = {"kind": m.group(2), "id": m.group(3), "size": size}
    w = max((len(r) for r in rows), default=0)
    rows = [r.ljust(w) for r in rows]
    claimed, pieces = set(), []
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == " " or (x, y) in claimed or ch not in legend:
                continue
            sw, sh = legend[ch]["size"]
            for j in range(sh):
                for i in range(sw):
                    claimed.add((x + i, y + j))
            pieces.append((ch, x, y, sw, sh))
    return head, rows, legend, pieces


def scale_deco(lines, old_rows, new_rows, spawn_at):
    head, rows, legend, pieces = parse_deco(lines)
    nw, nh = len(new_rows[0]), len(new_rows)
    grid = [[" "] * nw for _ in range(nh)]
    old_at = lambda x, y: old_rows[y][x] if 0 <= y < len(old_rows) and 0 <= x < len(old_rows[y]) else "#"
    free = lambda cells: all(0 <= cx < nw and 0 <= cy < nh and grid[cy][cx] == " " for cx, cy in cells)

    def put(ch, cells):
        for cx, cy in cells:
            grid[cy][cx] = ch

    # Fuente (monstruo de historia), para medir el hito.
    src_old = next(((x, y) for ch, x, y, _, _ in pieces if legend[ch]["id"] == "monster"), None)
    spawn_old = next(((x, y) for ch, x, y, _, _ in pieces if legend[ch]["kind"] == "spawn"), None)
    route_old = route(old_rows, spawn_old, src_old)
    route_new = set()
    src_new = None
    order = sorted(pieces, key=lambda p: (legend[p[0]]["id"] != "monster", legend[p[0]]["kind"] != "landmark"))
    offsets = sorted({(dx, dy) for dx in range(-6, 7) for dy in range(-6, 7)}, key=lambda o: (abs(o[0]) + abs(o[1]), o))
    for ch, x, y, sw, sh in order:
        entry = legend[ch]
        if entry["kind"] == "spawn" and spawn_at:
            put(ch, [tuple(spawn_at)])
            continue
        if entry["id"] == "blocker":
            # paso cerrado: tapa el camino de lado a lado
            ox, oy = x, y
            horiz = walkable(old_rows, ox - 1, oy) or walkable(old_rows, ox + 1, oy)
            nxs = [nx for nx in range(nw) if nx * DEN // NUM == ox]
            nys = [ny for ny in range(nh) if ny * DEN // NUM == oy]
            cells = [(nxs[len(nxs) // 2], ny) for ny in nys] if horiz else [(nx, nys[len(nys) // 2]) for nx in nxs]
            put(ch, [c for c in cells if grid[c[1]][c[0]] == " "])
            continue
        old_cells = [(x + i, y + j) for j in range(sh) for i in range(sw)]
        # Una viñeta se mide casilla a casilla contra el camino principal.
        vig = entry["kind"] == "vignette" and route_old
        d0 = route_dist(route_old, old_cells) if vig else cheb_to(old_rows, old_cells)
        ax, ay = round(x * NUM / DEN), round(y * NUM / DEN)
        land_d0 = None
        if entry["kind"] == "landmark" and src_old and src_new:
            land_d0 = min(max(abs(src_old[0] - cx), abs(src_old[1] - cy)) for cx, cy in old_cells)
        placed = False
        for level in range(4):
            for dx, dy in offsets:
                px, py = ax + dx, ay + dy
                cells = [(px + i, py + j) for j in range(sh) for i in range(sw)]
                if not free(cells):
                    continue
                pairs = [(new_rows[py + j][px + i], old_at(x + i, y + j)) for j in range(sh) for i in range(sw)]
                same_ground = all(a == b for a, b in pairs)
                # compatible: el camino sigue siendo camino y lo pisable, pisable
                compat = all((a == "=") == (b == "=") and (a in NOT_WALKABLE) == (b in NOT_WALKABLE) for a, b in pairs)
                if not compat:
                    continue
                d1 = route_dist(route_new, cells) if vig else cheb_to(new_rows, cells)
                if entry["kind"] == "vignette" and d0 <= 2:
                    dist_ok = d1 <= d0
                else:
                    dist_ok = (d1 <= d0) if d0 <= 2 else (d1 >= min(d0, 3))
                if entry["id"] == "monster":
                    # la fuente se toca desde el camino (vecino en cruz, no en diagonal)
                    def touches(rws, cs):
                        return any(0 <= cy + dy < len(rws) and 0 <= cx + dx < len(rws[0]) and rws[cy + dy][cx + dx] == "="
                                   for cx, cy in cs for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    if touches(old_rows, old_cells) and not touches(new_rows, cells):
                        continue
                if land_d0 is not None:
                    dist_ok = dist_ok and min(max(abs(src_new[0] - cx), abs(src_new[1] - cy)) for cx, cy in cells) <= min(3, land_d0)
                if level == 0 and not (same_ground and dist_ok):
                    continue
                if level == 1 and not dist_ok:
                    continue
                if level >= 2 and entry["kind"] == "landmark" and not dist_ok:
                    continue
                if level == 2 and not same_ground:
                    continue
                if level == 3 and entry["kind"] in ("vignette", "landmark"):
                    continue
                put(ch, cells)
                if entry["id"] == "monster":
                    src_new = (px, py)
                    route_new = route(new_rows, spawn_at, src_new)
                placed = True
                break
            if placed:
                break
        if not placed:
            print(f"  AVISO  pieza {ch} en ({x},{y}) no cabe tras escalar")
    return head + ["".join(r).rstrip() for r in grid]


def main(zones: list[str]) -> None:
    exits = json.loads(EXITS.read_text(encoding="utf-8"))
    data = {}
    # 1. Terreno.
    for z in zones:
        lines = (ZONES / f"{z}.txt").read_text(encoding="utf-8").rstrip("\n").split("\n")
        head, rows = split_header(lines)
        old = (max(len(r) for r in rows), len(rows))
        data[z] = {"head": head, "old_rows": [r.ljust(old[0]) for r in rows], "old": old, "rows": scale_grid(rows)}
    # 2. Salidas: primero las casillas de borde, luego las llegadas.
    old_to = {}
    for e in exits["exits"]:
        old_to[id(e)] = list(e["to_cell"])
        if e["from"] in data:
            d = data[e["from"]]
            e["cell"] = border_cell(d["rows"], e["cell"], d["old"])
    for e in exits["exits"]:
        if e["to"] in data:
            d = data[e["to"]]
            back = [r for r in exits["exits"] if r["from"] == e["to"] and r["to"] == e["from"]]
            if back:
                e["to_cell"] = inward(back[0]["cell"], (len(d["rows"][0]), len(d["rows"])))
    # 3. Borde.
    for z, d in data.items():
        cells = {tuple(e["cell"]) for e in exits["exits"] if e["from"] == z}
        d["rows"] = close_border(d["rows"], cells)
        (ZONES / f"{z}.txt").write_text("\n".join(d["head"] + d["rows"]) + "\n", encoding="utf-8")
    # 4. Decorado, con la aparición en la llegada más cercana a la original.
    for z, d in data.items():
        deco = ZONES / f"{z}.deco.txt"
        if not deco.exists():
            continue
        dl = deco.read_text(encoding="utf-8").rstrip("\n").split("\n")
        _, rows, legend, pieces = parse_deco(dl)
        spawn_old = next(((x, y) for ch, x, y, _, _ in pieces if legend[ch]["kind"] == "spawn"), None)
        spawn_at = None
        if spawn_old:
            arrivals = [(e, old_to[id(e)]) for e in exits["exits"] if e["to"] == z]
            if arrivals:
                e, oc = min(arrivals, key=lambda a: abs(a[1][0] - spawn_old[0]) + abs(a[1][1] - spawn_old[1]))
                spawn_at = e["to_cell"]
        deco.write_text("\n".join(scale_deco(dl, d["old_rows"], d["rows"], spawn_at)) + "\n", encoding="utf-8")
        print(f"{z}: {d['old'][0]}x{d['old'][1]} -> {len(d['rows'][0])}x{len(d['rows'])}")
    text = json.dumps(exits, ensure_ascii=False, indent=2)
    text = re.sub(r"\{\s+\"from\": (\"\w+\"),\s+\"cell\": \[\s*(\d+),\s*(\d+)\s*\],\s+\"to\": (\"\w+\"),\s+\"to_cell\": \[\s*(\d+),\s*(\d+)\s*\]\s+\}",
                  r'{"from": \1, "cell": [\2, \3], "to": \4, "to_cell": [\5, \6]}', text)
    EXITS.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
