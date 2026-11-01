"""Fondos de combate por región (estilo Pokémon NB: bandas de cielo, horizonte en capas,
plataformas elípticas) y composición de la pantalla de combate a 480x270."""
import numpy as np
from pal import P, h
from px import new, col, blit, ellipse, darker, shade
import ui
import font

W, H = 640, 360


def bands(img, y0, y1, colors, dither=True):
    """Bandas de cielo con una fila tramada entre cada par: el degradado del pixel art."""
    n = len(colors)
    hgt = y1 - y0
    for y in range(y0, y1):
        t = (y - y0) / hgt * (n - 1)
        i = int(t)
        f = t - i
        c0 = colors[min(i, n - 1)]
        c1 = colors[min(i + 1, n - 1)]
        for x in range(W):
            use1 = dither and f > 0.66 and ((x + y) % 2 == 0)
            use1 = use1 or (dither and f > 0.85)
            img[y, x] = col(c1 if use1 else c0)


def hills(img, base_y, amp, period, phase, color, top=None):
    xs = np.arange(W)
    ys = base_y - amp * (0.6 * np.sin(xs / period + phase) + 0.4 * np.sin(xs / (period * 0.47) + phase * 2.1))
    ys = ys.astype(int)
    for x in range(W):
        img[ys[x]:base_y + 200, x] = col(color)
        if top is not None:
            img[ys[x], x] = col(top)


def treeline(img, base_y, color, light, dark, step=11, size=9, seed=1):
    rng = np.random.default_rng(seed)
    x = -6
    while x < W + 10:
        r = size + rng.integers(-2, 3)
        cy = base_y - r + rng.integers(-2, 3)
        m = ellipse(W, H, x, cy, r * 0.8, r)
        img[m] = col(color)
        # luz en la copa
        ml = ellipse(W, H, x - r * 0.3, cy - r * 0.35, r * 0.4, r * 0.4) & m
        img[ml] = col(light)
        x += step + rng.integers(-2, 3)
    img[base_y:base_y + 3, :] = col(dark)


def burnt_line(img, base_y, color, seed=3):
    rng = np.random.default_rng(seed)
    x = 4
    while x < W:
        hgt = rng.integers(26, 46)
        img[base_y - hgt:base_y, x:x + 3] = col(color)
        # ramas
        for k in range(rng.integers(1, 3)):
            by = base_y - hgt + rng.integers(4, hgt // 2)
            d = rng.choice([-1, 1])
            for j in range(rng.integers(4, 9)):
                xx = x + 1 + d * (j + 1)
                yy = by - j // 2
                if 0 <= xx < W:
                    img[yy, xx] = col(color)
        x += rng.integers(14, 28)


def platform(img, cx, cy, rx, ry, top, rim, under):
    m_under = ellipse(W, H, cx, cy + 3, rx, ry)
    img[m_under] = col(under)
    m = ellipse(W, H, cx, cy, rx, ry)
    img[m] = col(rim)
    m2 = ellipse(W, H, cx, cy + 1, rx - 3, ry - 2)
    img[m2] = col(top)
    # brillo del borde superior
    m3 = ellipse(W, H, cx - rx * 0.15, cy - ry * 0.25, rx * 0.55, ry * 0.35) & m2
    return img


def background(region='bosque', state='enfermo'):
    img = new(W, H)
    if region == 'bosque' and state == 'enfermo':
        bands(img, 0, 200, ['#2b1830', '#3f1d33', '#5c2534', '#83342f', '#ad4f2d', '#d27a37'])
        hills(img, 168, 12, 70, 0.5, '#4a2a35', '#5c3540')
        burnt_line(img, 184, '#2a1a24', 5)
        hills(img, 198, 7, 46, 1.7, '#3a2530')
        burnt_line(img, 206, '#1e141c', 9)
        img[200:, :] = col(P['ash'][2])
        # suelo: vetas de ceniza y brasas
        rng = np.random.default_rng(4)
        for _ in range(260):
            x, y = rng.integers(0, W), rng.integers(202, H)
            img[y, x] = col(P['ash'][1] if rng.random() < 0.6 else P['ash'][3])
        for _ in range(40):
            x, y = rng.integers(0, W), rng.integers(206, H)
            img[y, x] = col(P['fire'][3]);
        # humo
        for _ in range(9):
            cx, cy = rng.integers(0, W), rng.integers(20, 150)
            m = ellipse(W, H, cx, cy, rng.integers(20, 40), rng.integers(4, 7))
            img[m] = np.array([darker(c, -1) if False else c for c in img[m]])
            for (yy, xx) in np.argwhere(m):
                if (xx + yy) % 2 == 0:
                    img[yy, xx] = col('#6e4a4e')
        platform(img, 470, 176, 100, 22, P['ash'][3], P['ash'][4], P['ash'][1])
        platform(img, 160, 268, 130, 26, P['ash'][3], P['ash'][4], P['ash'][1])
    else:
        bands(img, 0, 200, ['#4a8fd9', '#5ea6e6', '#78bdf0', '#98d2f5', '#bde5f8', '#dcf3fb'])
        # nubes
        for cx, cy, r in [(90, 50, 26), (124, 56, 18), (380, 36, 30), (420, 44, 20), (560, 80, 16)]:
            m = ellipse(W, H, cx, cy, r, r * 0.45)
            img[m] = col('#ffffff')
            img[ellipse(W, H, cx + 3, cy + 3, r * 0.9, r * 0.3) & m & ~ellipse(W, H, cx, cy - 1, r, r * 0.45 - 1)] = col('#cfe8f6')
        hills(img, 160, 14, 80, 0.4, '#6fae9e', '#8cc6b0')
        treeline(img, 182, P['leaf'][3], P['leaf'][4], P['leaf'][1], step=12, size=10, seed=2)
        treeline(img, 202, P['leaf'][2], P['leaf'][3], P['leaf'][0], step=10, size=9, seed=6)
        img[202:, :] = col(P['grass'][4])
        rng = np.random.default_rng(4)
        for _ in range(220):
            x, y = rng.integers(0, W - 2), rng.integers(204, H)
            img[y, x] = col(P['grass'][5]); img[y + 1 if y + 1 < H else y, x] = col(P['grass'][3])
        for _ in range(30):
            x, y = rng.integers(0, W), rng.integers(208, H)
            img[y, x] = col(P['flower'][rng.integers(0, 5)])
        platform(img, 470, 176, 100, 22, P['grass'][5], P['grass'][6], P['dirt'][3])
        platform(img, 160, 268, 130, 26, P['grass'][5], P['grass'][6], P['dirt'][3])
    return img


def compose(bg, enemy_sprite=None, party_sprites=(), purified=False, msg=None,
            enemy=('Llama de la Deforestación', 'FUEGO', 152, 180), selected='ECO',
            party=(('Ilan', 116, 120, 30, 30, True, None), ('Bruma', 52, 110, 12, 34, False, 'QUEM.'),
                   ('Coral', 100, 100, 38, 38, False, None))):
    img = bg.copy()
    if enemy_sprite is not None:
        ys, xs = np.where(enemy_sprite[..., 3] > 0)
        enemy_sprite = enemy_sprite[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        eh, ew = enemy_sprite.shape[:2]
        blit(img, enemy_sprite, 470 - ew // 2, 184 - eh)
    # grupo de espaldas, escalado 2x como los sprites traseros de NB; el más cercano delante
    n = len(party_sprites)
    for k, spr in reversed(list(enumerate(party_sprites))):
        sh, sw = spr.shape[:2]
        x = 150 - sw // 2 + (k - (n - 1) / 2) * 70
        y = 276 - sh + (0 if k == 0 else -8)
        blit(img, spr, int(x), int(y))
    blit(img, ui.enemy_plate(enemy[0], enemy[1], enemy[2], enemy[3], purified), 10, 10)
    for i, r in enumerate(party):
        blit(img, ui.party_row(*r, w=176), 456, 196 + i * 27)
    tb = ui.textbox(420, 72)
    blit(img, tb, 6, 282)
    lines = msg or ['¿Qué hará Ilan?']
    for i, l in enumerate(lines):
        ui.text(img, l, 20, 292 + i * 15, P['ink'][1], P['paper'][2])
    for i, lab in enumerate(['LUCHAR', 'ECO', 'BOLSA', 'HUIR']):
        sel = lab == selected
        b = ui.command(lab, sel, w=100, h=30)
        x = 432 + (i % 2) * 104 - (2 if sel else 0)
        y = 284 + (i // 2) * 36 - (2 if sel else 0)
        blit(img, b, x, y)
    return img
