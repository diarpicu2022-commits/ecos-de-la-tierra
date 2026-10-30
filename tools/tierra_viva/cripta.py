"""Cripta de la Avaricia: mazmorra bajo tierra. Enferma = el oro lo invade todo
(monedas derramadas, canal de oro fundido, telarañas, luz enfermiza); sana =
piedra con musgo, agua limpia en el canal, raíces y luz que entra del techo."""
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
import px
from pal import P
from px import new, col, outline, shade, ellipse, blit

W, H, T = 640, 360, 16
C = lambda r, i: np.array(col(P[r][i]), np.uint8)


def fill(img, m, c):
    img[m] = c


def flagstones(rng, stone, sick):
    """Losas cuadradas grandes (32x24) en hileras desplazadas, con bisel claro
    arriba-izquierda, junta oscura abajo-derecha, desgaste y alguna grieta."""
    img = np.zeros((H, W, 4), np.uint8)
    img[...] = C(stone, 1)
    yy, xx = np.indices((H, W))
    for r, y in enumerate(range(70, H, 32)):
        off = int(rng.integers(0, 40))
        for x in range(-off, W, 40):
            m = (yy >= y + 1) & (yy < y + 31) & (xx >= x + 1) & (xx < x + 39)
            tone = 3 + (rng.random() < 0.35) - (rng.random() < 0.2)
            img[m] = C(stone, tone)
            img[m & ((yy == y + 1) | (xx == x + 1))] = C(stone, min(6, tone + 1))
            img[m & ((yy == y + 30) | (xx == x + 38))] = C(stone, tone - 1)
            img[m & (yy == y + 29) & (xx > x + 2)] = C(stone, max(1, tone - 1))
            if rng.random() < 0.3:     # desgaste
                cx, cy = x + rng.uniform(8, 30), y + rng.uniform(6, 24)
                wm = m & (((xx - cx) / 6) ** 2 + ((yy - cy) / 4) ** 2 < 1) & ((xx + yy) % 2 == 0)
                img[wm] = C(stone, tone - 1)
            if rng.random() < 0.18:    # grieta
                cx, cy = x + rng.uniform(6, 32), y + rng.uniform(4, 26)
                a = rng.uniform(0, np.pi)
                for t in range(int(rng.integers(6, 14))):
                    xi, yi = int(cx + np.cos(a) * t), int(cy + np.sin(a) * t * .6)
                    if 0 <= xi < W and 0 <= yi < H and m[yi, xi]:
                        img[yi, xi] = C(stone, 1)
                    a += rng.uniform(-.5, .5)
    return img


def alcove(img, x, y, w, h, stone, sick):
    yy, xx = np.indices((h, w))
    arch = (yy >= w / 2) | (((xx - w / 2 + .5) / (w / 2)) ** 2 + ((yy - w / 2) / (w / 2)) ** 2 <= 1)
    sub = img[y:y + h, x:x + w]
    sub[arch] = C(stone, 0) if stone == 'ash' else C(stone, 1)
    inner = arch & (yy >= 3) & (xx >= 2) & (xx < w - 2)
    sub[inner] = C('ink', 0) if 'ink' in P else C(stone, 0)
    sub[arch & ~inner] = C(stone, 4)
    # estatua dentro
    st = (np.abs(xx - w / 2) < 4) & (yy > 8) & (yy < h - 2) | (((xx - w / 2) ** 2 + (yy - 7) ** 2) < 10)
    sub[st & inner] = C('gold', 3) if sick else C(stone, 4)
    sub[st & inner & (xx < w / 2)] = C('gold', 4) if sick else C(stone, 5)


def wall_face(img, y0, h, stone, rng):
    """Muro norte visto de frente: sillares con juntas y zócalo."""
    yy, xx = np.indices((h, W))
    face = np.zeros((h, W, 4), np.uint8)
    face[...] = C(stone, 3)
    rowh = 12
    for r in range(0, h, rowh):
        off = (r // rowh % 2) * 14
        face[r] = C(stone, 1)
        face[r + 1] = C(stone, 4)
        for x in range(-off, W, 28):
            if x >= 0:
                face[r:r + rowh, x] = C(stone, 1)
                if x + 1 < W:
                    face[r + 1:r + rowh, x + 1] = C(stone, 4)
    # degradado: más oscuro arriba (penumbra)
    k = np.clip(1 - yy / h, 0, 1)[..., None] * 0.45
    face[..., :3] = (face[..., :3] * (1 - k)).astype(np.uint8)
    face[h - 4:h] = C(stone, 1)
    face[h - 4] = C(stone, 4)
    img[y0:y0 + h] = face


def torch(sick):
    img = new(12, 26)
    img[10:26, 5:7] = C('wood', 2)
    img[8:11, 3:9] = C('stone', 2)
    fl = P['fire'] if not sick else ['#2a1d3a', '#5a2d6b', '#8f4fb0', '#c98ae0', '#f2d1ff']
    for i, (y, w_) in enumerate([(7, 3), (5, 2), (3, 2), (1, 1)]):
        img[y:y + 2, 6 - w_:6 + w_] = col(fl[min(len(fl) - 1, 2 + i)])
    return img


def pillar(sick):
    Wp, Hp = 40, 84
    img = new(Wp, Hp)
    s = 'stone'
    yy, xx = np.indices((Hp, Wp))
    shaft = (xx >= 6) & (xx < 34) & (yy >= 10) & (yy < Hp - 10)
    sh = shade(shaft, P[s][1:6], light=(-0.9, 0, 0.3), ambient=0.25)
    img[shaft] = sh[shaft]
    for y in range(14, Hp - 12, 9):
        img[y, 6:34] = C(s, 1)
    img[0:10, 1:39] = C(s, 4); img[0, 1:39] = C(s, 5); img[8:10, 1:39] = C(s, 2)
    img[Hp - 10:Hp, 1:39] = C(s, 3); img[Hp - 10, 1:39] = C(s, 5); img[Hp - 2:Hp, 1:39] = C(s, 1)
    if sick:   # vetas de oro que trepan
        for x in (10, 20, 28):
            for y in range(Hp - 12, Hp - 12 - int(20 + x), -1):
                img[y, x + int(2 * np.sin(y / 5))] = C('gold', 3)
    else:      # musgo y hiedra
        rng = np.random.default_rng(3)
        for _ in range(60):
            y, x = int(rng.integers(Hp - 40, Hp - 10)), int(rng.integers(6, 34))
            img[y, x] = C('grass', int(rng.integers(3, 6)))
    return outline(img)


def coin_pile(Wc=120, Hc=54, seed=0):
    m = ellipse(Wc, Hc, Wc / 2, Hc * .72, Wc / 2 - 2, Hc * .5)
    m |= ellipse(Wc, Hc, Wc / 2, Hc * .45, Wc / 3, Hc * .4)
    img = shade(m, P['gold'][1:6], ambient=0.3)
    rng = np.random.default_rng(seed)
    yy, xx = np.indices((Hc, Wc))
    for _ in range(140):
        x, y = int(rng.integers(0, Wc)), int(rng.integers(0, Hc))
        if m[y, x]:
            img[y, x:x + 2] = col(P['gold'][5]);
            if y + 1 < Hc:
                img[y + 1, x:x + 2] = col(P['gold'][2])
    for _ in range(14):   # gemas
        x, y = int(rng.integers(8, Wc - 8)), int(rng.integers(6, Hc - 6))
        if m[y, x]:
            c = [P['flower'][0], P['eco'][3], P['ice'][3], P['flower'][5]][int(rng.integers(4))]
            img[y:y + 2, x:x + 2] = col(c)
    return outline(img)


def chest(sick, open_=True):
    img = new(30, 26)
    w = P['wood']
    img[10:26, 2:28] = col(w[3]); img[10, 2:28] = col(w[5]); img[25, 2:28] = col(w[1])
    img[10:26, 2:4] = col(P['gold'][3]); img[10:26, 26:28] = col(P['gold'][3])
    img[16:20, 13:17] = col(P['gold'][4])
    if open_:
        img[2:10, 2:28] = col(w[2]); img[2, 2:28] = col(w[4])
        if sick:
            img[8:12, 5:25] = col(P['gold'][4]); img[8, 7:23] = col(P['gold'][5])
        else:
            img[8:12, 5:25] = col(w[1])
    else:
        img[4:10, 2:28] = col(w[4]); img[4, 3:27] = col(w[5])
    return outline(img)


def coins_decal(seed, n=20, Wd=60, Hd=30):
    rng = np.random.default_rng(seed)
    img = new(Wd, Hd)
    for _ in range(n):
        x, y = int(rng.integers(0, Wd - 3)), int(rng.integers(0, Hd - 2))
        img[y, x:x + 3] = col(P['gold'][4]); img[y + 1, x:x + 3] = col(P['gold'][2]); img[y, x] = col(P['gold'][5])
    return img


def web(seed):
    img = new(34, 34)
    c = col('#c9c3d6'); c2 = col('#8a8496')
    for a in np.linspace(0, np.pi / 2, 6):
        for t in range(34):
            x, y = int(np.cos(a) * t), int(np.sin(a) * t)
            if x < 34 and y < 34:
                img[y, x] = c2
    for r in (8, 15, 22, 29):
        for a in np.linspace(0, np.pi / 2, 40):
            x, y = int(np.cos(a) * r), int(np.sin(a) * r)
            if x < 34 and y < 34:
                img[y, x] = c
    return img


def skull_bones():
    img = new(22, 12)
    img[2:8, 2:9] = col('#e8e2d0'); img[4:6, 3:5] = col('#2a2434'); img[4:6, 6:8] = col('#2a2434'); img[8, 3:8] = col('#bdb5a0')
    img[9:11, 10:21] = col('#e8e2d0'); img[8:12, 10] = col('#e8e2d0'); img[8:12, 20] = col('#e8e2d0')
    return outline(img)


def spikes(raised=True):
    img = new(32, 18)
    img[12:18, 0:32] = C('stone', 1); img[12, 0:32] = C('stone', 3)
    if raised:
        for x in range(3, 32, 7):
            for k in range(8):
                img[12 - k, x - (7 - k) // 3: x + (7 - k) // 3 + 1] = C('stone', 4 if k < 6 else 5)
    else:
        for x in range(3, 32, 7):
            img[14:16, x - 1:x + 2] = C('ink', 1)
    return outline(img)


def plate():
    img = new(26, 14)
    m = ellipse(26, 14, 13, 7, 12, 6)
    img[m] = C('stone', 4); img[m & ~ellipse(26, 14, 13, 7, 10, 4.5)] = C('stone', 2)
    img[6:8, 10:16] = C('gold', 3)
    return img


def urn(sick, seed):
    m = ellipse(18, 24, 9, 15, 8, 8) | ((np.abs(np.indices((24, 18))[1] - 9) < 4) & (np.indices((24, 18))[0] < 10) & (np.indices((24, 18))[0] > 2))
    ramp = P['roofr'][1:6] if seed % 2 else P['wood'][1:6]
    img = shade(m, ramp, ambient=0.25)
    img[2:4, 4:14] = col(ramp[3])
    img[15, 2:16][m[15, 2:16]] = col(P['gold'][3] if sick else ramp[1])
    if sick and seed % 3 == 0:
        img[0:3, 6:12] = col(P['gold'][4])
    return outline(img)


def fern(seed):
    rng = np.random.default_rng(seed)
    img = new(24, 16)
    for k in range(7):
        a = np.pi * (1.1 + 0.8 * k / 6)
        for t in range(int(rng.integers(8, 12))):
            x, y = int(12 + np.cos(a) * t), int(15 + np.sin(a) * t * .8 + (t / 10) ** 2 * 3)
            if 0 <= x < 24 and 0 <= y < 16:
                img[y, x] = C('grass', 3 + (t % 3 == 0))
                if t % 2 and y + 1 < 16:
                    img[y + 1, x] = C('grass', 2)
    return outline(img)


def sprout():
    img = new(18, 16)
    img[6:16, 8:10] = C('grass', 3)
    for (x, y, d) in [(4, 5, 1), (13, 3, -1)]:
        m = ellipse(18, 16, x, y + 2, 4, 2.5)
        img[m] = C('grass', 5); img[m & ellipse(18, 16, x - d, y + 1, 2, 1)] = C('grass', 6)
    return outline(img)


def roots(seed):
    rng = np.random.default_rng(seed)
    img = new(60, 70)
    for k in range(5):
        x = rng.uniform(10, 50)
        for y in range(70):
            x += rng.uniform(-0.8, 0.8)
            xi = int(x)
            if 0 <= xi < 59:
                img[y, xi:xi + 2] = col(P['wood'][2 + (y % 6 == 0)])
            if y > 30 and rng.random() < 0.02:
                break
    return img


def light_shaft(img, x, w, a=0.22):
    yy, xx = np.indices(img.shape[:2])
    m = (xx > x + yy * 0.35) & (xx < x + w + yy * 0.35)
    out = img.astype(float)
    k = (a * m * np.clip(1 - yy / H, 0.2, 1))[..., None]
    out[..., :3] = out[..., :3] * (1 - k) + np.array([255, 245, 200]) * k
    return out.astype(np.uint8)


def lighting(img, lights, ambient, tint):
    """Oscurece con luz ambiente y añade resplandor del color de cada fuente,
    cuantizado en 4 bandas con tramado en los bordes (pixel art)."""
    yy, xx = np.indices(img.shape[:2])
    out = img.astype(float)
    L = np.full(img.shape[:2], ambient, float)
    glow = np.zeros(img.shape[:2] + (3,), float)
    for (x, y, r, s, c) in lights:
        d = np.sqrt((xx - x) ** 2 + ((yy - y) * 1.25) ** 2)
        f = np.clip(1 - d / r, 0, 1) ** 1.5
        L += s * f
        glow += (s * f)[..., None] * (np.array(c, float)[None, None] / 255 - 0.6)
    L = np.clip(ndi.gaussian_filter(L, 2), 0, 1.05)
    k = L[..., None] * np.array(tint)[None, None] * (1 + 0.5 * np.clip(glow, -0.3, 0.6))
    out[..., :3] = out[..., :3] * k
    return np.clip(out, 0, 255).astype(np.uint8)


def wall_tops(img, side, stone):
    """Muros laterales y sur vistos desde arriba: coronación de sillares, arista
    clara hacia la sala y sombra proyectada sobre el suelo."""
    yy, xx = np.indices((H, W))
    for left in (True, False):
        m = (xx < side) if left else (xx >= W - side)
        img[m] = C(stone, 1)
        # sillares de la coronación
        bx = xx if left else (W - 1 - xx)
        joint = m & ((((yy + (bx // 15) * 8) % 16) == 0) | ((bx % 15) == 0))
        img[m & ~joint & (((yy // 16 + bx // 15) % 2) == 0)] = C(stone, 2)
        img[joint] = C(stone, 0)
        edge = (xx == side - 1) if left else (xx == W - side)
        img[edge] = C(stone, 4)
        edge2 = (xx == side - 2) if left else (xx == W - side + 1)
        img[edge2 & (yy > 76)] = C(stone, 3)
        # sombra sobre el suelo (10 px, en dos bandas)
        for k, f in ((range(0, 5), 0.55), (range(5, 10), 0.75)):
            for d in k:
                col_ = side + d if left else W - side - 1 - d
                sl = img[76:H - 14, col_, :3]
                img[76:H - 14, col_, :3] = (sl * f).astype(np.uint8)
    # muro sur
    img[H - 14:H] = C(stone, 1); img[H - 14] = C(stone, 4)
    for x in range(0, W, 16):
        img[H - 13:H, x] = C(stone, 0)
    # sombra del muro norte sobre el suelo
    for d, f in enumerate([0.5, 0.55, 0.62, 0.7, 0.78, 0.86]):
        img[76 + d, side:W - side, :3] = (img[76 + d, side:W - side, :3] * f).astype(np.uint8)


def puddle(seed, sick):
    rng = np.random.default_rng(seed)
    w, h = int(rng.integers(26, 44)), int(rng.integers(10, 16))
    m = ellipse(w, h, w / 2, h / 2, w / 2 - 1, h / 2 - 1) | ellipse(w, h, w * .35, h * .6, w * .3, h * .38)
    img = new(w, h)
    c = P['gold'] if sick else P['water']
    img[m] = col(c[2]); img[m & ellipse(w, h, w / 2 - 2, h / 2 - 1, w / 2 - 5, h / 2 - 4)] = col(c[3])
    img[m & (np.indices((h, w))[0] == 2) & (np.indices((h, w))[1] % 5 < 2)] = col(c[5])
    return img


def rubble(seed, stone):
    rng = np.random.default_rng(seed)
    img = new(30, 14)
    for _ in range(6):
        x, y, r = rng.uniform(4, 26), rng.uniform(5, 11), rng.uniform(2, 4)
        m = ellipse(30, 14, x, y, r, r * .8)
        s_ = shade(m, P[stone][1:6], ambient=.3)
        img[m] = s_[m]
    return outline(img)


def render(state='enfermo'):
    sick = state != 'sano'
    rng = np.random.default_rng(7)
    stone = 'stone' if not sick else 'ash'
    img = flagstones(rng, stone, sick)
    # muros
    wall_face(img, 0, 76, stone, rng)
    img[0:10] = C(stone, 0)
    for x in (150, 466):
        alcove(img, x, 24, 24, 44, stone, sick)
    side = 30
    wall_tops(img, side, stone)
    # puerta al sur: hueco con escalones que bajan hacia la oscuridad
    img[H - 14:H, 300:340] = C(stone, 0)
    for k, y in enumerate(range(H - 14, H, 4)):
        img[y:y + 2, 302 + k:338 - k] = C(stone, 2 - min(2, k))
    img[H - 14:H, 298:300] = C(stone, 4); img[H - 14:H, 340:342] = C(stone, 4)
    # canal que cruza la sala
    cy0, cy1 = 214, 244
    yy, xx = np.indices((H, W))
    chan = (yy >= cy0) & (yy < cy1) & (xx >= side) & (xx < W - side)
    if sick:
        liq = P['gold']
        img[chan] = col(liq[3])
        wav = chan & ((yy % 5) == 2) & (((xx * 7 + (yy // 5) * 13) % 23) < 5)
        img[wav] = col(liq[5])
        img[chan & ((yy % 5) == 3) & (((xx * 7 + (yy // 5) * 13) % 23) < 4)] = col(liq[2])
        img[chan & (yy < cy0 + 3)] = col(liq[1])
    else:
        liq = P['water']
        img[chan] = col(liq[2])
        wav = chan & ((yy % 5) == 2) & (((xx * 7 + (yy // 5) * 13) % 29) < 5)
        img[wav] = col(liq[4])
        img[chan & ((yy % 5) == 3) & (((xx * 7 + (yy // 5) * 13) % 29) < 4)] = col(liq[1])
        img[chan & (yy < cy0 + 3)] = col(liq[0])
    img[cy0 - 2:cy0, side:W - side] = C(stone, 4)
    img[cy1:cy1 + 3, side:W - side] = C(stone, 1)
    # puente de piedra
    img[cy0 - 2:cy1 + 3, 296:344] = C(stone, 3)
    img[cy0 - 2:cy1 + 3, 296] = C(stone, 1); img[cy0 - 2:cy1 + 3, 343] = C(stone, 1)
    for y in range(cy0, cy1, 6):
        img[y, 297:343] = C(stone, 2)
    # alfombra del umbral al altar
    rug = (xx >= 304) & (xx < 336) & (yy >= 150) & (yy < H - 14) & ~((yy >= cy0 - 2) & (yy < cy1 + 3))
    rc = P['roofr']
    img[rug] = col(rc[2] if sick else rc[3])
    img[rug & ((xx == 305) | (xx == 334))] = col(P['gold'][3])
    img[rug & (((yy // 6) + (xx // 6)) % 2 == 0) & (xx > 310) & (xx < 330)] = col(rc[1] if sick else rc[2])
    if sick:
        tear = rug & (np.random.default_rng(2).random((H, W)) < 0.12)
        img[tear] = C(stone, 2)
    objs = []
    # antorchas en el muro
    for x in (90, 230, 400, 540):
        blit(img, torch(sick), x - 6, 30)
    # columnas
    for x, y in [(110, 200), (530, 200), (110, 330), (530, 330)]:
        objs.append((pillar(sick), x - 20, y))
    if sick:
        objs.append((coin_pile(150, 60, 1), 245, 150))
        objs.append((chest(True, True), 230, 160))
        objs.append((chest(True, True), 382, 158))
        rng2 = np.random.default_rng(5)
        for k in range(16):
            x, y = int(rng2.integers(40, 580)), int(rng2.integers(90, 340))
            if not (cy0 - 10 < y < cy1 + 10):
                blit(img, coins_decal(k), x, y)
        for x, y in [(30, 76), (W - 64, 76)]:
            w_ = web(1)
            blit(img, w_ if x < 100 else w_[:, ::-1], x, y)
        objs.append((skull_bones(), 170, 300))
        objs.append((skull_bones(), 450, 120))
        objs.append((spikes(True), 200, 286))
        objs.append((spikes(True), 410, 286))
        for i, (x, y) in enumerate([(60, 100), (78, 104), (560, 100), (64, 352), (556, 352), (420, 190)]):
            objs.append((urn(True, i), x, y))
        for x, y in [(150, 190), (470, 330), (60, 200)]:
            objs.append((coin_pile(40, 18, x), x, y))
    else:
        # altar purificado con brote
        alt = new(90, 40)
        alt[8:40, 4:86] = C('stone', 3); alt[8, 4:86] = C('stone', 5); alt[38:40, 4:86] = C('stone', 1)
        alt[14:34, 12:78] = C('stone', 4)
        objs.append((outline(alt), 275, 150))
        objs.append((sprout(), 311, 112))
        objs.append((chest(False, False), 230, 160))
        objs.append((spikes(False), 200, 286))
        objs.append((spikes(False), 410, 286))
        rngm = np.random.default_rng(9)
        for _ in range(500):    # musgo en juntas
            x, y = int(rngm.integers(side, W - side)), int(rngm.integers(80, H - 16))
            if not chan[y, x]:
                img[y, x] = C('grass', int(rngm.integers(2, 5)))
        blit(img, roots(1), 40, 0); blit(img, roots(2), 520, 0)
        for i, (x, y) in enumerate([(60, 100), (78, 104), (560, 100)]):
            objs.append((urn(False, i), x, y))
        for i, (x, y) in enumerate([(40, 90), (180, 88), (420, 90), (590, 92), (40, 352), (580, 352), (150, 260), (470, 210)]):
            objs.append((fern(i), x, y))
    objs.append((plate(), 307, 290))
    for i, (x, y) in enumerate([(70, 270), (520, 160), (380, 330), (160, 120)]):
        blit(img, puddle(i, sick), x, y)
    for i, (x, y) in enumerate([(48, 160), (560, 290), (240, 340)]):
        objs.append((rubble(i, stone), x, y))
    objs.sort(key=lambda o: o[2])
    for spr, x, yb in objs:
        sw = spr.shape[1] + 6
        sh = ellipse(sw, 8, sw / 2, 4, sw / 2 - 1, 3)
        ys, xs = np.where(sh)
        ys, xs = ys + yb - 5, xs + x - 3
        ok = (ys >= 0) & (ys < H) & (xs >= 0) & (xs < W)
        img[ys[ok], xs[ok], :3] = (img[ys[ok], xs[ok], :3] * 0.6).astype(np.uint8)
        blit(img, spr, x, yb - spr.shape[0])
    if sick:
        lights = [(x, 40, 110, .5, (190, 110, 240)) for x in (90, 230, 400, 540)] + \
                 [(320, 130, 170, .55, (255, 200, 80)), (320, 228, 320, .4, (255, 190, 60))]
        img = lighting(img, lights, 0.3, (0.95, 0.9, 1.05))
    else:
        img = light_shaft(img, 250, 70)
        lights = [(x, 40, 120, .4, (255, 150, 70)) for x in (90, 230, 400, 540)] + \
                 [(320, 140, 220, .5, (255, 240, 190))]
        img = lighting(img, lights, 0.5, (0.98, 1.0, 1.02))
    return img


if __name__ == '__main__':
    for st in ('enfermo', 'sano'):
        px.save(render(st), f'out2/z_cripta_{st}.png', scale=2)
