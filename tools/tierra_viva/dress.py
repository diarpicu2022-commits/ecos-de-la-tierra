"""Vestido de escena: agrupa vegetación, piedras y detalles de suelo en racimos
naturales sobre hierba libre, sin pisar caminos, agua, caras de roca ni otros
objetos. Lo comparten todas las zonas."""
import numpy as np
from scipy import ndimage as ndi
import px, flora, scene2
from pal import P
from px import new, col, outline, shade, ellipse

C = lambda r, i: col(P[r][i])


# --- piezas pequeñas ---------------------------------------------------------

def flower_patch(state, seed):
    rng = np.random.default_rng(seed)
    img = new(22, 12)
    hues = [(0, 2), (3, 4), (5, 6), (7, 7)]
    a, b = hues[seed % len(hues)]
    for _ in range(int(rng.integers(6, 11))):
        x, y = int(rng.integers(1, 20)), int(rng.integers(2, 11))
        img[y, x] = C('grass', 2)
        img[y - 1, x] = col(P['flower'][a]) if state == 'sano' else C('drygrass', 4)
        if state == 'sano':
            img[y - 2, x] = col(P['flower'][b])
    return img


def pebbles(state, seed):
    rng = np.random.default_rng(seed)
    img = new(20, 10)
    r = P['stone'] if state == 'sano' else P['ash']
    for _ in range(int(rng.integers(3, 7))):
        x, y = int(rng.integers(1, 17)), int(rng.integers(1, 8))
        w = int(rng.integers(2, 4))
        img[y:y + 2, x:x + w] = col(r[3]); img[y, x:x + w] = col(r[5]); img[y + 2, x:x + w] = col(r[1])
    return img


def grass_clump(state, seed):
    rng = np.random.default_rng(seed)
    g = P['grass'] if state == 'sano' else P['drygrass']
    img = new(14, 10)
    for x in range(1, 13, 2):
        h = int(rng.integers(3, 8))
        img[10 - h:10, x] = col(g[3 + (x % 3 == 0)])
        img[10 - h, x] = col(g[5])
    return img


def driftwood(state, seed):
    rng = np.random.default_rng(seed)
    L = int(rng.integers(22, 34))
    img = new(L, 8)
    w = P['wood'] if state == 'sano' else P['ash']
    img[3:6, 1:L - 1] = col(w[4]); img[3, 1:L - 1] = col(w[5]); img[5, 1:L - 1] = col(w[2])
    img[1:3, L // 3:L // 3 + 2] = col(w[3]); img[6:8, 2 * L // 3:2 * L // 3 + 2] = col(w[3])
    return outline(img)


def shell(state, seed):
    img = new(7, 5)
    c = P['flower'][2] if seed % 2 else P['sand'][4]
    img[1:4, 1:6] = col(c); img[1, 2:5] = col(P['flower'][4] if seed % 2 else P['flower'][7])
    img[3, 1:6] = col(P['sand'][1])
    return img


def beach_grass(state, seed):
    rng = np.random.default_rng(seed)
    g = P['grass'] if state == 'sano' else P['drygrass']
    img = new(18, 14)
    for k in range(7):
        a = np.pi * (1.15 + 0.7 * k / 6) + rng.uniform(-0.08, 0.08)
        for t in range(int(rng.integers(7, 12))):
            x, y = int(9 + np.cos(a) * t), int(13 + np.sin(a) * t)
            if 0 <= x < 18 and 0 <= y < 14:
                img[y, x] = col(g[4] if t > 4 else g[3])
    return img


def puya(state, seed):
    """Puya de páramo: roseta espinosa con espiga."""
    rng = np.random.default_rng(seed)
    img = new(24, 30)
    yy, xx = np.indices((30, 24))
    m = np.zeros((30, 24), bool)
    for k in range(11):
        a = np.pi * (1.0 + k / 10)
        L = rng.uniform(8, 11)
        for t in np.linspace(0, 1, 14):
            x, y = 12 + np.cos(a) * L * t, 26 + np.sin(a) * L * t * 0.9
            m |= ((xx - x) ** 2 + (yy - y) ** 2) <= (1.6 * (1 - t) + 0.4) ** 2
    ramp = ['#2d4a3c', '#466b4c', '#6a8f62', '#94b183', '#c3d6ae'] if state == 'sano' else \
        [P['deadleaf'][1], P['deadleaf'][2], P['deadleaf'][3], P['deadleaf'][4], P['deadleaf'][5]]
    s = shade(m, ramp, ambient=0.35)
    img[m] = s[m]
    if seed % 2 == 0:
        img[4:22, 11:13] = col(ramp[1])
        for y in range(5, 20, 2):
            img[y, 10:14] = col('#3f8f8a' if state == 'sano' else P['deadleaf'][3])
    return outline(img)


def pajonal(state, seed):
    """Macolla de paja de páramo, dorada y despeinada."""
    rng = np.random.default_rng(seed)
    img = new(22, 16)
    ramp = ['#56502e', '#7d7238', '#a6984a', '#cdbd66', '#e6d98a'] if state == 'sano' else \
        [P['drygrass'][1], P['drygrass'][2], P['drygrass'][3], P['drygrass'][4], P['drygrass'][5]]
    for k in range(16):
        a = np.pi * (1.05 + 0.9 * k / 15) + rng.uniform(-0.06, 0.06)
        L = rng.uniform(8, 14)
        for t in range(int(L)):
            x, y = int(11 + np.cos(a) * t), int(15 + np.sin(a) * t * 0.8 + (t / L) ** 2 * 3)
            if 0 <= x < 22 and 0 <= y < 16:
                img[y, x] = col(ramp[min(4, 1 + t * 4 // int(L))])
    return outline(img)


def log_(state, seed):
    return scene2.log_(state != 'sano')


def bush(state, seed):
    if state == 'sano':
        return scene2.bush2(state, seed)
    return twigs(seed)


def twigs(seed):
    """Arbusto muerto: ramitas secas en abanico, sin hojas."""
    rng = np.random.default_rng(seed)
    W, H = 26, 20
    img = new(W, H)
    w = P['deadleaf']
    def branch(x, y, a, L, d):
        for t in range(int(L)):
            x += np.cos(a); y += np.sin(a)
            xi, yi = int(round(x)), int(round(y))
            if 0 <= xi < W and 0 <= yi < H:
                img[yi, xi] = col(w[2 + (d > 0)])
        if d < 2:
            for da in (-0.5, 0.45):
                branch(x, y, a + da + rng.uniform(-0.2, 0.2), L * 0.6, d + 1)
    for a in np.linspace(np.pi * 1.15, np.pi * 1.85, 5):
        branch(13, H - 2, a + rng.uniform(-0.1, 0.1), rng.uniform(6, 9), 0)
    return outline(img)


def rock(state, seed):
    return flora.rock(state)


def big_rock(state, seed):
    return _big(state, seed)


def _big(state, seed):
    rng = np.random.default_rng(seed)
    W, H = 30, 22
    m = ellipse(W, H, 15, 13, 13, 8) | ellipse(W, H, 11 + rng.uniform(-2, 2), 9, 8, 6)
    r = P['stone'] if state == 'sano' else P['ash']
    img = shade(m, r[1:6], ambient=0.25)
    yy, xx = np.indices((H, W))
    img[m & ((xx * 3 + yy * 5) % 11 == 0)] = col(r[2])
    if state == 'sano':
        moss = m & (yy < 9) & ((xx + yy) % 3 == 0)
        img[moss] = C('grass', 4)
    return outline(img)


# --- reparto ------------------------------------------------------------------

def occupancy(info, objs):
    """Máscara de suelo ocupado: caminos, agua, caras de roca y la base de
    cada objeto ya colocado."""
    occ = info['path'] | info['wat'] | info['face']
    occ = ndi.binary_dilation(occ, iterations=4)
    H, W = occ.shape
    for o in objs:
        if isinstance(o[0], str):
            continue
        spr, x, yb = o[0], o[1], o[2]
        w = spr.shape[1]
        y0, y1 = max(0, yb - (spr.shape[0] + 30 if w >= 48 else 14)), min(H, yb + 4)
        x0, x1 = max(0, x + 2), min(W, x + w - 2)
        if y1 > y0 and x1 > x0:
            occ[y0:y1, x0:x1] = True
    return occ


def scatter(objs, info, state, kinds, clusters=10, per=(3, 6), spread=34, seed=0,
            where=None, decal=()):
    """kinds: lista de (fábrica, sombra, peso). Coloca `clusters` racimos de
    `per` piezas alrededor de centros aleatorios con hierba libre."""
    rng = np.random.default_rng(seed)
    occ = occupancy(info, objs)
    H, W = occ.shape
    ok = ~occ if where is None else (~occ & where)
    ys, xs = np.where(ok[20:H - 2, 4:W - 4])
    if not len(ys):
        return objs
    wts = np.array([k[2] for k in kinds], float); wts /= wts.sum()
    out = list(objs)
    for c in range(clusters):
        i = int(rng.integers(len(ys)))
        cy, cx = ys[i] + 20, xs[i] + 4
        for _ in range(int(rng.integers(per[0], per[1] + 1))):
            for _try in range(8):
                x = int(cx + rng.normal(0, spread / 2))
                y = int(cy + rng.normal(0, spread / 3))
                if not (4 <= x < W - 4 and 16 <= y < H - 1):
                    continue
                k = int(rng.choice(len(kinds), p=wts))
                fac, shd, _ = kinds[k]
                spr = fac(state, int(rng.integers(1000)))
                w = spr.shape[1]
                x0 = x - w // 2
                foot = ok[max(0, y - 6):y + 2, max(0, x0 + 2):min(W, x0 + w - 2)]
                if foot.size == 0 or not foot.all():
                    continue
                if fac in decal:
                    out.append(('decal', spr, x0, y - spr.shape[0]))
                else:
                    out.append((spr, x0, y, shd))
                    ok[max(0, y - 10):y + 3, max(0, x0):x0 + w] = False
                break
    return out


def shore(info, inner=2, outer=14):
    """Franja de tierra junto al agua (para juncos, conchas, madera)."""
    w = info['wat']
    return ndi.binary_dilation(w, iterations=outer) & ~ndi.binary_dilation(w, iterations=inner)


def tiles(info, chars):
    G = np.array([list(r) for r in info['G']]) if not isinstance(info['G'], np.ndarray) else info['G']
    return np.kron(np.isin(G, list(chars)), np.ones((16, 16), bool))


def trees(objs, info, state, n=12, seed=0, where=None, min_d=44, edge_bias=True):
    """Más árboles, con preferencia por los bordes del mapa (masa de bosque),
    validados igual que solve_trees: pie sobre hierba libre, copa sin tapar
    caminos ni agua, y válidos tanto sanos como quemados."""
    rng = np.random.default_rng(seed)
    occ = occupancy(info, objs) | tiles(info, 'a')
    H, W = occ.shape
    T_, B_ = scene2.TREE, scene2.BURNT
    feet = [(o[1] + scene2.foot_x(o[0]), o[2]) for o in objs if not isinstance(o[0], str) and scene2.is_tree(o[0])]
    big = [(o[1], o[2] - o[0].shape[0], o[1] + o[0].shape[1], o[2]) for o in objs
           if not isinstance(o[0], str) and o[0].shape[1] >= 40 and not scene2.is_tree(o[0])]
    out = list(objs)
    placed = 0
    for _ in range(n * 40):
        if placed >= n:
            break
        if edge_bias and rng.random() < 0.6:
            side = rng.integers(4)
            x = int(rng.integers(-30, 40)) if side == 0 else int(rng.integers(W - 40, W + 20)) if side == 1 else int(rng.integers(0, W))
            y = int(rng.integers(40, H + 30)) if side < 2 else (int(rng.integers(44, 80)) if side == 2 else int(rng.integers(H - 10, H + 40)))
        else:
            x, y = int(rng.integers(0, W)), int(rng.integers(50, H + 20))
        flip = rng.random() < 0.5
        sp = [T_[:, ::-1] if flip else T_, B_[:, ::-1] if flip else B_]
        x0 = x - scene2.foot_x(sp[0])
        if not all(scene2.tree_ok(s, x0, y, info) for s in sp):
            continue
        if 0 <= y < H and 0 <= x < W and occ[max(0, y - 8):y, max(0, x - 10):x + 10].any():
            continue
        if where is not None and 0 <= y < H and 0 <= x < W and not where[min(H - 1, y - 1), x]:
            continue
        if any((x - a) ** 2 + (y - b) ** 2 < min_d ** 2 for a, b in feet):
            continue
        h_, w_ = sp[0].shape[:2]
        if any(x0 < bx1 and x0 + w_ > bx0 and y - h_ < by1 + 6 and y > by0 for bx0, by0, bx1, by1 in big):
            continue
        feet.append((x, y))
        out.append((sp[0] if state == 'sano' else sp[1], x0, y, 54))
        placed += 1
    return out
