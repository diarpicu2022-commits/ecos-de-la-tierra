"""Escena de mapa del Bosque de las Cenizas, enfermo y purificado, a 640x360."""
import numpy as np
from PIL import Image
import maps, world, flora, scene, ui, px, terrain
from pal import P

TREE = scene.trim(np.array(Image.open('pl/obj2/tree_clean.png')))
BURNT = scene.trim(np.array(Image.open('pl/obj/burnt_clean.png')))

# bases (x de la esquina izquierda, y de la base) de los árboles: muros arriba, abajo y a los lados
TREES = [(-40, 70), (40, 58), (120, 74), (190, 52), (240, 78), (420, 60), (500, 50), (570, 72),
         (-30, 150), (-50, 230), (560, 168), (590, 250),
         (-20, 330), (70, 352), (150, 372), (420, 368), (500, 345), (580, 362)]
BUSHES = [(150, 120), (338, 104), (100, 300), (470, 296), (360, 330), (300, 190)]
ROCKS = [(212, 140), (520, 210), (60, 196), (386, 238)]
FLOWERS = [(176, 128), (272, 116), (320, 290), (140, 248), (470, 120), (520, 300), (220, 300)]


def render(state, actors=(), sign=None, dialog=None):
    sick = state != 'sano'
    C = maps.bosque()
    img, lv = world.terrain(C, state)
    img = img[:360].copy()
    objs = []
    for i, (x, y) in enumerate(TREES):
        t = BURNT if sick else TREE
        if i % 2:
            t = t[:, ::-1]
        objs.append((t, x, y, 46))
    for i, (x, y) in enumerate(BUSHES):
        objs.append((flora.bush('enfermo' if sick else 'sano', seed=i), x, y, 12))
    for x, y in ROCKS:
        objs.append((flora.rock('enfermo' if sick else 'sano'), x, y, 12))
    if not sick:
        for i, (x, y) in enumerate(FLOWERS):
            px.blit(img, flora.flowers(i), x, y - 16)
    else:
        rng = np.random.default_rng(3)
        for _ in range(90):   # brasas y ceniza sobre el suelo
            x, y = rng.integers(0, 640), rng.integers(0, 360)
            if img[y, x, 3]:
                img[y, x] = px.col(P['fire'][3] if rng.random() < 0.3 else P['ash'][3])
    objs += list(actors)
    world.place(img, objs)
    if sick:
        # humo: tramado suelto en bandas, sin mezclar colores
        rng = np.random.default_rng(9)
        for _ in range(4):
            cx, cy = rng.integers(0, 640), rng.integers(20, 300)
            rx, ry = rng.integers(30, 70), rng.integers(6, 12)
            yy, xx = np.mgrid[0:360, 0:640]
            m = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
            m &= ((xx + 2 * yy) % 5 == 0)
            img[m] = px.col(P['smog'][2])
    if sign:
        px.blit(img, ui.sign(*sign), 12, 12)
    if dialog:
        scene.dialog(img, *dialog)
    return img
