"""Constructor de edificios «Tierra Viva».

Todos los edificios del pueblo salen de aquí, en la misma vista que el mapa:
frente mirando a cámara y tejado visto desde arriba ocupando la parte alta,
como las casas de Pokémon NB y Minish Cap. Cada uno se compone de piezas
(tejado, muro, zócalo, puerta, ventanas, balcón, toldo, cartel, extras) con
materiales distintos, para que ningún edificio repita a otro.
"""
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from pal import P
from px import new, col, blit, outline, ellipse, shade

C = lambda r, i: col(P[r][i])
last_door = 0
DOOR = {}


# --- tejados ------------------------------------------------------------------

ROOF = {
    'teja':   dict(ramp='roofr'),
    'pizarra': dict(ramp='roofb'),
    'paja':   dict(ramp='gold'),
    'tabla':  dict(ramp='wood'),
    'chapa':  dict(ramp='stone'),
}


def roof(w, h, kind='teja', hip=0, seed=0, moss=False):
    """Faldón delantero visto desde arriba. hip>0 recorta las esquinas de
    arriba (tejado a cuatro aguas)."""
    r = P[ROOF[kind]['ramp']]
    img = new(w, h)
    yy, xx = np.indices((h, w))
    m = np.ones((h, w), bool)
    if hip:
        m &= (xx >= hip - yy * hip / max(1, h * 0.55)) & (xx <= w - 1 - hip + yy * hip / max(1, h * 0.55))
    rng = np.random.default_rng(seed)
    if kind == 'teja':
        img[m] = col(r[3])
        for y0 in range(3, h, 5):                      # hileras de tejas
            row = m & (yy == y0)
            img[row] = col(r[1])
            img[m & (yy == y0 - 1)] = col(r[2])
            off = (y0 // 5) % 2 * 3
            img[m & (yy > y0) & (yy < y0 + 5) & ((xx + off) % 6 == 0)] = col(r[2])
            img[m & (yy == y0 + 1) & ((xx + off) % 6 > 1)] = col(r[4])
        img[m & (yy < 3)] = col(r[4])
        img[m & (yy == 0)] = col(r[5])
    elif kind == 'pizarra':
        img[m] = col(r[2])
        for y0 in range(3, h, 4):
            img[m & (yy == y0)] = col(r[0])
            off = (y0 // 4) % 2 * 4
            img[m & (yy > y0) & (yy < y0 + 4) & ((xx + off) % 8 == 0)] = col(r[1])
            img[m & (yy == y0 + 1) & ((xx + off) % 8 > 1)] = col(r[3])
        img[m & (yy < 3)] = col(r[3])
        img[m & (yy == 0)] = col(r[4])
    elif kind == 'paja':
        img[m] = col(r[3])
        img[m & ((xx * 3 + yy // 2 + rng.integers(0, 3, (h, w))) % 5 == 0)] = col(r[2])
        img[m & ((xx * 5 + yy) % 7 == 0)] = col(r[4])
        for y0 in range(6, h, 7):                      # haces atados
            img[m & (yy == y0)] = col(r[2])
            img[m & (yy == y0 + 1) & (xx % 3 == 0)] = col(r[1])
        img[m & (yy < 3)] = col(r[4])
        img[m & (yy == 0)] = col(r[5])
    elif kind == 'tabla':
        img[m] = col(r[3])
        for y0 in range(2, h, 5):
            img[m & (yy == y0)] = col(r[1])
            off = (y0 // 5) % 2 * 5
            img[m & (yy > y0) & (yy < y0 + 5) & ((xx + off) % 10 == 0)] = col(r[2])
            img[m & (yy == y0 + 1)] = col(r[4])
        img[m & (yy < 2)] = col(r[4])
    elif kind == 'chapa':
        img[m] = col(r[3])
        img[m & (xx % 4 == 0)] = col(r[2])
        img[m & (xx % 4 == 1)] = col(r[4])
        # parches de otro color: reciclado
        for (px_, py, pw, ph, rr) in [(w // 5, h // 4, 12, 9, 'rust'), (w * 3 // 5, h // 2, 14, 8, 'plastic')]:
            pm = m & (xx >= px_) & (xx < px_ + pw) & (yy >= py) & (yy < py + ph)
            rp = P[rr]
            img[pm] = col(rp[2] if rr == 'rust' else rp[1])
            img[pm & (xx % 4 == 1)] = col(rp[3] if rr == 'rust' else rp[2])
            img[pm & ((xx == px_) | (yy == py))] = col(P['stone'][1])
        img[m & (yy < 2)] = col(r[5])
    if moss:
        for _ in range(w * h // 40):
            y, x = rng.integers(2, h - 3), rng.integers(1, w - 2)
            if m[y, x]:
                img[y:y + 2, x:x + 3][m[y:y + 2, x:x + 3]] = col(P['grass'][3 + rng.integers(0, 2)])
    # alero: dos filas oscuras abajo, y cantos laterales
    img[m & (yy >= h - 2)] = col(r[1])
    img[m & (yy == h - 1)] = col(r[0])
    side = m & ~np.roll(m, 1, 1) | m & ~np.roll(m, -1, 1)
    side[:, 0] |= m[:, 0]; side[:, -1] |= m[:, -1]
    img[side] = col(r[1])
    return img


# --- muros --------------------------------------------------------------------

def wall(w, h, kind='adobe', tint=None, seed=0):
    rng = np.random.default_rng(seed)
    img = new(w, h)
    yy, xx = np.indices((h, w))
    if kind == 'adobe':                          # revoque blanco, crema u ocre
        ramp = tint or P['wall']
        img[:] = col(ramp[4])
        for _ in range(max(2, w * h // 300)):     # desconchones con adobe a la vista
            x, y = rng.integers(2, w - 8), rng.integers(4, h - 6)
            bw, bh = rng.integers(5, 9), rng.integers(3, 5)
            img[y:y + bh, x:x + bw] = col(ramp[2])
            img[y, x:x + bw] = col(ramp[1])
            for k in range(x + 2, x + bw, 4):
                img[y + 1:y + bh, k] = col(ramp[1])
        img[rng.random((h, w)) < 0.025] = col(ramp[3])
        img[:, :2] = col(ramp[3]); img[:, -2:] = col(ramp[2])
    elif kind == 'tabla':
        r = P['wood']
        img[:] = col(r[3])
        for y0 in range(0, h, 4):
            img[y0, :] = col(r[1]); img[y0 + 1 if y0 + 1 < h else y0, :] = col(r[4])
        for x0 in range(0, w, 13):
            img[:, x0] = col(r[2])
        img[(yy % 4 == 2) & ((xx * 7) % 23 == 0)] = col(r[1])
    elif kind == 'troncos':
        r = P['wood']
        for y0 in range(0, h, 6):
            band = (yy >= y0) & (yy < y0 + 6)
            img[band] = col(r[3])
            img[band & (yy == y0)] = col(r[1])
            img[band & (yy == y0 + 1)] = col(r[4])
            img[band & (yy == y0 + 2)] = col(r[4])
            img[band & (yy == y0 + 5)] = col(r[2])
            # testas de los troncos en las esquinas
            for xe in (0, w - 5):
                tm = band & (xx >= xe) & (xx < xe + 5)
                img[tm] = col(P['sand'][2])
                img[tm & ((yy == y0) | (yy == y0 + 5) | (xx == xe) | (xx == xe + 4))] = col(r[2])
                img[tm & (yy == y0 + 2) & (xx == xe + 2)] = col(r[2])
    elif kind == 'piedra':
        r = P['stone']
        pts = np.array([(y + rng.integers(-1, 2), x + rng.integers(-2, 3) + (3 if (y // 5) % 2 else 0))
                        for y in range(-2, h + 4, 5) for x in range(-3, w + 6, 7)])
        ys, xs = np.mgrid[0:h, 0:w]
        d, idx = cKDTree(pts).query(np.c_[ys.ravel(), xs.ravel()], k=2)
        lab = idx[:, 0].reshape(h, w)
        j = ((d[:, 1] - d[:, 0]) < 1.2).reshape(h, w)
        tone = rng.integers(0, 3, len(pts))
        img[:] = col(r[3])
        img[np.isin(lab, np.where(tone == 0)[0])] = col(r[2])
        img[np.isin(lab, np.where(tone == 2)[0])] = col(r[4])
        up = np.zeros((h, w), bool); up[1:] = lab[1:] != lab[:-1]
        img[up & ~j] = col(r[5])
        img[j] = col(r[1])
    elif kind == 'ladrillo':
        r = P['roofr']
        img[:] = col(r[3])
        for y0 in range(0, h, 4):
            img[y0, :] = col(P['wall'][2])
            off = (y0 // 4) % 2 * 4
            img[(yy > y0) & (yy < y0 + 4) & ((xx + off) % 8 == 0)] = col(P['wall'][2])
            img[(yy == y0 + 1) & ((xx + off) % 8 > 1)] = col(r[4])
        img[rng.random((h, w)) < 0.03] = col(r[2])
    # sombra del alero arriba
    img[:3] = (img[:3].astype(int) * 0.7).astype(np.uint8)
    img[:3, :, 3] = 255
    return img


def plinth(w, h=6, seed=0):
    """Zócalo de piedra al pie del muro."""
    return wall(w, h, 'piedra', seed=seed + 50)


# --- huecos y piezas ----------------------------------------------------------------

def door(w=14, h=22, color='wood', arch=False, double=False):
    img = new(w, h)
    yy, xx = np.indices((h, w))
    r = P['wood']
    frame = np.ones((h, w), bool)
    if arch:
        frame &= ~((yy < w // 2) & (((xx - (w - 1) / 2) ** 2 + (yy - w / 2) ** 2) > (w / 2) ** 2))
    img[frame] = col(r[1])
    inner = ndi.binary_erosion(frame, iterations=2)
    if color == 'wood':
        img[inner] = col(r[3])
        img[inner & (xx % 4 == 0)] = col(r[2])
        img[inner & (xx % 4 == 1)] = col(r[4])
    else:
        rp = P[color]
        img[inner] = col(rp[2])
        img[inner & (xx % 4 == 0)] = col(rp[1])
        img[inner & (xx % 4 == 1)] = col(rp[3])
    img[inner & (yy == h // 2)] = col(r[1])
    if double:
        img[inner & (xx == w // 2)] = col(r[1])
    kx = w // 2 + (2 if not double else 1)
    img[h // 2 + 2, kx] = C('gold', 4)
    if double:
        img[h // 2 + 2, w // 2 - 2] = C('gold', 4)
    return img


def window(w=12, h=12, shutters=None, box=True, lit=False, arch=False):
    W_ = w + (6 if shutters else 0)
    H_ = h + (4 if box else 0)
    img = new(W_, H_)
    ox = 3 if shutters else 0
    yy, xx = np.indices((h, w))
    fr = np.ones((h, w), bool)
    if arch:
        fr &= ~((yy < w // 2) & (((xx - (w - 1) / 2) ** 2 + (yy - w / 2) ** 2) > (w / 2) ** 2))
    sub = img[0:h, ox:ox + w]
    sub[fr] = C('wood', 1)
    gl = ndi.binary_erosion(fr, iterations=1)
    sub[gl] = C('gold', 4) if lit else C('water', 4)
    sub[gl & (yy >= h // 2)] = C('gold', 3) if lit else C('water', 3)
    sub[gl & ((xx + yy) == w // 2)] = C('gold', 5) if lit else C('water', 6)
    sub[gl & (xx == w // 2)] = C('wood', 2)
    sub[gl & (yy == h // 2)] = C('wood', 2)
    if shutters:
        rp = P[shutters]
        for sx in (0, W_ - 3):
            img[0:h, sx:sx + 3] = col(rp[2])
            img[0:h, sx + 1] = col(rp[3])
            img[0:h:3, sx:sx + 3] = col(rp[1])
    if box:
        img[h:h + 4, 1:W_ - 1] = C('wood', 2)
        img[h + 3, 1:W_ - 1] = C('wood', 1)
        rng = np.random.default_rng(w * 3 + h)
        for x in range(2, W_ - 2, 2):
            c = P['flower'][[0, 1, 3, 7][rng.integers(0, 4)]]
            img[h - 1, x] = C('grass', 3)
            img[h, x] = col(c)
            img[h + 1, x + (1 if x + 1 < W_ - 1 else 0)] = C('grass', 4)
    return img


def awning(w, colors=('roofr', 'paper'), h=9):
    img = new(w, h)
    for x in range(w):
        rp = P[colors[(x // 4) % 2]]
        img[:h - 2, x] = col(rp[3] if colors[(x // 4) % 2] != 'paper' else rp[4])
        img[0, x] = col(rp[2])
        img[h - 3, x] = col(rp[2] if colors[(x // 4) % 2] != 'paper' else rp[2])
        # festón
        if x % 4 in (1, 2):
            img[h - 2, x] = img[h - 4, x]
            img[h - 1, x] = col(rp[1])
    return img


def sign(icon, w=16, h=12):
    img = new(w + 2, h + 5)
    img[0, 1:w + 1] = C('wood', 1)                     # ménsula
    img[1:5, 3] = C('wood', 1); img[1:5, w - 2] = C('wood', 1)
    img[4:4 + h, 1:w + 1] = C('wood', 4)
    img[4, 1:w + 1] = C('wood', 5)
    img[4 + h - 1, 1:w + 1] = C('wood', 2)
    img[4:4 + h, 1] = C('wood', 2); img[4:4 + h, w] = C('wood', 2)
    blit(img, icon, 1 + (w - icon.shape[1]) // 2, 4 + (h - icon.shape[0]) // 2)
    return outline(img)


def grid(rows, cmap):
    h, w = len(rows), max(len(r) for r in rows)
    a = new(w, h)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in cmap:
                a[y, x] = col(cmap[ch]) if isinstance(cmap[ch], str) else cmap[ch]
    return a


ICON = {
    'taza': grid([".s.s..", "..s...", "cccccw", "c...cw", "c...c.", ".ccc.."],
                 {'s': P['ui'][4], 'c': P['ui'][5], 'w': P['ui'][5]}),
    'bolsa': grid(["..bb..", ".b..b.", "gggggg", "gyyyyg", "gyyyyg", ".gggg."],
                  {'b': P['wood'][1], 'g': P['wood'][2], 'y': P['gold'][4]}),
    'engranaje': grid([".g.g.", "ggggg", ".g.g.", "ggggg", ".g.g."], {'g': P['stone'][2]}),
    'hoja': grid(["...gg", "..ggg", ".ggg.", "ggg..", "g...."], {'g': P['eco'][2]}),
    'espiga': grid(["..y..", ".yyy.", "..y..", ".yyy.", "..g..", "..g.."], {'y': P['gold'][3], 'g': P['grass'][3]}),
}


def chimney(h=12, kind='piedra'):
    img = new(8, h)
    img[:] = wall(8, h, 'piedra' if kind == 'piedra' else 'ladrillo', seed=h)
    img[0:2] = C('stone', 1)
    img[2, 1:7] = C('stone', 0)
    return outline(img)


def barrel():
    m = ellipse(10, 12, 5, 6, 4.6, 5.8)
    img = shade(m, P['wood'][1:6], ambient=0.25)
    img[2] = np.where(m[2][:, None], C('stone', 2), img[2]); img[9] = np.where(m[9][:, None], C('stone', 2), img[9])
    img[0:2][m[0:2]] = C('wood', 2)
    return outline(img)


def crate(fill='papa'):
    img = new(12, 10)
    img[:] = C('wood', 3)
    img[[0, 9], :] = C('wood', 1); img[:, [0, 11]] = C('wood', 1)
    img[4:6, :] = C('wood', 2)
    if fill:
        c = {'papa': P['sand'][1], 'naranja': P['flower'][3], 'manzana': P['flower'][0]}[fill]
        for x in range(1, 11, 2):
            img[0, x] = col(c)
            img[0, x + 1] = col(P['sand'][3] if fill == 'papa' else P['flower'][4])
    return outline(img)


def firewood():
    img = new(18, 10)
    for row, y in enumerate((6, 3, 0)):
        for x in range(row * 2, 15 - row * 2, 4):
            e = ellipse(4, 4, 2, 2, 1.8, 1.8)
            img[y:y + 4, x:x + 4][e] = C('sand', 2)
            img[y + 1, x + 1] = C('wood', 3)
            ring = e & ~ellipse(4, 4, 2, 2, 1.0, 1.0)
            img[y:y + 4, x:x + 4][ring & (np.indices((4, 4))[0] >= 2)] = C('wood', 2)
    return outline(img)


def lantern():
    img = grid([".dd.", "dyyd", "dyyd", ".dd.", "..d.", "..d."], {'d': P['ink'][1], 'y': P['gold'][4]})
    return img


def pot_plant(c=0):
    img = grid(["..g.g..", ".gGgGg.", "gGgfgGg", ".ggggg.", ".rrrrr.", "..rrr.."],
               {'g': P['grass'][3], 'G': P['grass'][5], 'f': P['flower'][[0, 3, 5][c % 3]], 'r': P['roofr'][3]})
    return outline(img)


# --- montaje -----------------------------------------------------------------------

def building(spec, seed=0):
    """spec: diccionario con las piezas. Devuelve el sprite completo.

    w         ancho del muro en px
    roof      (tipo, alto, hip, musgo)
    floors    [(alto, material, tinte)] de abajo arriba
    door      dict(x, color, arch, double, w, h) — x relativo al muro
    windows   [(x, piso, dict)]
    extras    [(sprite, x, y)] relativos a la esquina del muro
    tower     dict para campanario
    """
    w = spec['w']
    rk, rh, hip, moss = spec['roof']
    floors = spec['floors']
    wall_h = sum(f[0] for f in floors)
    pl_h = spec.get('plinth', 6)
    over = 3
    top_extra = spec.get('top_extra', 0)
    W_ = w + over * 2 + spec.get('pad_r', 0) + spec.get('pad_l', 0)
    H_ = top_extra + rh + wall_h + pl_h
    img = new(W_, H_)
    ox = over + spec.get('pad_l', 0)
    wy = top_extra + rh                         # arranque del muro
    # muros por pisos (el más alto arriba)
    y = wy + wall_h
    for i, (fh, mat, tint) in enumerate(floors):
        y -= fh
        blit(img, wall(w, fh, mat, tint=tint, seed=seed + i), ox, y)
        if i > 0:
            img[y + fh - 1, ox:ox + w] = C('wood', 1)
            img[y + fh - 2, ox:ox + w] = C('wood', 2)
    if pl_h:
        blit(img, plinth(w, pl_h, seed), ox, wy + wall_h)
    # sombra del alero sobre el muro
    img[wy:wy + 2, ox:ox + w] = (img[wy:wy + 2, ox:ox + w].astype(int) * 0.65).astype(np.uint8)
    img[wy:wy + 2, ox:ox + w, 3] = 255
    # tejado
    blit(img, roof(w + over * 2, rh, rk, hip, seed, moss), ox - over, top_extra)
    for x_, h_, kind in spec.get('chimneys', []):
        blit(img, chimney(h_, kind), ox + x_, top_extra + 8 - h_)
    # huecos
    def floor_y(fi):
        yy_ = wy + wall_h
        for k in range(fi + 1):
            yy_ -= floors[k][0]
        return yy_
    d = spec.get('door')
    global last_door
    if d:
        dw, dh = d.get('w', 14), d.get('h', 22)
        last_door = ox + d['x'] + dw // 2
        dd = door(dw, dh, d.get('color', 'wood'), d.get('arch', False), d.get('double', False))
        blit(img, dd, ox + d['x'], wy + wall_h - dh)
        # escalón
        img[wy + wall_h:wy + wall_h + 2, ox + d['x'] - 1:ox + d['x'] + dw + 1] = C('stone', 4)
        img[wy + wall_h + 2, ox + d['x'] - 1:ox + d['x'] + dw + 1] = C('stone', 2)
    for (x_, fi, kw) in spec.get('windows', []):
        win = window(**kw)
        fy = floor_y(fi)
        blit(img, win, ox + x_, fy + max(4, (floors[fi][0] - win.shape[0]) // 2))
    if spec.get('balcony'):
        fi = 1
        by = floor_y(fi) + floors[fi][0] - 2
        img[by - 9:by - 8, ox - 2:ox + w + 2] = C('wood', 1)
        img[by - 8:by - 7, ox - 2:ox + w + 2] = C('wood', 4)
        for x_ in range(ox - 2, ox + w + 2, 4):
            img[by - 7:by, x_] = C('wood', 2)
        img[by:by + 2, ox - 3:ox + w + 3] = C('wood', 2)
        img[by + 2, ox - 3:ox + w + 3] = C('wood', 1)
        rng = np.random.default_rng(seed + 3)
        for x_ in range(ox, ox + w, 9):         # macetas de geranios colgando
            img[by - 10:by - 8, x_:x_ + 5] = C('roofr', 3)
            for k in range(5):
                img[by - 12 + rng.integers(0, 2), x_ + k] = col(P['flower'][[0, 1][k % 2]])
                img[by - 11, x_ + k] = C('grass', 4)
        # pies derechos que bajan al suelo
        for x_ in (ox - 2, ox + w):
            img[by + 3:wy + wall_h + pl_h, x_:x_ + 2] = C('wood', 2)
            img[by + 3:wy + wall_h + pl_h, x_] = C('wood', 3)
    if spec.get('awning'):
        aw = spec['awning']
        a = awning(aw['w'], aw.get('colors', ('roofr', 'paper')))
        blit(img, a, ox + aw['x'], aw.get('y', wy + 2))
    if spec.get('sign'):
        sg = spec['sign']
        blit(img, sign(ICON[sg['icon']]), ox + sg['x'], wy + sg.get('y', 4))
    for spr, x_, y_ in spec.get('extras', []):
        blit(img, spr, ox + x_, wy + y_)
    return outline(img, color=P['ink'][0])


# --- catálogo de Valdehoja ----------------------------------------------------------

CREAM = [P['sand'][0], P['sand'][1], P['sand'][2], P['sand'][3], P['sand'][4]]
OCHRE = ['#7a4a2a', '#9c6436', '#c08646', '#dba45e', '#efc27c']
SKY = [P['roofb'][1], P['roofb'][2], P['roofb'][3], P['roofb'][4], P['roofb'][5]]


def posada():
    """La Posada del Cóndor: dos pisos, balcón de madera con geranios."""
    img = building(dict(
        w=112, roof=('teja', 36, 12, False), plinth=6, top_extra=8,
        floors=[(30, 'adobe', None), (26, 'adobe', None)],
        chimneys=[(84, 14, 'piedra')],
        door=dict(x=48, w=16, h=24, color='eco', arch=True, double=True),
        windows=[(10, 0, dict(shutters='eco')), (86, 0, dict(shutters='eco')),
                 (8, 1, dict(box=False)), (34, 1, dict(box=False)), (64, 1, dict(box=False)), (90, 1, dict(box=False))],
        balcony=True, sign=dict(icon='taza', x=30, y=28),
        extras=[(barrel(), -12, 50), (barrel(), 116, 50)], pad_l=12, pad_r=12), seed=11)
    DOOR['posada'] = last_door
    return img


def tienda():
    """Almacén de Doña Rosa: muro azul, toldo a rayas, cajas de papas y naranjas."""
    img = building(dict(
        w=96, roof=('pizarra', 30, 0, False), plinth=5,
        floors=[(40, 'tabla', None)],
        door=dict(x=60, w=14, h=24, color='wood'),
        windows=[(10, 0, dict(w=26, h=16, box=False, lit=True))],
        awning=dict(x=4, w=44, colors=('roofr', 'paper')),
        sign=dict(icon='bolsa', x=76, y=4),
        extras=[(crate('papa'), 6, 34), (crate('naranja'), 20, 34), (crate('manzana'), 34, 36)]), seed=21)
    DOOR['tienda'] = last_door
    return img


def taller():
    """Taller de Nix: chapa reciclada con parches, ladrillo, portón ancho."""
    img = building(dict(
        w=100, roof=('chapa', 28, 0, False), plinth=4,
        floors=[(40, 'ladrillo', None)],
        door=dict(x=36, w=30, h=30, color='stone', double=True),
        windows=[(8, 0, dict(box=False)), (78, 0, dict(box=False))],
        sign=dict(icon='engranaje', x=74, y=2),
        extras=[(barrel(), -10, 30), (barrel(), 104, 30)], pad_l=10, pad_r=12), seed=31)
    DOOR['taller'] = last_door
    return img


def cabana():
    """Cabaña de Bruma, guardabosques: troncos, tejado de tabla con musgo."""
    img = building(dict(
        w=80, roof=('tabla', 30, 0, True), plinth=4, top_extra=8,
        floors=[(34, 'troncos', None)],
        chimneys=[(10, 12, 'piedra')],
        door=dict(x=34, w=14, h=24, color='eco'),
        windows=[(10, 0, dict(shutters='wood')), (56, 0, dict(shutters='wood'))],
        sign=dict(icon='hoja', x=60, y=-2),
        extras=[(firewood(), 82, 26), (lantern(), 50, 8)], pad_r=20), seed=41)
    DOOR['cabana'] = last_door
    return img


def casita():
    """Casa de labranza: paja gruesa, adobe ocre, contraventanas azules."""
    img = building(dict(
        w=76, roof=('paja', 34, 10, False), plinth=5,
        floors=[(30, 'adobe', OCHRE)],
        door=dict(x=30, w=14, h=22, color='roofb'),
        windows=[(6, 0, dict(shutters='roofb')), (52, 0, dict(shutters='roofb'))],
        extras=[(pot_plant(0), -9, 22), (pot_plant(1), 78, 22)], pad_l=9, pad_r=9), seed=51)
    DOOR['casita'] = last_door
    return img


def casa_crema():
    """Casa de la abuela Toña: crema, teja, puerta roja y macetas."""
    img = building(dict(
        w=84, roof=('teja', 32, 0, False), plinth=6, top_extra=8,
        floors=[(32, 'adobe', CREAM)],
        chimneys=[(64, 12, 'ladrillo')],
        door=dict(x=12, w=14, h=22, color='roofr'),
        windows=[(36, 0, dict()), (60, 0, dict())],
        extras=[(pot_plant(2), 28, 24)]), seed=61)
    DOOR['casa_crema'] = last_door
    return img


def capilla():
    """Capilla de Valdehoja: encalada, campanario a la izquierda, portón en arco."""
    body = building(dict(
        w=88, roof=('teja', 34, 0, False), plinth=8, top_extra=0,
        floors=[(42, 'adobe', None)],
        door=dict(x=36, w=18, h=28, color='wood', arch=True, double=True),
        windows=[(12, 0, dict(w=10, h=14, arch=True, box=False)), (66, 0, dict(w=10, h=14, arch=True, box=False))],
        ), seed=71)
    door_body = last_door
    # campanario: torre de 30 px de ancho que sube por encima del tejado
    tw, th = 30, 100
    tower = new(tw + 6, th + 14)
    blit(tower, wall(tw, th, 'adobe', seed=72), 3, 14)
    blit(tower, roof(tw + 6, 14, 'teja', 12, 72), 0, 0)
    tower[14 + th - 8:14 + th, 3:3 + tw] = wall(tw, 8, 'piedra', seed=73)
    # hueco de la campana
    yy, xx = np.indices((20, 14))
    arch = ~((yy < 7) & (((xx - 6.5) ** 2 + (yy - 7) ** 2) > 49))
    hole = tower[22:42, 3 + 8:3 + 22]
    hole[arch] = C('ink', 1)
    bell = grid(["..gg..", ".gGGg.", ".gGGg.", "gGGGGg", "gggggg", "..g..."], {'g': P['gold'][2], 'G': P['gold'][4]})
    blit(tower, bell, 3 + 12, 30)
    tower[44:46, 3:3 + tw] = C('wall', 2)
    blit(tower, window(8, 10, box=False, arch=True), 3 + 11, 54)
    tower = outline(tower, color=P['ink'][0])
    H_ = max(body.shape[0], tower.shape[0])
    img = new(body.shape[1] + tw - 4, H_)
    blit(img, body, tw - 4, H_ - body.shape[0])
    blit(img, tower, 0, H_ - tower.shape[0])
    # cruz pequeña en la cumbre
    img[0:5, tw // 2 + 2] = C('wood', 1); img[1, tw // 2:tw // 2 + 5] = C('wood', 1)
    DOOR['capilla'] = tw - 4 + door_body
    return img


def molino():
    """Molino de agua: piedra abajo, tabla arriba, paja, rueda a la derecha."""
    body = building(dict(
        w=80, roof=('paja', 30, 0, False), plinth=4,
        floors=[(22, 'piedra', None), (18, 'tabla', None)],
        door=dict(x=12, w=14, h=20, color='wood'),
        windows=[(48, 1, dict(box=False)), (50, 0, dict(box=False, w=10, h=10))],
        sign=dict(icon='espiga', x=30, y=26),
        extras=[(crate('papa'), 30, 50)], pad_r=4), seed=81)
    door_body = last_door
    # rueda: aro, radios y paletas
    R_ = 26
    d = R_ * 2 + 2
    wheel = new(d, d)
    yy, xx = np.indices((d, d))
    cx = cy = R_
    rr = np.hypot(xx - cx, yy - cy)
    ang = np.degrees(np.arctan2(yy - cy, xx - cx)) % 360
    wheel[(rr <= R_) & (rr >= R_ - 3)] = C('wood', 2)
    wheel[(rr <= R_ - 3) & (rr >= R_ - 4)] = C('wood', 1)
    for a0 in range(0, 360, 30):
        sp = (np.abs(((ang - a0 + 180) % 360) - 180) < 3.5) & (rr < R_ - 3) & (rr > 4)
        wheel[sp] = C('wood', 3)
        pa = (np.abs(((ang - a0 + 180) % 360) - 180) < 7) & (rr <= R_ + 2) & (rr >= R_ - 4)
        wheel[pa] = C('wood', 4)
    wheel[rr <= 4] = C('stone', 2)
    wheel[rr <= 2] = C('stone', 4)
    wheel = outline(wheel, color=P['ink'][0])
    H_ = body.shape[0] + 6
    img = new(body.shape[1] + R_ * 2 - 6, H_)
    blit(img, body, 0, H_ - body.shape[0] - 6)
    blit(img, wheel, body.shape[1] - 10, H_ - d)
    DOOR['molino'] = door_body
    return img


def stall(colors=('gold', 'grass'), goods='fruta'):
    """Puesto de mercado: toldo a rayas sobre postes y mostrador con canastas."""
    w = 44
    img = new(w + 2, 46)
    a = awning(w, colors, 11)
    # toldo inclinado visto desde arriba: más alto
    top = new(w, 14)
    for x in range(w):
        rp = P[colors[(x // 5) % 2]]
        top[:, x] = col(rp[3] if colors[(x // 5) % 2] != 'paper' else rp[4])
        top[0, x] = col(rp[4] if colors[(x // 5) % 2] != 'paper' else rp[4])
    blit(img, top, 1, 0)
    blit(img, a, 1, 13)
    for x in (2, w - 1):
        img[22:42, x:x + 2] = C('wood', 2)
        img[22:42, x] = C('wood', 3)
    img[30:40, 1:w + 1] = C('wood', 3)
    img[30, 1:w + 1] = C('wood', 4)
    img[39, 1:w + 1] = C('wood', 1)
    for i, x in enumerate(range(5, w - 4, 9)):
        bsk = grid([".fffff.", "fFfFfFf", "bbbbbbb", ".bbbbb."],
                   {'f': P['flower'][[3, 0, 1, 5][i % 4]] if goods == 'fruta' else P['roofb'][3 + i % 2],
                    'F': P['flower'][[4, 2, 2, 6][i % 4]] if goods == 'fruta' else P['eco'][3],
                    'b': P['wood'][2]})
        blit(img, bsk, x, 26)
    return outline(img, color=P['ink'][0])


def fountain():
    """Fuente de piedra redonda vista desde arriba, con agua y caño central."""
    W_, H_ = 64, 44
    img = new(W_, H_)
    rim = ellipse(W_, H_, 32, 22, 30, 15)
    inner = ellipse(W_, H_, 32, 21, 25, 11)
    wall_ = ellipse(W_, H_, 32, 27, 30, 15) & ~rim
    img[wall_] = C('stone', 3)
    img[wall_ & (np.indices((H_, W_))[1] % 7 == 0)] = C('stone', 2)
    img[rim] = C('stone', 4)
    img[rim & ~ellipse(W_, H_, 32, 22, 29, 14)] = C('stone', 5)
    img[inner] = C('water', 3)
    img[inner & ~ellipse(W_, H_, 32, 21, 23, 9.5)] = C('water', 4)
    yy, xx = np.indices((H_, W_))
    img[inner & ((xx + yy * 3) % 11 == 0)] = C('water', 5)
    # pilar y chorro
    img[8:22, 30:35] = C('stone', 4); img[8:22, 33:35] = C('stone', 3)
    img[6:9, 29:36] = C('stone', 5)
    for k, (dx, dy) in enumerate([(-6, 6), (-3, 2), (0, 0), (3, 2), (6, 6)]):
        img[2 + dy:6 + dy, 31 + dx:33 + dx] = C('water', 5)
        img[2 + dy, 31 + dx] = C('water', 6)
    return outline(img, color=P['ink'][0])


def bench():
    img = new(26, 10)
    img[0:3, :] = C('wood', 4); img[2, :] = C('wood', 2)
    img[4:6, 1:25] = C('wood', 3); img[5, 1:25] = C('wood', 2)
    for x in (2, 22):
        img[3:10, x:x + 2] = C('wood', 1)
    return outline(img)


def lamp_post():
    img = new(8, 30)
    img[8:30, 3:5] = C('ink', 1); img[8:30, 3] = C('stone', 2)
    img[27:30, 1:7] = C('ink', 1)
    lamp = grid([".dddd.", "dyyyyd", "dyYYyd", "dyyyyd", ".dddd.", "..dd.."], {'d': P['ink'][1], 'y': P['gold'][4], 'Y': P['gold'][5]})
    blit(img, lamp, 1, 1)
    img[0, 2:6] = C('ink', 1)
    return img


def well():
    W_, H_ = 34, 44
    img = new(W_, H_)
    base = ellipse(W_, H_, 17, 34, 15, 8)
    img[base] = C('stone', 3)
    img[base & ~ellipse(W_, H_, 17, 33, 13, 6)] = C('stone', 4)
    img[ellipse(W_, H_, 17, 33, 11, 5)] = C('water', 1)
    for x in (3, 29):
        img[10:34, x:x + 3] = C('wood', 2); img[10:34, x] = C('wood', 3)
    img[12, 5:29] = C('wood', 1); img[11, 5:29] = C('wood', 3)
    img[18:24, 16:18] = C('wood', 1); img[23:27, 14:20] = C('wood', 3)
    rf = roof(W_, 12, 'teja', 6, 3)
    blit(img, rf, 0, 0)
    return outline(img, color=P['ink'][0])


def tabla_tint(w, h, ramp, seed=0):
    img = new(w, h)
    img[:] = col(ramp[3])
    for y0 in range(0, h, 4):
        img[y0, :] = col(ramp[1]); img[min(h - 1, y0 + 1), :] = col(ramp[4])
    for x0 in range(0, w, 13):
        img[:, x0] = col(ramp[2])
    img[:3] = (img[:3].astype(int) * 0.7).astype(np.uint8); img[:3, :, 3] = 255
    return img


def casa_pescador():
    """Casa de Mariela, pescadora: tablas azules, red colgada, remo y barril."""
    img = building(dict(
        w=80, roof=('teja', 30, 8, False), plinth=5,
        floors=[(32, 'tabla', None)],
        door=dict(x=12, w=14, h=22, color='plastic'),
        windows=[(40, 0, dict(shutters='roofr', box=False))],
        extras=[(barrel(), 84, 34)], pad_r=12), seed=91)
    door = last_door
    # recolor del muro de tabla a azul
    wb = P['roofb']
    src = [col(c) for c in P['wood']]
    dst = [col(wb[1]), col(wb[1]), col(wb[2]), col(wb[3]), col(wb[4]), col(wb[5])]
    a = img[..., 3] > 0
    H_ = img.shape[0]
    yy = np.indices(a.shape)[0]
    region = a & (yy > 30) & (yy < H_ - 7)
    out = img.copy()
    for s_, d_ in zip(src, dst):
        m = region & np.all(img == s_, axis=-1)
        out[m] = d_
    # red de pesca colgada
    net = np.zeros((14, 18, 4), np.uint8)
    yy2, xx2 = np.indices((14, 18))
    net[((xx2 + yy2) % 4 == 0) | ((xx2 - yy2) % 4 == 0)] = col(P['sand'][3])
    net[0, :] = col(P['wood'][1])
    blit(out, net, 66, 40)
    DOOR['casa_pescador'] = door
    return out
