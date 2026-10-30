"""Texturas de terreno 16x16, enlosables, en estado sano y enfermo."""
import numpy as np
from pal import P
from px import new, col, grid

T = 16


def fill(c):
    t = new(T, T)
    t[:] = col(c)
    return t


def stamp(t, motif, x, y, cmap):
    """Pega un motivo de caracteres con envoltura (la textura sigue siendo enlosable)."""
    for j, row in enumerate(motif):
        for i, ch in enumerate(row):
            if ch in '. ':
                continue
            t[(y + j) % T, (x + i) % T] = col(cmap[ch])
    return t


TUFT = ['.l...',
        'ld.l.',
        '.dld.',
        '..d..']
TUFT2 = ['..l.',
         '.ldl',
         'ld..',
         '.d..']
DOT = ['l', 'd']
LF = ['h.', '.l']


def grass(state='sano', variant=0):
    r = P['grass'] if state == 'sano' else P['drygrass']
    if state == 'enfermo':
        # suelo quemado: hierba seca oscurecida, con calvas de ceniza
        t = fill(r[2])
        cm = {'d': r[1], 'l': r[3], 'D': r[0], 'h': r[4]}
    else:
        t = fill(r[4])
        cm = {'d': r[3], 'l': r[5], 'D': r[2], 'h': r[6]}
    spots = [
        [(2, 2, TUFT), (10, 9, TUFT2), (12, 1, DOT), (5, 12, DOT), (8, 5, DOT), (14, 14, LF)],
        [(9, 3, TUFT), (1, 10, TUFT2), (6, 7, DOT), (14, 13, DOT), (3, 1, LF), (12, 12, DOT)],
        [(4, 5, TUFT2), (11, 11, TUFT), (13, 4, DOT), (1, 1, DOT), (7, 13, LF)],
        [(6, 1, DOT), (2, 9, DOT), (12, 6, DOT), (9, 13, DOT), (14, 1, LF), (4, 5, LF)],
    ][variant % 4]
    for x, y, m in spots:
        stamp(t, m, x, y, cm)
    if state != 'sano':
        # Calvas de tierra seca y hojas muertas.
        stamp(t, ['.ee.', 'eeee', '.ee.'], (variant * 5 + 7) % 16, (variant * 3 + 6) % 16,
              {'e': P['ash'][2]})
    return t


def tallgrass(state='sano', frame=0):
    r = P['grass'] if state == 'sano' else P['drygrass']
    rows = [
        '.h......h.......',
        'hlh....hlh......',
        'llh.h..llh.h....',
        'lldhlh.lldhlh.h.',
        'dlllld.dlllldhlh',
        'Ddlldd.DdlllDlld',
        'DDddDD.DDddDDdld',
        '..h..DDD..h..DdD',
        '.hlh....h.hlh...',
        '.llh.h.hlhllh.h.',
        'hlldhlhllhlldhlh',
        'llllllddlllllldl',
        'dlllllDDdllllllD',
        'DdlldDDDDdlldDDD',
        'DDddDDDDDDddDDDD',
        'DDDDDDDDDDDDDDDD']
    if frame:
        rows = [r_[1:] + r_[:1] if i < 7 else r_ for i, r_ in enumerate(rows)]
    t = fill(r[4])
    from px import blit
    blit(t, grid(rows, {'h': r[6], 'l': r[5], 'd': r[3], 'D': r[2]}), 0, 0)
    return t


def dirt(state='sano', variant=0):
    r = P['dirt'] if state == 'sano' else P['rust'] if state == 'oxido' else P['ash']
    base = r[4] if state == 'sano' else r[3]
    t = fill(base)
    cm = {'d': r[3] if state == 'sano' else r[2], 'l': r[5] if state == 'sano' else r[4],
          'D': r[2] if state == 'sano' else r[1]}
    pebble = ['.l.', 'ldD', '.D.']
    crack = ['d..', '.d.', '.dd']
    spots = [[(3, 3, pebble), (11, 10, ['ld', 'dD']), (7, 13, ['d']), (13, 2, ['d']), (1, 9, ['l'])],
             [(9, 4, pebble), (2, 11, ['ld', 'dD']), (13, 13, ['d']), (5, 1, ['d']), (14, 8, ['l'])]][variant % 2]
    for x, y, m in spots:
        stamp(t, m, x, y, cm)
    if state != 'sano':
        stamp(t, crack, (variant * 7 + 6) % 16, (variant * 5 + 5) % 16, cm)
    return t


def sand(variant=0, state='sano'):
    r = P['sand'] if state == 'sano' else [P['ash'][2], P['ash'][3], P['ash'][4], P['ash'][4], P['ash'][5]]
    t = fill(r[3])
    cm = {'d': r[2], 'l': r[4], 'D': r[1]}
    for x, y, m in [[(2, 3, ['d.d']), (9, 9, ['l']), (12, 2, ['d']), (5, 12, ['dl'])],
                    [(10, 4, ['d.d']), (3, 10, ['l']), (14, 13, ['d']), (7, 7, ['ld'])]][variant % 2]:
        stamp(t, m, x, y, cm)
    return t


def water(state='sano', frame=0):
    if state == 'sano':
        r = P['water']
        t = fill(r[3])
        cm = {'l': r[4], 'h': r[5], 'd': r[2]}
        waves = [(2, 3, ['.ll.', 'l..l']), (10, 10, ['.hl.', 'l..l']), (11, 2, ['ll'])]
    elif state == 'oil':
        r = P['oil']
        t = fill(r[2])
        cm = {'l': P['sheen'][0], 'h': P['sheen'][1], 'd': r[1]}
        waves = [(2, 3, ['.ll.', 'h..h']), (10, 10, ['.lh.', 'l..l']), (11, 2, ['hl'])]
    else:
        # agua turbia de ceniza: gris verdosa, con espuma sucia
        t = fill('#4a5452')
        cm = {'l': '#626b66', 'h': '#7d8078', 'd': '#3a4241'}
        waves = [(2, 3, ['.ll.', 'l..l']), (10, 10, ['.hl.', 'l..l']), (11, 2, ['ll'])]
    for x, y, m in waves:
        stamp(t, m, x + frame * 2, y, cm)
    stamp(t, ['dd'], 6 + frame, 7, cm)
    stamp(t, ['d'], 14, 14, cm)
    return t


def ash_ground(variant=0):
    r = P['ash']
    t = fill(r[2])
    cm = {'d': r[1], 'l': r[3], 'e': P['fire'][3], 'E': P['fire'][4]}
    for x, y, m in [[(3, 2, ['l.l', '.d.']), (10, 9, ['dd']), (12, 3, ['e']), (6, 12, ['l']), (1, 8, ['d'])],
                    [(9, 4, ['l.l', '.d.']), (2, 11, ['dd']), (5, 5, ['E']), (13, 12, ['l']), (14, 1, ['d'])]][variant % 2]:
        stamp(t, m, x, y, cm)
    return t


def tallgrass_overlay(state='sano'):
    r = P['grass'] if state == 'sano' else P['drygrass']
    rows = [
        '..h.......h.....',
        '.hlh..h..hlh..h.',
        '.llh.hlh.llh.hlh',
        'hlldhllh.lldhllh',
        'lllldlllhlllldll',
        'dlllddllllllddll',
        'DdllDdlldDllDdld',
        'DDddDDddDDdDDDdD',
        '..h..DDh..h.DDhD',
        '.hlh.hlh.hlh.hlh',
        'hlldhlldhlldhlld',
        'llllllllllllllll',
        'dlllldlllldllldl',
        'DdllDDdlDdllDDdl',
        'DDddDDDdDDddDDDd',
        'DDDDDDDDDDDDDDDD']
    return grid(rows, {'h': r[6], 'l': r[5], 'd': r[3], 'D': r[2]})
