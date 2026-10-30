"""HUD del combate de acción en el mapa «Tierra Viva».

Se pelea en el mismo mapa, en tiempo real, como en Minish Cap o Link's
Awakening. Manejas a un héroe y cambias de héroe con Q/E; cada uno lleva la
habilidad ecológica que ataja una causa. La bolsa no se abre en un menú que
pare el juego: está siempre a la vista en una barra rápida (1-4).

Piezas:
  hero_card     arriba a la izquierda: retrato, nombre, PV y energía.
  party_strip   bajo la tarjeta: los otros cuatro, con su PV y su causa.
  quickbar      abajo a la izquierda: la bolsa, cuatro huecos con cantidad.
  action_pad    abajo a la derecha: atacar, esquivar, eco y objeto, en rombo.
  nameplate     flotando sobre el monstruo: nombre, PV y si está purificado.
  toast         aviso breve arriba en el centro, en papel.
"""
import numpy as np
from PIL import Image
from pal import P
from px import new, col, blit, grid, ellipse, outline
import ui
import font

INK = P['ink'][0]


def g(rows, cmap):
    return grid(rows, cmap)


# --- iconos 12x12 -------------------------------------------------------------

def icon(name):
    if name == 'espada':
        return outline(g([
            "..........hh",
            ".........hlh",
            "........hlh.",
            ".......hlh..",
            "......hlh...",
            ".....hlh....",
            ".gg.hlh.....",
            "..gglh......",
            "...gg.......",
            "..wgwg......",
            ".ww..gg.....",
            "ww..........",
        ], {'h': P['stone'][6], 'l': P['stone'][4], 'g': P['gold'][3], 'w': P['wood'][3]}))
    if name == 'bota':
        return outline(g([
            "...bbbb.....",
            "...bccb.....",
            "...bccb.....",
            "...bccb.....",
            "...bccb.....",
            "..bbccbb....",
            "..bcccccb...",
            ".bcccccccbb.",
            ".bccccccccb.",
            ".dddddddddd.",
            "............",
            "............",
        ], {'b': P['wood'][1], 'c': P['wood'][3], 'd': P['wood'][0]}))
    if name == 'hoja':
        return outline(g([
            "........eee.",
            "......eeffe.",
            "....eeffffe.",
            "...efffffe..",
            "..effffhe...",
            "..efffhfe...",
            ".effhhffe...",
            ".efhffee....",
            ".ehfee......",
            ".hee........",
            "h...........",
            "............",
        ], {'e': P['eco'][1], 'f': P['eco'][3], 'h': P['eco'][5]}))
    if name == 'hierba':      # Hierba de Valdehoja
        return outline(g([
            "....g..g....",
            "...glg.lg...",
            "..gllgglg.g.",
            "..glllgllglg",
            "...gllglllg.",
            "....gglllg..",
            "......gg....",
            "...wwwwwww..",
            "..wbbbbbbbw.",
            "..wbbbbbbbw.",
            "...wbbbbbw..",
            "....wwwww...",
        ], {'g': P['grass'][2], 'l': P['grass'][5], 'w': P['wood'][1], 'b': P['wood'][3]}))
    if name == 'agua':        # Agua Purificada
        return outline(g([
            "....cccc....",
            "....cddc....",
            ".....cc.....",
            "....cwwc....",
            "...cwwwwc...",
            "..cwwhwwwc..",
            "..cwhwwwwc..",
            "..cbbbbbbc..",
            "..cbbbbbbc..",
            "..cbbbbbbc..",
            "...cbbbbc...",
            "....cccc....",
        ], {'c': P['ui'][4], 'd': P['wood'][2], 'w': P['ui'][5], 'h': P['ui'][6], 'b': P['water'][4]}))
    if name == 'antidoto':
        return outline(g([
            "....dddd....",
            "....d..d....",
            "...dppppd...",
            "..dppppppd..",
            "..dpphppppd.",
            ".dpphpppppd.",
            ".dppppppppd.",
            ".dpppppppd..",
            "..dppppppd..",
            "...dddddd...",
            "............",
            "............",
        ], {'d': P['ink'][1], 'p': P['flower'][5], 'h': P['flower'][6]}))
    if name == 'racion':
        return outline(g([
            "............",
            "..bbbbbbbb..",
            ".bccccccccb.",
            ".bcrrcccccb.",
            ".bccccccccb.",
            ".dddddddddd.",
            ".bccccccccb.",
            ".bccccrrccb.",
            ".bccccccccb.",
            "..bbbbbbbb..",
            "............",
            "............",
        ], {'b': P['wood'][2], 'c': P['sand'][3], 'r': P['roofr'][3], 'd': P['wood'][1]}))
    raise KeyError(name)


# --- piezas ---------------------------------------------------------------------

def slate(w, h, active=False):
    return ui.box(w, h, P['ui'][1], INK, inner=P['gold'][4] if active else P['ui'][2],
                  hi=P['ui'][2], radius=3)


def portrait(name, size=28):
    a = np.array(Image.open(f'final/chars/{name}_south.png'))
    ys, xs = np.where(a[..., 3] > 0)
    cx = (xs.min() + xs.max()) // 2
    crop = a[ys.min():ys.min() + size - 4, max(0, cx - (size - 4) // 2):max(0, cx - (size - 4) // 2) + size - 4]
    img = ui.box(size, size, P['ui'][0], INK, inner=P['ui'][2], radius=2)
    blit(img, crop, 2, 2)
    return img


ECO_OF = {'ilan': ('DESHIELO', 'Escudo de Albedo', 7), 'bruma': ('FUEGO', 'Línea Cortafuegos', 6),
          'coral': ('PETRÓLEO', 'Barrera Absorbente', 6), 'nix': ('PLÁSTICO', 'Separación en la Fuente', 6),
          'suri': ('MONOCULTIVO', 'Rotación de Cultivos', 6)}


def hero_card(name, hp, mx, en, emax):
    W, H = 168, 40
    img = slate(W, H)
    blit(img, portrait(name.lower(), 32), 4, 4)
    ui.text(img, name, 41, 3, P['gold'][5], P['ui'][0])
    b = ui.badge(ECO_OF[name.lower()][0])
    blit(img, b, W - b.shape[1] - 6, 5)
    ui.text(img, 'PV', 41, 16, P['gold'][4], P['ui'][0])
    t = f'{hp}/{mx}'
    blit(img, ui.bar(W - 41 - 16 - font.width(t) - 10, hp / mx), 55, 20)
    ui.text(img, t, W - font.width(t) - 6, 16, P['ui'][5], P['ui'][0])
    ui.text(img, 'EN', 41, 26, P['eco'][4], P['ui'][0])
    blit(img, ui.bar(W - 41 - 16 - 10, en / emax, 'en'), 55, 30)
    return img


def party_strip(members, keys=('Q', 'E')):
    """members: [(nombre, ratio_pv)] de los que esperan turno."""
    W = 8 + len(members) * 26 + 34
    img = new(W, 30)
    kq = key_chip(keys[0]); blit(img, kq, 0, 8)
    x = kq.shape[1] + 3
    for n, r in members:
        p = portrait(n, 22)
        blit(img, p, x, 0)
        blit(img, ui.bar(22, r), x, 24)
        ramp, i = ui.TYPE[ECO_OF[n][0]]
        img[2:5, x + 17:x + 20] = col(P[ramp][i]); img[1, x + 17:x + 20] = col(INK)
        x += 25
    blit(img, key_chip(keys[1]), x + 1, 8)
    return img


def key_chip(k):
    w = max(11, font.width(k) + 6)
    img = ui.box(w, 12, P['paper'][4], INK, inner=P['paper'][2], radius=1)
    img[10, 1:w - 1] = col(P['paper'][1])
    ui.text(img, k, (w - font.width(k)) // 2, -1, P['ink'][1])
    return img


def slot(ic, count=None, key=None, active=False, size=26, disabled=False):
    img = ui.box(size, size, P['ui'][1] if not active else P['ui'][2], INK,
                 inner=P['gold'][4] if active else P['ui'][2], radius=2)
    if ic is not None:
        blit(img, ic, (size - ic.shape[1]) // 2, (size - ic.shape[0]) // 2 - 1)
    if disabled:
        m = img[..., 3] > 0
        img[m & ((np.indices(m.shape).sum(0)) % 2 == 0)] = col(P['ui'][1])
    if count is not None:
        t = f'{count}'
        ui.text(img, t, size - font.width(t) - 3, size - 13, P['ui'][6], INK)
    out = new(size + 4, size + 8)
    blit(out, img, 0, 0)
    if key:
        kc = key_chip(key)
        blit(out, kc, (size - kc.shape[1]) // 2, size - 4)
    return out


def quickbar(items, active=0):
    """items: [(icono, cantidad)] — la bolsa, siempre a la vista."""
    img = new(len(items) * 30 + 44, 46)
    lab = 'BOLSA'
    ui.text(img, lab, 0, 0, P['gold'][5], INK)
    for i, (ic, n) in enumerate(items):
        blit(img, slot(icon(ic), n, str(i + 1), i == active), i * 30, 12)
    return img


def round_button(ic, ramp, key, label=None, r=14, cost=None, ready=True):
    d = r * 2 + 2
    img = new(d + 2, d + 12)
    m = ellipse(d, d, r + 1, r + 1, r, r)
    face = new(d, d)
    rp = P[ramp]
    face[m] = col(rp[2] if ready else P['ui'][2])
    inner = ellipse(d, d, r + 1, r, r - 2, r - 2)
    face[inner] = col(rp[3] if ready else P['ui'][2])
    hi = ellipse(d, d, r - 2, r - 4, r * 0.45, r * 0.3) & inner
    face[hi] = col(rp[4] if ready else P['ui'][3])
    ring = m & ~ellipse(d, d, r + 1, r + 1, r - 1, r - 1)
    face[ring] = col(INK)
    face[m & (np.indices(m.shape)[0] > r + r * 0.6) & ~ring] = col(rp[1] if ready else P['ui'][1])
    blit(face, ic, r + 1 - ic.shape[1] // 2, r + 1 - ic.shape[0] // 2)
    blit(img, face, 1, 0)
    kc = key_chip(key)
    blit(img, kc, d - kc.shape[1] + 3, d - 10)
    if cost is not None:
        cc = ui.box(font.width(str(cost)) + 6, 11, P['eco'][1], INK, radius=1)
        ui.text(cc, str(cost), 3, -1, P['eco'][5])
        blit(img, cc, -1, d - 9)
    return img


def action_pad(eco_ready=True, eco_cost=6, item_icon='hierba'):
    W, H = 104, 98
    img = new(W, H)
    pads = [
        ('bolsa', round_button(icon(item_icon), 'gold', 'V'), 36, 0),
        ('eco', round_button(icon('hoja'), 'eco', 'C', cost=eco_cost, ready=eco_ready), 0, 30),
        ('atacar', round_button(icon('espada'), 'rust', 'Z'), 72, 30),
        ('esquivar', round_button(icon('bota'), 'roofb', 'X'), 36, 58),
    ]
    for _, b, x, y in pads:
        blit(img, b, x, y)
    return img


def nameplate(name, typ, hp, mx, purified=False, hint=None):
    tw = font.width(name)
    W = max(tw + 12, 104)
    img = ui.box(W, 30 if not hint else 30, P['ui'][1], INK, inner=P['ui'][2], radius=2)
    ui.text(img, name, (W - tw) // 2, 1, P['ui'][6], P['ui'][0])
    st = 'PURIFICADO' if purified else 'SE REHACE'
    sb = ui.box(font.width(st) + 6, 11, P['eco'][1] if purified else P['rust'][1], INK, radius=1)
    ui.text(sb, st, 3, -1, P['eco'][4] if purified else P['paper'][4])
    b = ui.badge(typ)
    x0 = (W - b.shape[1] - sb.shape[1] - 3) // 2
    blit(img, b, x0, 13); blit(img, sb, x0 + b.shape[1] + 3, 13)
    out = new(W, 38)
    blit(out, img, 0, 0)
    blit(out, ui.bar(W - 8, hp / mx), 4, 31)
    return out


def toast(lines, w=300):
    h = 10 + 14 * len(lines)
    img = ui.textbox(w, h)
    for i, l in enumerate(lines):
        if isinstance(l, (tuple, list)):
            x = 14
            for seg, c in l:
                ui.text(img, seg, x, 4 + i * 14, c, P['paper'][2])
                x += font.width(seg) + 3
        else:
            ui.text(img, l, 14, 4 + i * 14, P['ink'][1], P['paper'][2])
    return img


def dmg(text, color, shadow=INK):
    t = font.render(text, color, shadow)
    # doble tamaño para las cifras: se leen a la carrera
    return np.kron(t, np.ones((2, 2, 1), np.uint8))


def slash(r=30, start=-70, end=70, thick=7):
    """Tajo en media luna, de blanco a oro, para el golpe de espada."""
    d = r * 2 + 4
    img = new(d, d)
    yy, xx = np.indices((d, d))
    cx = cy = d / 2
    ang = np.degrees(np.arctan2(yy - cy, xx - cx))
    dist = np.hypot(xx - cx, yy - cy)
    span = (ang >= start) & (ang <= end)
    t = (ang - start) / (end - start)
    w = thick * np.sin(np.pi * np.clip(t, 0, 1))
    band = span & (dist <= r) & (dist >= r - w)
    img[band] = col(P['gold'][4])
    img[band & (dist >= r - w * 0.55)] = col(P['gold'][5])
    img[band & (dist >= r - 1.5)] = col(P['ui'][6])
    return img


def spark(n=9):
    img = new(n, n)
    c = n // 2
    img[c, :] = col(P['gold'][5]); img[:, c] = col(P['gold'][5])
    img[c, c] = col(P['ui'][6])
    for k in (1, 2):
        img[c - k, c - k] = col(P['gold'][4]); img[c + k, c + k] = col(P['gold'][4])
        img[c - k, c + k] = col(P['gold'][4]); img[c + k, c - k] = col(P['gold'][4])
    return img
