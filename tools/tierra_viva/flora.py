"""Árboles, arbustos, flores y rocas, sanos y enfermos."""
import numpy as np
from pal import P
from px import new, col, shade, ellipse, poly, outline, blit, grid, darker


def clumps_canopy(W, H, circles, ramp, seed=0, light=(-0.6, -0.8)):
    """Copa de racimos al estilo de Minish Cap: cada racimo es una pequeña esfera con
    tres o cuatro tonos, dibujados de atrás (arriba) hacia delante (abajo); el borde
    inferior de cada racimo se separa con el tono más oscuro."""
    img = new(W, H)
    m = np.zeros((H, W), bool)
    yy, xx = np.mgrid[0:H, 0:W]
    lx, ly = light
    ys = [c[1] for c in circles]
    y0, y1 = min(ys), max(ys)
    for cx, cy, r in sorted(circles, key=lambda c: (c[1], -abs(c[0] - W / 2))):
        dx = (xx + 0.5 - cx) / r
        dy = (yy + 0.5 - cy) / (r * 0.9)
        d2 = dx * dx + dy * dy
        inside = d2 <= 1.0
        nz = np.sqrt(np.clip(1 - d2, 0, 1))
        lam = np.clip(-(dx * lx + dy * ly) * 0.8 + nz * 0.5, 0, 1)
        # oclusión: racimos bajos y a la derecha más oscuros
        depth = (cy - y0) / max(1, (y1 - y0))
        occl = 0.25 * depth + 0.12 * ((cx - W / 2) / (W / 2))
        v = lam - occl
        idx = np.where(v > 0.78, 5, np.where(v > 0.52, 4, np.where(v > 0.28, 3, 2)))
        layer = np.zeros((H, W, 4), np.uint8)
        for k in (2, 3, 4, 5):
            layer[inside & (idx == k)] = col(ramp[k])
        # separación: borde inferior/derecho del racimo
        edge = inside & (d2 > 0.72) & ((dy > 0.1) | (dx > 0.55))
        layer[edge] = col(ramp[1])
        img[inside] = layer[inside]
        m |= inside
    # brillo puntual en los racimos superiores
    for cx, cy, r in circles:
        if cy - y0 < (y1 - y0) * 0.5 and r > 5:
            x, y = int(cx - r * 0.4), int(cy - r * 0.45)
            if 0 <= y < H and 0 <= x < W and m[y, x]:
                img[y, x] = col(ramp[6]); img[y, x + 1] = col(ramp[6])
    return img, m


CLUMP_L = [
    '....5555....',
    '..55666554..',
    '.5566665544.',
    '.5666655443.',
    '455665544433',
    '455555444332',
    '445554443322',
    '.4444443322.',
    '.3444333221.',
    '..33332221..',
    '....2111....']
CLUMP_S = [
    '..5555..',
    '.566554.',
    '55665443',
    '45554433',
    '44444332',
    '.344332.',
    '..3322..',
    '...11...']


def canopy(W, H, placements, ramp, shift=1):
    img = new(W, H)
    cm = {str(i): ramp[max(1, i - shift)] for i in range(len(ramp))}
    for kind, x, y in placements:
        blit(img, grid(CLUMP_L if kind == 'L' else CLUMP_S, cm), x, y)
    return img


def tree(state='sano', seed=0):
    W, H = 32, 37
    img = new(W, H)
    if state == 'sano':
        ramp = P['leaf']
        trunk = P['wood']
        place = [('L', 10, 0), ('S', 4, 5), ('S', 20, 5), ('L', 3, 7), ('L', 17, 7),
                 ('L', 10, 9), ('S', 1, 14), ('S', 23, 14), ('L', 5, 15), ('L', 15, 15), ('S', 12, 20)]
        can = canopy(W, 30, place, ramp)
        tr = grid([
            '...tTTuuTt...',
            '...tTTuuTt...',
            '....tTuTt....',
            '....tTuTt....',
            '....tTuuT....',
            '....tTuuT....',
            '...ttTuuTt...',
            '..tt.tTTt.tt.',
        ], {'t': trunk[1], 'T': trunk[2], 'u': trunk[3]})
        blit(img, tr, 10, 27)
        blit(img, can, 0, 0)
        img = outline(img, color=P['leaf'][0])
    else:
        # Árbol quemado: tronco y ramas desnudas, carbón con grietas de brasa.
        ramp = P['ash']
        rows = [
            '..........o.......o.............',
            '..........ao.....oa.......o.....',
            '...o.......ao...oa.......oa.....',
            '...ao.......a..oa.......oa......',
            '....ao......aooa.......oa.......',
            '.....aa.....aaaa......oa........',
            '......aa....aaba.....aa.........',
            '.......aa...abba....aa..........',
            '........aaa.abba..aaa...........',
            '..........aaabbaaaa.............',
            '............abbba...............',
            '............abeba...............',
            '............abbba...............',
            '............aabba...............',
            '............abbeba..............',
            '...........aabbbba..............',
            '...........abbbbba..............',
            '...........abebbba..............',
            '...........abbbbbaa.............',
            '..........aabbbbbba.............',
            '.........aaabbbbbbaa............',
            '........aa..abbbba.aa...........',
            '.......a.....aaaa....a..........',
        ]
        cm = {'a': P['ash'][1], 'b': P['ash'][2], 'o': P['ash'][3], 'e': P['fire'][3]}
        g = grid(rows, cm)
        blit(img, g, 0, 16)
        img = outline(img, color=P['ink'][0])
    return img


def bush(state='sano', seed=1):
    W, H = 16, 14
    ramp = P['leaf'] if state == 'sano' else P['deadleaf']
    circles = [(8, 8, 6), (4.5, 9, 4), (11.5, 9, 4), (8, 5, 4)]
    can, m = clumps_canopy(W, H, circles, ramp if state == 'sano' else ramp + [ramp[-1]], seed)
    img = new(W, H)
    blit(img, can, 0, 0)
    if state == 'sano':
        for x, y in [(5, 7), (10, 9)]:
            img[y, x] = col(P['flower'][1]); img[y - 1, x] = col(P['flower'][2])
    return outline(img)


def flowers(kind=0):
    t = new(16, 16)
    cols = [(P['flower'][1], P['flower'][2]), (P['flower'][3], P['flower'][4]), (P['flower'][5], P['flower'][6])][kind % 3]
    for x, y in [(3, 3), (10, 5), (6, 10), (12, 12)]:
        blit(t, grid(['.a.', 'aca', '.a.', '.g.'], {'a': cols[0], 'c': cols[1], 'g': P['grass'][2]}), x, y)
    return t


def rock(state='sano'):
    W, H = 16, 13
    m = ellipse(W, H, 8, 7.5, 7, 5.5) | ellipse(W, H, 6, 6, 5, 4.5)
    r = P['stone'] if state == 'sano' else P['ash']
    img = shade(m, r[1:6], ambient=0.15)
    img[7, 5] = col(r[2]); img[8, 6] = col(r[2]); img[8, 10] = col(r[2])
    return outline(img)


CLUMP_XL = [
    '.....55555.....',
    '...556666554...',
    '..55666666554..',
    '.5566666655544.',
    '.5666666555444.',
    '556666655554443',
    '555666555544433',
    '455555555444333',
    '445555544443332',
    '.44444444333332',
    '.34444433333322',
    '..333333332222.',
    '...2223322221..',
    '.....111111....']


def big_tree(state='sano', seed=0):
    """Árbol grande para personajes de 48 px: 64 de ancho, copa de racimos en tres pisos."""
    W, H = 64, 78
    img = new(W, H)
    rng = np.random.default_rng(seed)
    if state == 'sano':
        ramp = P['leaf']
        trunk = P['wood']
        # tronco con raíces
        tr = grid([
            '.....tTTuuuTTt.....',
            '.....tTTuuuTTt.....',
            '.....tTTuuTTTt.....',
            '......tTuuTTt......',
            '......tTuuTTt......',
            '......tTTuTTt......',
            '.....ttTTuTTtt.....',
            '....tTTTTuTTTTt....',
            '...tTTt.tTTt.tTTt..',
            '..tTt...tTt....tTt.',
            '..tt....tt......tt.',
        ], {'t': trunk[1], 'T': trunk[2], 'u': trunk[3]})
        blit(img, tr, 23, 60)
        cm = {str(i): ramp[max(1, i - 1)] for i in range(len(ramp))}
        place = [  # (plantilla, x, y) de atrás hacia delante
            ('XL', 24, 0), ('L', 14, 4), ('L', 38, 4), ('XL', 7, 11), ('XL', 41, 11), ('L', 26, 9),
            ('XL', 18, 16), ('XL', 32, 16), ('L', 2, 24), ('L', 50, 24), ('XL', 9, 27), ('XL', 39, 27),
            ('XL', 24, 30), ('L', 15, 40), ('L', 36, 40), ('L', 26, 45)]
        for kind, x, y in place:
            blit(img, grid(CLUMP_XL if kind == 'XL' else CLUMP_L, cm), x, y)
        # brillos sueltos y algún fruto
        for _ in range(6):
            y, x = rng.integers(4, 30), rng.integers(10, 54)
            if img[y, x, 3] and img[y + 1, x, 3]:
                img[y, x] = col(ramp[6])
        img = outline(img, color=P['leaf'][0])
    else:
        ash, fire = P['ash'], P['fire']
        rows = [
            '..........o.................o..........',
            '.........oa.......o........ao..........',
            '..o......a.......oa.......aa.......o...',
            '..ao.....a......oa.......aa.......oa...',
            '...ao....aa.....a.......aa.......oa....',
            '....aa....a.....a......aa.......aa.....',
            '.....aa...aa....aa....aa.......aa......',
            '......aa...a.....a...aa......aaa.......',
            '.......aa..aa....aa.aa......aa.........',
            '........aaaaaa...abba......aa..........',
            '..........aaabaaabbbaa...aaa...........',
            '.............aabbbbbbaaaa..............',
            '...............abbebba.................',
            '...............abbbbba.................',
            '...............abbebba.................',
            '..............aabbbbbba................',
            '..............abbbbebba................',
            '..............abbbbbbba................',
            '..............abebbbbba................',
            '.............aabbbbbbbaa...............',
            '.............abbbbbbebba...............',
            '............aabbbbbbbbbaa..............',
            '...........aaabbbbebbbbaaa.............',
            '..........aa..abbbbbbba..aa............',
            '.........a....aabbbbbaa....a...........',
            '..............a.aaaaa.a................',
        ]
        g = grid(rows, {'a': ash[1], 'b': ash[2], 'o': ash[3], 'e': fire[3]})
        # escalar el esqueleto a 64 de ancho no se hace: se centra
        blit(img, g, 12, 50)
        img = outline(img, color=P['ink'][0])
    return img
