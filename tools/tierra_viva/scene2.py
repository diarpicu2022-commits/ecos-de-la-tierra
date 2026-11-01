"""Escena de mapa v2: terreno de map2 + hierba alta, flores, puente, piedras de
orilla, parches de hierba y objetos con sombra ordenados por la base."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import map2, maps2, px, world, flora, scene, ui
from map2 import T, shift, edge, rounded


def g2(rows, cmap):
    h, w = len(rows), max(len(r) for r in rows)
    a = np.zeros((h, w, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in cmap:
                a[y, x] = cmap[ch]
    return a


TALL = [
    "......o.....o...",
    ".....oho...oho..",
    "..o..olo..olho..",
    ".oho.olo..olo.o.",
    ".olo.oll.ollo.oh",
    ".ollooll.oml.olo",
    "oollmlmlooml.oml",
    "omlmllmmlommlmml",
    "omlmmlmmmmmmmmmo",
    "odmmdmmmdmmdmmdo",
    ".oddmdddmdddmddo",
    ".oddddddddddddo.",
    "..oooooooooooo..",
]

FLOWER = [".pp.", "pccp", ".pp.", "..g."]


def tall_tuft(P, seed=0, sway=0):
    """Mata de hierba alta cortable, una por casilla (16x14), como en Link's
    Awakening: briznas en abanico, luz arriba a la izquierda, contorno oscuro
    de su propia rampa y la tierra asomando entre mata y mata."""
    g = P['grass']
    rng = np.random.default_rng(seed)
    W_, H_ = 16, 14
    yy, xx = np.indices((H_, W_))
    m = np.zeros((H_, W_), int)
    blades = [(3, 4), (6, 1), (8, 0), (10, 2), (13, 5)]
    for i, (bx, tip) in enumerate(blades):
        bx += rng.integers(-1, 2) if 0 < i < 4 else 0
        tip += rng.integers(0, 2)
        tx = bx + (1 if sway else 0) * (1 if tip < 3 else 0)
        for y in range(tip, H_ - 1):
            f = (y - tip) / max(1, (H_ - 2 - tip))
            half = 0.5 + f * 1.6
            cx = tx + (bx - tx) * f
            sel = (np.abs(xx[y] - cx) <= half)
            m[y, sel] = i + 1
    body = m > 0
    img = px.new(W_, H_)
    img[body] = px.col(g[3])
    # luz: mitad izquierda de cada brizna y puntas
    for i in range(1, 6):
        bm = m == i
        if not bm.any():
            continue
        xs = np.where(bm.any(0))[0]
        mid = (xs.min() + xs.max()) / 2
        img[bm & (xx <= mid)] = px.col(g[4])
        top = np.where(bm.any(1))[0].min()
        img[bm & (yy <= top + 2)] = px.col(g[5])
        img[bm & (yy == top)] = px.col(g[6])
        img[bm & (yy >= H_ - 4) & (xx > mid)] = px.col(g[2])
    img[body & (yy >= H_ - 2)] = px.col(g[2])
    return px.outline(img, color=g[0])


def tall_sprite(P, sway=0):
    g = P['grass']
    rows = TALL if not sway else [r[1:] + r[:1] if i < 5 else r for i, r in enumerate(TALL)]
    return g2(rows, {'o': g[0], 'd': g[2], 'm': g[3], 'l': g[5], 'h': g[6]})


def macro_patches(img, info, P, seed=4):
    """Parches de pradera más clara y de hierba en sombra: rompen la alfombra."""
    H, W = img.shape[:2]
    rng = np.random.default_rng(seed)
    noise = ndi.gaussian_filter(rng.random((H // 4, W // 4)), 5)
    noise = np.kron(noise, np.ones((4, 4)))[:H, :W]
    hi_t = noise > np.quantile(noise, 0.80)
    lo_t = noise < np.quantile(noise, 0.12)
    free = ~info['path'] & ~info['wat'] & ~info['face']
    free = ndi.binary_erosion(free, iterations=3)
    g = P['grass']
    yy, xx = np.indices((H, W))
    for m, step in ((hi_t, 1), (lo_t, -1)):
        m = ndi.binary_opening(m, map2.disk(5)) & free
        tex = map2.tile_tex(H, W, map2.grass_tex({'grass': g[max(0, step):] + [g[-1]] * max(0, step)
                                                  if step > 0 else [g[0]] + g[:-1]}))
        core = ndi.binary_erosion(m, iterations=2)
        img[core] = tex[core]
        ring = m & ~core
        img[ring & ((xx + yy) % 2 == 0)] = tex[ring & ((xx + yy) % 2 == 0)]


def bank_stones(img, info, P, seed=7):
    """Piedras redondas a lo largo de las orillas laterales del agua."""
    wat = info['wat']
    s = P['stone']
    side = edge(wat, 1) & (shift(~wat, 0, 1) | shift(~wat, 0, -1))
    ys, xs = np.where(side)
    rng = np.random.default_rng(seed)
    order = np.argsort(ys * 1000 + xs)
    last = -99
    for k in order:
        y, x = ys[k], xs[k]
        if y - last < 9 + rng.integers(0, 6):
            continue
        last = y
        w = 3 + rng.integers(0, 3)
        st = g2(["." + "a" * (w - 2) + ".", "a" + "b" * (w - 2) + "a", "c" * w], {'a': s[4], 'b': s[3], 'c': s[1]})
        px.blit(img, st, x - w // 2, y - 1)


TUFT = [".l.l.", "ldldl", ".ddd."]
CLUMPG = ["..h...h.", ".hlh.hl.", ".lml.lmh", "dmmdlmml", ".dd.dd.d"]
REED = [".h..h", ".l.hl", "lm.lm", "mm.mm", "dd.dd"]


def free_grass(info):
    G = info['G']
    occ = info['path'] | info['wat'] | info['face'] | map2.up(np.isin(G, list('tf')))
    return ~ndi.binary_dilation(occ, iterations=4)


def tufts(img, info, P, seed=9):
    """Matas sueltas en una rejilla con desfase: detalle sin manchas."""
    g = P['grass']
    sp = g2(TUFT, {'l': g[5], 'd': g[3]})
    free = free_grass(info)
    rng = np.random.default_rng(seed)
    H, W = free.shape
    for y in range(6, H - 6, 22):
        for x in range(4 + (y // 22 % 2) * 11, W - 6, 22):
            jx, jy = x + rng.integers(-5, 6), y + rng.integers(-4, 5)
            if rng.random() < 0.55 and free[jy, jx]:
                px.blit(img, sp, jx, jy)
    big = g2(CLUMPG, {'h': g[6], 'l': g[5], 'm': g[3], 'd': g[2]})
    for y in range(14, H - 8, 38):
        for x in range(10 + (y // 38 % 2) * 19, W - 10, 38):
            jx, jy = x + rng.integers(-8, 9), y + rng.integers(-6, 7)
            if rng.random() < 0.6 and free[jy, jx] and free[jy + 4, jx + 7]:
                px.blit(img, big, jx, jy)


def water_life(img, info, P, state, seed=5):
    wat = info['wat']
    d = ndi.distance_transform_edt(wat)
    g = P['grass']
    rng = np.random.default_rng(seed)
    # juncos en la orilla
    if state == 'sano':
        reed = g2(REED, {'h': g[6], 'l': g[5], 'm': g[3], 'd': g[1]})
        shore = (d >= 1) & (d <= 2) & ~shift(~wat, 3, 0)
        ys, xs = np.where(shore)
        for k in rng.choice(len(ys), size=min(10, len(ys)), replace=False):
            px.blit(img, reed, xs[k] - 2, ys[k] - 4)
        # nenúfares en agua abierta
        lily = g2([".gg.g", "gllgg", ".ggg."], {'g': g[3], 'l': g[5]})
        ys, xs = np.where(d > 7)
        for k in rng.choice(len(ys), size=min(6, len(ys)), replace=False):
            px.blit(img, lily, xs[k] - 2, ys[k] - 1)
            if k % 3 == 0:
                img[ys[k] - 1, xs[k]] = P['flower'][2]
    # piedras que asoman en el agua
    s = P['stone']
    rock = g2([".abb.", "abbbc", "ccccc", ".www."], {'a': s[5], 'b': s[3], 'c': s[1], 'w': P['water'][5]})
    ys, xs = np.where(d > 6)
    for k in rng.choice(len(ys), size=min(3, len(ys)), replace=False):
        px.blit(img, rock, xs[k] - 2, ys[k] - 2)


def bridge(img, info, P):
    """Puentes y muelles: cada grupo de casillas 'B' es una pieza. Si es más
    ancho que alto cruza en horizontal (tablas verticales y barandillas arriba
    y abajo); si no, es un muelle que entra en el agua (tablas horizontales)."""
    G = info['G']
    lab, n = ndi.label(G == 'B')
    w = P['wood']
    H, W = img.shape[:2]
    for k in range(1, n + 1):
        ys, xs = np.where(lab == k)
        horiz = (xs.max() - xs.min()) >= (ys.max() - ys.min())
        if horiz:
            y0, y1 = ys.min() * T, (ys.max() + 1) * T
            x0, x1 = max(0, xs.min() * T - 6), min(W, (xs.max() + 1) * T + 6)
            deck = img[y0 - 2:y1 + 2, x0:x1]
            deck[:] = w[3]
            for i in range(0, x1 - x0, 5):
                deck[:, i] = w[1]
                deck[:, i + 1:i + 2] = w[4]
            deck[:2] = w[1]; deck[-3:-1] = w[1]; deck[-1] = P['water'][0]
            for yy in (y0 - 6, y1 - 2):
                img[yy:yy + 2, x0:x1] = w[4]
                img[yy + 2, x0:x1] = w[1]
                for x in range(x0, x1, 12):
                    img[yy - 2:yy + 5, x:x + 3] = w[2]
                    img[yy - 2, x:x + 3] = w[5]
        else:
            x0, x1 = xs.min() * T + 2, (xs.max() + 1) * T - 2
            y0, y1 = ys.min() * T - 4, min(H, (ys.max() + 1) * T)
            deck = img[y0:y1, x0:x1]
            deck[:] = w[3]
            for i in range(0, y1 - y0, 5):
                deck[i, :] = w[1]
                deck[i + 1, :] = w[4]
            deck[:, :2] = w[1]; deck[:, -2:] = w[1]
            img[y1:y1 + 2, x0:x1] = P['water'][0]
            for x in (x0, x1 - 3):
                for y in range(y0 + 6, y1, 14):
                    img[y - 3:y + 3, x:x + 3] = w[2]
                    img[y - 3, x:x + 3] = w[5]


def overlays(img, info, P, sway=0, state='sano'):
    G = info['G']
    G2 = G
    for (y, x) in np.argwhere(G2 == 't'):
        tuft = tall_tuft(P, seed=int(x * 7 + y * 13), sway=sway)
        px.blit(img, tuft, x * T, y * T + 2)
    if state == 'sano':
        crop = g2(["..g..", ".gGg.", "gGfGg", ".gGg.", "d...d"], {'g': P['grass'][3], 'G': P['grass'][5], 'f': P['flower'][7], 'd': P['dirt'][1]})
        corn = g2([".y.", "gyg", "g.g", ".g.", ".g.", "gg."], {'y': P['gold'][4], 'g': P['grass'][4]})
    else:
        crop = g2(["..d..", ".gdg.", "g.d.g", "..d..", "....."], {'g': P['drygrass'][4] if 'drygrass' in P else P['grass'][4], 'd': P['dirt'][2]})
        corn = g2([".d.", "gdg", "..g", ".g.", ".g.", "g.."], {'d': P['dirt'][2], 'g': P['grass'][4]})
    fm = info.get('farm')
    if fm is not None and fm.any():
        H_, W_ = fm.shape
        for y in range(3, H_ - 6, 6):
            for x in range(2 + (y // 6 % 2) * 3, W_ - 6, 6):
                if fm[y, x] and fm[y + 5, x + 4]:
                    sp = corn if (x // 32) % 3 == 1 else crop
                    px.blit(img, sp, x, y - 1)
    fc = [P['flower'][7], P['flower'][2], P['flower'][4]]
    rng = np.random.default_rng(2)
    if state == 'sano':
        for (y, x) in np.argwhere(G == 'f'):
            for j in range(4):
                fx, fy = x * T + (j % 2) * 7 + rng.integers(0, 4), y * T + (j // 2) * 7 + rng.integers(0, 3)
                c = fc[rng.integers(0, 3)]
                f = g2(FLOWER, {'p': c, 'c': P['flower'][3], 'g': P['grass'][2]})
                px.blit(img, f, fx, fy)
    else:
        for (y, x) in np.argwhere(G == 'f'):
            for j in range(3):
                fx, fy = x * T + rng.integers(1, 13), y * T + rng.integers(1, 13)
                img[fy + 1, fx + 1] = P['ash'][4]; img[fy + 2, fx + 1] = P['ash'][2]


TREE = scene.trim(np.array(Image.open('pl/obj2/tree_clean.png')))
import burnt as _burnt
BURNT = _burnt.burnt_tree_v2(scene.trim(np.array(Image.open('pl/obj2/tree_clean.png'))), 3)


def bush2(state='sano', seed=0):
    """Arbusto de 28x22 con los mismos racimos que la copa de los árboles."""
    ramp = flora.P['leaf'] if state == 'sano' else flora.P['deadleaf'] + [flora.P['deadleaf'][-1]]
    rng = np.random.default_rng(seed)
    circles = [(14, 12, 9), (7, 14, 6), (21, 14, 6), (10, 8, 6), (18, 7, 6), (14, 16, 6)]
    circles = [(x + rng.uniform(-1, 1), y + rng.uniform(-1, 1), r) for x, y, r in circles]
    can, m = flora.clumps_canopy(28, 22, circles, ramp, seed)
    img = px.new(28, 22)
    px.blit(img, can, 0, 0)
    if state == 'sano' and seed % 2 == 0:
        for x, y in [(9, 9), (17, 12), (13, 6)]:
            img[y, x] = px.col(flora.P['flower'][1]); img[y - 1, x] = px.col(flora.P['flower'][2])
    return px.outline(img)


def stump(state='sano'):
    """Tocón 24x20: anillos arriba, corteza sombreada y raíces."""
    w = flora.P['wood']
    W_, H_ = 24, 20
    top = px.ellipse(W_, H_, 12, 6, 10, 5)
    body = px.ellipse(W_, H_, 12, 13, 10, 5) | (np.indices((H_, W_))[0] >= 6) & (np.indices((H_, W_))[0] <= 13) & (np.abs(np.indices((H_, W_))[1] - 11.5) <= 10)
    roots = px.ellipse(W_, H_, 3, 16, 3, 2.5) | px.ellipse(W_, H_, 20, 16, 3.5, 2.5) | px.ellipse(W_, H_, 12, 16, 5, 3)
    img = px.shade(body | roots, w[1:6], ambient=0.2)
    yy, xx = np.indices((H_, W_))
    img[(body | roots) & ((xx * 2 + yy) % 7 == 0) & ~top] = px.col(w[1])
    ring = px.shade(top, [flora.P['sand'][0], flora.P['sand'][1], flora.P['sand'][2], flora.P['sand'][3], flora.P['sand'][4]], ambient=0.4)
    img[top] = ring[top]
    for rx, ry in ((7, 3.4), (4, 2)):
        e = px.ellipse(W_, H_, 12, 6, rx, ry) & ~px.ellipse(W_, H_, 12, 6, rx - 1, ry - 0.8)
        img[e] = px.col(flora.P['sand'][1])
    img[6, 12] = px.col(w[2])
    return px.outline(img)


def sign():
    """Cartel de madera 22x24."""
    w = flora.P['wood']
    W_, H_ = 22, 24
    img = px.new(W_, H_)
    board = np.zeros((H_, W_), bool); board[1:12, 1:21] = True
    post = np.zeros((H_, W_), bool); post[11:24, 9:13] = True
    img[post] = px.col(w[2]); img[post & (np.indices((H_, W_))[1] == 9)] = px.col(w[3])
    img[board] = px.col(w[4])
    img[2:4, 1:21] = px.col(w[5])
    img[10:12, 1:21] = px.col(w[2])
    for y in (5, 8):
        img[y, 4:17] = px.col(w[2])
    img[5, 13:15] = px.col(w[4])
    return px.outline(img)


def log_(sick=False):
    """Tronco caído 44x16 con la sección cortada a la derecha."""
    w = flora.P['wood']
    W_, H_ = 44, 16
    body = np.zeros((H_, W_), bool); body[2:14, 3:38] = True
    body |= px.ellipse(W_, H_, 4, 8, 4, 6)
    img = px.shade(body, w[1:6], light=(-0.2, -0.9, 0.5), ambient=0.2)
    yy, xx = np.indices((H_, W_))
    img[body & (yy % 4 == 1) & ((xx + yy) % 9 < 6)] = px.col(w[2])
    end = px.ellipse(W_, H_, 38, 8, 5, 6.5)
    img[end] = px.col(flora.P['sand'][2])
    e2 = px.ellipse(W_, H_, 38, 8, 3, 4) & ~px.ellipse(W_, H_, 38, 8, 2, 3)
    img[e2] = px.col(flora.P['sand'][0])
    img[end & ~px.ellipse(W_, H_, 38, 8, 4, 5.5)] = px.col(w[4])
    moss = body & (yy <= 4) & ((xx % 11) < 5) & (xx > 6) & (xx < 34) & (not sick)
    img[moss] = px.col(flora.P['grass'][4])
    img[moss & (yy == 2)] = px.col(flora.P['grass'][5])
    return px.outline(img)


def mushrooms():
    f = flora.P['flower']
    return px.outline(g2([
        ".rrr.....",
        "rwrrr.rr.",
        "rrrwr.rwr",
        ".sss.rrr.",
        "..s...s..",
        ".gsg.gsg.",
    ], {'r': f[0], 'w': f[7], 's': flora.P['wall'][3], 'g': flora.P['grass'][2]}))


def char(spr, sick):
    """En la versión enferma la madera de los props también está quemada:
    se pasa a la rampa de carbón por luminancia, con alguna brasa."""
    if not sick:
        return spr
    out = spr.copy()
    a = out[..., 3] > 0
    lum = out[..., :3].astype(float) @ [0.3, 0.59, 0.11]
    ramp = [px.col(c) for c in _burnt.CHAR] + [px.col(_burnt.CHAR[-1])]
    q = np.quantile(lum[a], [0.15, 0.4, 0.65, 0.85])
    idx = np.digitize(lum, q)
    for k in range(5):
        out[a & (idx == k)] = ramp[k]
    yy, xx = np.indices(a.shape)
    out[a & (idx >= 3) & ((xx * 7 + yy * 3) % 23 == 0)] = px.col(flora.P['fire'][3])
    return out


def forest_objects(state, info=None):
    sick = state != 'sano'
    t = BURNT if sick else TREE
    objs = []
    spots = [(-40, 48), (40, 30), (150, 40), (250, 30), (300, 66), (380, 40),
             (-60, 140), (-56, 350),
             (150, 420), (230, 432),
             (560, 64), (590, 10), (604, 128), (590, 220), (604, 320), (560, 430)]
    for i, x, y in solve_trees(spots, info, 'bosque'):
        sp = t if i % 2 else t[:, ::-1]
        objs.append((sp, x, y, 54))
    for i, (x, y) in enumerate([(118, 190), (300, 182), (420, 238), (196, 256), (420, 120), (30, 250), (560, 340)]):
        objs.append((bush2(state, i), x, y, 22))
    for x, y in [(170, 100), (380, 196), (470, 262), (276, 310), (110, 352)]:
        objs.append((flora.rock('enfermo' if sick else 'sano'), x, y, 12))
    objs.append((char(stump(), sick), 196, 124, 22))
    objs.append((char(stump(), sick), 470, 304, 22))
    objs.append((sign(), 280, 206, 10))
    objs.append((char(log_(sick), sick), 76, 100, 40))
    if not sick:
        objs.append((mushrooms(), 220, 126, 0))
        objs.append((mushrooms(), 196, 330, 0))
    return objs


def foot_x(spr):
    """Centro del pie del sprite: media de las columnas opacas de las 6 filas de abajo."""
    a = spr[-6:, :, 3] > 0
    xs = np.where(a.any(0))[0]
    return int(xs.mean()) if len(xs) else spr.shape[1] // 2


def is_tree(spr):
    return any(spr is t or spr.base is t for t in (TREE, BURNT))


def tree_ok(spr, x, yb, info, max_canopy=0.08):
    H, W = info['path'].shape
    blocked = info['path'] | info['wat'] | info['face']
    cx = x + foot_x(spr)
    yy, xx = np.mgrid[yb - 8:yb, cx - 10:cx + 10]
    ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
    if ok.any() and blocked[yy[ok], xx[ok]].any():
        return False
    h_, w_ = spr.shape[:2]
    ys, xs = np.where(spr[..., 3] > 0)
    Y, X = ys + yb - h_, xs + x
    on = (Y >= 0) & (Y < H) & (X >= 0) & (X < W)
    return not on.any() or (info['path'] | info['wat'])[Y[on], X[on]].mean() <= max_canopy


_SOLVED = {}


def solve_trees(spots, info, key):
    """Ajusta cada sitio al válido más cercano para el árbol sano Y el quemado
    (el bosque no se mueve al purificarse). Si no hay hueco cerca, se quita."""
    if key in _SOLVED:
        return _SOLVED[key]
    out = []
    offs = sorted({(dx, dy) for dx in range(-48, 49, 8) for dy in range(-32, 33, 8)},
                  key=lambda o: o[0] ** 2 + o[1] ** 2)
    for i, (x, y) in enumerate(spots):
        sprites = [TREE if i % 2 else TREE[:, ::-1], BURNT if i % 2 else BURNT[:, ::-1]]
        for dx, dy in offs:
            if all(tree_ok(sp, x + dx, y + dy, info) for sp in sprites):
                out.append((i, x + dx, y + dy))
                break
    _SOLVED[key] = out
    return out


def check_trees(objs, info, max_canopy=0.08):
    """Regla: el pie de un árbol va sobre hierba libre y su copa casi no tapa
    agua ni camino. Si algo la incumple, la escena no se genera."""
    H, W = info['path'].shape
    blocked = info['path'] | info['wat'] | info['face']
    bad = []
    for o in objs:
        spr, x, yb = o[0], o[1], o[2]
        if not is_tree(spr):
            continue
        cx = x + foot_x(spr)
        yy, xx = np.mgrid[yb - 8:yb, cx - 10:cx + 10]
        ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
        foot_hit = blocked[yy[ok], xx[ok]].any() if ok.any() else False
        h_, w_ = spr.shape[:2]
        ys, xs = np.where(spr[..., 3] > 0)
        Y, X = ys + yb - h_, xs + x
        on = (Y >= 0) & (Y < H) & (X >= 0) & (X < W)
        frac = (info['path'] | info['wat'])[Y[on], X[on]].mean() if on.any() else 0
        if foot_hit or frac > max_canopy:
            bad.append((x, yb, 'pie' if foot_hit else f'copa {frac:.0%}'))
    if bad:
        raise ValueError(f'árboles mal puestos: {bad}')


def render(state='sano', actors=(), frame=0, sign=None, dialog=None, spec=None, objects=None, view=(0, 0, 640, 360)):
    img, info = map2.render(spec or maps2.BOSQUE, state, frame)
    P = info['P']
    tufts(img, info, P)
    water_life(img, info, P, state)
    bridge(img, info, P)
    overlays(img, info, P, frame % 2, state)
    objs = (objects(state, info) if objects else forest_objects(state, info)) + list(actors)
    for o in [o for o in objs if isinstance(o[0], str)]:     # calcos de suelo
        px.blit(img, o[1], o[2], o[3])
    objs = [o for o in objs if not isinstance(o[0], str)]
    check_trees(objs, info)
    if state != 'sano':
        for o in objs:
            if is_tree(o[0]):
                cx = o[1] + foot_x(o[0])
                dec = _burnt.soot(64, 14, seed=abs(int(cx)))
                px.blit(img, dec, cx - 32, o[2] - 9)
    world.place(img, objs)
    if view:
        x0, y0, w0, h0 = view
        img = img[y0:y0 + h0, x0:x0 + w0].copy()
    if sign:
        px.blit(img, ui.sign(*sign), 12, 12)
    if dialog:
        scene.dialog(img, *dialog)
    return img


HOUSE = np.array(Image.open('pl/obj3/house.png'))


def fence(n):
    """Valla de n tramos de 12 px: postes con caperuza y dos travesaños."""
    w = flora.P['wood']
    W_ = n * 12 + 4
    img = px.new(W_, 16)
    for k in range(n):
        x = k * 12
        img[5:7, x:x + 14] = px.col(w[4]); img[7, x:x + 14] = px.col(w[2])
        img[10:12, x:x + 14] = px.col(w[4]); img[12, x:x + 14] = px.col(w[2])
    for k in range(n + 1):
        x = k * 12
        img[2:16, x:x + 3] = px.col(w[3]); img[2:16, x + 2] = px.col(w[2])
        img[1, x:x + 3] = px.col(w[5]); img[2, x] = px.col(w[4])
    return px.outline(img)


def ashen(spr, k=0.55, dark=0.82):
    """Lo construido en zona enferma: el color se apaga hacia el gris ceniza
    y baja de valor, y las flores de las ventanas se secan. Nada de colores
    nuevos: se queda entre la rampa ash y el color original."""
    out = spr.copy()
    a = out[..., 3] > 0
    rgb = out[..., :3].astype(float)
    lum = rgb @ [0.3, 0.59, 0.11]
    ash = np.stack([lum * 0.98, lum * 0.94, lum * 1.0], -1)
    mix = (rgb * (1 - k) + ash * k) * dark
    out[..., :3][a] = np.clip(mix[a], 0, 255).astype(np.uint8)
    return out


def village_objects(state, info=None):
    sick = state != 'sano'
    t = BURNT if sick else TREE
    objs = []
    house = ashen(HOUSE) if sick else HOUSE
    for x, yb in [(61, 146), (397, 146), (61, 334), (397, 334)]:
        objs.append((house, x, yb, 0))
    spots = [(-50, 40), (160, 30), (250, 36), (560, 30), (-60, 250), (626, 300)]
    for i, x, y in solve_trees(spots, info, 'valdehoja'):
        sp = t if i % 2 else t[:, ::-1]
        objs.append((sp, x, y, 54))
    for x, y, n in [(4, 162, 4), (134, 162, 3), (342, 162, 1), (500, 162, 3),
                    (4, 226, 4), (500, 226, 3)]:
        objs.append((ashen(fence(n)) if sick else fence(n), x, y, 0))
    for i, (x, y) in enumerate([(176, 120), (240, 270), (520, 120), (340, 280)]):
        objs.append((bush2(state, i), x, y, 22))
    objs.append((sign(), 244, 168, 10))
    objs.append((char(stump(), sick), 470, 280, 22))
    return objs


import buildings as B


def hay():
    m = px.ellipse(22, 16, 11, 9, 10.5, 7)
    img = px.shade(m, flora.P['gold'][1:6], ambient=0.2)
    yy, xx = np.indices(m.shape)
    img[m & ((xx * 3 + yy) % 5 == 0)] = px.col(flora.P['gold'][2])
    img[m & (np.abs(xx - 7) < 1)] = px.col(flora.P['wood'][2]); img[m & (np.abs(xx - 15) < 1)] = px.col(flora.P['wood'][2])
    return px.outline(img)


def cart():
    """Carreta de madera con costales."""
    w = flora.P['wood']
    img = px.new(40, 26)
    img[6:16, 4:36] = px.col(w[3]); img[6, 4:36] = px.col(w[4]); img[15, 4:36] = px.col(w[1])
    for x in range(4, 36, 6):
        img[6:16, x] = px.col(w[2])
    for cx in (12, 28):
        m = px.ellipse(40, 26, cx, 19, 6, 6) & ~px.ellipse(40, 26, cx, 19, 4, 4)
        img[m] = px.col(w[1])
        img[19, cx - 4:cx + 5] = px.col(w[2]); img[15:24, cx] = px.col(w[2])
    img[10:12, 36:40] = px.col(w[2])
    for cx in (12, 22, 30):
        sk = px.ellipse(40, 26, cx, 5, 5, 4)
        img[sk] = px.col(flora.P['sand'][2]); img[sk & (np.indices((26, 40))[0] < 4)] = px.col(flora.P['sand'][3])
    return px.outline(img)


def laundry():
    """Tendedero entre dos postes con ropa de colores."""
    img = px.new(70, 30)
    w = flora.P['wood']
    for x in (1, 66):
        img[2:30, x:x + 3] = px.col(w[2]); img[2:30, x] = px.col(w[3])
    for x in range(4, 66):
        y = 4 + int(3 * np.sin(np.pi * (x - 4) / 62))
        img[y, x] = px.col(flora.P['stone'][2])
    for i, (x, c, hh) in enumerate([(10, 'roofr', 12), (22, 'paper', 9), (34, 'roofb', 14), (48, 'gold', 10)]):
        y = 5 + int(3 * np.sin(np.pi * (x - 4) / 62))
        r = flora.P[c]
        img[y:y + hh, x:x + 9] = px.col(r[3] if c != 'paper' else r[4])
        img[y:y + hh, x + 8] = px.col(r[2])
        img[y + hh - 1, x:x + 9] = px.col(r[2])
    return px.outline(img)


def ring_planter(state='sano'):
    """Cerco de piedra bajo el Árbol del Vínculo: muro bajo con hierba dentro."""
    W_, H_ = 84, 30
    img = px.new(W_, H_)
    yy, xx = np.indices((H_, W_))
    outer = ((xx - 42) / 41) ** 2 + ((yy - 13) / 12) ** 2 <= 1
    wall_ = ((xx - 42) / 41) ** 2 + ((yy - 17) / 12) ** 2 <= 1
    inner = ((xx - 42) / 36) ** 2 + ((yy - 13) / 9) ** 2 <= 1
    s = flora.P['stone']
    img[wall_] = px.col(s[2])
    img[wall_ & (xx % 6 == 0)] = px.col(s[1])
    img[outer] = px.col(s[4])
    img[outer & ((xx + yy * 2) % 9 == 0)] = px.col(s[3])
    img[outer & ~(((xx - 42) / 40) ** 2 + ((yy - 13) / 11) ** 2 <= 1)] = px.col(s[5])
    gr = flora.P['grass'] if state == 'sano' else flora.P['drygrass']
    img[inner] = px.col(gr[3])
    img[inner & ((xx * 3 + yy) % 7 == 0)] = px.col(gr[5])
    return px.outline(img)


def place_door(spr, name, door_col, base_row):
    """Coloca un edificio con la puerta encima de su senda (columna) y el
    escalón tocando la casilla donde empieza."""
    return (spr, (door_col + 1) * 16 - B.DOOR[name], base_row * 16 + 4, 0)


BLD_OVERRIDE = {}   # nombre -> (sprite, x de la puerta) cuando hay versión de PixelLab
# sprites elegidos de PixelLab: archivo y centro de la puerta (x en el sprite)
BLD_PL = {'posada': ('posadaC_0', 51), 'panaderia': ('panaderia_0', 49), 'escuela': ('escuela_0', 51),
          'alcaldia': ('alcaldia_0', 50), 'granero': ('granero_0', 52), 'botes': ('botes_0', 52), 'torre': ('torre_0', 17),
          'xx': ('posada_0', 52), 'tienda': ('tienda_0', 26), 'taller': ('taller_0', 52),
          'cabana': ('cabana_0', 53), 'casita': ('casita_0', 52), 'casa_pescador': ('pescador_0', 53),
          'molino': ('molino_0', 52), 'capilla': ('capilla_0', 53), 'casa_crema': ('casa_crema_0', 51)}


def load_overrides():
    import os
    for name, (fn, door) in BLD_PL.items():
        p = f'pl/bld/{fn}.png'
        if os.path.exists(p):
            import roofix
            a = np.array(Image.open(p).convert('RGBA'))
            rows = np.where(a[..., 3].any(1))[0]
            BLD_OVERRIDE[name] = (roofix.fix_top(a[:rows.max() + 1]), door)   # sin filas vacías abajo: que pise el suelo


def bld(name):
    if name in BLD_OVERRIDE:
        return BLD_OVERRIDE[name]
    spr = getattr(B, name)()
    return spr, B.DOOR[name]


def yard(objs, spr, x, yb, door_cx, sh, fence_l=True, fence_r=True, pots=True):
    """Patio delantero compuesto: valla a cada lado de la senda, alineada con
    el frente, y una maceta a cada lado de la puerta."""
    w = spr.shape[1]
    fy = yb + 14
    left_w = door_cx - 14 - (x + 4)
    right_w = (x + w - 4) - (door_cx + 14)
    if fence_l and left_w >= 16:
        objs.append((sh(fence(left_w // 12)), x + 4, fy, 0))
    if fence_r and right_w >= 16:
        n = right_w // 12
        objs.append((sh(fence(n)), door_cx + 14 + (right_w - (n * 12 + 4)), fy, 0))
    if pots:
        objs.append((sh(B.pot_plant(door_cx)), door_cx - 20, yb + 4, 0))
        objs.append((sh(B.pot_plant(door_cx + 1)), door_cx + 13, yb + 4, 0))


def village2_objects(state, info=None):
    load_overrides()
    sick = state != 'sano'
    sh = (lambda s: ashen(s)) if sick else (lambda s: s)
    objs = []
    # edificios: (nombre, columna de la senda de la puerta, fila donde empieza)
    plan = [('capilla', 27, 8, False), ('cabana', 10, 6, True), ('casita', 36, 6, True),
            ('posada', 13, 20, False), ('tienda', 39, 20, False), ('molino', 47, 19, False),
            ('taller', 7, 29, True), ('casa_crema', 18, 29, True), ('casa_pescador', 37, 29, True)]
    for name, c, r, has_yard in plan:
        spr, door = bld(name)
        spr = sh(spr)
        door_cx = (c + 1) * 16
        x, yb = door_cx - door, r * 16 + 4
        objs.append((spr, x, yb, 0))
        if has_yard:
            yard(objs, spr, x, yb, door_cx, sh)
        elif name in ('posada', 'tienda'):
            yard(objs, spr, x, yb, door_cx, sh, fence_l=False, fence_r=False)
    # plaza simétrica: el Árbol del Vínculo en su cerco, un puesto a cada lado,
    # bancos enfrentados mirando al árbol y un farol en cada esquina
    t = BURNT if sick else TREE
    cx = 448
    objs.append(('decal', ring_planter(state), cx - 42, 304 - 17))
    objs.append((t.copy(), cx - foot_x(t), 304, 60))
    objs.append((sh(B.stall()), cx - 128, 266, 0))
    objs.append((sh(B.stall(('roofb', 'paper'), 'tela')), cx + 128 - 46, 266, 0))
    objs.append((sh(B.bench()), cx - 84, 336, 0))
    objs.append((sh(B.bench()), cx + 58, 336, 0))
    for x, y in [(cx - 142, 232), (cx + 136, 232), (cx - 142, 352), (cx + 136, 352)]:
        objs.append((B.lamp_post(), x, y, 6))
    objs.append((sign(), cx - 64, 372, 10))
    # el rincón del molino: carreta, pacas y cajas juntas, junto a su puerta
    objs.append((sh(cart()), 700, 430, 0))
    objs.append((sh(hay()), 744, 440, 0))
    objs.append((sh(hay()), 760, 452, 0))
    # bancales: pacas al borde, y la fuente en la terraza, frente a la capilla
    objs.append((sh(hay()), 760, 128, 0))
    objs.append((sh(B.fountain()), 260, 128, 0))
    # patio trasero entre el taller y la casa crema: el tendedero
    objs.append((sh(laundry()), 196, 420, 0))
    # pozo en la esquina del jardín de flores del oeste
    objs.append((sh(B.well()), 112, 232, 0))
    # arbustos solo en pares: a los lados de las dos escaleras
    for i, (x, y) in enumerate([(392, 186), (476, 186), (742, 84), (804, 84)]):
        objs.append((bush2(state, i), x, y, 22))
    # bosquecillos del borde, no árboles sueltos en medio
    spots = [(-40, 60), (30, 40), (100, 76), (600, 40), (690, 60),
             (-50, 200), (-30, 300), (880, 120), (920, 200), (900, 330), (930, 440),
             (-50, 560), (60, 580), (160, 590), (330, 600), (560, 600), (720, 590), (840, 570)]
    for i, x, y in solve_trees(spots, info, 'valdehoja2b'):
        sp = t if i % 2 else t[:, ::-1]
        objs.append((sp, x, y, 54))
    return objs


def fruit_tree(state='sano', seed=0, fruit=3):
    """Frutal del huerto: copa redonda de racimos, tronco corto y fruta."""
    ramp = flora.P['leaf'] if state == 'sano' else flora.P['deadleaf'] + [flora.P['deadleaf'][-1]]
    rng = np.random.default_rng(seed)
    W_, H_ = 42, 46
    circles = [(21, 16, 13), (11, 19, 8), (31, 19, 8), (15, 9, 8), (27, 9, 8), (21, 22, 9)]
    circles = [(x + rng.uniform(-1, 1), y + rng.uniform(-1, 1), r) for x, y, r in circles]
    can, m = flora.clumps_canopy(W_, 32, circles, ramp, seed)
    img = px.new(W_, H_)
    w = flora.P['wood']
    img[28:44, 18:24] = px.col(w[3]); img[28:44, 18] = px.col(w[4]); img[28:44, 22:24] = px.col(w[2])
    img[42:44, 15:27] = px.col(w[2])
    px.blit(img, can, 0, 0)
    if state == 'sano':
        ys, xs = np.where(m & (np.indices(m.shape)[0] > 6))
        for k in rng.choice(len(ys), size=9, replace=False):
            y, x = ys[k], xs[k]
            img[y, x] = px.col(flora.P['flower'][fruit]); img[y, x + 1] = px.col(flora.P['flower'][fruit])
            img[y + 1, x] = px.col(flora.P['flower'][fruit]); img[y + 1, x + 1] = px.col(flora.P['roofr'][2])
            img[y - 1, x] = px.col(flora.P['flower'][4])
    return px.outline(img)


def village3_objects(state, info=None):
    load_overrides()
    sick = state != 'sano'
    sh = (lambda s: ashen(s)) if sick else (lambda s: s)
    objs = []
    plan = [('torre', 4, 8, False), ('cabana', 12, 8, True), ('granero', 24, 8, False), ('capilla', 39, 8, False), ('casita', 56, 8, True),
            ('botes', 65, 45, False),
            ('escuela', 10, 26, True), ('posada', 24, 26, False), ('tienda', 54, 26, False), ('molino', 72, 24, False),
            ('alcaldia', 40, 42, False),
            ('taller', 10, 48, True), ('casa_crema', 18, 48, True), ('panaderia', 27, 48, True),
            ('casa_pescador', 52, 48, True)]
    for name, c, r, has_yard in plan:
        if name not in BLD_OVERRIDE and not hasattr(B, name):
            continue
        spr, door = bld(name)
        spr = sh(spr)
        door_cx = (c + 1) * 16
        x, yb = door_cx - door, r * 16 + 4
        objs.append((spr, x, yb, 0))
        if has_yard:
            yard(objs, spr, x, yb, door_cx, sh)
        elif name in ('posada', 'tienda', 'molino'):
            yard(objs, spr, x, yb, door_cx, sh, fence_l=False, fence_r=False)
    t = BURNT if sick else TREE
    # plaza del Árbol del Vínculo (cols 30-49, filas 18-27)
    cx, cy = 40 * 16, 23 * 16 + 8
    objs.append(('decal', ring_planter(state), cx - 42, cy - 17))
    objs.append((t.copy(), cx - foot_x(t), cy, 60))
    objs.append((sh(B.stall()), 31 * 16, 21 * 16, 0))
    objs.append((sh(B.stall(('roofb', 'paper'), 'tela')), 46 * 16 + 6, 21 * 16, 0))
    objs.append((sh(B.stall(('roofr', 'paper'), 'fruta')), 31 * 16, 26 * 16, 0))
    objs.append((sh(B.stall(('eco', 'paper'), 'tela')), 46 * 16 + 6, 26 * 16, 0))
    objs.append((sh(B.bench()), cx - 84, cy + 34, 0))
    objs.append((sh(B.bench()), cx + 58, cy + 34, 0))
    for x, y in [(30 * 16 + 2, 18 * 16 + 14), (50 * 16 - 10, 18 * 16 + 14), (30 * 16 + 2, 28 * 16 - 2), (50 * 16 - 10, 28 * 16 - 2)]:
        objs.append((B.lamp_post(), x, y, 6))
    # plazoleta del ayuntamiento con su fuente (cols 34-47, filas 42-48)
    f = sh(B.fountain())
    objs.append((f, 41 * 16 - f.shape[1] // 2, 47 * 16, 0))
    for x, y in [(34 * 16 + 2, 43 * 16), (48 * 16 - 10, 43 * 16), (34 * 16 + 2, 49 * 16 - 2), (48 * 16 - 10, 49 * 16 - 2)]:
        objs.append((B.lamp_post(), x, y, 6))
    objs.append((sh(B.bench()), 36 * 16, 48 * 16, 0))
    objs.append((sh(B.bench()), 44 * 16, 48 * 16, 0))
    # huerto de frutales al sur del camino, en rejilla
    for i, (x, y) in enumerate([(x, y) for y in range(36 * 16, 41 * 16, 44) for x in range(12 * 16, 27 * 16, 52)]):
        tr = fruit_tree(state, i, [3, 0, 1][i % 3])
        objs.append((tr, x, y, 26))
    objs.append((sh(cart()), 4 * 16, 38 * 16, 0))
    objs.append((sh(hay()), 3 * 16, 41 * 16, 0))
    objs.append((sh(B.well()), 28 * 16, 40 * 16, 0))
    # muelle: barca y cajas de pesca
    objs.append((sh(crate_fish()), 64 * 16, 39 * 16, 0))
    objs.append(('decal', boat(), 70 * 16 + 4, 40 * 16 + 2))
    # carteles en las salidas
    for x, y in [(2 * 16, 29 * 16 + 4), (86 * 16, 29 * 16 + 4), (42 * 16 + 4, 57 * 16), (62 * 16 + 4, 9 * 16)]:
        objs.append((sign(), x, y, 10))
    # potrero del sur: valla perimetral y pacas
    for y in (52 * 16 + 8, 58 * 16):
        objs.append((sh(fence(14)), 7 * 16, y, 0))
    for i, (x, y) in enumerate([(9 * 16, 55 * 16), (13 * 16, 56 * 16), (17 * 16, 55 * 16 + 6)]):
        objs.append((sh(hay()), x, y, 0))
    # mirador en la terraza alta: banco frente al valle
    objs.append((sh(B.bench()), 66 * 16, 4 * 16 + 4, 0))
    objs.append((B.lamp_post(), 70 * 16, 4 * 16, 6))
    # molino: pacas
    objs.append((sh(hay()), 69 * 16, 26 * 16, 0))
    objs.append((sh(laundry()), 21 * 16, 46 * 16 - 8, 0))
    # pares de arbustos en las escaleras
    for i, (x, y) in enumerate([(37 * 16 - 8, 14 * 16), (41 * 16 + 4, 14 * 16), (58 * 16, 7 * 16 + 4), (62 * 16 + 4, 7 * 16 + 4)]):
        objs.append((bush2(state, i), x, y, 22))
    # bosquecillos del borde
    spots = [(-40, 60), (40, 40), (180, 30), (300, 50), (560, 40), (680, 36), (1300, 80), (1360, 140),
             (-50, 300), (-40, 420), (-30, 560), (-40, 740), (60, 960), (220, 980), (400, 990), (760, 990),
             (1000, 980), (1180, 990), (1340, 960), (1380, 640), (1380, 520), (1300, 300), (1050, 200), (900, 210)]
    for i, x, y in solve_trees(spots, info, 'valdehoja3'):
        sp = t if i % 2 else t[:, ::-1]
        objs.append((sp, x, y, 54))
    return objs


def boat():
    """Barca de madera amarrada al muelle, vista desde arriba."""
    w = flora.P['wood']
    W_, H_ = 34, 14
    yy, xx = np.indices((H_, W_))
    hull = ((xx - 17) / 16.5) ** 2 + ((yy - 7) / 6.5) ** 2 <= 1
    inner = ((xx - 17) / 14) ** 2 + ((yy - 7) / 4.5) ** 2 <= 1
    img = px.new(W_, H_)
    img[hull] = px.col(w[2])
    img[hull & (yy < 5)] = px.col(w[4])
    img[inner] = px.col(w[3])
    img[inner & (xx % 8 == 0)] = px.col(w[1])
    img[inner & (yy == 7) & (xx > 8) & (xx < 26)] = px.col(w[4])
    return px.outline(img)


def crate_fish():
    img = B.crate('papa')
    img[1:3, 2:10] = px.col(flora.P['stone'][4])
    img[1, 3:9:2] = px.col(flora.P['water'][5])
    return img


if __name__ == '__main__':
    import sys
    for st in ('sano', 'enfermo'):
        try:
            px.save(render(st), f'out2/bosque_{st}.png', scale=2)
        except ValueError as e:
            print('bosque', st, e)
        px.save(render(st, spec=maps2.VALDEHOJA, objects=village_objects), f'out2/valdehoja_{st}.png', scale=2)
    for st in ('sano', 'enfermo'):
        px.save(render(st), f'out2/bosque_{st}.png', scale=2)


# ---------------------------------------------------------------------------
# Valdehoja densa (VALDEHOJA4)
NEW_HOUSES = ['azul', 'balcon', 'piedra', 'esquina', 'mostaza', 'naranja', 'lavanda', 'sastre']


def roof_variant(spr, shift_deg):
    """Variante de color: gira solo el tono de los tejados rojos/naranjas, y
    deja muros y madera como están. Así una misma tipología da casas vecinas
    distintas, como en un pueblo real."""
    import colorsys
    out = spr.copy()
    a = out[..., 3] > 0
    rgb = out[..., :3].astype(float) / 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b_ = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hue = np.degrees(np.arctan2(np.sqrt(3) * (g - b_), 2 * r - g - b_)) % 360
    roofm = a & (sat > 0.45) & ((hue < 25) | (hue > 345)) & (mx > 0.3)
    ys, xs = np.where(roofm)
    ys = ys[ys < out.shape[0] * 0.6]
    for y, x in zip(*np.where(roofm & (np.indices(roofm.shape)[0] < out.shape[0] * 0.6))):
        h, s, v = colorsys.rgb_to_hsv(*rgb[y, x])
        r2, g2, b2 = colorsys.hsv_to_rgb((h + shift_deg / 360) % 1, s * 0.85, v)
        out[y, x, :3] = (np.array([r2, g2, b2]) * 255).astype(np.uint8)
    return out


def village4_objects(state, info=None):
    import os
    load_overrides()
    for n in NEW_HOUSES:
        p = f'pl/bld/{n}_0.png'
        if os.path.exists(p) and n not in BLD_OVERRIDE:
            a = np.array(Image.open(p).convert('RGBA'))
            rows = np.where(a[..., 3].any(1))[0]
            BLD_OVERRIDE[n] = (a[:rows.max() + 1], NEW_DOOR.get(n, 52))
    sick = state != 'sano'
    sh = (lambda s: ashen(s)) if sick else (lambda s: s)
    objs = []
    # asignación de edificios a los huecos de cada calle
    assign = {
        'terraza': ['torre', 'cabana', 'piedra', 'granero', 'capilla', ('azul', 200), 'casita', ('casa_crema', 200)],
        'mayor': ['escuela', 'azul', 'posada', 'tienda', 'esquina', 'molino'],
        'media': ['taller', 'balcon', 'casa_crema', 'mostaza', 'alcaldia', ('piedra', 140), 'panaderia'],
        'sur': [('balcon', 200), 'casa_pescador', ('mostaza', 230), ('esquina', 150), ('piedra', 25), ('casita', 180), 'botes'],
    }
    for st, names in assign.items():
        r = maps2.STREETS4[st] - 2
        for c, nm in zip(maps2.SLOTS4[st], names):
            shift = 0
            if isinstance(nm, tuple):
                nm, shift = nm
            if nm not in BLD_OVERRIDE and not hasattr(B, nm):
                continue
            spr, door = bld(nm)
            if shift:
                spr = roof_variant(spr, shift)
            spr = sh(spr)
            door_cx = (c + 1) * 16
            x, yb = door_cx - door, r * 16 + 4
            objs.append((spr, x, yb, 0))
            if nm not in ('capilla', 'torre', 'granero', 'molino', 'botes', 'alcaldia', 'posada', 'tienda'):
                yard(objs, spr, x, yb, door_cx, sh)
            else:
                yard(objs, spr, x, yb, door_cx, sh, fence_l=False, fence_r=False, pots=nm in ('posada', 'tienda', 'alcaldia'))
    t = BURNT if sick else TREE
    # plaza del Árbol del Vínculo
    cx, cy = 40 * 16, 23 * 16 + 8
    objs.append(('decal', ring_planter(state), cx - 42, cy - 17))
    objs.append((t.copy(), cx - foot_x(t), cy, 60))
    objs.append((sh(B.stall()), 31 * 16, 21 * 16, 0))
    objs.append((sh(B.stall(('roofb', 'paper'), 'tela')), 46 * 16 + 6, 21 * 16, 0))
    objs.append((sh(B.stall(('roofr', 'paper'), 'fruta')), 31 * 16, 26 * 16, 0))
    objs.append((sh(B.stall(('eco', 'paper'), 'tela')), 46 * 16 + 6, 26 * 16, 0))
    objs.append((sh(B.bench()), cx - 84, cy + 34, 0))
    objs.append((sh(B.bench()), cx + 58, cy + 34, 0))
    for x, y in [(30 * 16 + 2, 18 * 16 + 14), (50 * 16 - 10, 18 * 16 + 14), (30 * 16 + 2, 28 * 16 - 2), (50 * 16 - 10, 28 * 16 - 2)]:
        objs.append((B.lamp_post(), x, y, 6))
    # plazoleta de la fuente
    f = sh(B.fountain())
    objs.append((f, 41 * 16 - f.shape[1] // 2, 48 * 16, 0))
    for x, y in [(34 * 16 + 2, 44 * 16), (48 * 16 - 10, 44 * 16), (34 * 16 + 2, 51 * 16 - 2), (48 * 16 - 10, 51 * 16 - 2)]:
        objs.append((B.lamp_post(), x, y, 6))
    objs.append((sh(B.bench()), 36 * 16, 49 * 16 + 4, 0))
    objs.append((sh(B.bench()), 44 * 16, 49 * 16 + 4, 0))
    # faroles a lo largo de la calle mayor, entre casas
    for c in (9, 17, 26, 59, 67):
        objs.append((B.lamp_post(), c * 16 + 4, 29 * 16 + 4, 6))
    # huerto de frutales al oeste de la plaza, entre la terraza y la calle mayor
    for i, (x, y) in enumerate([(x, y) for y in (17 * 16, 20 * 16) for x in range(4 * 16, 26 * 16, 56)]):
        objs.append((fruit_tree(state, i, [3, 0, 1][i % 3]), x, y, 26))
    objs.append((sh(B.well()), 27 * 16, 19 * 16, 0))
    # muelle y barca
    objs.append(('decal', boat(), 71 * 16, 44 * 16 + 4))
    objs.append((sh(crate_fish()), 66 * 16, 50 * 16, 0))
    # carteles en las salidas
    for x, y in [(2 * 16, 29 * 16 + 4), (86 * 16, 29 * 16 + 4), (42 * 16 + 4, 58 * 16), (86 * 16, 9 * 16 + 4)]:
        objs.append((sign(), x, y, 10))
    # rincones: carreta y pacas junto al molino y el granero; tendederos en los patios traseros
    objs.append((sh(cart()), 66 * 16, 27 * 16, 0))
    objs.append((sh(hay()), 33 * 16, 8 * 16 + 4, 0))
    objs.append((sh(hay()), 35 * 16, 8 * 16 + 8, 0))
    objs.append((sh(laundry()), 8 * 16, 37 * 16 - 8, 0)) if False else None
    for i, (x, y) in enumerate([(37 * 16 - 8, 14 * 16), (41 * 16 + 4, 14 * 16)]):
        objs.append((bush2(state, i), x, y, 22))
    spots = [(-40, 60), (1300, 60), (1380, 160), (1320, 300), (1380, 420), (1300, 560), (1380, 700),
             (1320, 980), (60, 990), (220, 980), (420, 990), (760, 990), (980, 980), (1160, 990),
             (-40, 560), (-40, 760)]
    for i, x, y in solve_trees(spots, info, 'valdehoja4'):
        sp = t if i % 2 else t[:, ::-1]
        objs.append((sp, x, y, 54))
    return objs


NEW_DOOR = {'azul': 52, 'balcon': 51, 'piedra': 53, 'esquina': 60, 'mostaza': 53}
