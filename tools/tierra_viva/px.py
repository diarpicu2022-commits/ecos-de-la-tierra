"""Herramientas de pixel art: lienzos, rejillas de caracteres, contorno selectivo y
sombreado por volumen para sprites construidos con formas."""
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, gaussian_filter
from pal import P, h

_ALL = [(name, ramp) for name, ramp in P.items()]
_DARK = {}
for name, ramp in _ALL:
    for i, c in enumerate(ramp):
        _DARK.setdefault(c[:3], (name, i))


def new(w, hgt):
    return np.zeros((hgt, w, 4), np.uint8)


def col(c):
    if isinstance(c, str):
        return np.array(h(c), np.uint8)
    return np.array(c, np.uint8)


def grid(rows, cmap):
    """Rejilla de caracteres -> imagen. '.' y ' ' son transparentes."""
    rows = [r for r in rows]
    hgt, w = len(rows), max(len(r) for r in rows)
    img = new(w, hgt)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in '. ':
                continue
            img[y, x] = col(cmap[ch])
    return img


def blit(dst, src, x, y, flip=False):
    if flip:
        src = src[:, ::-1]
    sh, sw = src.shape[:2]
    H, W = dst.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + sw), min(H, y + sh)
    if x0 >= x1 or y0 >= y1:
        return dst
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    m = s[..., 3] > 0
    dst[y0:y1, x0:x1][m] = s[m]
    return dst


def mask(img):
    return img[..., 3] > 0


def darker(c, steps=1):
    """Color del mismo material, `steps` tonos más oscuro (o tinta si no hay)."""
    key = tuple(int(v) for v in c[:3])
    if key in _DARK:
        name, i = _DARK[key]
        ramp = P[name]
        return np.array(ramp[max(0, i - steps)], np.uint8)
    return np.array(P['ink'][0], np.uint8)


def outline(img, color=None, sel=True, inner_steps=2, diag=False):
    """Contorno exterior de 1 px. Con `sel`, el contorno toma la tinta del material
    vecino (sel-out); el borde superior iluminado queda un tono más claro."""
    m = mask(img)
    out = img.copy()
    H, W = m.shape
    ink = np.array(P['ink'][0], np.uint8)
    nbrs = [(0, 1), (1, 0), (0, -1), (-1, 0)] + ([(1, 1), (-1, -1), (1, -1), (-1, 1)] if diag else [])
    for y in range(H):
        for x in range(W):
            if m[y, x]:
                continue
            found = None
            for dy, dx in nbrs:
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx]:
                    found = (dy, dx, img[yy, xx])
                    break
            if found is None:
                continue
            if color is not None:
                out[y, x] = col(color)
            elif sel:
                c = darker(found[2], 9)
                out[y, x] = c if found[0] != 1 else darker(found[2], 9)
            else:
                out[y, x] = ink
    return out


def shade(m, ramp, light=(-0.55, -0.75, 0.55), ambient=0.18, blur=0.8, power=0.5,
          bias=0.0, levels=None):
    """Sombrea una máscara como un volumen: altura = distancia al borde, luz arriba-izquierda,
    cuantizada a la rampa sin mezclas."""
    m = m.astype(bool)
    if not m.any():
        return new(m.shape[1], m.shape[0])
    d = distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1]
    hgt = d ** power
    if blur:
        hgt = gaussian_filter(hgt, blur)
    gy, gx = np.gradient(hgt)
    n = np.dstack([-gx, -gy, np.ones_like(gx) * 0.9])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    L = np.array(light, float)
    L /= np.linalg.norm(L)
    lam = np.clip((n * L).sum(axis=2), 0, 1)
    v = ambient + (1 - ambient) * lam + bias
    ramp = [col(c) for c in ramp]
    k = len(ramp) if levels is None else levels
    idx = np.clip((v * k).astype(int), 0, k - 1)
    out = new(m.shape[1], m.shape[0])
    for i in range(k):
        sel = m & (idx == i)
        out[sel] = ramp[min(i, len(ramp) - 1)]
    return out


def ellipse(W, H, cx, cy, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2 <= 1.0


def poly(W, H, pts):
    from PIL import ImageDraw
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=1)
    return np.array(im).astype(bool)


def to_pil(img):
    return Image.fromarray(img, 'RGBA')


def save(img, path, scale=1, bg=None):
    im = to_pil(img)
    if bg is not None:
        b = Image.new('RGBA', im.size, bg)
        b.alpha_composite(im)
        im = b
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)
    return im


def sheet(items, cols, pad=4, bg=(40, 36, 52, 255), scale=3):
    """Hoja de contacto para revisar: lista de imágenes RGBA numpy."""
    cw = max(i.shape[1] for i in items) + pad
    ch = max(i.shape[0] for i in items) + pad
    rows = (len(items) + cols - 1) // cols
    canvas = new(cw * cols + pad, ch * rows + pad)
    canvas[:] = bg
    for k, it in enumerate(items):
        x = pad + (k % cols) * cw
        y = pad + (k // cols) * ch
        blit(canvas, it, x, y)
    return to_pil(canvas).resize(((cw * cols + pad) * scale, (ch * rows + pad) * scale), Image.NEAREST)
