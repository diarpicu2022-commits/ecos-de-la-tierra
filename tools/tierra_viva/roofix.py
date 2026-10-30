"""Repara tejados cortados por el borde superior del lienzo de PixelLab:
prolonga cada faldón hacia arriba con su misma pendiente y su textura hasta
cerrar la cumbrera, y le pone el contorno oscuro del propio sprite."""
import numpy as np


def runs(mask_row):
    xs = np.where(mask_row)[0]
    if not len(xs):
        return []
    out, s = [], xs[0]
    for a, b in zip(xs[:-1], xs[1:]):
        if b != a + 1:
            out.append((s, a)); s = b
    out.append((s, xs[-1]))
    return out


def fix_top(spr, pad=40):
    a = spr[..., 3] > 0
    if a[0].sum() == 0:
        return spr
    H, W = a.shape
    # pendiente de los bordes en las primeras filas
    ls, rs = [], []
    for y in range(0, 8):
        xs = np.where(a[y])[0]
        if len(xs):
            ls.append(xs.min()); rs.append(xs.max())
    sl = max(1, int(round(np.mean(np.diff(ls)) * -1))) if len(ls) > 2 and np.mean(np.diff(ls)) < -0.3 else 1
    sr = max(1, int(round(np.mean(np.diff(rs))))) if len(rs) > 2 and np.mean(np.diff(rs)) > 0.3 else 1
    sl, sr = min(sl, 3), min(sr, 3)
    lum = spr[..., :3].astype(int).sum(-1)
    dark = spr[a][np.argmin(lum[a])]
    out = np.zeros((H + pad, W, 4), np.uint8)
    out[pad:] = spr
    prev = [(l, r) for l, r in runs(a[0])]
    y = pad - 1
    while prev and y >= 0:
        new = []
        for l, r in prev:
            l2, r2 = l + sl, r - sr
            if r2 - l2 < 1:
                continue
            new.append((l2, r2))
            # textura: copia la fila de dos más abajo (misma columna)
            src = out[y + 2, l2:r2 + 1].copy()
            src[src[..., 3] == 0] = out[y + 1, l2:r2 + 1][src[..., 3] == 0]
            out[y, l2:r2 + 1] = src
            out[y, l2] = dark; out[y, r2] = dark
        prev = new
        y -= 1
    # cumbrera: el último tramo, oscuro
    rows = np.where(out[..., 3].any(1))[0]
    top = rows.min()
    out[top][out[top, :, 3] > 0] = dark
    return out[top:]
