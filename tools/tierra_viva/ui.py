"""Piezas de interfaz «Tierra Viva»: cajas, botones de mando, placas de combate,
barras de PV/energía, cartel de lugar. Todo en píxel entero con la paleta."""
import numpy as np
from pal import P
from px import new, col, blit, grid
import font

INK = P['ink'][0]


def box(w, h, fill, border, inner=None, hi=None, radius=2, border_w=1):
    """Caja con esquinas recortadas en escalera (radio en píxeles)."""
    img = new(w, h)
    img[:] = 0
    cut = {1: [1], 2: [2, 1], 3: [3, 1, 1]}[radius]
    def inside(x, y, shrink=0):
        if x < shrink or y < shrink or x >= w - shrink or y >= h - shrink:
            return False
        for i, c in enumerate(cut):
            for (yy, side_y) in ((y, shrink + i), (h - 1 - y, shrink + i)):
                if yy == side_y:
                    if x < shrink + c or x > w - 1 - shrink - c:
                        return False
        return True
    for y in range(h):
        for x in range(w):
            if inside(x, y):
                img[y, x] = col(border)
                if inside(x, y, border_w):
                    img[y, x] = col(inner if inner is not None else fill)
                    if inner is None or inside(x, y, border_w + 1):
                        img[y, x] = col(fill)
    if hi is not None:
        for x in range(w):
            for y in range(h):
                if inside(x, y, border_w + (1 if inner is not None else 0)) and not inside(x, y - 1, border_w + (1 if inner is not None else 0)):
                    img[y, x] = col(hi)
    return img


def text(img, s, x, y, color, shadow=None):
    blit(img, font.render(s, color, shadow), x, y)
    return font.width(s)


def bar(w, ratio, kind='hp'):
    """Barra de 4 px: marco oscuro, pista, relleno con brillo superior."""
    img = new(w, 5)
    img[:] = col(P['ui'][0])
    img[1:4, 1:w - 1] = col(P['ui'][1])
    fill_w = max(0, round((w - 2) * ratio))
    if kind == 'hp':
        if ratio > 0.5:
            c, l = P['hp'][1], P['hp'][2]
        elif ratio > 0.2:
            c, l = P['hp'][4], P['gold'][5]
        else:
            c, l = P['hp'][6], P['flower'][2]
    else:
        c, l = P['eco'][3], P['eco'][4]
    if fill_w:
        img[1:4, 1:1 + fill_w] = col(c)
        img[1, 1:1 + fill_w] = col(l)
    return img


TYPE = {
    'FUEGO': ('fire', 2), 'PETRÓLEO': ('sheen', 0), 'PLÁSTICO': ('plastic', 0),
    'MONOCULTIVO': ('drygrass', 3), 'DESHIELO': ('ice', 1), 'AVARICIA': ('gold', 1),
    'ECO': ('eco', 1),
}
CMD_FILL = {'LUCHAR': 2, 'ECO': 1, 'BOLSA': 1, 'HUIR': 2}


def badge(label):
    ramp, i = TYPE.get(label, ('stone', 3))
    c = P[ramp][i]
    w = font.width(label) + 6
    img = box(w, 11, c, P['ink'][0], radius=1)
    text(img, label, 3, -1, P['ui'][6])
    return img


def plate(w, h):
    return box(w, h, P['ui'][1], P['ink'][0], inner=P['ui'][2], hi=P['ui'][2], radius=3)


def enemy_plate(name, typ, hp, mx, purified=False):
    W = 184
    img = plate(W, 46)
    text(img, name, 8, 3, P['ui'][6], P['ui'][0])
    x = 8
    b = badge(typ); blit(img, b, x, 17); x += b.shape[1] + 3
    st = 'PURIFICADO' if purified else 'CORRUPTO'
    sb = box(font.width(st) + 6, 11, P['eco'][1] if purified else P['rust'][1], P['ink'][0], radius=1)
    text(sb, st, 3, -1, P['eco'][4] if purified else P['paper'][4])
    blit(img, sb, x, 17)
    text(img, 'PV', 8, 30, P['gold'][4], P['ui'][0])
    t = f'{hp}/{mx}'
    tw = font.width(t)
    blit(img, bar(W - 8 - 24 - tw - 6, hp / mx), 22, 34)
    text(img, t, W - tw - 8, 30, P['ui'][5], P['ui'][0])
    return img


def party_row(name, hp, mx, en, emax, active=False, status=None, w=150):
    img = box(w, 25, P['ui'][1] if not active else P['ui'][2], P['ink'][0],
              inner=P['ui'][2] if not active else P['gold'][4], radius=2)
    tc = P['gold'][5] if active else P['ui'][6]
    text(img, name, 6, 2, tc, P['ui'][0])
    if status:
        s = box(font.width(status) + 6, 11, P['rust'][2], P['ink'][0], radius=1)
        text(s, status, 3, -1, P['ui'][6])
        blit(img, s, 6 + font.width(name) + 4, 3)
    t = f'{hp}/{mx}'
    text(img, t, w - font.width(t) - 6, 2, P['ui'][5], P['ui'][0])
    blit(img, bar(w - 12, hp / mx), 6, 15)
    blit(img, bar(w - 12, en / emax, 'en')[1:], 6, 19)
    return img


def textbox(w, h):
    img = box(w, h, P['paper'][4], P['wood'][1], inner=P['paper'][2], radius=3, border_w=2)
    # hojita en la esquina: el eco
    blit(img, grid(['.gg', 'ggG', 'Gg.'], {'g': P['eco'][3], 'G': P['eco'][1]}), 3, 3)
    return img


CMD = {'LUCHAR': 'rust', 'ECO': 'eco', 'BOLSA': 'gold', 'HUIR': 'roofb'}


def command(label, selected=False, w=78, h=26):
    ramp = P[CMD[label]]
    f = CMD_FILL[label]
    img = box(w, h, ramp[f], P['ink'][0], inner=ramp[f - 1], hi=ramp[f + 1], radius=3)
    # base más oscura: botón con canto
    for x in range(3, w - 3):
        img[h - 3, x] = col(ramp[0])
    if selected:
        sel = box(w + 4, h + 4, P['ui'][6], P['ink'][0], radius=3)
        sel[2:h + 2, 2:w + 2][img[..., 3] > 0] = img[img[..., 3] > 0]
        img = sel
        off = 2
    else:
        off = 0
    tw = font.width(label)
    text(img, label, off + (w - tw) // 2, off + (h - 13) // 2, P['ui'][6], ramp[0])
    return img


def sign(label, sub=None):
    tw = max(font.width(label), font.width(sub) if sub else 0)
    w, h = tw + 24, 22 if not sub else 34
    img = box(w, h, P['wood'][4], P['wood'][0], inner=P['wood'][2], hi=P['wood'][5], radius=2)
    # clavos
    for x, y in ((4, 4), (w - 5, 4), (4, h - 5), (w - 5, h - 5)):
        img[y, x] = col(P['stone'][5])
    text(img, label, (w - font.width(label)) // 2, 4, P['paper'][4], P['wood'][1])
    if sub:
        text(img, sub, (w - font.width(sub)) // 2, 17, P['paper'][3], P['wood'][1])
    return img
