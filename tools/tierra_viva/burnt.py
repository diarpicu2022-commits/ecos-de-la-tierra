"""Árbol quemado sacado del propio árbol sano: misma silueta y mismo pie, para
que asiente en el suelo igual. Tronco calcinado con grietas de brasa, ramas
desnudas hacia donde estaba la copa y solo restos de hojas secas."""
import numpy as np
from scipy import ndimage as ndi
from pal import P
from px import col, outline

CHAR = ['#0e0b12', '#1c1620', '#2b2230', '#3d3240', '#544650']
DEAD = ['#2a1d1c', '#43302a', '#5e4535', '#7a5c42', '#977653']


def _lum(a):
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def burnt_from(tree, seed=3):
    t = tree.copy()
    H, W = t.shape[:2]
    a = t[..., 3] > 0
    r, g, b = [t[..., i].astype(int) for i in range(3)]
    black = a & (r + g + b < 60)
    leaf = a & ~black & (g > r + 6)
    trunk = a & ~black & ~leaf
    out = np.zeros_like(t)
    lum = _lum(t.astype(float))
    # tronco: rampa de carbón por luminancia
    if trunk.any():
        q = np.quantile(lum[trunk], [0.25, 0.5, 0.75])
        idx = np.digitize(lum, q) + 1
        for k in range(1, 5):
            out[trunk & (idx == k)] = col(CHAR[k])
    yy, xx = np.indices((H, W))
    crack = trunk & (((xx * 3 + yy) % 11) == 0) & (yy > H * 0.75)
    out[crack] = col(P['fire'][3])
    out[crack & (yy % 2 == 0)] = col(P['fire'][4])
    # ramas: del arranque del tronco a los centros de los racimos de la copa
    ty = np.where(trunk.any(1))[0]
    top_trunk = ty.min() if len(ty) else H * 0.7
    tx = int(np.median(np.where(trunk[top_trunk + 2])[0])) if trunk[top_trunk + 2].any() else W // 2
    lab, n = ndi.label(ndi.binary_erosion(leaf, iterations=3))
    centers = ndi.center_of_mass(leaf, lab, range(1, n + 1)) if n else []
    centers = sorted(centers, key=lambda c: -ndi.sum(leaf, lab, 0) if False else c[0])
    rng = np.random.default_rng(seed)
    if len(centers) < 5:
        ys, xs = np.where(leaf)
        pick = rng.choice(len(ys), size=min(7, len(ys)), replace=False)
        centers = [(ys[k], xs[k]) for k in pick]
    branch = np.zeros((H, W), bool)
    for cy, cx in centers[:9]:
        y0, x0 = top_trunk + 4, tx + rng.integers(-3, 4)
        steps = int(np.hypot(cy - y0, cx - x0)) + 1
        for s in range(steps):
            f = s / steps
            y = y0 + (cy - y0) * f
            x = x0 + (cx - x0) * f + np.sin(f * 3.1) * 3
            th = 2 if f < 0.55 else 1
            branch[max(0, int(y)):int(y) + th, max(0, int(x)):int(x) + th] = True
    branch &= a | ndi.binary_dilation(a, iterations=2)
    out[branch] = col(CHAR[2])
    out[branch & np.roll(~branch, 1, 0)] = col(CHAR[3])
    # restos de hojas secas en manchas, más abajo y en los extremos
    noise = ndi.gaussian_filter(rng.random((H, W)), 3)
    keep = leaf & (noise > np.quantile(noise[leaf], 0.72))
    if keep.any():
        q = np.quantile(lum[keep], [0.3, 0.6, 0.85])
        idx = np.digitize(lum, q)
        for k in range(4):
            out[keep & (idx == k)] = col(DEAD[k + 1])
    emb = keep & (rng.random((H, W)) < 0.04)
    out[emb] = col(P['fire'][4])
    out = outline(out)
    return out


def soot(w=60, h=14, seed=1):
    """Hollín al pie del árbol quemado: tierra quemada tramada, sin puntos rojos."""
    img = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.indices((h, w))
    d = ((xx + 0.5 - w / 2) / (w / 2)) ** 2 + ((yy + 0.5 - h / 2) / (h / 2)) ** 2
    img[d <= 0.5] = col(WARM_CHAR[1])
    img[(d > 0.5) & (d <= 1) & ((xx + yy) % 2 == 0)] = col(WARM_CHAR[2])
    rng = np.random.default_rng(seed)
    for _ in range(5):
        y, x = rng.integers(2, h - 2), rng.integers(8, w - 8)
        if d[y, x] < 0.7:
            img[y, x] = col(P['fire'][2])
    return img


def scorch(w=46, h=12, seed=1):
    """Cerco de ceniza y tierra quemada al pie: lo que lo asienta en el suelo."""
    img = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.indices((h, w))
    d = ((xx + 0.5 - w / 2) / (w / 2)) ** 2 + ((yy + 0.5 - h / 2) / (h / 2)) ** 2
    rng = np.random.default_rng(seed)
    n = rng.random((h, w))
    img[(d <= 1) & (n > d * 0.9)] = col(P['ash'][1])
    img[(d <= 0.55) & (n > 0.25)] = col(P['ash'][0])
    img[(d <= 1) & (d > 0.3) & (n > 0.93)] = col(P['ash'][3])
    img[(d <= 0.8) & (n < 0.03)] = col(P['fire'][3])
    return img


# ---------------------------------------------------------------------------
# v2: el árbol quemado ES el árbol sano sin copa. Se queda con el mismo tronco y
# las mismas raíces (que ya asientan bien en el suelo) y se le dibujan ramas
# desnudas con el mismo estilo de sombreado. Carbón cálido, no negro azulado,
# para que case con la tierra quemada.
WARM_CHAR = ['#16110f', '#241a17', '#35271f', '#4a3729', '#604a36', '#7a6046']


def burnt_tree_v2(tree, seed=3):
    from px import shade, new
    H, W = tree.shape[:2]
    a = tree[..., 3] > 0
    r, g, b = [tree[..., i].astype(int) for i in range(3)]
    black = a & (r + g + b < 60)
    leaf = a & ~black & (g > r + 6)
    trunk = a & ~black & ~leaf
    # solo el tronco que llega al suelo, y solo donde es grueso (>= 8 px)
    lab, n = ndi.label(trunk)
    bottom = set(lab[-8:][lab[-8:] > 0].ravel())
    trunk = np.isin(lab, list(bottom))
    wide = np.where(trunk.sum(1) >= 8)[0]
    top = wide.min()
    trunk[:top] = False
    ys, xs = np.where(trunk)
    row = np.where(trunk[top + 3])[0]
    tx0, tx1 = row.min(), row.max()
    cx = (tx0 + tx1) / 2
    rng = np.random.default_rng(seed)
    m = np.zeros((H, W), bool)
    yy, xx = np.indices((H, W))

    def stroke(x0, y0, x1, y1, w0, w1):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 1.5) + 2
        for k in range(n + 1):
            f = k / n
            x = x0 + (x1 - x0) * f
            y = y0 + (y1 - y0) * f
            w = w0 + (w1 - w0) * f
            m[((xx - x) ** 2 + (yy - y) ** 2) <= (w / 2) ** 2] = True

    # prolongación del tronco hacia arriba
    trunk_top_y = max(18, top - 34)
    tw = (tx1 - tx0 + 1)
    stroke(cx, top + 4, cx + rng.uniform(-3, 3), trunk_top_y, tw * 0.9, tw * 0.45)

    def branch(x, y, ang, length, w, depth):
        x1 = x + np.cos(np.radians(ang)) * length
        y1 = y - np.sin(np.radians(ang)) * length
        x1 = np.clip(x1, 3, W - 4); y1 = np.clip(y1, 3, H - 4)
        stroke(x, y, x1, y1, w, max(1.2, w * 0.55))
        if depth > 0:
            for d_ang in (rng.uniform(18, 38), -rng.uniform(18, 38)):
                if rng.random() < 0.85:
                    branch(x1, y1, ang + d_ang, length * rng.uniform(0.55, 0.75), max(1.2, w * 0.6), depth - 1)

    base_y = top + 6
    for ang, ln, w in [(150, 26, 6), (125, 22, 5), (95, 24, 5), (62, 22, 5), (32, 26, 6)]:
        sy = rng.uniform(trunk_top_y + 4, base_y - 6) if ang in (150, 32) else trunk_top_y + rng.uniform(0, 8)
        branch(cx + rng.uniform(-2, 2), sy, ang + rng.uniform(-8, 8), ln * rng.uniform(0.9, 1.15), w, 2)
    keep_upper = yy <= top + 8
    # raíces que se abren y se hunden en la tierra
    by = H - 2
    for side in (-1, 1):
        for k, (dx, dy, w) in enumerate([(9, 1, 3.5), (6, -3, 3), (12, 0, 2.5)]):
            x0 = cx + side * (tw / 2 - 2)
            stroke(x0, by - 5 - k, x0 + side * dx, by + dy - k * 0.5, w, 1.3)
    body = (m & (keep_upper | ~trunk)) | trunk
    ramp = WARM_CHAR[1:]
    img = shade(body, ramp, light=(-0.7, -0.5, 0.5), ambient=0.12, blur=0.6, power=0.6)
    # vetas de la corteza y grietas con brasa en el tronco
    bark = body & (((xx * 2 + (yy // 3)) % 7) == 0) & (yy > trunk_top_y)
    img[bark] = col(WARM_CHAR[1])
    crack = trunk & (((xx * 5 + yy * 2) % 17) == 0) & (yy < H - 6)
    img[crack] = col(P['fire'][3])
    for _ in range(14):
        ys_, xs_ = np.where(m & (yy < top))
        if len(ys_):
            k = rng.integers(0, len(ys_))
            img[ys_[k], xs_[k]] = col(P['fire'][4] if rng.random() < 0.5 else P['fire'][3])
    # restos de hojas secas colgando de algunas puntas
    tips = m & ~ndi.binary_erosion(m, iterations=1) & (yy < top - 10)
    ys_, xs_ = np.where(tips)
    for k in rng.choice(len(ys_), size=min(10, len(ys_)), replace=False) if len(ys_) else []:
        y, x = ys_[k], xs_[k]
        for dy, dx in [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0)]:
            if 0 <= y + dy < H and 0 <= x + dx < W and rng.random() < 0.8:
                img[y + dy, x + dx] = col(DEAD[rng.integers(1, 4)])
    out = outline(img, color=WARM_CHAR[0])
    # las raíces del sano conservan su contorno original
    keep_black = black & ndi.binary_dilation(trunk, iterations=1) & (yy > top + 8)
    out[keep_black] = col(WARM_CHAR[0])
    return out
