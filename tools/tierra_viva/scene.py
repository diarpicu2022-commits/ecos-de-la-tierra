"""Escenas de muestra a 640x360: mapa con objetos, personaje y piezas de interfaz."""
import numpy as np
from PIL import Image, ImageSequence
from pal import P
from px import new, col, blit
import world, ui, font

W, H = 640, 360


def load(path, frame=0):
    im = Image.open(path)
    if getattr(im, 'n_frames', 1) > 1:
        im.seek(frame)
    return np.array(im.convert('RGBA'))


def trim(a):
    ys, xs = np.where(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def dialog(img, name, lines, portrait=None):
    """Caja de diálogo: papel abajo, chapa con el nombre y retrato opcional."""
    bx, by, bw, bh = 12, H - 84, W - 24, 76
    blit(img, ui.textbox(bw, bh), bx, by)
    tx = bx + 16
    if portrait is not None:
        ph, pw = portrait.shape[:2]
        frame = ui.box(pw + 8, ph + 8, P['paper'][3], P['wood'][1], inner=P['paper'][2], radius=2)
        blit(frame, portrait, 4, 4)
        blit(img, frame, bx + 10, by + (bh - ph - 8) // 2)
        tx = bx + pw + 28
    tag = ui.box(font.width(name) + 16, 17, P['eco'][1], P['ink'][0], inner=P['eco'][2], hi=P['eco'][3], radius=2)
    ui.text(tag, name, 8, 2, P['ui'][6], P['eco'][0])
    blit(img, tag, tx - 4, by - 9)
    for i, l in enumerate(lines):
        ui.text(img, l, tx, by + 14 + i * 15, P['ink'][1], P['paper'][2])
    ui.text(img, '▼', bx + bw - 20, by + bh - 18, P['rust'][2])
    return img
