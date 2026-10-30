"""Motor de mapas v2 «Tierra Viva».

Cambio de método respecto a world.py: nada sale de un campo de ruido. El mapa
se escribe por casillas de 16 px (como un tilemap de verdad) y cada material se
convierte en una máscara de píxeles con esquinas redondeadas por morfología
(apertura + cierre con un disco). Así los bordes rectos son rectos y las
esquinas son curvas limpias, como en Minish Cap, y cada casilla depende solo de
sus 8 vecinas: se puede trasladar a un autotile de Godot sin perder nada.

Capas, de abajo arriba:
  1. Hierba (textura propia de 32x32).
  2. Camino de tierra con borde oscuro y briznas que lo pisan.
  3. Agua hundida: orilla de tierra al norte, sombra, espuma y destellos.
  4. Mesetas (altura 1): superficie + cara de roca de una casilla al sur,
     escaleras y labio de luz.
  5. Hierba alta, flores, decorado y objetos con sombra, ordenados por la base.
"""
import numpy as np
from scipy import ndimage as ndi
from pal import R

T = 16


def hexrgba(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], np.uint8)


TURBID = ['#1f2a2c', '#2c3a3a', '#3b4a48', '#4b5a55', '#5f6d66', '#7d877c', '#a3a898']
SICK_SAND = ['#4a4252', '#645c6b', '#827a88', '#a39ca6', '#c7c1c6']


OIL_WATER = ['#07050c', '#110c1a', '#1b1428', '#261d36', '#3a2c4c', '#5a3f8c', '#3f7f86']
PLASTIC_WATER = ['#1d2a33', '#2a3b45', '#3a4d57', '#4b5f68', '#61757b', '#839393', '#b5bfbb']
SLUDGE_GRASS = ['#1f1d14', '#2b2a19', '#3a3820', '#4b4826', '#5d592d', '#77713a', '#938b4c']


def palette(state, region='bosque'):
    p = {k: [hexrgba(c) for c in v] for k, v in R.items()}
    if state != 'sano' and region == 'cuenca':
        p['water'] = [hexrgba(c) for c in OIL_WATER]
        p['grass'] = [hexrgba(c) for c in SLUDGE_GRASS]
        p['dirt'] = [hexrgba(c) for c in R['ash']]
        p['sand'] = [hexrgba(c) for c in SICK_SAND]
        return p
    if state != 'sano' and region == 'costa':
        p['water'] = [hexrgba(c) for c in PLASTIC_WATER]
        dg = [hexrgba(c) for c in R['drygrass']]
        p['grass'] = [dg[0], dg[0], dg[1], dg[2], dg[3], dg[4], dg[5]]
        p['sand'] = [hexrgba(c) for c in ['#7d7466', '#988e7d', '#b0a690', '#c4baa2', '#d6cdb6']]
        return p
    if region == 'cumbre':
        # páramo: pajonal verde oliva y dorado; la 'arena' es nieve (sano) o
        # pedregal desnudo del glaciar derretido (enfermo)
        if state == 'sano':
            p['grass'] = [hexrgba(c) for c in ['#1c2f2a', '#2a4434', '#3d5c3a', '#587a42', '#7a954c', '#a3b45e', '#cdd17c']]
            p['sand'] = [hexrgba(c) for c in ['#7d8fb8', '#a9bbd9', '#cfdcef', '#e9f1fa', '#ffffff']]
            return p
        p['grass'] = [hexrgba(c) for c in ['#2a2226', '#3d302c', '#56432f', '#6e5838', '#8a7044', '#a58a55', '#bea56a']]
        p['sand'] = [hexrgba(c) for c in ['#3e3943', '#57505a', '#726a72', '#8f878c', '#aca4a6']]
        p['water'] = [hexrgba(c) for c in TURBID]
        p['dirt'] = [hexrgba(c) for c in ['#2a2226', '#3d322f', '#54463d', '#6f5f50', '#8c7a64', '#a8957a', '#c2b092']]
        return p
    if state != 'sano':
        dg = [hexrgba(c) for c in R['drygrass']]
        p['grass'] = [dg[0], dg[0], dg[1], dg[2], dg[2], dg[3], dg[4]]
        p['water'] = [hexrgba(c) for c in TURBID]
        p['leafg'] = p['grass']
        p['dirt'] = [hexrgba(c) for c in ['#2a2226', '#3d322f', '#54463d', '#6f5f50', '#8c7a64', '#a8957a', '#c2b092']]
        p['sand'] = [hexrgba(c) for c in SICK_SAND]
        p['wall'] = [hexrgba(c) for c in R['ash'][1:6]]
        wd = [hexrgba(c) for c in R['wood']]
        p['wood'] = [wd[0], wd[0], wd[1], wd[2], wd[3], wd[4]]
    return p


# --- máscaras -----------------------------------------------------------------

def disk(r):
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r + r * 0.8


def up(tiles):
    return np.kron(np.asarray(tiles, bool), np.ones((T, T), bool))


def rounded(tiles, r, sigma=0):
    """Casillas -> máscara de píxeles con esquinas convexas y cóncavas de radio r.
    Con sigma, además se alisa (desenfoque + umbral): curvas orgánicas pero de
    borde limpio, sin escalones."""
    m = up(tiles)
    if sigma:
        pad = int(3 * sigma) + 2
        mm = np.pad(m.astype(float), pad, mode='edge')
        mm = ndi.gaussian_filter(mm, sigma) > 0.5
        m = mm[pad:-pad, pad:-pad]
    pad = r + 2
    m = np.pad(m, pad, mode='edge')
    d = disk(r)
    m = ndi.binary_opening(m, d)
    m = ndi.binary_closing(m, d)
    return m[pad:-pad, pad:-pad]


def shift(m, dy, dx, fill=False):
    out = np.full_like(m, fill)
    H, W = m.shape
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = m[ys, xs]
    return out


def edge(m, n=1):
    """Píxeles de m a distancia <= n de fuera (4-vecindad)."""
    return m & ~ndi.binary_erosion(m, iterations=n, border_value=1)


# --- texturas -----------------------------------------------------------------

def tile_tex(h, w, tex):
    th, tw = tex.shape[:2]
    return np.tile(tex, (h // th + 1, w // tw + 1, 1))[:h, :w]


def grass_tex(P):
    """32x32. Base media con matas en V sobre rejilla con desfase; luz arriba,
    sombra abajo, como la hierba de Minish Cap: regular pero no mecánica."""
    g = P['grass']
    t = np.zeros((32, 32, 4), np.uint8)
    t[:] = g[4]
    V = [(0, 0, 3), (2, 0, 3), (1, 1, 2), (0, -1, 5), (2, -1, 5)]  # dx, dy, tono
    V2 = [(0, 0, 3), (1, 1, 3), (2, 0, 3), (3, 1, 3), (4, 0, 3), (1, -1, 5), (3, -1, 5)]
    seeds = [(3, 4, V), (19, 2, V2), (11, 12, V), (27, 13, V), (5, 20, V2), (21, 22, V),
             (14, 28, V), (29, 29, V2)]
    for sx, sy, motif in seeds:
        for dx, dy, k in motif:
            t[(sy + dy) % 32, (sx + dx) % 32] = g[k]
    for x, y in [(9, 6), (25, 8), (2, 14), (17, 17), (30, 21), (9, 25), (24, 30)]:
        t[y, x] = g[5]
    for x, y in [(15, 5), (7, 16), (26, 25), (1, 29)]:
        t[y, x] = g[3]
    return t


def dirt_tex(P):
    d = P['dirt']
    t = np.zeros((32, 32, 4), np.uint8)
    t[:] = d[4]
    rng = np.random.default_rng(11)
    for _ in range(26):
        x, y = rng.integers(0, 32, 2)
        t[y, x] = d[3]
    for x, y in [(5, 6), (20, 3), (13, 17), (27, 22), (8, 27), (24, 12)]:   # guijarros
        t[y, x] = d[5]; t[y, (x + 1) % 32] = d[5]; t[(y + 1) % 32, x] = d[3]; t[(y + 1) % 32, (x + 1) % 32] = d[3]
    return t


def water_tex(P, frame=0):
    w = P['water']
    t = np.zeros((32, 32, 4), np.uint8)
    t[:] = w[2]
    # bandas suaves de profundidad cada 8 filas, y olas cortas que se desplazan
    for y in range(32):
        if (y // 4) % 4 == 1:
            t[y, (np.arange(32) + y) % 4 == 0] = w[3]
    waves = [(2, 3, 4), (18, 5, 3), (10, 13, 4), (26, 15, 3), (4, 22, 3), (20, 25, 4), (12, 29, 3)]
    for x, y, n in waves:
        for i in range(n):
            t[y, (x + i + frame * 2) % 32] = w[4]
        t[y - 1, (x + 1 + frame * 2) % 32] = w[5]
    return t


def paint_water(img, wat, P, frame=0):
    """Profundidad por distancia a la orilla: bajío claro, medio, fondo oscuro,
    con transiciones tramadas; destellos solo en el agua abierta."""
    w = P['water']
    d = ndi.distance_transform_edt(wat)
    yy, xx = np.indices(wat.shape)
    chk = (xx + yy) % 2 == 0
    img[wat] = w[2]
    img[wat & (d <= 9)] = w[3]
    img[wat & (d > 9) & (d <= 10) & chk] = w[3]
    img[wat & (d <= 4)] = w[4]
    img[wat & (d > 4) & (d <= 5) & chk] = w[4]
    img[wat & (d <= 1.5)] = w[1]
    # destellos: rayitas horizontales que derivan con el cuadro
    open_ = wat & (d > 5)
    rng = np.random.default_rng(3)
    ys, xs = np.where(open_)
    if len(ys):
        for k in rng.choice(len(ys), size=max(1, len(ys) // 90), replace=False):
            y, x = ys[k], xs[k] + frame * 2
            n = 2 + (k % 3)
            for i in range(n):
                if 0 <= x + i < wat.shape[1] and open_[y, min(x + i, wat.shape[1] - 1)]:
                    img[y, x + i] = w[5]
            if 0 <= x + 1 < wat.shape[1] and y > 0 and open_[y - 1, x + 1] and k % 2:
                img[y - 1, x + 1] = w[6]


# --- dibujo de capas ------------------------------------------------------------

def paint(img, m, c):
    img[m] = c


def render(spec, state='sano', frame=0, seed=1):
    P = palette(state, spec.get('region', 'bosque'))
    rows = spec['ground']
    Hn, Wn = len(rows), len(rows[0])
    H, W = Hn * T, Wn * T
    G = np.array([list(r) for r in rows])
    LV = np.array([[int(c) for c in r] for r in spec['height']])
    img = np.zeros((H, W, 4), np.uint8)
    img[:] = tile_tex(H, W, grass_tex(P))

    # ---------- arena de playa
    sand_t = np.isin(G, ['a'])
    if sand_t.any():
        sm = rounded(sand_t, 6, sigma=10)
        sd = P['sand']
        yy0, xx0 = np.indices(sm.shape)
        img[sm] = sd[3]
        rr = np.random.default_rng(seed + 31).random(sm.shape)
        img[sm & (rr < 0.05)] = sd[2]
        img[sm & (rr > 0.97)] = sd[4]
        img[sm & ((xx0 * 3 + yy0 * 7) % 41 == 0)] = sd[1]
        img[edge(sm, 1)] = sd[1]
        img[edge(sm, 3) & ~edge(sm, 1)] = sd[2]

    # ---------- camino
    path_t = np.isin(G, list('pSBc'))
    path = rounded(path_t, 4, sigma=9)
    rng = np.random.default_rng(seed)
    # bocados de hierba que invaden el borde: borde orgánico pero limpio
    ey, ex = np.where(edge(path, 1))
    bite = np.zeros_like(path)
    yy, xx = np.indices(path.shape)
    if len(ey):
        for k in rng.choice(len(ey), size=0, replace=False):
            r = rng.uniform(1.6, 3.2)
            y0, x0 = ey[k], ex[k]
            sl = (slice(max(0, y0 - 4), y0 + 5), slice(max(0, x0 - 4), x0 + 5))
            bite[sl] |= ((yy[sl] - y0) ** 2 + (xx[sl] - x0) ** 2) <= r * r
    path &= ~bite
    path = ndi.binary_opening(path, disk(1))
    d = ndi.distance_transform_edt(path)
    img[path] = tile_tex(H, W, dirt_tex(P))[path]
    chk = (xx + yy) % 2 == 0
    # rodadas: las dos curvas de nivel a media distancia del borde
    rut = path & (d > 6.5) & (d <= 8) & ~np.isin(G, list('cB')).repeat(T, 0).repeat(T, 1)
    img[rut & chk] = P['dirt'][3]
    img[path & (d > 6) & (d <= 6.5)] = img[path & (d > 6) & (d <= 6.5)]
    # centro gastado, más claro, tramado en su borde
    img[path & (d > 11)] = P['dirt'][5]
    img[path & (d > 10) & (d <= 11) & chk] = P['dirt'][5]
    img[edge(path, 1)] = P['dirt'][2]
    img[edge(path, 2) & ~edge(path, 1)] = P['dirt'][3]
    # sombra de la hierba sobre el borde norte del camino
    img[path & shift(~path, 2, 0, True) & ~edge(path, 1)] = P['dirt'][3]
    # manchas de tierra de dos tonos (baja frecuencia, borde tramado): rompen el color plano
    nz = ndi.gaussian_filter(rng.random((H // 4 + 2, W // 4 + 2)), 2.0)
    nz = ndi.zoom(nz, 4, order=1)[:H, :W]
    hi_, lo_ = np.quantile(nz, 0.82), np.quantile(nz, 0.22)
    img[path & (d > 3) & (nz > hi_)] = P['dirt'][5]
    img[path & (d > 3) & (nz > hi_ - 0.01) & (nz <= hi_) & chk] = P['dirt'][5]
    # bordillo de piedrecitas a lo largo de los dos bordes, cada pocos píxeles
    ring = path & (d > 1.5) & (d <= 3.2)
    ys, xs = np.where(ring)
    for k in range(0, len(ys), 1):
        y, x = ys[k], xs[k]
        if (x * 5 + y * 3) % 23 == 0 and y < H - 2 and x < W - 3:
            img[y, x:x + 2] = P['stone'][4]
            img[y + 1, x:x + 2] = P['stone'][2]
    # piedras sueltas con luz y sombra
    ys, xs = np.where(path & (d > 3) & (yy < H - 3) & (xx < W - 4))
    for k in rng.choice(len(ys), size=len(ys) // 260, replace=False) if len(ys) else []:
        y, x = ys[k], xs[k]
        w = 2 + (k % 2)
        img[y, x:x + w] = P['stone'][4]
        img[y + 1, x:x + w] = P['stone'][2]
        img[y + 1, x + w] = P['dirt'][2]
    # briznas que pisan el borde: rompen la línea sin ensuciarla
    ey, ex = np.where(edge(path, 1) & shift(~path, -1, 0) )
    for k in rng.choice(len(ey), size=min(len(ey) // 14, 400), replace=False) if len(ey) else []:
        y, x = ey[k], ex[k]
        for dx, dy, kk in [(0, 0, 3), (1, -1, 4), (2, 0, 3), (1, 1, 2)]:
            if 0 <= y + dy < H and 0 <= x + dx < W:
                img[y + dy, x + dx] = P['grass'][kk]

    # ---------- plaza empedrada
    plaza_t = np.isin(G, ['c'])
    if plaza_t.any():
        plaza = rounded(plaza_t, 14, sigma=16)
        paint_plaza(img, plaza, P, seed)
        path = path | plaza

    # ---------- agua hundida
    wat_t = np.isin(G, list('wB'))
    wat = rounded(wat_t, 8, sigma=12)
    land = ~wat
    beach = ndi.binary_dilation(rounded(np.isin(G, ['a']), 6, sigma=10), iterations=3) if np.isin(G, ['a']).any() else np.zeros_like(wat)
    paint_water(img, wat, P, frame)
    if beach.any():
        # playa: sin talud; el agua llega en bajío claro con espuma en ondas
        bw = wat & ndi.binary_dilation(beach, iterations=10)
        yy0, xx0 = np.indices(wat.shape)
        dd = ndi.distance_transform_edt(wat)
        img[bw & (dd <= 3)] = P['water'][5]
        img[bw & (dd > 3) & (dd <= 6) & (((xx0 // 3 + yy0 + frame) % 4) != 0)] = P['water'][4]
        img[bw & (dd > 8) & (dd <= 9) & ((xx0 + frame * 2) % 7 < 4)] = P['water'][5]
    land_nb = land & ~beach
    # orilla norte: cara de tierra de 6 px que baja hasta el agua
    bank = np.zeros_like(wat)
    for k in range(1, 7):
        bank |= wat & shift(land_nb, k, 0)
    face_rows = np.zeros_like(wat)
    for k in range(1, 3):
        face_rows |= wat & shift(land_nb, k, 0)
    yy, xx = np.indices(wat.shape)
    img[bank] = P['dirt'][2]
    img[bank & ~face_rows & (((xx * 3) // 4) % 4 == 0)] = P['dirt'][1]
    img[face_rows] = P['dirt'][3]
    img[bank & shift(land, 1, 0) & (xx % 6 < 2)] = P['grass'][3]   # raíces y briznas que cuelgan
    under = wat & ~bank & shift(bank, 1, 0)
    img[under] = P['water'][0]
    img[wat & ~bank & shift(bank, 2, 0) & ~under] = P['water'][1]
    # orillas laterales y sur: talud de tierra de 1 px en el lado de tierra
    shore = land_nb & ndi.binary_dilation(wat) & ~shift(wat, -1, 0)
    img[shore] = P['dirt'][2]
    img[land_nb & shift(wat, -1, 0) & ~shift(wat, -2, 0)] = P['grass'][2]

    # ---------- bancales de cultivo: tierra arada en surcos
    farm = rounded(np.isin(G, ['u']), 2)
    if farm.any():
        d_ = P['dirt']
        yy, xx = np.indices(farm.shape)
        img[farm] = d_[3]
        img[farm & (yy % 6 == 0)] = d_[2]
        img[farm & (yy % 6 == 1)] = d_[1]
        img[farm & (yy % 6 == 3)] = d_[4]
        img[farm & (yy % 6 == 4) & ((xx * 7) % 9 == 0)] = d_[5]
        img[edge(farm, 1)] = d_[1]
        path = path | farm

    # ---------- cotas: se pintan de la más baja a la más alta
    top_all = np.zeros(path.shape, bool)
    face_all = np.zeros(path.shape, bool)
    for k in range(1, int(LV.max()) + 1):
        top, face = paint_level(img, LV >= k, G, wat, P, frame, seed + k)
        top_all |= top
        face_all |= face
    return img, dict(path=path, wat=wat, top=top_all, face=face_all, G=G, P=P, farm=farm)


def organic_top(hi, G, seed, amp=12.0):
    """Borde de cota natural: distancia con signo al borde de las casillas,
    alisada, más un desplazamiento de baja frecuencia (entrantes y salientes de
    hasta ~9 px). Junto a las escaleras el desplazamiento se anula para que
    encajen."""
    m = up(hi)
    if m.all() or not m.any():
        return m
    d = ndi.distance_transform_edt(m) - ndi.distance_transform_edt(~m)
    d = ndi.gaussian_filter(d, 4)
    H, W = m.shape
    rng = np.random.default_rng(seed * 17 + 3)
    n = rng.uniform(-1, 1, (H // 24 + 3, W // 24 + 3))
    n = ndi.zoom(n, 24, order=3)[:H, :W]
    n = ndi.gaussian_filter(n, 6)
    n = n / (np.abs(n).max() + 1e-6)
    stairs = up(np.isin(G, ['S']))
    if stairs.any():
        ds = ndi.distance_transform_edt(~stairs)
        n = n * np.clip((ds - 6) / 40, 0, 1)
    top = (d + amp * n) > 0
    top = np.pad(top, 8, mode='edge')
    top = ndi.binary_closing(ndi.binary_opening(top, disk(5)), disk(5))[8:-8, 8:-8]
    return top


def paint_level(img, hi, G, wat, P, frame, seed):
    """Una cota: superficie + cara de roca al sur, escaleras, cascadas, labio."""
    face_t = np.zeros_like(hi)
    face_t[1:] = hi[:-1] & ~hi[1:]
    top = organic_top(hi, G, seed)
    face = shift(top, T, 0) & ~top
    # la cara cubre la casilla de debajo; sus extremos se redondean con la meseta
    st = rounded(np.isin(G, ['S']), 1)
    st = st & face
    fall = face & wat
    rock = face & ~st & ~fall
    s = P['stone']
    rel_full = np.zeros(rock.shape, int)
    for k in range(1, T + 1):
        rel_full[shift(top, k, 0) & face & (rel_full == 0)] = k
    r = rel_full
    yy, xx = np.indices(rock.shape)
    paint_rockface(img, rock, r, s, seed)
    # flecos de hierba que cuelgan sobre la roca
    gp = P['grass']
    hang = ((xx * 5) % 7)
    img[rock & (r <= 2) & (hang < 3)] = gp[3]
    img[rock & (r == 1) & (hang >= 3)] = gp[2]
    img[rock & (r == 3) & (hang == 0)] = gp[2]
    # cascada: donde la cara cruza el río, el agua cae en hilos
    if fall.any():
        w = P['water']
        img[fall] = w[3]
        img[fall & ((xx + frame) % 4 == 0)] = w[4]
        img[fall & ((xx * 3 + yy // 3 + frame) % 7 == 0)] = w[5]
        img[fall & (r <= 1)] = w[5]
        img[edge(fall, 1) & (shift(~fall, 0, 1) | shift(~fall, 0, -1))] = w[1]
        spray = shift(fall, 1, 0) & ~fall & wat
        for k in range(1, 4):
            sp = shift(fall, k, 0) & ~fall & wat & (((xx + yy + frame) % (k + 1)) == 0)
            img[sp] = w[5 if k < 3 else 4]
    # escaleras: peldaños de piedra clara
    if st.any():
        rs = np.zeros_like(r)
        for k in range(1, T + 1):
            rs[shift(top, k, 0) & st & (rs == 0)] = k
        img[st] = s[4]
        img[st & (rs % 4 == 0)] = s[2]
        img[st & (rs % 4 == 1)] = s[5]
        img[edge(st, 1) & ~shift(top, 1, 0)] = s[2]
    # sombra proyectada al pie de la cara, sobre la cota baja
    foot = shift(face, 1, 0) & ~face & ~top
    foot2 = shift(face, 2, 0) & ~face & ~top & ~foot
    for m in (foot, foot2):
        sel = m & ~wat
        img[sel] = np.array([darker_rgba(c, P) for c in img[sel]]) if sel.any() else img[sel]
    # bordes laterales de la meseta: canto oscuro hacia fuera
    side = top & (shift(~top, 0, 1) | shift(~top, 0, -1)) & ~shift(~top, -1, 0)
    img[side] = P['grass'][2]
    img[top & ~shift(top, 0, 2) & ~side & ~shift(~top, -1, 0) & shift(top, 0, 1)] = P['grass'][3]
    # labio: borde sur de la superficie, luz de 1 px y canto de 1 px
    lip = top & shift(face, -1, 0)
    img[lip] = P['grass'][6]
    img[top & shift(lip, -1, 0)] = P['grass'][5]
    # borde norte de la meseta (no se ve la cara): línea oscura en la cota baja
    img[~top & shift(top, -1, 0) & ~wat] = P['grass'][2]
    return top, face


def darker_rgba(c, P):
    """Baja un tono dentro de la rampa a la que pertenece el color."""
    for ramp in P.values():
        for i, rc in enumerate(ramp):
            if np.array_equal(rc, c):
                return ramp[max(0, i - 1)]
    return (c.astype(int) * 0.82).astype(np.uint8)


def paint_rockface(img, rock, r, s, seed=1):
    """Cara de acantilado hecha de bloques de roca (celdas de Voronoi), cada uno
    con luz arriba a la izquierda y sombra abajo: roca, no ladrillo."""
    H, W = rock.shape
    rng = np.random.default_rng(seed + 5)
    pts = []
    for y in range(-4, H + 8, 7):
        for x in range(-4, W + 8, 9):
            pts.append((y + rng.integers(-2, 3), x + rng.integers(-3, 4) + (4 if (y // 7) % 2 else 0)))
    pts = np.array(pts)
    ys, xs = np.where(rock)
    # vecino más cercano con un kd-tree barato
    from scipy.spatial import cKDTree
    tree = cKDTree(pts)
    d, idx = tree.query(np.c_[ys, xs], k=2)
    lab = np.full(rock.shape, -1)
    lab[ys, xs] = idx[:, 0]
    border = np.zeros_like(rock)
    border[ys, xs] = (d[:, 1] - d[:, 0]) < 1.3
    img[rock] = s[3]
    # luz y sombra por celda
    up_ = np.zeros_like(rock); up_[1:] = lab[1:] != lab[:-1]
    lf = np.zeros_like(rock); lf[:, 1:] = lab[:, 1:] != lab[:, :-1]
    img[rock & (up_ | lf)] = s[4]
    tone = rng.integers(0, 3, len(pts))
    dark_cells = np.isin(lab, np.where(tone == 0)[0]) & rock
    img[dark_cells & ~(up_ | lf)] = s[2]
    img[rock & border] = s[1]
    img[rock & (r <= 2)] = s[1]          # sombra bajo el labio de hierba
    img[rock & (r == 3)] = s[2]
    img[rock & (r >= T)] = s[0]          # pie
    img[rock & (r == T - 1)] = s[1]


def paint_plaza(img, m, P, seed=1):
    """Plaza con volumen: un poco elevada sobre la calle (escalón de piedra al
    sur con su sombra), bordillo de losas grandes, empedrado dentro y anillos
    de losa clara alrededor del centro de cada plaza."""
    s = P['stone']
    yy, xx = np.indices(m.shape)
    # escalón al sur: 4 px de cara de piedra bajo el borde, y sombra
    step = np.zeros_like(m)
    for k in range(1, 5):
        step |= shift(m, k, 0) & ~m
    img[step] = s[2]
    img[step & ~shift(m, 1, 0)] = s[1]
    img[step & (xx % 9 == 0)] = s[1]
    img[step & shift(m, 1, 0) & ~m] = s[4]
    sh_ = shift(step | m, 1, 0) & ~(step | m)
    img[sh_] = (img[sh_].astype(int) * 0.7).astype(np.uint8)
    img[sh_, 3] = 255
    paint_cobble(img, m, P, seed)
    # anillos claros alrededor del centro de cada plaza
    lab, n = ndi.label(m)
    for k in range(1, n + 1):
        ys, xs = np.where(lab == k)
        cy, cx = ys.mean(), xs.mean()
        rr = np.hypot((xx - cx) / 1.25, yy - cy)
        ring = (lab == k) & (((rr % 22) < 2.2) | (rr < 6))
        img[ring] = P['wall'][3] if 'wall' in P else s[4]
        img[ring & (((rr % 22) < 0.9))] = P['wall'][4] if 'wall' in P else s[5]
    # bordillo: losas grandes de 4 px y luz en el borde norte
    curb = m & (ndi.distance_transform_edt(m) <= 4)
    img[curb] = s[4]
    img[curb & (((xx // 7) + (yy // 7)) % 2 == 0)] = s[3]
    img[curb & (ndi.distance_transform_edt(m) <= 1)] = s[1]
    img[curb & ((xx % 7 == 0) | (yy % 7 == 0)) & (ndi.distance_transform_edt(m) > 1)] = s[2]


def paint_cobble(img, m, P, seed=1):
    """Empedrado: losas de Voronoi con junta oscura y luz arriba a la izquierda."""
    from scipy.spatial import cKDTree
    s = P['wall'] if 'wall' in P else P['stone']
    H, W = m.shape
    rng = np.random.default_rng(seed + 9)
    pts = np.array([(y + rng.integers(-2, 3), x + rng.integers(-2, 3) + (3 if (y // 6) % 2 else 0))
                    for y in range(-3, H + 6, 6) for x in range(-3, W + 6, 7)])
    ys, xs = np.where(m)
    d, idx = cKDTree(pts).query(np.c_[ys, xs], k=2)
    lab = np.full(m.shape, -1); lab[ys, xs] = idx[:, 0]
    joint = np.zeros_like(m); joint[ys, xs] = (d[:, 1] - d[:, 0]) < 1.2
    tone = rng.integers(0, 4, len(pts))
    img[m] = s[2]
    img[m & np.isin(lab, np.where(tone == 0)[0])] = s[1]
    img[m & np.isin(lab, np.where(tone == 3)[0])] = s[3]
    up_ = np.zeros_like(m); up_[1:] = lab[1:] != lab[:-1]
    img[m & up_ & ~joint] = s[3]
    img[m & joint] = s[0]
    img[edge(m, 1)] = P['stone'][1]
    img[edge(m, 2) & ~edge(m, 1)] = P['stone'][3]
