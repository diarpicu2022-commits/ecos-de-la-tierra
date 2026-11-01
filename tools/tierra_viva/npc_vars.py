"""Variantes de aldeanos a partir de los 6 NPC de PixelLab: cambio de tono de
ropa (rotación de matiz) y de piel, para poblar las zonas sin créditos nuevos.
Cada variante conserva las 8 direcciones."""
import os
import colorsys
import numpy as np
from PIL import Image

DIRS = ['south', 'south-east', 'east', 'north-east', 'north', 'north-west', 'west', 'south-west']


def skin_colors(base):
    """Colores de piel: tonos cálidos de la cara en la vista sur."""
    a = np.array(Image.open(f'pl/npc/{base}/south.png').convert('RGBA'))
    out = set()
    for y in range(14, 22):
        for x in range(19, 29):
            r, g, b, al = a[y, x]
            if al < 200:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if (h <= 0.11 or h >= 0.96) and 0.2 <= s <= 0.8 and v >= 0.3 and r > b and r >= g:
                out.add((int(r), int(g), int(b)))
    # amplía a todos los tonos del sprite parecidos a la piel de la cara (brazos, manos)
    seeds = np.array(sorted(out), float)
    allc = set()
    for d in DIRS:
        b_ = np.array(Image.open(f'pl/npc/{base}/{d}.png').convert('RGBA'))
        for c in b_[b_[..., 3] > 0][:, :3]:
            allc.add(tuple(int(v) for v in c))
    for c in allc:
        if len(seeds) and np.min(np.abs(seeds - np.array(c)).sum(1)) < 28:
            h, s_, v = colorsys.rgb_to_hsv(*(np.array(c) / 255))
            if (h <= 0.12 or h >= 0.95) and s_ > 0.15:
                out.add(c)
    return out


def recolor(a, skin, hue=0.0, sat=1.0, val=1.0, skin_k=1.0, hue_range=None):
    a = a.copy()
    H, W = a.shape[:2]
    for y in range(H):
        for x in range(W):
            r, g, b, al = a[y, x]
            if al == 0:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if (int(r), int(g), int(b)) in skin:
                # piel: oscurece/aclara conservando el matiz
                v2 = min(1, v * skin_k)
                s2 = min(1, s * (1 + (1 - skin_k) * 0.4))
                rr, gg, bb = colorsys.hsv_to_rgb(h, s2, v2)
            else:
                if s < 0.12 or v < 0.12:       # contornos y grises se quedan
                    continue
                if hue_range and not (hue_range[0] <= h <= hue_range[1]):
                    continue
                rr, gg, bb = colorsys.hsv_to_rgb((h + hue) % 1, min(1, s * sat), min(1, v * val))
            a[y, x, :3] = [int(rr * 255), int(gg * 255), int(bb * 255)]
    return a


VARIANTS = {
    # nombre: (base, hue, sat, val, skin_k, hue_range)
    'pescador': ('aurelio', 0.52, 1.0, 1.0, 0.62, None),
    'pescadora': ('mariela', 0.0, 1.0, 1.0, 0.7, None),
    'petrolero': ('aurelio', 0.0, 0.35, 0.62, 0.9, None),
    'campesina': ('rosa', 0.28, 1.0, 1.0, 1.0, None),
    'campesino': ('aurelio', 0.13, 0.75, 1.0, 0.85, None),
    'abuela_paramo': ('tona', 0.6, 1.1, 0.95, 1.0, None),
    'nino_costa': ('tito', 0.55, 1.1, 1.0, 0.62, None),
    'nina_llanura': ('tito', 0.85, 1.1, 1.0, 1.0, None),
}


def build(name):
    base, hue, sat, val, sk, hr = VARIANTS[name]
    skin = skin_colors(base)
    os.makedirs(f'pl/npc_var/{name}', exist_ok=True)
    for d in DIRS:
        a = np.array(Image.open(f'pl/npc/{base}/{d}.png').convert('RGBA'))
        Image.fromarray(recolor(a, skin, hue, sat, val, sk, hr)).save(f'pl/npc_var/{name}/{d}.png')


def sprite(name, d='south'):
    p = f'pl/npc_var/{name}/{d}.png' if name in VARIANTS else f'pl/npc/{name}/{d}.png'
    return np.array(Image.open(p).convert('RGBA'))


if __name__ == '__main__':
    for n in VARIANTS:
        build(n)
    ims = [Image.fromarray(sprite(n)) for n in VARIANTS]
    c = Image.new('RGBA', (48 * len(ims), 48), (60, 90, 60, 255))
    for i, im in enumerate(ims):
        c.alpha_composite(im, (48 * i, 0))
    c.resize((c.width * 4, c.height * 4), Image.NEAREST).save('out2/npc_vars.png')
