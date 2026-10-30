"""Render de mapas: terreno en rejilla dual (esquinas) con transiciones redondeadas,
bordes con sombra y espuma, y objetos ordenados por profundidad con sombra propia."""
import numpy as np
from pal import P
from px import new, col, blit, darker
import terrain as tx

T = 16
LEVEL = {'w': 0, 's': 1, 'd': 2, 'g': 3, 't': 4}


def smooth(t):
    return t * t * (3 - 2 * t)


def jag(n):
    """Irregularidad del borde, periódica en 16 px para que las losetas encajen."""
    return 0.035 * np.sin(n * 2 * np.pi / 16) + 0.025 * np.sin(n * 2 * np.pi / 8 + 1.3)


def level_field(corners, L):
    """Campo [0,1] por píxel: ¿el terreno de esquina alcanza el nivel L?"""
    rows, cols = len(corners), len(corners[0])
    W, H = (cols - 1) * T, (rows - 1) * T
    c = np.array([[1.0 if LEVEL[ch] >= L else 0.0 for ch in r] for r in corners])
    yy, xx = np.mgrid[0:H, 0:W]
    gx, gy = (xx + 0.5) / T, (yy + 0.5) / T
    i, j = np.floor(gx).astype(int), np.floor(gy).astype(int)
    fx, fy = gx - i, gy - j
    f = (c[j, i] * (1 - fx) * (1 - fy) + c[j, i + 1] * fx * (1 - fy) +
         c[j + 1, i] * (1 - fx) * fy + c[j + 1, i + 1] * fx * fy)
    return f + jag(xx + yy) * (f > 0.05) * (f < 0.95)


def terrain(corners, state='sano'):
    rows, cols = len(corners), len(corners[0])
    W, H = (cols - 1) * T, (rows - 1) * T
    tall_corners = [[ch == 't' for ch in r] for r in corners]
    corners = [r.replace('t', 'g') for r in corners]
    lv = np.zeros((H, W), int)
    for L in (1, 2, 3):
        lv[level_field(corners, L) > 0.5] = L
    sick = state != 'sano'
    tex = {
        0: tx.water(state),
        1: tx.sand(0, 'sano' if not sick else 'enfermo'),
        2: tx.dirt('sano' if not sick else 'enfermo'),
        3: tx.grass(state, 0),
        4: tx.tallgrass(state),
    }
    alt = {3: [tx.grass(state, v) for v in range(4)], 2: [tx.dirt('sano' if not sick else 'enfermo', v) for v in range(2)]}
    img = new(W, H)
    rng = np.random.default_rng(7)
    vmap = rng.integers(0, 4, size=(H // T + 1, W // T + 1))
    for L in range(5):
        for ty in range(H // T):
            for tx_ in range(W // T):
                t = alt[L][vmap[ty, tx_] % len(alt[L])] if L in alt else tex[L]
                sl = (slice(ty * T, ty * T + T), slice(tx_ * T, tx_ * T + T))
                m = lv[sl] == L
                img[sl][m] = t[m]
    # bordes
    g = P['grass'] if not sick else P['drygrass']
    up = np.roll(lv, 1, 0); up[0] = lv[0]
    up2 = np.roll(lv, 2, 0); up2[:2] = lv[:2]
    nb = [np.roll(lv, s, a) for s, a in [(1, 0), (-1, 0), (1, 1), (-1, 1)]]
    lower_nb = np.min(nb, axis=0)
    water_dark = P['water'][1] if not sick else '#343c3b'
    foam = P['water'][5] if not sick else '#8a8c82'
    dirt_c = P['dirt'] if not sick else P['ash']
    for y in range(H):
        for x in range(W):
            L = lv[y, x]
            if L >= 3 and lower_nb[y, x] < 3:
                img[y, x] = col(g[2])                       # filo de la hierba
            elif L == 2 and up[y, x] >= 3:
                img[y, x] = col(dirt_c[2])                  # sombra bajo la hierba
            elif L == 2 and up2[y, x] >= 3:
                img[y, x] = col(dirt_c[3])
            elif L == 0 and up[y, x] >= 1:
                bank = (P['sand'][1] if not sick else P['ash'][1]) if up[y, x] == 1 else (P['dirt'][2] if not sick else P['ash'][1])
                img[y, x] = col(bank)                       # talud
            elif L == 0 and up2[y, x] >= 1:
                img[y, x] = col(water_dark)
            elif L == 0 and lower_nb[y, x] == 0 and max(n[y, x] for n in nb) >= 1:
                img[y, x] = col(foam)  # espuma
            elif L == 1 and lower_nb[y, x] == 0:
                img[y, x] = col(P['sand'][4] if not sick else P['ash'][5])
    # hierba alta: losetas completas, con las puntas recortadas sobre la hierba
    tg = tx.tallgrass_overlay(state)
    for ty in range(H // T):
        for tx_ in range(W // T):
            if all(tall_corners[ty + a][tx_ + b] for a in (0, 1) for b in (0, 1)):
                blit(img, tg, tx_ * T, ty * T)
    return img, lv


def shadow(img, mask_xy, x, y, steps=2):
    """Sombra proyectada: oscurece el suelo bajo la máscara con tonos de la propia rampa."""
    H, W = img.shape[:2]
    for (yy, xx) in np.argwhere(mask_xy):
        Y, X = y + yy, x + xx
        if 0 <= Y < H and 0 <= X < W and img[Y, X, 3]:
            img[Y, X] = darker(img[Y, X], steps)


def ellipse_mask(w, hgt):
    yy, xx = np.mgrid[0:hgt, 0:w]
    return ((xx + 0.5 - w / 2) / (w / 2)) ** 2 + ((yy + 0.5 - hgt / 2) / (hgt / 2)) ** 2 <= 1


def place(img, objs):
    """objs: (sprite, x, y_base, shadow_w) — se ordenan por la base."""
    for spr, x, yb, sw in sorted(objs, key=lambda o: o[2]):
        h_, w_ = spr.shape[:2]
        if sw:
            sh_h = max(3, sw // 3)
            shadow(img, ellipse_mask(sw, sh_h), x + (w_ - sw) // 2 + 2, yb - sh_h // 2 - 1, 1)
        blit(img, spr, x, yb - h_)
    return img
