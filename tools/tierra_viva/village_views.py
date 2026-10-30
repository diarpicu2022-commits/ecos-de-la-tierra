"""Vistas de Valdehoja con sus vecinos: plaza, terrazas y mapa entero."""
import os
import numpy as np
from PIL import Image
import scene2, maps2, px, scene, ui
from pal import P

NPCS = [  # nombre, dirección, pie x, pie y
    ('rosa', 'south', 344, 302),          # delante de su puesto de fruta
    ('tona', 'east', 392, 346),           # junto al banco, mirando al árbol
    ('aurelio', 'west', 800, 334),        # a la puerta del molino
    ('tito', 'south-east', 530, 336),     # jugando en la plaza
    ('julian', 'south', 474, 150),        # a la puerta de la capilla
    ('mariela', 'south-west', 640, 490),  # delante de su casa
]


def npc_actors(names=None):
    out = []
    for n, d, x, y in NPCS:
        if names and n not in names:
            continue
        p = f'pl/npc/{n}/{d}.png'
        if not os.path.exists(p):
            p = f'pl/npc/{n}/south.png'
        if not os.path.exists(p):
            continue
        s = scene.trim(np.array(Image.open(p)))
        out.append((s, x - s.shape[1] // 2, y, 22))
    return out


def hero(x, y, d='south'):
    s = scene.trim(np.array(Image.open(f'final/chars/ilan_{d}.png')))
    return (s, x - s.shape[1] // 2, y, 22)


def render(state, view, extra=(), sign=None, dialog=None):
    return scene2.render(state, actors=npc_actors() + list(extra), spec=maps2.VALDEHOJA2,
                         objects=scene2.village2_objects, view=view, sign=sign, dialog=dialog)


NPCS3 = [
    ('rosa', 'south', 528, 384), ('tona', 'east', 584, 414), ('tito', 'south-east', 720, 404),
    ('julian', 'south', 664, 152), ('aurelio', 'west', 1196, 412), ('mariela', 'south-west', 1090, 748),
]


def render3(state, view, extra=(), sign=None, dialog=None):
    global NPCS
    old = NPCS
    NPCS = NPCS3
    try:
        return scene2.render(state, actors=npc_actors() + list(extra), spec=maps2.VALDEHOJA3,
                             objects=scene2.village3_objects, view=view, sign=sign, dialog=dialog)
    finally:
        NPCS = old


NPCS4 = [
    ('rosa', 'south', 528, 384), ('tona', 'east', 584, 414), ('tito', 'south-east', 720, 404),
    ('julian', 'south', 664, 152), ('aurelio', 'west', 1180, 478), ('mariela', 'south-west', 1150, 836),
]


def render4(state, view, extra=(), sign=None, dialog=None):
    global NPCS
    old = NPCS
    NPCS = NPCS4
    try:
        return scene2.render(state, actors=npc_actors() + list(extra), spec=maps2.VALDEHOJA4,
                             objects=scene2.village4_objects, view=view, sign=sign, dialog=dialog)
    finally:
        NPCS = old
