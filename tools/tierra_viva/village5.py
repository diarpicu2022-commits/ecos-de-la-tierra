"""Valdehoja orgánica.

Las calles serpentean y cada casa se coloca a su aire: unas más adelante y
otras más atrás de la calle (con su senda propia hasta la puerta), con huecos
distintos entre vecinas, algunas en segunda fila detrás de otras y patios que
no se repiten (valla, seto, huerto o nada). Se valida que nada se pise.
"""
import numpy as np
from PIL import Image
import maps2, scene2, px, scene
import buildings as B
from scene2 import bld, ashen, fence, yard, ring_planter, foot_x, fruit_tree, hay, cart, laundry, boat, crate_fish, sign, bush2, solve_trees, roof_variant, TREE, BURNT

W, H, T = 90, 64, 16
RNG_SEED = 7

# calles: nombre -> (fila base, amplitud, fase, col ini, col fin)
STREETS = {
    'terraza': (10, 1.0, 0.3, 2, 74),
    'mayor': (31, 1.4, 1.1, 0, 89),
    'media': (45, 1.3, 2.4, 0, 63),
    'sur': (58, 1.2, 0.7, 0, 74),
}


def srow(name, c):
    """Fila de la calle en la columna c: dos ondas superpuestas, una larga y
    otra corta, para que serpentee sin parecer una sinusoide."""
    b, a, ph, _, _ = STREETS[name]
    return b + int(round(a * 1.6 * np.sin(c / 13.0 + ph)))


WIDTH = {'terraza': 2, 'mayor': 3, 'media': 2, 'sur': 2}


# edificios: (nombre, calle, columna aproximada de la puerta, retranqueo en filas, variante de tejado)
PLAN = [
    ('torre', 'terraza', 5, 1, 0), ('cabana', 'terraza', 13, 2, 0), ('piedra', 'terraza', 22, 1, 0),
    ('granero', 'terraza', 30, 2, 0), ('capilla', 'terraza', 40, 1, 0), (('azul', 200), 'terraza', 50, 3, 0),
    ('casita', 'terraza', 58, 1, 0), (('casa_crema', 200), 'terraza', 67, 2, 0),
    ('escuela', 'mayor', 5, 2, 0), ('posada', 'mayor', 26, 1, 0), ('azul', 'mayor', 13, 1, 0), (('balcon', 30), 'mayor', 19, 5, 0), ('tienda', 'mayor', 55, 1, 0), ('esquina', 'mayor', 63, 3, 0), ('molino', 'mayor', 72, 1, 0),
    ('taller', 'media', 5, 1, 0), ('balcon', 'media', 13, 3, 0), ('casa_crema', 'media', 21, 1, 0),
    ('mostaza', 'media', 29, 2, 0), ('alcaldia', 'media', 40, 1, 0), (('piedra', 140), 'media', 52, 2, 0),
    ('panaderia', 'media', 60, 1, 0),
    (('balcon', 200), 'sur', 6, 2, 0), ('casa_pescador', 'sur', 14, 1, 0), (('mostaza', 230), 'sur', 23, 3, 0),
    (('esquina', 150), 'sur', 29, 1, 0), (('piedra', 25), 'sur', 52, 2, 0), (('casita', 180), 'sur', 60, 1, 0),
    ('botes', 'sur', 69, 1, 0),
]
UNIQUE = {'capilla', 'torre', 'granero', 'molino', 'botes', 'alcaldia', 'posada', 'tienda', 'escuela', 'panaderia', 'taller'}


def plan_layout(seed=RNG_SEED):
    """Coloca las casas con desfase y huecos irregulares, sin solaparse."""
    scene2.load_overrides()
    for n, door in scene2.NEW_DOOR.items():
        p = f'pl/bld/{n}_0.png'
        import os
        if os.path.exists(p) and n not in scene2.BLD_OVERRIDE:
            a = np.array(Image.open(p).convert('RGBA'))
            rows = np.where(a[..., 3].any(1))[0]
            import roofix
            scene2.BLD_OVERRIDE[n] = (roofix.fix_top(a[:rows.max() + 1]), door)
    rng = np.random.default_rng(seed)
    placed, rects = [], []
    # zonas vetadas: plaza, plazoleta y el lago
    banned = [(30 * T - 8, 18 * T - 8, 50 * T + 8, 28 * T + 8), (34 * T, 47 * T, 48 * T, 55 * T)]
    for item, st, c0, setback, _ in PLAN:
        nm, shift = (item if isinstance(item, tuple) else (item, 0))
        if nm not in scene2.BLD_OVERRIDE and not hasattr(B, nm):
            continue
        spr, door = bld(nm)
        if shift:
            spr = roof_variant(spr, shift)
        h, w = spr.shape[:2]
        ok = False
        for attempt in range(40):
            jitter = int(rng.integers(-2, 3)) if attempt else 0
            sb = setback + (int(rng.integers(-1, 2)) if attempt > 3 else 0)
            sb = max(1, sb)
            c = c0 + jitter
            r_st = min(srow(st, c), srow(st, c + 1))
            r_door = r_st - sb
            door_cx = (c + 1) * T
            x, yb = door_cx - door, r_door * T + 4
            rect = (x - 6, yb - h - 4, x + w + 6, yb + 10)
            if rect[0] < -20 or rect[2] > W * T + 20 or rect[1] < 0:
                continue
            if any(not (rect[2] <= r[0] or rect[0] >= r[2] or rect[3] <= r[1] or rect[1] >= r[3]) for r in rects + banned):
                continue
            # no pisar la calle de arriba
            above = [n for n in STREETS if STREETS[n][0] < STREETS[st][0]]
            if above:
                up = max(above, key=lambda n: STREETS[n][0])
                if (yb - h + 10) // T <= max(srow(up, cc) for cc in range(int(x // T), int((x + w) // T) + 1)) + 1:
                    continue
            ok = True
            break
        if not ok:
            continue
        rects.append(rect)
        placed.append(dict(name=nm, spr=spr, x=x, yb=yb, door_cx=door_cx, c=c, r_door=r_door, r_st=r_st, st=st,
                           yard=['valla', 'seto', 'huerto', 'nada'][int(rng.integers(0, 4))] if nm not in UNIQUE else 'nada'))
    return placed


LAYOUT = None


def layout():
    global LAYOUT
    if LAYOUT is None:
        LAYOUT = plan_layout()
    return LAYOUT


def spec():
    b = maps2.Builder(W, H)
    # terraza con borde natural
    b.high([(r, 0, 89) for r in range(0, 13)] + [(13, 3, 30), (13, 34, 58), (14, 5, 26), (14, 44, 56),
            (13, 62, 89), (14, 66, 72)])
    b.high([(r, 76, 89) for r in range(0, 5)] + [(5, 78, 86)], level=2)
    river = {r: (78 + int(round(1.4 * np.sin(r / 6.0))), 80 + int(round(1.4 * np.sin(r / 6.0)))) for r in range(H)}
    b.run('w', river)
    b.run('w', [(47, 70, 76), (48, 68, 77), (49, 67, 78), (50, 67, 78), (51, 68, 77), (52, 70, 76)])
    for name, (base, amp, ph, c0, c1) in STREETS.items():
        wd = WIDTH[name]
        # ancho que respira: a veces una casilla más
        b.run('p', [(srow(name, c) + k, c, c) for c in range(c0, c1 + 1)
                    for k in range(wd)])
    # callejones que cosen las calles, también en curva
    for c0, r0, r1 in [(1, 32, 58), (33, 33, 45), (47, 33, 45), (17, 46, 58)]:
        b.run('p', [(r, c0 + int(round(1.6 * np.sin(r / 3.5 + c0))), c0 + 1 + int(round(1.6 * np.sin(r / 3.5 + c0)))) for r in range(r0, r1 + 1)])
    def oval(cr, cc, rr, rc):
        out = []
        for r in range(int(cr - rr), int(cr + rr) + 1):
            dy = (r + 0.5 - cr) / rr
            if abs(dy) <= 1:
                half = rc * np.sqrt(1 - dy * dy)
                out.append((r, int(round(cc - half)), int(round(cc + half))))
        return out
    b.run('c', oval(23, 40, 6.2, 11.5))
    b.run('p', [(r, 39, 40) for r in range(14, 18)])
    b.run('S', [(13, 39, 40)])
    b.run('c', oval(51.5, 41, 4.2, 7.5))
    b.run('p', [(r, 40, 41) for r in range(59, 64)])
    for p in layout():
        c = p['c']
        # senda a la puerta que se tuerce un poco antes de llegar a la calle
        drift = 1 if (c * 7) % 3 else -1
        for r in range(p['r_door'], p['r_st'] + 1):
            k = r - p['r_door']
            off = 0 if k < 1 else drift * min(k, 2) // 2 if k < 3 else drift
            b.run('p', [(r, c + off, c + off + 1)])
        if p['yard'] == 'huerto':
            side = -1 if (c % 2) else 1
            cc = c - 6 if side < 0 else c + 3
            b.run('u', [(p['r_door'] - 1, cc, cc + 2), (p['r_door'], cc, cc + 2)]) if False else None
    b.run('p', [(r, 82, 83) for r in range(6, 11)] + [(10, 75, 83), (11, 75, 83)])
    b.run('u', [(r, 77, 88) for r in (1, 2)] + [(r, 84, 88) for r in (7, 8)])
    b.run('f', [(r, 82, 87) for r in range(17, 21)] + [(r, 83, 88) for r in range(38, 41)] +
          [(16, 30, 33), (17, 29, 33), (16, 46, 49), (17, 46, 50)])
    b.run('t', [(r, 84, 89) for r in range(23, 29)] + [(r, 0, 3) for r in range(60, 64)] + [(r, 81, 89) for r in range(52, 62)])
    return b.spec()


SPEC = None


def get_spec():
    global SPEC
    if SPEC is None:
        SPEC = spec()
    return SPEC


def objects(state, info=None):
    sick = state != 'sano'
    sh = (lambda s: ashen(s)) if sick else (lambda s: s)
    rng = np.random.default_rng(11)
    objs = []
    for p in layout():
        spr = sh(p['spr'])
        objs.append((spr, p['x'], p['yb'], 0))
        y = p['yard']
        if y == 'valla':
            yard(objs, spr, p['x'], p['yb'], p['door_cx'], sh, pots=bool(rng.integers(0, 2)))
        elif y == 'seto':
            for k, dx in enumerate((-30, 18)):
                objs.append((bush2(state, k + p['c']), p['door_cx'] + dx - 6, p['yb'] + 14, 22))
        elif y == 'huerto':
            objs.append((sh(B.pot_plant(p['c'])), p['door_cx'] - 20, p['yb'] + 4, 0))
            objs.append((sh(hay()), p['x'] + p['spr'].shape[1] - 10, p['yb'] + 4, 0))
        elif p['name'] in ('posada', 'tienda', 'alcaldia', 'panaderia', 'escuela'):
            objs.append((sh(B.pot_plant(p['c'])), p['door_cx'] - 20, p['yb'] + 4, 0))
            objs.append((sh(B.pot_plant(p['c'] + 1)), p['door_cx'] + 13, p['yb'] + 4, 0))
    t = BURNT if sick else TREE
    cx, cy = 40 * T, 23 * T + 8
    objs.append(('decal', ring_planter(state), cx - 42, cy - 17))
    objs.append((t.copy(), cx - foot_x(t), cy, 60))
    objs.append((sh(B.stall()), 31 * T, 21 * T, 0))
    objs.append((sh(B.stall(('roofb', 'paper'), 'tela')), 46 * T + 6, 21 * T, 0))
    objs.append((sh(B.stall(('roofr', 'paper'), 'fruta')), 32 * T, 26 * T + 4, 0))
    objs.append((sh(B.stall(('eco', 'paper'), 'tela')), 45 * T, 26 * T - 4, 0))
    objs.append((sh(B.bench()), cx - 84, cy + 34, 0))
    objs.append((sh(B.bench()), cx + 52, cy + 30, 0))
    for x, y in [(30 * T + 2, 18 * T + 14), (50 * T - 10, 19 * T), (31 * T, 28 * T - 2), (49 * T - 4, 28 * T - 2)]:
        objs.append((B.lamp_post(), x, y, 6))
    f = sh(B.fountain())
    objs.append((f, 41 * T - f.shape[1] // 2, 53 * T, 0))
    objs.append((sh(B.bench()), 36 * T, 54 * T, 0))
    objs.append((B.lamp_post(), 34 * T + 2, 49 * T, 6))
    objs.append((B.lamp_post(), 47 * T - 6, 55 * T, 6))
    for i, (x, y) in enumerate([(x, y) for y in (18 * T, 21 * T + 6) for x in range(4 * T, 16 * T, 58)]):
        objs.append((fruit_tree(state, i, [3, 0, 1][i % 3]), x + int(rng.integers(-6, 7)), y + int(rng.integers(-4, 5)), 26))
    objs.append((sh(B.well()), 27 * T, 20 * T, 0))
    objs.append(('decal', boat(), 71 * T, 48 * T + 4))
    objs.append((sh(crate_fish()), 66 * T, 54 * T, 0))
    for x, y in [(2 * T, srow('mayor', 2) * T - 12), (86 * T, srow('mayor', 86) * T - 12), (42 * T + 4, 63 * T)]:
        objs.append((sign(), x, y, 10))
    objs.append((sh(cart()), 64 * T, 27 * T, 0))
    objs.append((sh(laundry()), 9 * T, 41 * T, 0))
    for i, (x, y) in enumerate([(37 * T - 8, 15 * T), (41 * T + 4, 15 * T)]):
        objs.append((bush2(state, i), x, y, 22))
    # árboles: bosquecillos del borde y algunos sueltos en los huecos entre casas
    spots = [(-40, 70), (1300, 60), (1380, 170), (1320, 320), (1380, 460), (1300, 600), (1380, 760),
             (1320, 1040), (60, 1060), (220, 1050), (420, 1060), (760, 1060), (980, 1050), (1160, 1060),
             (-40, 600), (-40, 820),
             (300, 400), (820, 420), (180, 640), (700, 640), (560, 860), (300, 880), (900, 820), (120, 120), (1000, 120)]
    for i, x, y in solve_trees(spots, info, 'valdehoja5'):
        sp = t if i % 2 else t[:, ::-1]
        objs.append((sp, x, y, 54))
    return objs


NPCS = [('rosa', 'south', 528, 384), ('tona', 'east', 584, 414), ('tito', 'south-east', 720, 404)]


def npc_actors():
    import os
    out = list()
    places = list(NPCS)
    for p in layout():
        if p['name'] == 'capilla':
            places.append(('julian', 'south', p['door_cx'] + 22, p['yb'] + 14))
        if p['name'] == 'molino':
            places.append(('aurelio', 'west', p['door_cx'] + 30, p['yb'] + 18))
        if p['name'] == 'botes':
            places.append(('mariela', 'south-west', p['door_cx'] + 26, p['yb'] + 22))
    for n, d, x, y in places:
        pth = f'pl/npc/{n}/{d}.png'
        if not os.path.exists(pth):
            continue
        s = scene.trim(np.array(Image.open(pth)))
        out.append((s, x - s.shape[1] // 2, y, 22))
    return out


def hero(x, y, d='south'):
    s = scene.trim(np.array(Image.open(f'final/chars/ilan_{d}.png')))
    return (s, x - s.shape[1] // 2, y, 22)


def render(state, view, extra=(), sign_=None, dialog=None):
    return scene2.render(state, actors=npc_actors() + list(extra), spec=get_spec(), objects=objects,
                         view=view, sign=sign_, dialog=dialog)


if __name__ == '__main__':
    for p in layout():
        print(p['name'], p['c'], p['r_door'], p['yard'])
    im = render('sano', None)
    px.save(im, 'out2/v5_sano.png')
    Image.open('out2/v5_sano.png').resize((1080, 768)).save('out2/v5_small.png')
