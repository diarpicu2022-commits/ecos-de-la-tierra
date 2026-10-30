"""Otras zonas de Solmira con el mismo motor: Costa Quebrada (Pacífico de
Nariño: playa, manglar, palafitos y residuos de plástico) y Cuenca de
Alquitrán (humedal con derrame de crudo, balancines y tubería)."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import maps2, scene2, px, scene, flora
from pal import P
from px import new, col, blit, outline, shade, ellipse
import buildings as B

T = 16
C = lambda r, i: col(P[r][i])


# --- mapas --------------------------------------------------------------------

def costa():
    b = maps2.Builder(40, 23)
    # acantilado verde al norte con la senda que baja
    b.high([(r, 0, 39) for r in range(0, 5)] + [(5, 0, 14), (5, 24, 39), (6, 2, 10)])
    # línea de costa en diagonal: el mar ocupa el sureste
    def c_sea(r):
        return 34 - (r - 8) * 2 + int(round(1.5 * np.sin(r / 2.3)))
    for r in range(8, 23):
        c = max(0, c_sea(r))
        b.run('a', [(r, max(0, c - 5), min(39, c + 1))])
        b.run('w', [(r, c, 39)])
    b.run('a', [(7, 27, 39), (8, 30, 39)])
    b.run('p', [(r, 18, 19) for r in range(0, 5)] + [(r, 18, 19) for r in range(6, 14)])
    b.run('S', [(5, 18, 19)])
    b.run('B', [(r, 26, 27) for r in range(11, 19)])
    b.run('t', [(1, 3, 8), (2, 2, 9), (3, 4, 7), (8, 1, 5), (9, 0, 6)])
    b.run('f', [(2, 26, 30), (3, 27, 31)])
    s = b.spec()
    s['region'] = 'costa'
    return s


def cuenca():
    b = maps2.Builder(40, 23)
    b.high([(r, 0, 39) for r in range(0, 4)] + [(4, 0, 12), (4, 28, 39), (5, 2, 9)])
    # gran ciénaga en el centro y arroyo que la alimenta
    lake = [(8, 14, 25), (9, 11, 28), (10, 9, 30), (11, 8, 31), (12, 8, 31), (13, 9, 30), (14, 10, 29),
            (15, 12, 27), (16, 15, 24)]
    b.run('w', lake)
    b.run('w', [(r, 19 + int(round(1.5 * np.sin(r))), 21 + int(round(1.5 * np.sin(r)))) for r in range(0, 9)])
    b.run('w', [(r, 30 + int(round(np.sin(r / 2))), 32 + int(round(np.sin(r / 2)))) for r in range(16, 23)])
    b.run('w', [(16, 24, 31), (17, 27, 31)])
    # camino de tierra que rodea la ciénaga, con pasarela
    b.run('p', [(18, 0, 39), (19, 0, 39)])
    b.run('p', [(r, 5, 6) for r in range(6, 18)] + [(6, 5, 16), (7, 5, 16)])
    b.run('B', [(r, 30, 32) for r in (18, 19)])
    b.run('t', [(r, 33, 39) for r in range(6, 12)] + [(r, 0, 3) for r in range(10, 16)])
    s = b.spec()
    s['region'] = 'cuenca'
    return s


COSTA = costa()
CUENCA = cuenca()


# --- objetos propios -------------------------------------------------------------

def palm(state='sano', seed=0, lean=1):
    """Palma de coco: tronco curvo anillado y penacho de frondas."""
    rng = np.random.default_rng(seed)
    W, H = 60, 86
    img = new(W, H)
    pts = []
    for i in range(46):
        t = i / 45
        x = 30 + lean * 10 * t ** 1.6
        y = H - 2 - i * 1.25
        pts.append((x, y))
    trunk = np.zeros((H, W), bool)
    yy, xx = np.indices((H, W))
    for k, (x, y) in enumerate(pts):
        w_ = 3.2 - 1.2 * k / 45
        trunk |= ((xx - x) ** 2 + (yy - y) ** 2) <= w_ ** 2
    wood = P['wood'] if state == 'sano' else P['ash']
    img[trunk] = col(wood[3])
    img[trunk & (xx < np.array([p[0] for p in pts]).mean() - 0)] = col(wood[4])
    img[trunk & (yy % 4 == 0)] = col(wood[2])
    tx, ty = pts[-1]
    leaf = P['leaf'] if state == 'sano' else P['deadleaf'] + [P['deadleaf'][-1]]
    frond = np.zeros((H, W), bool)
    angs = [200, 230, 260, 290, 320, 345, 15, 160, 135]
    for a in angs:
        a += rng.uniform(-8, 8)
        L = rng.uniform(20, 27) if state == 'sano' else rng.uniform(12, 18)
        for s_ in np.linspace(0, 1, 40):
            x = tx + np.cos(np.radians(a)) * L * s_
            y = ty + np.sin(np.radians(a)) * L * s_ * 0.55 + (s_ ** 2) * 10
            wd = 3.0 * (1 - s_) + 0.6
            frond |= ((xx - x) ** 2 + (yy - y) ** 2) <= wd ** 2
    fimg = shade(frond, leaf[1:6], light=(-0.4, -0.9, 0.5), ambient=0.25)
    img[frond] = fimg[frond]
    if state == 'sano':
        for dx in (-2, 2, 0):
            m = ellipse(W, H, tx + dx, ty + 4, 2.4, 2.4)
            img[m] = C('wood', 2); img[m & (yy < ty + 3)] = C('wood', 4)
    return outline(img)


def mangrove(state='sano', seed=0):
    """Mangle: copa baja sobre raíces en arco."""
    rng = np.random.default_rng(seed)
    W, H = 56, 48
    img = new(W, H)
    yy, xx = np.indices((H, W))
    roots = np.zeros((H, W), bool)
    for x0, x1 in ((24, 6), (26, 15), (28, 23), (30, 34), (31, 43), (33, 51)):
        x0 += rng.uniform(-1, 1)
        for t in np.linspace(0, 1, 50):
            x = (1 - t) ** 2 * x0 + 2 * t * (1 - t) * (x1 * 0.6 + x0 * 0.4) + t ** 2 * x1
            y = (1 - t) ** 2 * 26 + 2 * t * (1 - t) * 28 + t ** 2 * (H - 3)
            roots |= ((xx - x) ** 2 + (yy - y) ** 2) <= 1.4
    wd = P['wood'] if state == 'sano' else P['ash']
    img[roots] = col(wd[2])
    ramp = P['leaf'] if state == 'sano' else P['deadleaf'] + [P['deadleaf'][-1]]
    circles = [(28, 16, 13), (15, 21, 9), (41, 21, 9), (21, 10, 9), (35, 10, 9)]
    can, m = flora.clumps_canopy(W, 34, circles, ramp, seed)
    blit(img, can, 0, 0)
    return outline(img)


def stilt_house(state='sano'):
    """Palafito: la casa de pescadores sobre pilotes."""
    import scene2 as S
    S.load_overrides()
    spr, door = S.bld('casa_pescador')
    h, w = spr.shape[:2]
    img = new(w, h + 18)
    blit(img, spr, 0, 0)
    for x in range(6, w - 6, 16):
        img[h - 2:h + 18, x:x + 4] = C('wood', 2); img[h - 2:h + 18, x] = C('wood', 3)
    img[h:h + 3, 2:w - 2] = C('wood', 3)
    return img


def rowboat(state='sano', color='roofb'):
    W, H = 46, 20
    img = new(W, H)
    yy, xx = np.indices((H, W))
    hull = ((xx - 23) / 22) ** 2 + ((yy - 10) / 9) ** 2 <= 1
    inner = ((xx - 23) / 19) ** 2 + ((yy - 9) / 6) ** 2 <= 1
    img[hull] = C(color, 3); img[hull & (yy > 12)] = C(color, 2)
    img[inner] = C('wood', 3); img[inner & (xx % 7 == 0)] = C('wood', 2)
    img[hull & (yy == 4)] = C(color, 4)
    return outline(img)


def debris(seed=0, n=1):
    """Basura de plástico: botellas, bolsas, tapas, redes enredadas."""
    rng = np.random.default_rng(seed)
    pieces = []
    bottle = new(10, 4); bottle[1:3, 0:8] = C('plastic', 2); bottle[1:3, 8:10] = C('plastic', 4); bottle[1, 1:7] = C('plastic', 3)
    pieces.append(outline(bottle))
    bag = new(9, 8); m = ellipse(9, 8, 4.5, 4, 4, 3.5); bag[m] = C('ui', 5); bag[m & (np.indices((8, 9))[0] > 4)] = C('ui', 4)
    pieces.append(outline(bag))
    cap = new(4, 4); cap[1:3, 1:3] = C('plastic', 4)
    pieces.append(cap)
    can = new(8, 5); can[1:4, 0:7] = C('stone', 4); can[1:4, 2:5] = C('roofr', 3)
    pieces.append(outline(can))
    net = new(16, 10); yy, xx = np.indices((10, 16)); net[((xx + yy) % 3 == 0) | ((xx - yy) % 3 == 0)] = C('eco', 2)
    net[(((xx - 8) / 8) ** 2 + ((yy - 5) / 5) ** 2) > 1] = 0
    pieces.append(net)
    return pieces[seed % len(pieces)]


def pumpjack(state='enfermo'):
    """Balancín petrolero: viga, cabeza de caballo, contrapeso y base."""
    W, H = 64, 58
    img = new(W, H)
    s = P['stone']
    img[H - 8:H, 6:W - 6] = C('stone', 2); img[H - 8, 6:W - 6] = C('stone', 4)
    # trípode
    for t in np.linspace(0, 1, 40):
        for x0 in (22, 34):
            x = x0 + (28 - x0) * t
            y = H - 8 - 34 * t
            img[int(y):int(y) + 2, int(x):int(x) + 2] = C('stone', 1)
    # viga
    img[14:19, 6:56] = C('rust', 2); img[14, 6:56] = C('rust', 3); img[18, 6:56] = C('rust', 1)
    # cabeza de caballo
    head = ellipse(W, H, 54, 20, 7, 11) & (np.indices((H, W))[1] >= 52)
    img[head] = C('rust', 3)
    img[30:H - 8, 57:58] = C('ink', 1)
    # contrapeso y manivela
    cw = ellipse(W, H, 12, 34, 8, 8)
    img[cw] = C('stone', 3); img[cw & ~ellipse(W, H, 12, 34, 6, 6)] = C('stone', 1)
    img[20:30, 11:14] = C('stone', 1)
    img[H - 16:H - 8, 4:22] = C('stone', 3)
    return outline(img)


def pipe(length=120):
    img = new(length, 14)
    img[4:10, :] = C('stone', 3); img[4, :] = C('stone', 5); img[9, :] = C('stone', 1)
    for x in range(0, length, 40):
        img[2:12, x:x + 4] = C('rust', 2); img[2, x:x + 4] = C('rust', 3)
        img[10:14, x + 1:x + 3] = C('stone', 1)
    img[6:8, length // 3:length // 3 + 3] = C('oil', 2)
    return outline(img)


def reeds(state='sano'):
    g = P['grass'] if state == 'sano' else P['drygrass']
    img = new(14, 18)
    for i, x in enumerate((2, 5, 8, 11)):
        h = 12 + (i % 2) * 4
        img[18 - h:18, x] = col(g[3]); img[18 - h:18 - h // 2, x] = col(g[5])
        if state == 'sano' and i % 2 == 0:
            img[18 - h - 3:18 - h + 1, x - 1:x + 1] = C('wood', 2)
    return img


def oil_drum():
    m = ellipse(14, 18, 7, 9, 6.5, 8.5)
    img = shade(m, [P['roofb'][1], P['roofb'][2], P['roofb'][3], P['roofb'][4], P['roofb'][5]], ambient=0.3)
    img[5][m[5]] = C('ink', 1); img[13][m[13]] = C('ink', 1)
    img[14:17, 2:6] = C('oil', 1)
    return outline(img)


def costa_objects(state, info=None):
    sick = state != 'sano'
    objs = []
    rng = np.random.default_rng(4)
    for i, (x, y) in enumerate([(40, 120), (110, 140), (480, 60), (560, 90), (600, 40), (20, 260), (240, 120), (380, 110)]):
        objs.append((palm(state, i, 1 if i % 2 else -1), x, y, 26))
    objs.append((mangrove(state, 1), 560, 240, 30))
    objs.append((mangrove(state, 2), 600, 200, 30))
    sh = (lambda s: scene2.ashen(s)) if sick else (lambda s: s)
    objs.append((sh(stilt_house(state)), 330, 250, 0))
    objs.append(('decal', rowboat(state, 'roofr'), 470, 250))
    objs.append(('decal', rowboat(state, 'eco'), 440, 330))
    objs.append((scene2.sign(), 300, 96, 10))
    objs.append((sh(scene2.crate_fish()), 300, 232, 0))
    if sick:
        for k in range(60):
            x, y = int(rng.integers(0, 620)), int(rng.integers(130, 360))
            objs.append(('decal', debris(k), x, y))
    else:
        for k in range(8):
            x, y = int(rng.integers(40, 400)), int(rng.integers(200, 290))
            sh_ = new(5, 3); sh_[1, 1:4] = C('flower', 2); sh_[0, 2] = C('flower', 4)
            objs.append(('decal', sh_, x, y))
    import dress as D
    sand = D.tiles(info, 'a')
    objs = D.scatter(objs, info, state, [(palm, 26, 3)] if False else [(lambda st, sd: palm(st, sd, 1 if sd % 2 else -1), 26, 1)],
                     clusters=4, per=(1, 2), spread=40, seed=31, where=~sand)
    objs = D.scatter(objs, info, state, [(D.bush, 22, 4), (D.big_rock, 18, 0.6), (D.rock, 10, 0.8), (D.flower_patch, 0, 4),
                                         (D.grass_clump, 0, 4), (D.pebbles, 0, 2)],
                     clusters=14, per=(3, 6), seed=32, where=~sand, decal=(D.flower_patch, D.grass_clump, D.pebbles))
    objs = D.scatter(objs, info, state, [(D.beach_grass, 0, 4), (D.driftwood, 8, 2), (D.shell, 0, 4), (D.rock, 10, 2), (D.pebbles, 0, 2)],
                     clusters=12, per=(2, 5), seed=33, where=sand, decal=(D.shell, D.pebbles, D.beach_grass))
    return objs


def cuenca_objects(state, info=None):
    sick = state != 'sano'
    objs = []
    t = scene2.BURNT if sick else scene2.TREE
    spots = [(-40, 60), (60, 40), (480, 50), (560, 70), (620, 30), (-30, 300), (600, 330), (380, 380)]
    for i, x, y in scene2.solve_trees(spots, info, 'cuenca' + state):
        objs.append((t if i % 2 else t[:, ::-1], x, y, 54))
    if sick:
        for x, y in [(355, 124), (90, 362), (560, 170)]:
            objs.append((pumpjack(), x, y, 40))
        objs.append((pipe(300), 150, 336, 0))
        objs.append((pipe(130), 520, 336, 0))
        for x, y in [(130, 180), (150, 186), (430, 126), (448, 132), (40, 250)]:
            objs.append((oil_drum(), x, y, 10))
    else:
        for x, y in [(130, 180), (500, 196)]:
            objs.append((scene2.bush2(state, x), x, y, 22))
    for i, (x, y) in enumerate([(150, 150), (200, 132), (440, 150), (470, 168), (180, 250), (400, 262), (320, 268)]):
        objs.append((reeds(state), x, y, 0))
    objs.append((scene2.sign(), 100, 300, 10))
    import dress as D
    sh_ = D.shore(info)
    objs = D.trees(objs, info, state, n=14, seed=40)
    objs = D.scatter(objs, info, state, [(lambda st, sd: reeds(st), 0, 6), (D.grass_clump, 0, 2), (D.bush, 22, 1)],
                     clusters=22, per=(3, 6), spread=24, seed=41, where=sh_, decal=(D.grass_clump,))
    objs = D.scatter(objs, info, state, [(D.bush, 22, 5), (D.log_, 16, 1), (D.big_rock, 18, 0.5), (D.flower_patch, 0, 4),
                                         (D.grass_clump, 0, 5), (D.pebbles, 0, 1), (D.rock, 10, 0.7)],
                     clusters=18, per=(3, 6), seed=42, where=~sh_, decal=(D.flower_patch, D.grass_clump, D.pebbles))
    return objs


# --- Llanura Marchita: campos de cultivo (sequía y monocultivo cuando enferma) ---

def llanura(state='sano'):
    b = maps2.Builder(40, 23)
    b.high([(r, 0, 39) for r in range(0, 3)] + [(3, 0, 9), (3, 30, 39)])
    # camino principal en curva suave y desvío a la granja
    for c in range(40):
        r = 12 + int(round(1.6 * np.sin(c / 7.0)))
        b.run('p', [(r, c, c), (r + 1, c, c)])
    b.run('p', [(r, 22, 23) for r in range(3, 12)])
    b.run('S', [(2, 22, 23)])
    b.run('p', [(0, 22, 23), (1, 22, 23)])
    # parcelas de cultivo (mosaico)
    b.run('u', [(r, 2, 9) for r in range(5, 10)])
    b.run('u', [(r, 11, 14) for r in range(5, 10)])
    b.run('u', [(r, 3, 12) for r in range(16, 21)])
    b.run('u', [(r, 14, 21) for r in range(16, 21)])
    b.run('u', [(r, 27, 35) for r in range(17, 21)])
    # estanque de riego: agua si está sano, barro cuarteado si enfermo
    pond = [(5, 30, 34), (6, 28, 36), (7, 28, 36), (8, 29, 35), (9, 30, 33)]
    b.run('w' if state == 'sano' else 'a', pond)
    b.run('t', [(r, 37, 39) for r in range(5, 10)] + [(r, 0, 1) for r in range(15, 22)])
    if state == 'sano':
        b.run('f', [(4, 12, 16), (21, 23, 26)])
    s = b.spec()
    s['region'] = 'llanura'
    return s


def scarecrow(state='sano'):
    img = new(20, 34)
    img[8:34, 9:11] = C('wood', 2)
    img[12:14, 1:19] = C('wood', 3)
    shirt = C('roofr', 3) if state == 'sano' else C('ash', 3)
    img[11:22, 5:15] = shirt; img[11:22, 5] = C('roofr', 2) if state == 'sano' else C('ash', 2)
    img[12:15, 1:5] = shirt; img[12:15, 15:19] = shirt
    head = ellipse(20, 34, 10, 7, 4, 4)
    img[head] = C('gold', 3)
    img[2:5, 4:16] = C('wood', 2); img[0:3, 7:13] = C('wood', 3)
    img[7, 8] = C('ink', 1); img[7, 11] = C('ink', 1)
    return outline(img)


def cracks(seed=0, W=40, H=22):
    """Grietas de tierra seca como calco de suelo."""
    rng = np.random.default_rng(seed)
    img = new(W, H)
    for _ in range(5):
        x, y = rng.uniform(4, W - 4), rng.uniform(3, H - 3)
        a = rng.uniform(0, np.pi * 2)
        for _ in range(int(rng.integers(6, 14))):
            xi, yi = int(x), int(y)
            if 0 <= xi < W and 0 <= yi < H:
                img[yi, xi] = C('ink', 1)
            a += rng.uniform(-0.7, 0.7)
            x += np.cos(a); y += np.sin(a) * 0.6
    return img


def dry_shrub(seed=0):
    rng = np.random.default_rng(seed)
    img = new(18, 12)
    for _ in range(9):
        a = rng.uniform(np.pi * 1.1, np.pi * 1.9)
        for t in range(int(rng.integers(4, 8))):
            x, y = int(9 + np.cos(a) * t), int(11 + np.sin(a) * t * 0.9)
            if 0 <= x < 18 and 0 <= y < 12:
                img[y, x] = C('drygrass', 3 + (t > 4))
    return img


def llanura_objects(state, info=None):
    sick = state != 'sano'
    objs = []
    scene2.load_overrides()
    sh = (lambda s: scene2.ashen(s)) if sick else (lambda s: s)
    mol, _ = scene2.bld('molino')
    gra, _ = scene2.bld('granero')
    objs.append((sh(mol), 240, 172, 0))
    objs.append((sh(gra), 380, 178, 0))
    objs.append((sh(scene2.fence(10)), 30, 174, 0))
    objs.append((sh(scene2.fence(8)), 50, 352, 0))
    objs.append((scarecrow(state), 100, 120, 10))
    objs.append((scarecrow(state), 280, 330, 10))
    for i, (x, y) in enumerate([(470, 200), (494, 206), (482, 214)]):
        h = scene2.hay()
        objs.append((scene2.ashen(h, 0.5, 0.75) if sick else h, x, y, 12))
    objs.append((sh(scene2.cart()), 520, 236, 16))
    objs.append((scene2.sign(), 330, 64, 10))
    t = scene2.BURNT if sick else scene2.TREE
    spots = [(560, 330), (600, 260), (-30, 300), (430, 280), (40, 40), (600, 40)]
    for i, x, y in scene2.solve_trees(spots, info, 'llanura' + state):
        objs.append((t if i % 2 else t[:, ::-1], x, y, 54))
    rng = np.random.default_rng(11)
    if sick:
        for k in range(26):
            x, y = int(rng.integers(0, 600)), int(rng.integers(60, 350))
            objs.append(('decal', cracks(k), x, y))
        for k in range(10):
            x, y = int(rng.integers(0, 620)), int(rng.integers(70, 360))
            objs.append((dry_shrub(k), x, y, 0))
        for k in range(6):
            objs.append(('decal', cracks(100 + k, 34, 18), 460 + (k % 3) * 34, 84 + (k // 3) * 22))
    else:
        for x, y in [(70, 260), (590, 200), (320, 380)]:
            objs.append((scene2.bush2(state, x), x, y, 22))
    import dress as D
    farm = D.tiles(info, 'u')
    objs = D.trees(objs, info, state, n=8, seed=50, where=~farm)
    objs = D.scatter(objs, info, state, [(D.bush, 22, 5), (D.flower_patch, 0, 5), (D.grass_clump, 0, 5),
                                         (D.pebbles, 0, 1), (D.rock, 10, 0.7), (D.big_rock, 18, 0.4)],
                     clusters=18, per=(3, 6), seed=52, where=~farm, decal=(D.flower_patch, D.grass_clump, D.pebbles))
    return objs


# --- Cumbre Menguante: páramo y glaciar (se derrite cuando enferma) -------------

def cumbre(state='sano'):
    b = maps2.Builder(40, 23)
    b.high([(r, 0, 39) for r in range(0, 9)] + [(9, 0, 14), (9, 28, 39), (10, 0, 8)], 1)
    b.high([(r, 0, 39) for r in range(0, 4)] + [(4, 0, 20), (5, 4, 14), (4, 31, 39)], 2)
    # sendero en zigzag con escaleras entre cotas
    b.run('p', [(r, 10, 11) for r in range(14, 23)] + [(14, 10, 24)] + [(r, 25, 26) for r in range(10, 15)])
    b.run('p', [(r, 25, 26) for r in range(5, 10)] + [(r, 25, 26) for r in range(10, 15)] + [(5, 17, 26), (6, 17, 26)] + [(r, 17, 18) for r in range(0, 5)])
    b.run('S', [(9, 25, 26)])
    b.run('S', [(5, 17, 18)])
    # nieve: casquete grande en la cima si está sano; jirones si enfermo
    if state == 'sano':
        b.run('a', [(r, 0, 39) for r in range(0, 3)] + [(3, 0, 15), (3, 22, 39), (4, 33, 39)])
        b.run('a', [(r, 0, 6) for r in range(5, 8)] + [(r, 33, 39) for r in range(5, 7)])
    else:
        b.run('a', [(0, 0, 10), (1, 0, 6), (0, 28, 39), (1, 33, 39)])
    b.run('p', [(r, 17, 18) for r in range(0, 4)])
    # laguna de páramo
    lag = [(15, 27, 33), (16, 25, 35), (17, 24, 36), (18, 24, 36), (19, 25, 35), (20, 27, 33)]
    if state != 'sano':
        lag = [(16, 27, 33), (17, 26, 34), (18, 27, 33)]
        b.run('a', [(15, 27, 33), (16, 25, 35), (17, 24, 36), (18, 24, 36), (19, 25, 35), (20, 27, 33)])
    b.run('w', lag)
    b.run('t', [(r, 0, 6) for r in range(12, 20)] + [(r, 14, 22) for r in range(17, 22)])
    s = b.spec()
    s['region'] = 'cumbre'
    return s


def frailejon(state='sano', seed=0, h=None, stub=False):
    """Frailejón: tronco grueso forrado por su falda de hojas secas y una roseta
    ancha de hojas plateadas y afelpadas, vista un poco desde arriba."""
    rng = np.random.default_rng(seed)
    h = h if h is not None else int(rng.integers(6, 26))
    if stub:
        h = int(rng.integers(4, 12))
    R = 17 if state == 'sano' else 13
    W, H = 2 * R + 8, h + R + 10
    img = new(W, H)
    yy, xx = np.indices((H, W))
    cx, top = W // 2, R // 2 + 3
    # falda: tronco ancho y peludo, más ancho abajo
    tw = 4.0 + (yy - top) / max(1, H - top) * 2.0
    trunk = (np.abs(xx - cx) <= tw) & (yy >= top) & (yy < H - 1)
    sk = P['deadleaf'] if state == 'sano' else P['ash']
    img[trunk] = col(sk[4])
    img[trunk & (((xx * 2 + yy * 3) % 5) < 2)] = col(sk[3])
    img[trunk & (((xx * 3 - yy * 2) % 7) == 0)] = col(sk[5])
    img[trunk & (xx > cx + tw - 2)] = col(sk[1])
    if stub:
        img[top:top + 3][trunk[top:top + 3]] = col(sk[1])
        return outline(img)
    # roseta: hojas lanceoladas radiales en un disco aplastado
    if state == 'sano':
        ramp = ['#4d6a4a', '#7b9670', '#a7bc9a', '#cfdcc4', '#eef4e6']
    else:
        ramp = [P['deadleaf'][1], P['deadleaf'][2], P['deadleaf'][3], P['deadleaf'][4], P['deadleaf'][5]]
    n = 16
    for k in range(n):
        a = 2 * np.pi * k / n + rng.uniform(-0.1, 0.1)
        L = R * rng.uniform(0.85, 1.0)
        droop = 0 if state == 'sano' else 6
        leaf = np.zeros((H, W), bool)
        for t in np.linspace(0, 1, 22):
            x = cx + np.cos(a) * L * t
            y = top + np.sin(a) * L * t * 0.55 + droop * t * t
            leaf |= ((xx - x) ** 2 + (yy - y) ** 2) <= (2.6 * np.sin(np.pi * min(1, t + 0.15)) + 0.5) ** 2
        back = np.sin(a) < 0
        sh_ = shade(leaf, ramp, ambient=0.35 if back else 0.5)
        img[leaf] = sh_[leaf]
    cen = ellipse(W, H, cx, top, 3, 2)
    img[cen] = col(ramp[4])
    if state == 'sano' and seed % 3 == 0:
        for dx in (-2, 2):
            img[top - 3:top - 1, cx + dx - 1:cx + dx + 1] = C('gold', 4)
    return outline(img)


def apacheta():
    """Apacheta: montículo de piedras apiladas que marca el paso."""
    img = new(22, 22)
    for (cx, cy, r) in [(11, 18, 8), (11, 12, 6), (11, 7, 4.5), (11, 3, 2.8)]:
        m = ellipse(22, 22, cx, cy, r, r * 0.65)
        sh_ = shade(m, P['stone'][1:6], ambient=0.25)
        img[m] = sh_[m]
    return outline(img)


def haze(img, a=0.28):
    """Velo de neblina gris para el páramo enfermo."""
    H, W = img.shape[:2]
    rng = np.random.default_rng(3)
    n = ndi.gaussian_filter(rng.uniform(0, 1, (H // 8 + 2, W // 8 + 2)), 1.5)
    n = ndi.zoom(n, 8, order=1)[:H, :W]
    n = (n - n.min()) / (n.max() - n.min() + 1e-6)
    k = (a * (0.4 + 0.6 * n))[..., None]
    fog = np.array([150, 140, 145], float)
    out = img.copy().astype(float)
    out[..., :3] = out[..., :3] * (1 - k) + fog * k
    return out.astype(np.uint8)


def cumbre_objects(state, info=None):
    sick = state != 'sano'
    objs = []
    rng = np.random.default_rng(21)
    pts = []
    free = None
    if info is not None:
        free = ~(info['path'] | info['wat'] | info['face'])
    k = 0
    while len(pts) < 26 and k < 2000:
        k += 1
        x, y = int(rng.integers(8, 630)), int(rng.integers(40, 366))
        if free is not None and not free[max(0, y - 10):y + 18, max(0, x - 14):x + 14].all():
            continue
        if any((x - a) ** 2 + (y - b_) ** 2 < 26 ** 2 for a, b_ in pts):
            continue
        pts.append((x, y))
    for i, (x, y) in enumerate(pts):
        f = frailejon(state, i, stub=sick and i % 3 == 0)
        objs.append((f, x - f.shape[1] // 2, y, 14))
    for x, y in [(150, 300), (360, 120), (560, 210), (60, 160), (470, 80)]:
        objs.append((flora.rock(state), x, y, 10))
        objs.append((flora.rock(state), x + 14, y + 4, 8))
    objs.append((apacheta(), 236, 118, 14))
    objs.append((scene2.sign(), 196, 240, 10))
    import dress as D
    snow = D.tiles(info, 'a')
    objs = D.scatter(objs, info, state, [(D.pajonal, 8, 7), (D.puya, 12, 2), (D.big_rock, 18, 1), (D.rock, 10, 1),
                                         (D.pebbles, 0, 1), (D.flower_patch, 0, 2)],
                     clusters=28, per=(3, 6), seed=62, where=~snow, decal=(D.pebbles, D.flower_patch))
    objs = D.scatter(objs, info, state, [(D.big_rock, 18, 2), (D.rock, 10, 3), (D.pebbles, 0, 2)],
                     clusters=6, per=(2, 4), seed=63, where=snow, decal=(D.pebbles,))
    return objs


ZONE_NPC = {
    'costa': [('pescador', 'south-west', 452, 214), ('pescadora', 'south', 250, 292), ('nino_costa', 'east', 206, 304)],
    'cuenca': [('petrolero', 'south', 430, 160), ('julian', 'south-east', 70, 330)],
    'llanura': [('campesina', 'south', 150, 196), ('campesino', 'south-west', 470, 248), ('nina_llanura', 'east', 330, 232)],
    'cumbre': [('abuela_paramo', 'south', 270, 140), ('julian', 'south-west', 220, 252)],
}


def npcs(zone):
    import npc_vars
    out = []
    for name, d, x, yb in ZONE_NPC.get(zone, []):
        s = scene.trim(npc_vars.sprite(name, d))
        out.append((s, x - s.shape[1] // 2, yb, 18))
    return out


def render(zone, state, extra=(), sign_=None):
    specs = {'costa': (lambda st: COSTA, costa_objects), 'cuenca': (lambda st: CUENCA, cuenca_objects),
             'llanura': (llanura, llanura_objects), 'cumbre': (cumbre, cumbre_objects)}
    specf, objf = specs[zone]
    img = scene2.render(state, actors=npcs(zone) + list(extra), spec=specf(state), objects=objf, sign=sign_)
    if zone == 'cumbre' and state != 'sano':
        img = haze(img)
    return img


def hero(x, y, d='south'):
    s = scene.trim(np.array(Image.open(f'final/chars/ilan_{d}.png')))
    return (s, x - s.shape[1] // 2, y, 22)


def monster(name, x, yb):
    s = scene.trim(np.array(Image.open(f'pl/monsters/{name}.png')))
    return (s, x - s.shape[1] // 2, yb, 60)


if __name__ == '__main__':
    import sys
    for z in (sys.argv[1:] or ('costa', 'cuenca', 'llanura', 'cumbre')):
        for st in ('enfermo', 'sano'):
            im = render(z, st)
            px.save(im, f'out2/z_{z}_{st}.png', scale=2)
