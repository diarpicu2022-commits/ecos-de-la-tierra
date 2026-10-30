"""Interiores «Tierra Viva»: la habitación vista como en Pokémon NB y Minish
Cap — pared del fondo de frente (con zócalo, ventanas y estantes), suelo en
planta, muros laterales gruesos con su remate, y la puerta abajo con su
felpudo. Todo en código con la paleta del sistema; los muebles se sombrean
igual que los objetos del mapa (luz arriba a la izquierda, contorno oscuro de
su propio material).
"""
import numpy as np
from PIL import Image
from pal import P
import px
from px import new, col, blit, outline, shade, ellipse
import scene, ui

T = 16
C = lambda r, i: col(P[r][i])


# --- paredes y suelos -----------------------------------------------------------

def wall_tex(w, h, style, rng):
    img = new(w, h)
    yy, xx = np.indices((h, w))
    if style == 'encalado':          # posada: encalado con vigas de madera
        img[:] = C('wall', 4)
        img[rng.random((h, w)) < 0.03] = C('wall', 3)
        for x0 in range(0, w, 64):
            img[:, x0:x0 + 6] = C('wood', 2); img[:, x0] = C('wood', 3); img[:, x0 + 5] = C('wood', 1)
        img[0:5] = C('wood', 2); img[4] = C('wood', 1)
    elif style == 'tabla':           # almacén: tablas verticales
        img[:] = C('wood', 4)
        img[xx % 10 == 0] = C('wood', 2)
        img[xx % 10 == 1] = C('wood', 5)
        img[(yy * 3 + xx) % 37 == 0] = C('wood', 2)
    elif style == 'adobe':           # casa: adobe crema con cenefa andina
        img[:] = C('sand', 3)
        img[rng.random((h, w)) < 0.04] = C('sand', 2)
        band = (yy >= 10) & (yy < 16)
        img[band] = C('roofr', 3)
        tri = band & (((xx % 12) - 6).__abs__() <= (yy - 10))
        img[tri] = C('gold', 4)
        img[(yy == 10) | (yy == 15)] = C('roofr', 1)
    # zócalo de madera abajo
    img[h - 14:h] = C('wood', 3)
    img[h - 14] = C('wood', 4)
    img[h - 13] = C('wood', 1) if style != 'tabla' else C('wood', 2)
    img[h - 2:h] = C('wood', 1)
    img[(yy >= h - 12) & (yy < h - 2) & (xx % 24 == 0)] = C('wood', 2)
    return img


def floor_tex(w, h, style):
    img = new(w, h)
    yy, xx = np.indices((h, w))
    if style == 'tablas':
        img[:] = C('wood', 4)
        img[yy % 8 == 0] = C('wood', 2)
        img[yy % 8 == 1] = C('wood', 5)
        off = (yy // 8) % 3 * 21
        img[((xx + off) % 64 == 0) & (yy % 8 != 0)] = C('wood', 2)
        img[((xx * 7 + yy * 13) % 97 == 0)] = C('wood', 3)
    elif style == 'baldosa':         # barro cocido en damero
        a = ((xx // 16) + (yy // 16)) % 2 == 0
        img[a] = C('roofr', 4)
        img[~a] = C('roofr', 3)
        img[(xx % 16 == 0) | (yy % 16 == 0)] = C('roofr', 1)
        img[((xx % 16) == 1) & (yy % 16 != 0)] = C('roofr', 5)
    elif style == 'piedra':
        img[:] = C('stone', 4)
        a = ((xx // 12) + (yy // 10)) % 2 == 0
        img[a] = C('stone', 3)
        img[(xx % 12 == 0) | (yy % 10 == 0)] = C('stone', 2)
    return img


def room(cols, rows, wall='encalado', floor='tablas', wall_h=56, seed=0):
    """Devuelve (lienzo 640x360, rect del suelo en píxeles de pantalla)."""
    rng = np.random.default_rng(seed)
    W, H = cols * T, rows * T
    scr = new(640, 360)
    scr[:] = C('ink', 0)
    x0, y0 = (640 - W) // 2, (360 - H) // 2 + 6
    side = 8
    # muros laterales y remate (grosor que da volumen)
    body = new(W + side * 2, H + 10)
    body[:] = C('wood', 1) if wall != 'adobe' else C('sand', 0)
    body[0:6] = C('wood', 2) if wall != 'adobe' else C('sand', 1)
    body[0] = C('ink', 1)
    for i in range(side):
        body[6:, i] = C('wood', 2 if i % 3 else 1) if wall != 'adobe' else C('sand', 1 if i % 3 else 0)
        body[6:, -1 - i] = C('wood', 1) if wall != 'adobe' else C('sand', 0)
    blit(scr, body, x0 - side, y0 - 10)
    blit(scr, wall_tex(W, wall_h, wall, rng), x0, y0 - 4)
    fl = floor_tex(W, H - wall_h + 4, floor)
    blit(scr, fl, x0, y0 + wall_h - 4)
    # sombra del muro del fondo sobre el suelo
    sh_y = y0 + wall_h - 4
    scr[sh_y:sh_y + 3, x0:x0 + W] = (scr[sh_y:sh_y + 3, x0:x0 + W].astype(int) * 0.72).astype(np.uint8)
    scr[sh_y:sh_y + 3, x0:x0 + W, 3] = 255
    # sombra de los muros laterales
    scr[y0 - 4:y0 + H, x0:x0 + 3] = (scr[y0 - 4:y0 + H, x0:x0 + 3].astype(int) * 0.75).astype(np.uint8)
    scr[y0 - 4:y0 + H, x0:x0 + 3, 3] = 255
    # muro de abajo con el hueco de la puerta y el felpudo
    by = y0 + H
    scr[by:by + 8, x0 - side:x0 + W + side] = C('wood', 1) if wall != 'adobe' else C('sand', 0)
    scr[by, x0 - side:x0 + W + side] = C('wood', 3) if wall != 'adobe' else C('sand', 2)
    dx = x0 + W // 2 - 16
    scr[by:by + 8, dx:dx + 32] = C('ink', 0)
    mat = new(32, 12)
    mat[:] = C('roofr', 2); mat[2:10, 2:30] = C('gold', 3); mat[4:8, 4:28] = C('roofr', 3)
    blit(scr, outline(mat), dx, by - 12)
    return scr, (x0, y0 + wall_h, W, H - wall_h)


# --- muebles ----------------------------------------------------------------------

def box(w, h, ramp, top=None, top_h=4):
    img = new(w, h)
    img[:] = col(ramp[3])
    img[:, 0] = col(ramp[4]); img[:, -1] = col(ramp[1])
    img[-2:] = col(ramp[1])
    if top is not None:
        img[:top_h] = col(top[4]); img[0] = col(top[5] if len(top) > 5 else top[4]); img[top_h - 1] = col(top[2])
    return img


def counter(w=120):
    """Mostrador de madera: tablero visto desde arriba y frente de cuarterones."""
    img = box(w, 40, P['wood'], P['wood'], 12)
    img[0:12] = C('wood', 4); img[0] = C('wood', 5); img[1:11:3] = C('wood', 5)
    img[11] = C('wood', 1)
    for x in range(6, w - 6, 22):
        img[16:34, x:x + 16] = C('wood', 2)
        img[17:33, x + 1:x + 15] = C('wood', 3)
        img[17, x + 1:x + 15] = C('wood', 4)
    return outline(img)


def shelf(w=96, goods='botellas', seed=0):
    rng = np.random.default_rng(seed)
    img = new(w, 40)
    for y0 in (10, 26):
        img[y0:y0 + 3, :] = C('wood', 3); img[y0 + 2, :] = C('wood', 1)
        x = 3
        while x < w - 6:
            if goods == 'botellas':
                c = P[['eco', 'roofb', 'gold', 'roofr'][rng.integers(0, 4)]]
                hh = rng.integers(6, 10)
                img[y0 - hh:y0, x:x + 3] = col(c[2]); img[y0 - hh:y0, x] = col(c[4])
                img[y0 - hh - 2:y0 - hh, x + 1] = C('wood', 2)
                x += 5
            elif goods == 'tarros':
                c = P[['flower', 'gold', 'sand', 'roofr'][rng.integers(0, 4)]]
                img[y0 - 7:y0, x:x + 6] = C('ui', 4); img[y0 - 6:y0 - 1, x + 1:x + 5] = col(c[2])
                img[y0 - 8, x:x + 6] = C('wood', 2)
                x += 8
            elif goods == 'telas':
                c = P[['roofr', 'eco', 'gold', 'flower', 'roofb'][rng.integers(0, 5)]]
                img[y0 - 8:y0, x:x + 9] = col(c[3]); img[y0 - 8:y0:2, x:x + 9] = col(c[2])
                x += 10
            elif goods == 'libros':
                c = P[['roofr', 'eco', 'roofb', 'gold', 'wood'][rng.integers(0, 5)]]
                hh = rng.integers(6, 9)
                img[y0 - hh:y0, x:x + 2] = col(c[3]); img[y0 - hh, x:x + 2] = col(c[4])
                x += 3
    img[:, 0:2] = C('wood', 2); img[:, -2:] = C('wood', 1)
    return outline(img)


def window_in(w=28, h=24, night=False):
    img = new(w, h)
    img[:] = C('wood', 2)
    g = C('water', 5) if not night else C('roofb', 1)
    img[3:h - 5, 3:w - 3] = g
    img[3:h // 2, 3:w - 3] = C('water', 6) if not night else C('roofb', 2)
    img[3:h - 5, w // 2] = C('wood', 2); img[h // 2 - 1, 3:w - 3] = C('wood', 2)
    img[h - 5:h - 2, 0:w] = C('wood', 4); img[h - 3] = C('wood', 1)
    # cortina
    img[1:h - 6, 0:4] = C('roofr', 3); img[1:h - 6, w - 4:w] = C('roofr', 3)
    img[1:h - 6:2, 0:4] = C('roofr', 2); img[1:h - 6:2, w - 4:w] = C('roofr', 2)
    return outline(img)


def fireplace(lit=True):
    w, h = 60, 70
    img = new(w, h)
    stone = np.zeros((h, w), bool); stone[8:, 2:w - 2] = True
    img[stone] = C('stone', 3)
    yy, xx = np.indices((h, w))
    img[stone & ((yy % 7 == 0) | (((xx + (yy // 7) * 5) % 11) == 0))] = C('stone', 2)
    img[stone & (yy % 7 == 1)] = C('stone', 4)
    img[4:12, 0:w] = C('wood', 3); img[4] = C('wood', 4); img[11] = C('wood', 1)
    hole = (yy >= 30) & (yy < h - 2) & (xx >= 13) & (xx < w - 13)
    arch = (yy >= 26) & (yy < 30) & (xx >= 15) & (xx < w - 15)
    img[arch] = C('ink', 0)
    img[hole] = C('ink', 0)
    if lit:
        for x in range(12, w - 12):
            hgt = 14 + int(6 * np.sin(x * 1.3))
            if x < 15 or x >= w - 15:
                continue
            img[h - 3 - hgt:h - 3, x] = C('fire', 3)
            img[h - 3 - hgt // 2:h - 3, x] = C('fire', 4)
            img[h - 5:h - 3, x] = C('fire', 5)
        img[h - 4:h - 2, 14:w - 14] = C('wood', 1)
        img[2:4, 10:16] = C('gold', 3); img[0:4, 44:48] = C('roofr', 3)
    return outline(img)


def table_round(chairs=True):
    w, h = 64, 46
    img = new(w, h)
    yy, xx = np.indices((h, w))
    top = ellipse(w, h, 32, 13, 29, 11)
    img[top] = C('wood', 4)
    img[top & ~ellipse(w, h, 31, 12, 26, 8.5)] = C('wood', 3)
    img[top & (yy >= 20)] = C('wood', 2)
    img[top & ellipse(w, h, 26, 9, 10, 3)] = C('wood', 5)
    img[24:41, 28:36] = C('wood', 2); img[24:41, 28:30] = C('wood', 3)
    img[40:43, 20:44] = C('wood', 1)
    # mantel, vela, jarra y platos
    img[top & ellipse(w, h, 32, 12, 14, 6)] = C('paper', 4)
    img[5:11, 30:33] = C('ui', 5); img[4, 30:33] = C('fire', 4); img[3, 31] = C('fire', 5)
    img[10:13, 16:24] = C('ui', 4); img[11, 17:23] = C('ui', 5)
    img[8:14, 42:47] = C('roofr', 3); img[8, 42:47] = C('roofr', 4)
    out = new(w + 34, h + 6)
    if chairs:
        for cx in (0, w + 17):
            ch = new(17, 34)
            ch[0:20, 2:15] = C('wood', 3); ch[0:20, 2] = C('wood', 4); ch[3:18:4, 4:13] = C('wood', 2)
            ch[20:24, 0:17] = C('wood', 4); ch[23, 0:17] = C('wood', 2)
            ch[24:34, 1:4] = C('wood', 2); ch[24:34, 13:16] = C('wood', 2)
            blit(out, outline(ch), cx, 14)
    blit(out, outline(img), 17, 2)
    return out


def bed():
    w, h = 40, 54
    img = new(w, h)
    img[0:12, 0:w] = C('wood', 3); img[0:12, 0] = C('wood', 4); img[2:10:3, 3:w - 3] = C('wood', 2)
    img[10:h - 4, 2:w - 2] = C('ui', 5)
    img[12:20, 6:w - 6] = C('ui', 6); img[19, 6:w - 6] = C('ui', 4)
    q = np.zeros((h, w), bool); q[22:h - 4, 2:w - 2] = True
    yy, xx = np.indices((h, w))
    img[q] = C('roofr', 3)
    img[q & ((xx // 6 + yy // 6) % 2 == 0)] = C('gold', 4)
    img[q & ((xx % 6 == 0) | (yy % 6 == 0))] = C('roofr', 1)
    img[h - 4:h, 0:w] = C('wood', 2)
    return outline(img)


def rug(w=96, h=44):
    """Alfombra andina: franjas y rombos de colores."""
    img = new(w, h)
    yy, xx = np.indices((h, w))
    img[:] = C('roofr', 3)
    for y0, c in ((4, ('gold', 4)), (h - 8, ('gold', 4))):
        img[y0:y0 + 4] = C(*c)
    img[(yy >= 10) & (yy < h - 10)] = C('roofb', 2)
    cy = h // 2
    dia = (np.abs(((xx % 24) - 12)) + np.abs(yy - cy)) <= 7
    img[dia & (yy >= 10) & (yy < h - 10)] = C('eco', 3)
    dia2 = (np.abs(((xx % 24) - 12)) + np.abs(yy - cy)) <= 3
    img[dia2 & (yy >= 10) & (yy < h - 10)] = C('flower', 3)
    img[(xx < 2) | (xx >= w - 2)] = C('paper', 3)
    img[((xx < 2) | (xx >= w - 2)) & (yy % 2 == 0)] = C('paper', 1)
    return img


def barrel():
    w, h = 20, 26
    m = ellipse(w, h, 10, 13, 9.5, 12.5)
    img = shade(m, P['wood'][1:6], ambient=0.25)
    for y in (5, 19):
        img[y][m[y]] = C('stone', 2); img[y + 1][m[y + 1]] = C('stone', 4)
    top = ellipse(w, h, 10, 4, 8, 3)
    img[top] = C('wood', 4); img[top & ~ellipse(w, h, 10, 4, 6, 2)] = C('wood', 2)
    return outline(img)


def sacks(n=3):
    img = new(18 * n, 22)
    for i in range(n):
        m = ellipse(20, 22, 10, 12, 8.5, 9.5)
        s = shade(m, P['sand'][0:5], ambient=0.3)
        s[3:5, 7:13] = C('sand', 1)
        blit(img, outline(s), i * 16, 0)
    return img


def plant():
    import buildings as B
    p = B.pot_plant(1)
    return np.kron(p, np.ones((2, 2, 1), np.uint8))[::1] if False else p


def painting(w=26, h=20):
    img = new(w, h)
    img[:] = C('gold', 2); img[2:h - 2, 2:w - 2] = C('water', 5)
    img[h // 2:h - 2, 2:w - 2] = C('grass', 4)
    img[h // 2 - 3:h // 2, 8:16] = C('stone', 3)
    img[4:7, w - 8:w - 5] = C('gold', 4)
    return outline(img)


def crate_big(fill='papa'):
    w, h = 26, 20
    img = new(w, h)
    img[:] = C('wood', 3)
    img[[0, h - 1], :] = C('wood', 1); img[:, [0, w - 1]] = C('wood', 1)
    img[h // 2 - 1:h // 2 + 1, :] = C('wood', 2)
    img[2:h - 2, 2] = C('wood', 4)
    c, c2 = {'papa': ('sand', 'sand'), 'naranja': ('flower', 'flower'), 'manzana': ('flower', 'roofr'), 'maiz': ('gold', 'gold')}[fill]
    i1, i2 = {'papa': (1, 3), 'naranja': (3, 4), 'manzana': (0, 3), 'maiz': (4, 5)}[fill]
    for x in range(1, w - 2, 3):
        img[0:3, x:x + 3] = C(c, i1)
        img[0, x + 1] = C(c2, i2)
    return outline(img)


def basket_table(w=80):
    img = new(w, 34)
    img[10:14, 0:w] = C('wood', 4); img[13, 0:w] = C('wood', 1)
    for x in (3, w - 7):
        img[14:34, x:x + 4] = C('wood', 2)
    goods = [('flower', 3, 4), ('grass', 4, 5), ('flower', 0, 2), ('gold', 4, 5), ('roofb', 3, 4)]
    for i, x in enumerate(range(2, w - 14, 15)):
        r, a, b = goods[i % len(goods)]
        img[4:11, x:x + 14] = C('wood', 2); img[5:10, x + 1:x + 13] = C('wood', 3)
        for k in range(x + 1, x + 13, 2):
            img[2:5, k:k + 2] = C(r, a); img[2, k] = C(r, b)
    return outline(img)


def scale_counter():
    img = new(18, 14)
    img[10:14, 4:14] = C('stone', 2); img[2:10, 8:10] = C('stone', 3)
    img[2, 1:17] = C('stone', 4)
    img[3:6, 0:5] = C('gold', 3); img[3:6, 13:18] = C('gold', 3)
    return outline(img)


def stairs_up():
    w, h = 34, 54
    img = new(w, h)
    for i, y in enumerate(range(h - 8, -1, -8)):
        img[y:y + 8, :] = C('wood', 3 if i % 2 else 4)
        img[y, :] = C('wood', 5); img[y + 7, :] = C('wood', 1)
    img[:, 0:3] = C('wood', 2); img[:, -3:] = C('wood', 1)
    return outline(img)


# --- personas -------------------------------------------------------------------

def npc(name, d='south'):
    import os
    p = f'pl/npc/{name}/{d}.png'
    if not os.path.exists(p):
        p = f'pl/npc/{name}/south.png'
    return scene.trim(np.array(Image.open(p)))


def hero(d='north'):
    return scene.trim(np.array(Image.open(f'final/chars/ilan_{d}.png')))


def place(scr, objs):
    """objs: (sprite, x, y_base). Orden por la base, con sombra suave."""
    for spr, x, yb in sorted(objs, key=lambda o: o[2]):
        h, w = spr.shape[:2]
        sw = max(8, int(w * 0.7))
        m = ellipse(sw, 6, sw / 2, 3, sw / 2, 2.6)
        ys, xs = np.where(m)
        Y, X = ys + yb - 4, xs + x + (w - sw) // 2
        ok = (Y >= 0) & (Y < scr.shape[0]) & (X >= 0) & (X < scr.shape[1])
        scr[Y[ok], X[ok], :3] = (scr[Y[ok], X[ok], :3].astype(int) * 0.72).astype(np.uint8)
        blit(scr, spr, x, yb - h)


# --- las tres habitaciones ---------------------------------------------------------

def posada():
    scr, (fx, fy, fw, fh) = room(24, 14, 'encalado', 'tablas', seed=1)
    wy = fy - 56
    # pared del fondo: ventanas, estante de botellas tras la barra, cuadro, chimenea
    blit(scr, window_in(), fx + 20, wy + 10)

    blit(scr, shelf(120, 'botellas', 2), fx + fw // 2 + 14, wy + 4)
    blit(scr, painting(), fx + 128, wy + 14)
    objs = [(fireplace(), fx + 54, fy + 8)]
    objs.append((counter(140), fx + fw // 2 + 4, fy + 52))
    objs.append((barrel(), fx + fw - 30, fy + 22))
    objs.append((barrel(), fx + fw - 50, fy + 26))
    for tx, ty in ((fx + 8, fy + 120), (fx + 128, fy + 132)):
        objs.append((table_round(), tx, ty))
    rugi = rug(110, 40)
    blit(scr, rugi, fx + fw // 2 - 70, fy + 62)
    # gente
    objs.append((npc('mariela', 'south'), fx + fw // 2 + 60, fy + 30))      # tras la barra
    objs.append((npc('aurelio', 'east'), fx + 0, fy + 126))
    objs.append((npc('tona', 'west'), fx + 222, fy + 138))
    objs.append((hero('north'), fx + fw // 2 - 12, fy + fh - 4))
    place(scr, objs)
    return scr


def tienda():
    scr, (fx, fy, fw, fh) = room(24, 14, 'tabla', 'piedra', wall_h=60, seed=2)
    wy = fy - 60
    blit(scr, shelf(120, 'tarros', 3), fx + 8, wy + 4)
    blit(scr, shelf(120, 'telas', 5), fx + fw - 128, wy + 4)
    blit(scr, window_in(28, 24), fx + fw // 2 - 14, wy + 12)
    objs = [(counter(150), fx + fw // 2 - 75, fy + 58)]
    blit_scale = scale_counter()
    objs.append((sacks(3), fx + 12, fy + 46))
    objs.append((sacks(2), fx + fw - 40, fy + 40))
    import buildings as B
    for i, (x, y) in enumerate([(fx + 10, fy + 120), (fx + 34, fy + 126), (fx + 10, fy + 146), (fx + fw - 40, fy + 118), (fx + fw - 40, fy + 142)]):
        objs.append((crate_big(['papa', 'naranja', 'manzana', 'maiz', 'papa'][i]), x, y))
    objs.append((barrel(), fx + fw - 30, fy + 90))
    objs.append((barrel(), fx + fw - 52, fy + 94))
    objs.append((basket_table(84), fx + 120, fy + 120))
    objs.append((basket_table(84), fx + fw - 160, fy + 132))
    objs.append((npc('rosa', 'south'), fx + fw // 2 - 10, fy + 40))
    objs.append((npc('tito', 'north-east'), fx + 76, fy + 150))
    objs.append((hero('north'), fx + fw // 2 + 10, fy + fh - 4))
    place(scr, objs)
    blit(scr, blit_scale, fx + fw // 2 + 30, fy + 34)
    return scr


def casa():
    scr, (fx, fy, fw, fh) = room(22, 14, 'adobe', 'baldosa', wall_h=54, seed=3)
    wy = fy - 54
    blit(scr, window_in(), fx + 20, wy + 16)
    blit(scr, shelf(70, 'libros', 7), fx + 80, wy + 6)
    blit(scr, painting(), fx + fw - 90, wy + 16)
    blit(scr, rug(96, 44), fx + fw // 2 - 48, fy + 56)
    objs = [(bed(), fx + fw - 62, fy + 52), (fireplace(), fx + 160, fy + 6)]
    objs.append((table_round(), fx + 24, fy + 110))
    objs.append((stairs_up(), fx + 6, fy + 52))
    import buildings as B
    objs.append((B.pot_plant(2), fx + fw - 18, fy + 120))
    objs.append((npc('tona', 'south'), fx + fw // 2 - 8, fy + 96))
    objs.append((hero('north'), fx + fw // 2 + 4, fy + fh - 4))
    place(scr, objs)
    return scr


if __name__ == '__main__':
    import os
    os.makedirs('out2', exist_ok=True)
    for n, f in (('posada', posada), ('tienda', tienda), ('casa', casa)):
        px.save(f(), f'out2/int_{n}.png', scale=2)
