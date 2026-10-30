import numpy as np
from PIL import Image
import maps, world, flora, scene, ui, px
from pal import P
HOUSE = np.array(Image.open('pl/obj3/house.png'))
TREE = scene.trim(np.array(Image.open('pl/obj2/tree_clean.png')))


def render(actors=(), sign=None, dialog=None):
    C = maps.valdehoja()
    img, lv = world.terrain(C, 'sano')
    img = img[:360].copy()
    objs = [(HOUSE, 70, 182, 90), (HOUSE, 196, 168, 90), (HOUSE, 360, 182, 90), (HOUSE[:, ::-1], 400, 350, 90)]
    for i, (x, y) in enumerate([(-50, 60), (560, 40), (600, 140), (-40, 300), (40, 372), (590, 330), (480, 70)]):
        t = TREE[:, ::-1] if i % 2 else TREE
        objs.append((t, x, y, 46))
    for i, (x, y) in enumerate([(60, 196), (176, 196), (300, 186), (470, 196), (150, 260), (360, 250)]):
        px.blit(img, flora.flowers(i), x, y - 16)
    for i, (x, y) in enumerate([(30, 198), (282, 190), (470, 206), (320, 352)]):
        objs.append((flora.bush('sano', seed=i), x, y, 12))
    objs += list(actors)
    world.place(img, objs)
    if sign:
        px.blit(img, ui.sign(*sign), 12, 12)
    if dialog:
        scene.dialog(img, *dialog)
    return img
